import json

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from kafka import KafkaConsumer

influx = InfluxDBClient(
    url="http://localhost:8086",
    token="admin-token",
    org="ar-edu-itba-inge2",
)
write_api = influx.write_api(write_options=SYNCHRONOUS)

consumer = KafkaConsumer(
    "temperature",
    "humidity",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
)

for msg in consumer:
    data = msg.value
    topic = msg.topic

    point = Point(topic).tag("location", data["location"]).field("value", float(data["value"])).time(int(data["timestamp"] * 1e9))
    write_api.write(bucket="sensor-data", record=point)
    print(f"Escrito a InfluxDB: {point.to_line_protocol()}")
