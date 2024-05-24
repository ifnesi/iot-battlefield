CREATE TABLE IF NOT EXISTS `$FLC.kafka.topic_data` (
    `key` STRING PRIMARY KEY
)
WITH (
    KAFKA_TOPIC = '$FLC.kafka.topic_data',
    VALUE_FORMAT = 'AVRO',
    timestamp = 'timestamp'
);
