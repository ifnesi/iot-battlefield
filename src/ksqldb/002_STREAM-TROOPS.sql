CREATE STREAM IF NOT EXISTS `$TROOPS.kafka.topic_data-joined` AS
SELECT
    TM.id AS `id`,
    T.`key` AS `key`,
    T.unit AS `unit`,
    T.name AS `name`,
    T.rank AS `rank`,
    T.height AS `height`,
    T.weight AS `weight`,
    T.blood_type AS `blood_type`,
    TM.lat AS `lat`,
    TM.lon AS `lon`,
    TM.health AS `health`,
    TM.body_temperature AS `body_temperature`,
    TM.pulse_rate AS `pulse_rate`,
    TM.ammo AS `ammo`,
    TM.injury AS `injury`,
    TM.injury_time AS `injury_time`,
    TM.deceased AS `deceased`,
    TM.timestamp AS `timestamp`
FROM `$TROOPS.kafka.topic_move` AS TM
JOIN `$TROOPS.kafka.topic_data` AS T ON TM.id = T.`key`;
