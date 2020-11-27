#!/usr/bin/env python


from RepoDateCutoff import RepoDateCutoff


import argparse


def main():
	
	args = get_args()
	
	checker = RepoDateCutoff(
		use_multithreading=args.use_multithreading
	)
	
	checker.check(
		repos_dir=args.source,
		branch_name=args.branch_name,
		cutoff_date_string=args.cutoff_date,
		do_first_commit=args.do_first_commit
	)


def get_args():
	
	parser = argparse.ArgumentParser(
		prog="Repo cutoff date checker, by Mike Peralta",
		description="Checks all repos inside a source directory against a cutoff date, and prints results in a tidy table."
	)
	
	parser.add_argument(
		"--source", "--source-path", "--dir", "--repos",
		dest="source",
		default=".",
		help="Directory containing repo directories."
	)
	
	parser.add_argument(
		"--branch", "--branch-name",
		dest="branch_name",
		default=None,
		required=False,
		help="Specify a branch to use"
	)
	
	parser.add_argument(
		"--cutoff", "--date", "--cutoff-date",
		dest="cutoff_date",
		required=False,
		default=None,
		help="Cutoff date; Any commits made after this date will show a warning."
	)
	parser.add_argument(
		"--first-commit",
		dest="do_first_commit",
		default=False,
		action="store_true",
		help="Ignore the cutoff date and just checkout every repo's initial commit."
	)
	
	parser.add_argument(
		"--single-thread", "--one-thread", "--no-multithreading",
		dest="use_multithreading",
		default=True,
		action="store_false",
		help="Don't use multithreading"
	)
	
	args = parser.parse_args()
	# print("Args:", args)
	
	return args


if __name__ == "__main__":
	main()
