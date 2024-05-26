CREATE STREAM IF NOT EXISTS `$TROOPS.kafka.topic_data-deceased` AS
SELECT
    `id`,
    `key`,
    `unit`,
    `name`,
    `rank`,
    `height`,
    `weight`,
    `blood_type`,
    `lat`,
    `lon`,
    `ammo`,
    `injury`,
    `injury_time`,
    `timestamp`
FROM `$TROOPS.kafka.topic_data-joined`
WHERE `deceased`;