
# Check Repos Against Cutoff Date

Simple utility that checks git repositories against a cutoff date, by Mike Peralta.

This program does the following:

1. Takes a cutoff date via CLI argument

2. Takes a parent directory to scan via CLI argument

3. Scans every git repository under the parent directory

4. For each repo found:

    1. Examines the most recent commit in the repo (currently staged branch)

    2. Starting with the default branch, locates the most recent commit that happened before the cutoff date

    3. Emits various summary tables of the current and recommended states

5. Will adjust each repo one by one (interactive), or do them all automatically.

By default, the program will use multiple threads to analyze the repositories, to help reduce lag caused by executing git commands under the hood.

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

#### --first-commit

Instead of comparing against a cutoff date, just reset each repository to the very first commit of its default branch.

#### --single-thread

Only use 1 thread for all operations (helpful for debugging)

#### --help

See all options with ***--help***

### Invocation Examples

*See help / available options*
```shell script
$ cd /path/to/repo
$ pipenv run python ./main.py --help
```

*Check a directory containing repositories*
```shell script
$ cd /path/to/repo
$ pipenv run python ./main.py --source /parent/path/to/the/submitted/repos --cutoff "1997-08-29 02:14:00"
```

*Set all repositories to the first commit of their default branch*
```shell script
$ cd /path/to/repo
$ pipenv run python ./main.py --source /parent/path/to/the/submitted/repos --first-commit
```




