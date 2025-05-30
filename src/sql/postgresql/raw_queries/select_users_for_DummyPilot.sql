-- This Query generates a csv file used to fill user table for DummyPilot (the 20 users with the most charging sessions are selected )
SELECT u.*
FROM evinsights."User" u, evinsights."ChargingSession" cse
WHERE cse.fk_user_id = u.id
AND cse.fk_user_id IN (
    SELECT cse.fk_user_id
    FROM evinsights."ChargingSession" as cse
    WHERE cse.fk_user_id IS NOT NULL
    GROUP BY cse.fk_user_id
    ORDER BY count(*) DESC
    LIMIT 20
)
GROUP BY u.id;
