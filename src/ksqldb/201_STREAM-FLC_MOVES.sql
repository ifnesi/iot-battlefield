CREATE STREAM IF NOT EXISTS `$FLC.kafka.topic_move`
WITH (
    KAFKA_TOPIC = '$FLC.kafka.topic_move',
    VALUE_FORMAT = 'AVRO',
    timestamp = 'timestamp'
);
