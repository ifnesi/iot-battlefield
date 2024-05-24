CREATE STREAM IF NOT EXISTS `$FLC.kafka.topic_data-joined` AS
SELECT
    TM.id AS `ID`,
    T.`key` AS `KEY`,
    T.city,
    T.lat,
    T.lon,
    TM.food,
    TM.health,
    TM.ammo,
    TM.timestamp AS `TIMESTAMP`
FROM `$FLC.kafka.topic_move` AS TM
JOIN `$FLC.kafka.topic_data` AS T ON TM.id = T.`key`;
