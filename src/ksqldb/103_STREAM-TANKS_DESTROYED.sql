CREATE STREAM IF NOT EXISTS `$TANKS.kafka.topic_data-destroyed` AS
SELECT
    T.ID,
    T.MODEL,
    T.LAT,
    T.LON,
    T.AMMO,
    T.DAMAGE,
    T.TIMESTAMP
FROM `$TANKS.kafka.topic_data-joined` AS T
WHERE T.DESTROYED;