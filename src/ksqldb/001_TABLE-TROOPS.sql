CREATE TABLE IF NOT EXISTS `$TROOPS.kafka.topic_data` (
    `key` STRING PRIMARY KEY
)
WITH (
    KAFKA_TOPIC = '$TROOPS.kafka.topic_data',
    VALUE_FORMAT = 'AVRO',
    timestamp = 'timestamp'
);
