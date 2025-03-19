from typing import Any


import logging

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
#    StringSerializer,
)

_logger = logging.getLogger("KafkaAvroProducer")

class KafkaAvroProducer:
    def __init__(self, broker: str, schema_registry_url: str, topic: str, key_schema: Any, value_schema: Any) -> None:
        """
        Initialisiert den KafkaAvroSender.

        Args:
            broker (str): Adresse des Kafka Brokers.
            schema_registry_url (str): URL der Schema Registry.
            topic (str): Kafka Topic, in das die Nachrichten gesendet werden.
            key_schema (Any): Avro-Schema für den Schlüssel.
            value_schema (Any): Avro-Schema für den Wert.
        """
        config_producer = {
            'bootstrap.servers': broker
        }

        config_src = {
            'url': schema_registry_url
        }

        self.topic = topic

        self.src = SchemaRegistryClient(config_src)
                
        self.key_serializer = AvroSerializer(
            self.src, key_schema, self.key_to_dict
        )
        self.value_serializer = AvroSerializer(
            self.src, value_schema, self.value_to_dict
        )
        
        self.kafka_producer = Producer(config_producer)
        _logger.info(f'Connected to Kafka broker at {broker}, topic: {self.topic}')

    def key_to_dict(self, data: Any, ctx):
        return data.dict()
       
    def value_to_dict(self, data: Any, ctx):
        return data.dict()   
    
    def produce(self, key: Any, value: Any) -> None:
        """
        Sendet eine Nachricht an das konfigurierte Kafka-Topic.

        Args:
            key (Any): Schlüssel der Nachricht.
            value (Any): Wert der Nachricht.
        """
        try:            
            self.kafka_producer.produce(
                topic = self.topic, 
                key = self.key_serializer(key, SerializationContext(self.topic, MessageField.KEY)),
                value = self.value_serializer(value, SerializationContext(self.topic, MessageField.VALUE)),
                on_delivery=self.delivery_callback,
            )            
            
            # Trigger any available delivery report callbacks from previous produce() calls
            events_processed = self.kafka_producer.poll(1)
            #print(f"events_processed: {events_processed}")

            messages_in_queue = self.kafka_producer.flush(1)
            #print(f"messages_in_queue: {messages_in_queue}")
                        
            _logger.info(f'Message sent to Kafka')
        except Exception as e:
            _logger.error(f'Failed to send data to Kafka: {e}')

    def delivery_callback(self, err, msg):
        if err:
            _logger.error("ERROR: Message failed delivery: {}".format(err))
        #else:
            #_logger.info(f'Data sent to Kafka.')
            #_logger.debug(
            #    "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
            #        topic=msg.topic(),
            #        key="",  # msg.key().decode("utf-8"),
            #        value=msg.value() #.decode("utf-8"),
            #    )
            #)