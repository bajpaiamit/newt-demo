SELECT
    locations.record_location.field_id.name AS field_name,
    info_type.name,
    likelihood,
    COUNT(*) AS count_total
FROM
`{}.{}.{}`,
UNNEST(location.content_locations) AS locations
WHERE (likelihood in ("{}"))
AND job_name = '{}'
GROUP BY
    locations.record_location.field_id.name,
    info_type.name,
    likelihood
ORDER BY locations.record_location.field_id.name