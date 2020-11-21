#!/usr/bin/env python


from RepoDateCutoff import RepoDateCutoff


import argparse


def main():
	
	args = get_args()
	
	checker = RepoDateCutoff()

	checker.check(
		repos_dir=args.source, cutoff_date_string=args.cutoff_date
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
		"--cutoff", "--date", "--cutoff-date",
		dest="cutoff_date",
		required=True,
		help="Cutoff date; Any commits made after this date will show a warning."
	)
	
	args = parser.parse_args()
	# print("Args:", args)
	
	return args


if __name__ == "__main__":
	main()
