-- This Query generates a csv file used to fill charging station table for DummyPilot (the 20 users with the most charging sessions are selected )
SELECT cst.*
FROM evinsights."ChargingStation" cst, evinsights."ChargingSession" cse
WHERE cse.fk_charging_station_id = cst.id
AND cse.fk_charging_station_id IN (
    SELECT cse.fk_charging_station_id
    FROM evinsights."ChargingSession" as cse
    WHERE cse.fk_charging_station_id IS NOT NULL
    GROUP BY cse.fk_charging_station_id
    ORDER BY count(*) DESC
    LIMIT 20
)
GROUP BY cst.id;
