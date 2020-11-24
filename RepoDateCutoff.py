

# https://gitpython.readthedocs.io/en/stable/index.html
import git
from git import Repo


import datetime
from dateutil import parser as date_parser
from dateutil.tz import tzlocal
import multiprocessing
import os
import tabulate
import threading


class RepoDateCutoff:
	
	def __init__(self, use_multithreading=True):
		
		self.__use_multithreading = use_multithreading
		
		# noinspection PyTypeChecker
		self.__valid_repos: list = None
	
	def log(self, s=""):
		
		to_log = s
		
		if to_log == "":
			to_print = ""
		else:
			to_print = "[%s] %s" % (type(self).__name__, to_log)
		
		print(to_print)
	
	def check(self, repos_dir, cutoff_date_string=None, do_first_commit=False):
		
		self.log("Repo date cutoff checker, by Mike Peralta")
		
		self.log("Begin checking repos against cutoff date")
		self.log("> Repos directory: %s" % (repos_dir,))
		self.log("> Cutoff date string: %s" % (cutoff_date_string,))
		
		if cutoff_date_string is None:
			cutoff_date_string = str(self.get_now())
			self.log("> No cutoff date specified; Using now: %s" % (cutoff_date_string,))
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
		
		threads_count = self._get_thread_count_to_use()
		repos_to_parse = repo_entries.copy()
		threads = []
		mutex = threading.RLock()
		for i in range(threads_count):
			t = threading.Thread(
				target=self._repo_entries_check_thread,
				kwargs={
					"repo_entries": repos_to_parse,
					"do_first_commit": do_first_commit,
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
		self.__valid_repos = valid_repo_entries
		
		self.log("Found %s valid repo entries" % (len(valid_repo_entries)))
		
		self.log()
		self.log(self._render_current_commits_report())
		
		self.log("")
		self.log(self._render_current_state_report())
		
		self.log("")
		self.log(self._render_recommended_checkouts())
		
		self._do_recommended_checkouts()
	
	def _get_thread_count_to_use(self):
		
		if self.__use_multithreading:
			return multiprocessing.cpu_count()
	
		return 1
	
	@staticmethod
	def _repo_entries_check_thread(repo_entries: list, do_first_commit, mutex: threading.RLock):
		
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
			
			repo.consume(do_first_commit=do_first_commit)
			print(".", end="")
	
	def _do_recommended_checkouts(self, force=False):
	
		self.log("Performing recommended checkouts in %s mode" % ("auto" if force is True else "interactive"))
		
		headers = self.row = self._render_recommended_checkouts_headers()
		
		for repo in self.__valid_repos:
			
			repo: RepoEntry
			
			if repo.get_current_commit() == repo.get_recommended_commit():
				continue
			
			table = tabulate.tabulate(
				headers=headers,
				tabular_data=[self._render_recommended_checkout_row(repo=repo)],
				tablefmt="grid"
			)
			self.log("")
			self.log("Next repo with recommended action:\n%s" % (table,))
			
			do_checkout = force
			if do_checkout is False:
				
				the_input = input("Force this repo? [Y]es / [N]o / [A]ll / [Q]uit ===> ")
				assert the_input in ["Y", "y", "N", "n", "A", "a", "Q", "q"], "Invalid input"
				
				if the_input == "Q" or the_input == "q":
					self.log("Quitting!")
					return
				if the_input == "Y" or the_input == "y" or the_input == "A" or the_input == "a":
					do_checkout = True
				if the_input == "A" or the_input == "a":
					force = True
			
			if do_checkout is True:
				
				self.log("> Doing checkout")
				
				repo.do_recommended_checkout()
				
				self.log("> Checkout complete")
				
			else:
				self.log("> Ignoring checkout")
		
		self.log("")
		self.log("Done performing recommended checkouts")
	
	def _render_recommended_checkouts(self):
		
		s = ""
		data = []
		
		for repo in self.__valid_repos:
			
			repo: RepoEntry
			
			if repo.get_current_commit() == repo.get_recommended_commit():
				continue
			
			row = self._render_recommended_checkout_row(repo=repo)
			
			data.append(row)
		
		s += "%s recommended checkouts:\n" % (len(data),)
		s += tabulate.tabulate(
			headers=self._render_recommended_checkouts_headers(),
			tabular_data=data,
			tablefmt="grid"
		)
		
		return s
	
	@staticmethod
	def _render_recommended_checkouts_headers():
		
		return ["Repo", "Commits (Total)", "Commits (Exclude)", "Commit", "Author", "Commit Date", "Delta"]
	
	@staticmethod
	def _render_recommended_checkout_row(repo):
		
		repo: RepoEntry
		
		row = [
			repo.get_dir_name(),
			repo.get_branch_commits_count(),
			repo.get_excluded_commits_count(),
			str(repo.get_recommended_commit())[0:8],
			repo.get_recommended_commit_author(),
			repo.get_recommended_commit_date(),
			repo.get_recommended_commit_delta()
		]
		
		return row
	
	def _render_current_commits_report(self):
		
		s = ""
		data = []
		headers = ["Repo", "Commits", "Commit", "Date"]
		
		for entry in self.__valid_repos:
			
			entry: RepoEntry
			
			row = [
				entry.get_dir_name(),
				entry.get_branch_commits_count(),
				str(entry.get_current_commit())[:8],
				entry.get_current_commit_date()
			]
			
			data.append(row)
		
		s += "\nCurrent state of commits:\n"
		s += tabulate.tabulate(
			headers=headers,
			tabular_data=data,
			tablefmt="grid"
		)
		s += "\n"
		
		return s
	
	def _render_current_state_report(self):
		
		s = ""
		data = []
		headers = ["Repo", "Commits", "Commit", "Author", "Date", "Delta"]
		
		for entry in self.__valid_repos:
			
			entry: RepoEntry
			
			row = [
				entry.get_dir_name(),
				entry.get_branch_commits_count(),
				str(entry.get_current_commit())[:8],
				entry.get_current_commit_author(),
				entry.get_current_commit_date(),
				entry.get_current_commit_delta()
			]
			
			data.append(row)
		
		s += "\nCurrent state; %s valid repos:\n" % (len(self.__valid_repos))
		s += tabulate.tabulate(
			headers=headers,
			tabular_data=data,
			tablefmt="grid"
		)
		s += "\n"
		
		return s
	
	def parse_date_string(self, date_string):
		
		self.log("Parsing date string: %s" % (date_string,))
		
		try:
			now = self.get_now()
			date_parsed = date_parser.parse(date_string, default=now)
		except ValueError as e:
			self.log("Failed to parse date: %s !!!" % (date_string,))
			raise e
		
		self.log("Date is actually: %s" % (date_parsed,))
		
		return date_parsed
	
	@staticmethod
	def get_now():
		
		this_machine_now = datetime.datetime.now(tzlocal())
		
		return this_machine_now


class RepoEntry:
	
	def __init__(self, path, cutoff_date):
		
		self.__path = os.path.abspath(path)
		self.__dir_name = os.path.basename(self.__path)
		
		# noinspection PyTypeChecker
		self.__repo: Repo = None
		self.__cutoff_date = cutoff_date
		
		# noinspection PyTypeChecker
		self.__commits_count: int = None
		self.__valid_repo = None
		
		# noinspection PyTypeChecker
		self.__first_commit: git.objects.commit.Commit = None
		
		# noinspection PyTypeChecker
		self.__current_commit: git.objects.commit.Commit = None
		self.__current_commit_author = None
		self.__current_commit_delta = None
		
		# noinspection PyTypeChecker
		self.__recommended_commit: git.objects.commit.Commit = None
		self.__recommended_commit_author = None
		self.__recommended_commit_delta = None
		self.__excluded_commit_count = None
		
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
	
	def consume(self, do_first_commit):
		
		if not self.__is_dirty:
			return
		
		try:
			
			self.__logs = []
			self.log("Begin consume")
			
			self.__repo = Repo(self.__path)
			
			if self.__repo.head.is_detached:
				self.__current_commit = self.__repo.head.commit
			else:
				self.__current_commit = self.__repo.head.reference.commit
			self.__current_commit_author = self.__current_commit.author
			self.__current_commit_delta = self.__current_commit.committed_datetime - self.__cutoff_date
			self.log("Current commit delta: %s" % (self.__current_commit_delta,))
			
			self._determine_recommended_commit(do_first_commit=do_first_commit)
			
			self.__valid_repo = True
		
		# commit_vars = dir(commit)
		# print(commit_vars)
		
		except git.exc.InvalidGitRepositoryError:
			# This path was not a repo
			self.__valid_repo = False
		
		self.__is_dirty = False
	
	def _determine_recommended_commit(self, do_first_commit):
		
		# Default to the recommended commit being the latest one on the active branch
		latest_master_commit = self.__repo.heads.master.commit
		latest_master_commit: git.objects.commit.Commit
		
		self.__author = latest_master_commit.author
		self.log("Commit author: %s" % (self.__author,))
		
		# Find the first commit, and count them all
		self.__commits_count = 1
		self.__first_commit = latest_master_commit
		for c in latest_master_commit.iter_parents():
			self.__first_commit = c
			self.__commits_count += 1
		
		# Possibly just checkout the first commit
		if do_first_commit is True:
			
			self.__recommended_commit = self.__first_commit
			self.__excluded_commit_count = self.__commits_count - 1
		
		# If the latest commit is beyond the cutoff date, search backward for one that is within the cutoff
		elif latest_master_commit.committed_datetime > self.__cutoff_date:
			
			self.log("Searching for a previous commit within the cutoff date, starting with %s:" % (latest_master_commit,))
			self.__recommended_commit = self.__first_commit
			self.__excluded_commit_count = 0
			for c in latest_master_commit.iter_parents():
				self.log("Examining: %s" % (c,))
				self.__excluded_commit_count += 1
				if c.committed_datetime <= self.__cutoff_date:
					self.__recommended_commit = c
					self.log("> Commit %s is within the cutoff, at: %s" % (c, c.committed_datetime))
					break
				else:
					self.log("> Commit also isn't within cutoff date: %s" % (str(c),))
			if self.__recommended_commit == latest_master_commit:
				self.log("> Failed to find a commit within the cutoff date!")
		
		else:
			
			self.__recommended_commit = latest_master_commit
			self.__excluded_commit_count = 0
			self.log("Looks like the latest master commit is within the cutoff")
		
		self.__recommended_commit_delta = self.__recommended_commit.committed_datetime - self.__cutoff_date
		self.log("Recommended commit delta: %s" % (self.__recommended_commit_delta,))
	
	def do_recommended_checkout(self):
		
		self.__repo.head.reference = self.__recommended_commit
	
	def get_dir_name(self):
	
		return self.__dir_name
	
	def is_valid_repo(self):
		
		return self.__valid_repo
	
	def get_current_commit_date(self):
		
		return self.__current_commit.committed_datetime
	
	def get_current_commit_delta(self):
		
		return self.__current_commit_delta
	
	def get_recommended_commit_delta(self):
		
		return self.__recommended_commit_delta
	
	def get_current_commit_author(self):
		
		return self.__current_commit_author
	
	def get_branch_commits_count(self):
		
		return self.__commits_count
	
	def get_included_commits_count(self):
		
		return self.get_branch_commits_count() - self.get_excluded_commits_count()
	
	def get_excluded_commits_count(self):
		
		return self.__excluded_commit_count
	
	def get_current_commit(self):
		
		return self.__current_commit
	
	def get_recommended_commit(self):
		
		return self.__recommended_commit
	
	def get_recommended_commit_author(self):
		
		return self.__recommended_commit.author
	
	def get_recommended_commit_date(self):
		
		return self.__recommended_commit.committed_datetime
