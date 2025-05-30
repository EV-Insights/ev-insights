SELECT u.id, COUNT(cs.id) AS num_sessions
FROM evinsights."User" u
LEFT JOIN evinsights."ChargingSession" cs ON u.id = cs.fk_user_id
GROUP BY u.id
ORDER BY num_sessions DESC;