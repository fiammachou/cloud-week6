import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "mysql"),
        user=os.getenv("DB_USER", "clouduser"),
        password=os.environ["DB_PASSWORD"],
        database=os.getenv("DB_NAME", "clouddb")
    )

@app.route("/")
def home():
    return "Backend is working"

@app.route("/status")
def status():
    return jsonify({"message": "Backend API is working"})

@app.route("/visits")
def visits():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("UPDATE visits SET count = count + 1 WHERE id = 1")
    connection.commit()

    cursor.execute("SELECT count FROM visits WHERE id = 1")
    count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return jsonify({"visits": count})


@app.route("/weather")
def weather():
    url = "https://opendata.fmi.fi/wfs"

    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "getFeature",
        "storedquery_id": "fmi::forecast::harmonie::surface::point::timevaluepair",
        "place": "oulu",
        "parameters": "temperature,windspeedms"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    result = {
        "place": "Oulu"
    }

    for member in root.findall(".//{*}member"):
        observed_property = member.find(".//{*}observedProperty")

        if observed_property is None:
            continue

        href = observed_property.attrib.get(
            "{http://www.w3.org/1999/xlink}href", ""
        )

        forecast_value = None
        forecast_time = None

        for point in member.findall(".//{*}MeasurementTVP"):
            time_element = point.find(".//{*}time")
            value_element = point.find(".//{*}value")

            if (
                value_element is not None
                and value_element.text
                and value_element.text != "NaN"
            ):
                forecast_value = float(value_element.text)

                if time_element is not None:
                    forecast_time = time_element.text

                break

        if "param=temperature" in href.lower():
            result["temperature_c"] = forecast_value
            result["forecast_time"] = forecast_time

        elif "param=windspeedms" in href.lower():
            result["wind_speed_ms"] = forecast_value

    return jsonify(result)
