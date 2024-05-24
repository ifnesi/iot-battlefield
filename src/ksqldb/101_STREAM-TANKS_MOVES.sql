CREATE STREAM IF NOT EXISTS `$TANKS.kafka.topic_move`
WITH (
    KAFKA_TOPIC = '$TANKS.kafka.topic_move',
    VALUE_FORMAT = 'AVRO',
    timestamp = 'timestamp'
);
