import pika
import os
import sys
from datetime import datetime
import json
import time
from collections import defaultdict
import sqlite3


def create_db(db_name):
    conn = sqlite3.connect(f"db/{db_name}.db")
    cursor = conn.cursor()

    #create db
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS aggregated_data (
                   timestamp TEXT PRIMARY KEY,
                   global_edits INTEGER,
                   german_edits INTEGER
            )
''')
    conn.commit()
    conn.close()
    print("db created or exists")


def main(exchange_name, db_name):
    #conncetion
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    #exchange
    
    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type="fanout"
    )

    #temporary queue
    queue = channel.queue_declare(queue="", exclusive=True)
    queue_name = queue.method.queue

    #queue binding
    channel.queue_bind(
        exchange=exchange_name,
        queue=queue_name
        )

    # callback to be called by pika
    global_edits = defaultdict(int)
    german_edits = defaultdict(int)
    def callback(ch, method, properties, body):
        data =json.loads(body)
        timestamp = data["timestamp"]
        origin = data["wiki"]
        # convert timestamp
        timestamp_iso = datetime.fromtimestamp(int(timestamp)).isoformat()

        # Calculate intervals (e.g., per minute) and update aggregations
        interval = int(datetime.fromisoformat(timestamp_iso).timestamp()) // 60
        global_edits[interval]+=1

        #check for german wiki
        if "dewiki" in origin.lower():
            german_edits[interval]+=1

        #write to db
        conn = sqlite3.connect(f'db/{db_name}.db')
        cursor = conn.cursor()

        #insert or update data
        cursor.execute('''
            INSERT OR REPLACE INTO aggregated_data (timestamp, global_edits, german_edits)
                VALUES (?,?,?)
        ''', (timestamp_iso, global_edits[interval], german_edits[interval]))
        conn.commit()
        conn.close()

        print(f"Inserted data for timestamp: {timestamp_iso}")

    channel.basic_consume(
        queue=queue_name,
        auto_ack=True,
        on_message_callback=callback
    )

    #listen
    print("[*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
    

if __name__=="__main__":
    try:
        exchange_name="edit_events"
        db_name = "wiki_stats"
        create_db(db_name)
        main(exchange_name, db_name)
    except KeyboardInterrupt:
        print("Interrupted by user")
        