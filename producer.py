import pika
import csv
from datetime import datetime
import time
import random
import json

#conncetion
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

#exchange
exchange_name = "edit_events"
channel.exchange_declare(
    exchange=exchange_name,
    exchange_type="fanout"
)

#Daten einlesen
with open("assets/dataset.csv","r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        #nachricht an exchange senden
        message = json.dumps(row)
        channel.basic_publish(
            exchange=exchange_name,
            routing_key="",
            body=message
        )
        print(f"{datetime.now()}: sent message with id: {row['id']}")
        time.sleep(random.uniform(0,1))
        


#Verbindung schliessen
connection.close()