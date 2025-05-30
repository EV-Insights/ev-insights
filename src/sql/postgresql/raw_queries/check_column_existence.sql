SELECT table_name
FROM information_schema.columns
WHERE column_name = 'energy_supplied'
AND table_schema = 'evinsights';