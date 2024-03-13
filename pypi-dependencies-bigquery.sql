# Query to find all packages that have ever depended on a package (here, qiskit)
# Query that can be entered into Google BigQuery
# "qiskit" can be replaced with another package name
#
# Note that the dataset includes packages that were removed from PyPI so some
# might not be available now.
#
# Query does not preserve version. The dependency could have been removed in a
# later version

SELECT sq.name, MAX(sq.upload_time)
FROM (
  SELECT raw.name as name, raw.upload_time as upload_time
  FROM `bigquery-public-data.pypi.distribution_metadata` as raw
  WHERE (
    SELECT COUNT(1)
    FROM UNNEST(raw.requires_dist) as rd
    WHERE rd LIKE "qiskit %" OR rd = "qiskit"
  ) >= 1
  ORDER BY raw.upload_time
) as sq
GROUP BY sq.name
