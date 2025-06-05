import json

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from kafka import KafkaConsumer

# InfluxDB setup
influx = InfluxDBClient(
    url="http://localhost:8086",
    token="admin-token",
    org="ar-edu-itba-inge2",
)
write_api = influx.write_api(write_options=SYNCHRONOUS)

# Kafka consumer
consumer = KafkaConsumer(
    "iot-temperature",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
)

for msg in consumer:
    data = msg.value

    temperature_point = Point("temperature").tag("location", data["location"]).field("value", float(data["temperature"])).time(int(data["timestamp"] * 1e9))
    humidity_point = Point("humidity").tag("location", data["location"]).field("value", float(data["humidity"])).time(int(data["timestamp"] * 1e9))

    write_api.write(bucket="sensor-data", record=temperature_point)
    write_api.write(bucket="sensor-data", record=humidity_point)
    print("Escrito a InfluxDB:", temperature_point.to_line_protocol())
