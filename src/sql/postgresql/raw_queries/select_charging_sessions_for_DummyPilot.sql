-- This Query generates a csv file used to fill charging session table for DummyPilot
SELECT cse.*, u.orig_id as user_orig_id, cst.orig_id as charging_station_orig_id
FROM evinsights."ChargingSession" cse, evinsights."User" u, evinsights."ChargingStation" cst
WHERE cse.fk_user_id = u.id
AND cse.fk_charging_station_id = cst.id
AND cse.fk_user_id in (88, 52, 90, 55, 9406, 9414, 69, 101, 37, 65);
