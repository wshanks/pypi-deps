# Python dependency usage search

This repository contains two main files:

+ `pypi-dependencies-bigquery.sql`: A sql script which can be pasted into
  [Google BigQuery](https://console.cloud.google.com/bigquery). As written, it
searches for all Python packages that have declared `qiskit` as a dependency,
but it is easy to replace that string with a different package name. The PyPI
dataset contains all packages including removed ones. Also, the search does not
filter for the latest version first, so it could find packages that used to
depend on something but no longer do.

+ `check_deps.py`: A Python script that searches a list of Python projects for
  a given regular expression. The package list is supplied with the `--file`
argument which should be the path to a file with one package per line (possibly
followed by a comma and additional text). The script uses `pip download` to
download the package (taking a wheel if possible and sdist otherwise). It
currently does not allow specifying an alternate Python version or alternate
platform from the current one. The script also requires a `--regex` argument to
specify the regular expression to use for searching each package. The number of
concurrent download and search threads to use can be set with the `-j`
argument.

There is also the file `qiskit-deps-2024-03-13.csv` showing an example of the
output from running the BigQuery query.
