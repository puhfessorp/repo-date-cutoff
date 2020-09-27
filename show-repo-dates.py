

# https://gitpython.readthedocs.io/en/stable/index.html
import git
from git import Repo


import argparse
import datetime
from dateutil import parser as date_parser
from dateutil.tz import tzlocal
import time
import os


def main():
	
	args = get_args()
	
	this_machine_now = datetime.datetime.now(tzlocal())
	default_datetime = datetime.datetime.combine(
		this_machine_now,
		datetime.time(0, tzinfo=tzlocal())
	)
	# print("this_machine_now", this_machine_now)
	# print("default_datetime", default_datetime)
	
	cutoff_date_str = args.cutoff_date
	cutoff_date = date_parser.parse(cutoff_date_str, default=default_datetime)
	print("Cutoff date:", cutoff_date)
	
	print()
	for item in os.scandir(args.source):
		
		path = os.path.join(args.source, item)
		
		try:
			
			repo = Repo(path)
			
			head = repo.head
			master = head.reference
			# print("Head is at:", master)
			
			#
			commit = master.commit
			
			status = "OK"
			message = "Last commit happened before the cutoff\t\t\t\t"
			if commit.committed_datetime > cutoff_date:
				
				delta = commit.committed_datetime - cutoff_date
				
				status = "WARN"
				message = "Last commit happened AFTER the cutoff\t(%s)\t" % (delta,)
			
			print(
				"[%s]\t" % (status,),
				message,
				"===>", os.path.basename(repo.working_dir),
				"(%s)" % (commit.author,)
			)
			
			# commit_vars = dir(commit)
			# print(commit_vars)
			
		except git.exc.InvalidGitRepositoryError:
			# This path was not a repo
			pass


def get_args():
	
	parser = argparse.ArgumentParser(prog="Show dates of last commits in repos")
	parser.add_argument(
		"--source", "--source-path", "--dir",
		dest="source",
		default=".",
		help="Directory containing repo directories"
	)
	parser.add_argument(
		"--cutoff", "--date", "--cutoff-date",
		dest="cutoff_date",
		required=True,
		help="Cutoff date; Any commits made after this date will show a warning"
	)
	
	args = parser.parse_args()
	# print("Args:", args)
	
	return args


if __name__ == "__main__":
	main()
