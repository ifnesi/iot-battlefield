CREATE STREAM IF NOT EXISTS `$TROOPS.kafka.topic_move`
WITH (
    KAFKA_TOPIC = '$TROOPS.kafka.topic_move',
    VALUE_FORMAT = 'AVRO',
    timestamp = 'timestamp'
);
