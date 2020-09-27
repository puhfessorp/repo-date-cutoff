
# Check Repos Against Cutoff Date

Simple utility that checks git repos against a cutoff date:

1. Takes a cutoff date via CLI argument
2. Takes a parent directory to scan via CLI argument
3. Scans every git repository under the parent directory
4. For each repo found:
    1. Examines the most recent commit in the repo (currently staged branch)
    2. Checks the commit's date against the cutoff date
    3. Emits an "OK" if the commit happened before the cutoff date; Emits a "WARN" otherwise

This is only a quick report. You must manually checkout older commits if you wish to enforce a cutoff date.

## Setup

CD to the repo's directory, then run the following command to setup a pipenv environment:

```bash
pipenv install
```

## Invocation

Run the program by navigating to the repo's directory, then executing the following command:

```bash
pipenv run python show-repo-dates.py
```

### Arguments

You'll need to provide at least two arguments

#### --source

Provide the parent folder that contains all submitted repo folders with: the ***--source*** argument

#### --cutoff

Provide the cutoff date with the ***--cutoff*** argument

#### --help

See all options with ***--help***

### Invocation Examples

*See help / available options*
```bash
pipenv run python ./check-repos-against-date.py --help
```

```bash
pipenv run python ./check-repos-against-date.py --source /parent/path/to/the/submitted/repos --cutoff "1997-08-29 02:14:00"
```




