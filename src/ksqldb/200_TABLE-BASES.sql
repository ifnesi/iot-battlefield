CREATE TABLE IF NOT EXISTS `$BASES.kafka.topic_data` (
    `key` STRING PRIMARY KEY
)
WITH (
    KAFKA_TOPIC = '$BASES.kafka.topic_data',
    VALUE_FORMAT = 'AVRO',
    timestamp = 'timestamp'
);
