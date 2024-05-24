CREATE STREAM IF NOT EXISTS `$TROOPS.kafka.topic_data-injuried` AS
SELECT
    T.id,
    T.name,
    T.rank,
    T.height,
    T.weight,
    T.blood_type,
    T.lat,
    T.lon,
    T.body_temperature,
    T.pulse_rate,
    T.ammo,
    T.injury,
    T.injury_time,
    T.deceased,
    T.timestamp AS `TIMESTAMP`
FROM `$TROOPS.kafka.topic_data-joined` AS T
WHERE
    T.injury IS NOT NULL;
