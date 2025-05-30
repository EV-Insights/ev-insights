# Queries for data ingestion
get_charging_point_type_id_by_type = """
    SELECT id
    FROM evinsights."ChargingPointType"
    WHERE charging_point_type = (%s)
"""

get_charging_stations = """
    SELECT id, orig_id
    FROM evinsights."ChargingStation"
    WHERE dataset_id = %s
"""

get_users = """
    SELECT id, orig_id
    FROM evinsights."User"
    WHERE dataset_id = %s OR %s IS NULL
"""

insert_charging_point_types = """
    INSERT INTO evinsights."ChargingPointType" (charging_point_type)
    VALUES (%s)
"""

insert_dataset_info = """ 
    INSERT INTO evinsights."Dataset" (name, url, description, owner, country, region, city, file_name, file_type, delimiter, encoding, 
                                   license, charging_point_type, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

insert_charging_stations = """
    INSERT INTO evinsights."ChargingStation" (orig_id, manufacturer, model, type, num_plugs, max_charging_power, max_discharging_power, 
                                           dataset_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

insert_charging_sessions = """
    INSERT INTO evinsights."ChargingSession" (plug_in_datetime, plug_out_datetime, charge_end_datetime, charge_end_datetime_presence, 
                                             energy_supplied, fk_dataset_id, fk_charging_station_id, fk_user_id) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

insert_users = """
    INSERT INTO evinsights."User" (orig_id, ev_id, ev_manufacturer, ev_model, ev_battery_capacity, ev_battery_type, 
                                  ev_battery_useable_capacity, ev_v2g, ev_max_charging_power, ev_max_discharging_power, dataset_id) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Queries for analysis
get_plug_in_datetime_and_energy_supplied = """
    SELECT plug_in_datetime, energy_supplied
    FROM evinsights."ChargingSession"
"""


# TODO generic query for analysis to select any column from DB
# Queries for analysis


# Queries for getting dataset info
get_dataset_list = """
    SELECT name
    FROM evinsights."Dataset";
"""

# Query to get the number of tables
get_number_of_tables = """
     SELECT schemaname, tablename
     FROM pg_tables
     WHERE schemaname IN ('evinsights');
 """

# Get dataset_id by name
get_dataset_id_by_name = """
    SELECT id
    FROM evinsights."Dataset"
    WHERE name = %s;
"""

# Get dataset_name by id
get_dataset_name_by_id = """
    SELECT name
    FROM evinsights."Dataset"
    WHERE id = %s;
"""

# Check column existence
check_column_existence = """
    SELECT table_name
    FROM information_schema.columns
    WHERE column_name = %s
    AND table_schema = 'evinsights';
"""

# Dynamic query
dynamic_query = """
    SELECT %s
    FROM evinsights."ChargingSession" as cse 
	LEFT JOIN evinsights."Dataset" as d ON cse.fk_dataset_id = d.id 
	LEFT JOIN evinsights."ChargingStation" as cst ON cse.fk_charging_station_id = cst.id
	LEFT JOIN evinsights."User" as u ON cse.fk_user_id = u.id
    WHERE d.name IN %s
    AND (%s IS NULL OR cse.plug_in_datetime >= %s)
    AND (%s IS NULL OR cse.plug_in_datetime <= %s)
    AND (%s IS NULL OR u.id = %s)
    AND (%s IS NULL OR cst.id = %s);
"""

insert_charging_station_forecast = """ 
    INSERT INTO evinsights."ChargingStationForecast" (date, energy, connections, experiment_id, run_id, created_at, fk_charging_station_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

insert_user_forecast = """ 
    INSERT INTO evinsights."UserForecast" (date, energy, duration, experiment_id, run_id, created_at, fk_user_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

# Get last user prediction
get_user_prediction = """
    SELECT *
    FROM evinsights."UserForecast"
    WHERE fk_user_id = %s
    AND date = %s
    ORDER BY created_at DESC
    LIMIT 1;
"""

# Get last charging_station prediction
get_charging_station_prediction = """
    SELECT *
    FROM evinsights."ChargingStationForecast"
    WHERE fk_charging_station_id = %s
    AND date = %s
    ORDER BY created_at DESC
    LIMIT 1;
"""

get_user_ids = """
    SELECT id
    FROM evinsights."User"
    WHERE dataset_id = %s OR %s IS NULL
"""

get_charging_station_ids = """
    SELECT id
    FROM evinsights."ChargingStation"
    WHERE dataset_id = %s OR %s IS NULL
"""