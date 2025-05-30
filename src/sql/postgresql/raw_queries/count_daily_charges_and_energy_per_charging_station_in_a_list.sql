SELECT 
    DATE(plug_in_datetime) AS date,
    fk_charging_station_id, COUNT(*) as number_charges,
    SUM(energy_supplied) AS total_energy_supplied
FROM 
    evinsights."ChargingSession"
WHERE 
    fk_charging_station_id IN (1855, 1870, 1874, 1865, 1862, 1867)
GROUP BY 
    DATE(plug_in_datetime), 
    fk_charging_station_id
ORDER BY 
    fk_charging_station_id ASC,
    date ASC;