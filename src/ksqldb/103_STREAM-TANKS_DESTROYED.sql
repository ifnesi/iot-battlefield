CREATE STREAM IF NOT EXISTS `$TANKS.kafka.topic_data-destroyed` AS
SELECT
    `id`,
    `key`,
    `unit`,
    `model`,
    `lat`,
    `lon`,
    `ammo`,
    `damage`,
    `timestamp`
FROM `$TANKS.kafka.topic_data-joined`
WHERE `destroyed`;