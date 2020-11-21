

# https://gitpython.readthedocs.io/en/stable/index.html
import git
from git import Repo


import datetime
import dateutil
from dateutil import parser as date_parser
from dateutil.tz import tzlocal
import multiprocessing
import os
import tabulate
import threading
# import time


class RepoDateCutoff:
	
	def __init__(self):
		
		pass
	
	def log(self, s):
		
		to_log = s
		to_print = "[%s] %s" % (type(self).__name__, to_log)
		
		print(to_print)
	
	def check(self, repos_dir, cutoff_date_string):
		
		self.log("Repo date cutoff checker, by Mike Peralta")
		
		self.log("Begin checking repos against cutoff date")
		self.log("> Repos directory: %s" % (repos_dir,))
		self.log("> Cutoff date string: %s" % (cutoff_date_string,))
		
		cutoff_date = self.parse_date_string(date_string=cutoff_date_string)
		self.log("> Cutoff date: %s" % (cutoff_date,))
		
		repos_dirs = [f for f in os.scandir(repos_dir)]
		self.log("> Found %s potential repo directories" % (len(list(repos_dirs))))
		
		self.log("Gathering repo dirs")
		repo_entries = []
		for item in repos_dirs:
			path = os.path.join(repos_dir, item)
			repo = RepoEntry(path=path, cutoff_date=cutoff_date)
			repo_entries.append(repo)
		
		cpus_count = multiprocessing.cpu_count()
		repos_to_parse = repo_entries.copy()
		threads = []
		mutex = threading.RLock()
		for i in range(cpus_count):
			t = threading.Thread(
				target=self._repo_entries_check_thread,
				kwargs={
					"repo_entries": repos_to_parse,
					"mutex": mutex
				}
			)
			threads.append(t)
		self.log("Starting %s threads" % (len(threads)))
		for t in threads:
			t.start()
		self.log("Waiting for all threads to finish")
		for t in threads:
			t.join()
		print()
		self.log("All threads finished")
		
		valid_repo_entries = []
		for entry in repo_entries:
			for line in entry.get_logs():
				self.log(line)
			if entry.is_valid_repo():
				valid_repo_entries.append(entry)
		
		self.log("Found %s valid repo entries" % (len(valid_repo_entries)))
		
		self.log("Final report:\n%s" % (self._render_report(repo_entries=valid_repo_entries)))
	
	def _repo_entries_check_thread(self, repo_entries: list, mutex: threading.RLock):
		
		self.log("")
		
		while True:
			
			# noinspection PyTypeChecker
			repo: RepoEntry = None
			
			# Grab the next repo to check
			mutex.acquire()
			if len(repo_entries) > 0:
				repo = repo_entries.pop()
			mutex.release()
			
			if repo is None:
				break
			
			repo.consume()
			print(".", end="")
	
	@staticmethod
	def _render_report(repo_entries):
	
		s = ""
		data_ok = []
		data_late = []
		headers = ["Repo", "Author", "Status", "Delta", "Message"]
		
		for entry in repo_entries:
			
			row = [
				entry.get_dir_name(),
				entry.get_author(),
				entry.get_status(),
				entry.get_delta(),
				entry.get_message()
			]
			
			if entry.is_late():
				data_late.append(row)
			
			else:
				data_ok.append(row)
		
		s += "\n%s OK entries:\n" % (len(data_ok))
		s += tabulate.tabulate(
			headers=headers,
			tabular_data=data_ok,
			tablefmt="grid"
		)
		s += "\n"
		
		s += "\n%s late entries:\n" % (len(data_late))
		s += tabulate.tabulate(
			headers=headers,
			tabular_data=data_late,
			tablefmt="grid"
		)
		
		return s
	
	def parse_date_string(self, date_string):
		
		self.log("Parsing date string: %s" % (date_string,))
		
		this_machine_now = datetime.datetime.now(tzlocal())
		
		default_datetime = datetime.datetime.combine(
			this_machine_now,
			datetime.time(0, tzinfo=tzlocal())
		)
		
		try:
			date_parsed = date_parser.parse(date_string, default=default_datetime)
		except ValueError as e:
			self.log("Failed to parse date: %s !!!" % (date_string,))
			raise e
		
		self.log("Date is actually: %s" % (date_parsed,))
		
		return date_parsed


class RepoEntry:
	
	def __init__(self, path, cutoff_date):
		
		self.__path = os.path.abspath(path)
		self.__dir_name = os.path.basename(self.__path)
		
		self.__cutoff_date = cutoff_date
		
		self.__author = None
		self.__status = None
		self.__message = None
		self.__delta = None
		self.__valid_repo = None
		self.__late = None
		
		# noinspection PyTypeChecker
		self.__logs: list = None
		
		self.__is_dirty = True
	
	def log(self, s):
		
		to_log = "[%s][%s] %s" % (type(self).__name__, self.__dir_name, s)
		
		self.__logs.append(to_log)
	
	def get_logs(self):
		
		return self.__logs
	
	def set_path(self, p):
		
		self.__path = p
		
		self.__is_dirty = True
	
	def consume(self):
		
		if not self.__is_dirty:
			return
		
		try:
			
			self.__logs = []
			self.log("Begin consume")
			
			repo = Repo(self.__path)
			
			head = repo.head
			master = head.reference
			# print("Head is at:", master)
			
			#
			commit = master.commit
			
			self.__author = commit.author
			self.__status = "OK"
			self.__message = "Last commit within cutoff"
			self.__late = False
			self.__delta = 0
			
			self.log("Commit author: %s" % (self.__author,))
			
			if commit.committed_datetime > self.__cutoff_date:
				
				self.__delta = commit.committed_datetime - self.__cutoff_date
				
				self.__status = "LATE"
				self.__message = "Last commit AFTER cutoff!"
				self.__late = True
				# self.log("Debug: %s vs. %s ==> %s" % (self.__cutoff_date, commit.committed_datetime, self.__delta))
				
				self.log("Last commit happened %s seconds after the cutoff date" % (self.__delta,))
				
			else:
				
				self.log("Last commit with cutoff")
			
			self.__valid_repo = True
		
		# commit_vars = dir(commit)
		# print(commit_vars)
		
		except git.exc.InvalidGitRepositoryError:
			# This path was not a repo
			self.__valid_repo = False
		
		self.__is_dirty = False
	
	def get_dir_name(self):
	
		return self.__dir_name
	
	def is_valid_repo(self):
		
		return self.__valid_repo

	def is_late(self):
		
		return self.__late
	
	def get_status(self):
		
		return self.__status
	
	def get_message(self):
		
		return self.__message
	
	def get_delta(self):
		
		return self.__delta

	def get_author(self):
		
		return self.__author
