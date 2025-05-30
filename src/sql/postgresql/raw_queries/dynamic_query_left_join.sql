SELECT d.name, cse.plug_in_datetime, cse.plug_out_datetime, cse.energy_supplied, u.ev_max_charging_power
FROM evinsights."ChargingSession" as cse
	LEFT JOIN evinsights."Dataset" as d ON cse.fk_dataset_id = d.id
	LEFT JOIN evinsights."ChargingStation" as cst ON cse.fk_charging_station_id = cst.id
	LEFT JOIN evinsights."User" as u ON cse.fk_user_id = u.id
WHERE d.name='ACN_Caltech';

