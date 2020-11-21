
# Check Repos Against Cutoff Date

Simple utility that checks git repos against a cutoff date, by Mike Peralta.

This progam does the following:

1. Takes a cutoff date via CLI argument
2. Takes a parent directory to scan via CLI argument
3. Scans every git repository under the parent directory
4. For each repo found:
    1. Examines the most recent commit in the repo (currently staged branch)
    2. Checks the commit's date against the cutoff date
    3. Emits a message regarding the previous comparison, in a tidy table

This is only a quick report. You must manually checkout older commits if you wish to enforce a cutoff date.

## Requirements

* python3
* pipenv

## Setup

CD to the repo's directory, then run the following command to setup a pipenv environment that satisfies all python-related dependencies:

```shell script
$ cd /path/to/repo
$ pipenv install
```

## Invocation

Run directly by navigating to the repo's directory, then executing the following command:

```shell script
$ cd /path/to/repo
$ pipenv run python main.py --help
```

Alternatively, run in a pipenv shell like so:

```shell script
$ cd /path/to/repo
$ pipenv shell
$ ./main.py --help
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
```shell script
$ cd /path/to/repo
$ pipenv run python ./main.py --help
```

*Check a directory containing repos*
```shell script
$ cd /path/to/repo
$ pipenv run python ./main.py --source /parent/path/to/the/submitted/repos --cutoff "1997-08-29 02:14:00"
```




