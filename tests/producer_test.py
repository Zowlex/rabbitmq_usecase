import pika
import csv
from datetime import datetime
import time
import random
import json
import unittest

class TestProducer(unittest.TestCase):
    def test_rabbitmq_connection(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
        self.assertTrue(connection.is_open)
        connection.close()

    def test_data_read_from_csv(self):
        with open("assets/dataset.csv", "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            row_count = sum(1 for _ in csv_reader)
        self.assertGreater(row_count, 0)

    def test_message_sending(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
        
        exchange_name = "edit_events"
        channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")
        
        test_message = {"id": "123", "data": "test"}
        message = json.dumps(test_message)
        
        channel.basic_publish(
            exchange=exchange_name,
            routing_key="",
            body=message
        )

        # Assuming there's a consumer listening, wait a bit to give it time to process
        time.sleep(2)

        # You can add more assertions here based on your consumer's expected behavior

        connection.close()

if __name__ == "__main__":
    unittest.main()
