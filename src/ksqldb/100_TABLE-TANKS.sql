CREATE TABLE IF NOT EXISTS `$TANKS.kafka.topic_data` (
    `key` STRING PRIMARY KEY
)
WITH (
    KAFKA_TOPIC = '$TANKS.kafka.topic_data',
    VALUE_FORMAT = 'AVRO',
    timestamp = 'timestamp'
);
