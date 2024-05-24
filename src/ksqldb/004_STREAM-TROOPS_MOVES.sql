CREATE STREAM IF NOT EXISTS `$TROOPS.kafka.topic_data_moves`
WITH (
    KAFKA_TOPIC = '$TROOPS.kafka.topic_data_moves',
    VALUE_FORMAT = 'AVRO',
    timestamp = 'timestamp'
);
