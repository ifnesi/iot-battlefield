CREATE STREAM IF NOT EXISTS `$TROOPS.kafka.topic_data-joined` AS
SELECT
    TM.id AS `ID`,
    T.`key` AS `KEY`,
    T.name,
    T.rank,
    T.height,
    T.weight,
    T.blood_type,
    TM.lat,
    TM.lon,
    TM.body_temperature,
    TM.pulse_rate,
    TM.ammo,
    TM.injury,
    TM.injury_time,
    TM.deceased,
    TM.timestamp AS `TIMESTAMP`
FROM `$TROOPS.kafka.topic_move` AS TM
JOIN `$TROOPS.kafka.topic_data` AS T ON TM.id = T.`key`;
