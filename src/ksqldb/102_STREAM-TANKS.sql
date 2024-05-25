CREATE STREAM IF NOT EXISTS `$TANKS.kafka.topic_data-joined` AS
SELECT
    TM.id AS `id`,
    T.`key` AS `key`,
    T.model AS `model`,
    TM.lat AS `lat`,
    TM.lon AS `lon`,
    TM.ammo AS `ammo`,
    TM.damage AS `damage`,
    TM.destroyed AS `destroyed`,
    TM.current_speed AS `current_speed`,
    TM.timestamp AS `timestamp`
FROM `$TANKS.kafka.topic_move` AS TM
JOIN `$TANKS.kafka.topic_data` AS T ON TM.id = T.`key`;
