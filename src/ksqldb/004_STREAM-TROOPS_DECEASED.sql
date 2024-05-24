CREATE STREAM IF NOT EXISTS `$TROOPS.kafka.topic_data-deceased` AS
SELECT
    T.id,
    T.name,
    T.rank,
    T.height,
    T.weight,
    T.blood_type,
    T.lat,
    T.lon,
    T.ammo,
    T.injury,
    T.injury_time,
    T.timestamp AS `TIMESTAMP`
FROM `$TROOPS.kafka.topic_data-joined` AS T
WHERE T.DECEASED;