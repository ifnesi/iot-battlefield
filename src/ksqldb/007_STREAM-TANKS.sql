CREATE STREAM IF NOT EXISTS `$TANKS.kafka.topic_data-joined` AS
SELECT
    TM.id AS `ID`,
    T.model,
    TM.lat,
    TM.lon,
    TM.ammo,
    TM.damage,
    TM.destroyed,
    TM.current_speed,
    TM.timestamp AS `TIMESTAMP`
FROM `$TANKS.kafka.topic_data_moves` AS TM
JOIN `$TANKS.kafka.topic_data` AS T ON TM.id = T.`key`;
