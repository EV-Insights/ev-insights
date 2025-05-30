SELECT cst.id, COUNT(css.id) as num_charges
FROM evinsights."ChargingStation" as cst, evinsights."ChargingSession" as css, evinsights."Dataset" as d, evinsights."User" as u
WHERE css.fk_charging_station_id = cst.id
AND css.fk_dataset_id = d.id
AND css.fk_user_id = u.id
GROUP BY cst.id
ORDER BY num_charges DESC;
