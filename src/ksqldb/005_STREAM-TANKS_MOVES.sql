CREATE STREAM IF NOT EXISTS `$TANKS.kafka.topic_data_moves`
WITH (
    KAFKA_TOPIC = '$TANKS.kafka.topic_data_moves',
    VALUE_FORMAT = 'AVRO',
    timestamp = 'timestamp'
);
