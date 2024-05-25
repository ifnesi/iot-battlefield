CREATE STREAM IF NOT EXISTS `$TROOPS.kafka.topic_data-injuried` AS
SELECT
    `id`,
    `key`,
    `name`,
    `rank`,
    `height`,
    `weight`,
    `blood_type`,
    `lat`,
    `lon`,
    `body_temperature`,
    `pulse_rate`,
    `ammo`,
    `injury`,
    `injury_time`,
    `deceased`,
    `timestamp`
FROM `iot_battlefield_troops-joined`
WHERE
    `injury` IS NOT NULL;