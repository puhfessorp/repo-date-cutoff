
# Show Repo Dates

Simple utility that scans every git repository under a parent directory, and prints the date of it's latest commit (to the currently staged branch).

## Setup

CD to the repo's directory, then run the following command to setup a pipenv environment:

```pipenv install```

## Invocation

Run the program by navigating to the repo's directory, then executing the following command:

```pipenv run python show-repo-dates.py```

### Arguments

You'll need to provide at least two arguments

#### --source

Provide the parent folder that contains all submitted repo folders with: the ***--source*** argument

#### --cutoff

Provide the cutoff date with the ***--cutoff*** argument

#### --help

See all options with ***--help***

### Invocation Examples

```bash
pipenv run python ./show-repo-dates.py --source /parent/path/to/the/submitted/repos --cutoff "1997-08-29 02:14:00"
```


