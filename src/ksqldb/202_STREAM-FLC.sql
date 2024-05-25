CREATE STREAM IF NOT EXISTS `$FLC.kafka.topic_data-joined` AS
SELECT
    TM.id AS `id`,
    T.`key` AS `key`,
    T.city AS `city`,
    T.lat AS `lat`,
    T.lon AS `lon`,
    TM.food AS `food`,
    TM.health AS `health`,
    TM.ammo AS `ammo`,
    TM.timestamp AS `timestamp`
FROM `$FLC.kafka.topic_move` AS TM
JOIN `$FLC.kafka.topic_data` AS T ON TM.id = T.`key`;
