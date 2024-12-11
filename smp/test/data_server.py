import random
import time
from flask import Flask, jsonify, Response
import json

app = Flask(__name__)

# Static data for other endpoints
shift_data = [
    {
        "shift_id": 1,
        "start_time": "06:00",
        "end_time": "14:00",
        "shift_lead": "John Doe",
        "total_workers": 25,
        "completed_tasks": ["Roof inspection", "Ventilation maintenance", "Equipment check"],
    },
    {
        "shift_id": 2,
        "start_time": "14:00",
        "end_time": "22:00",
        "shift_lead": "Jane Smith",
        "total_workers": 20,
        "completed_tasks": ["Material transport", "Gas monitoring system check", "Safety drill"],
    },
]

user_data = [
    {
        "id": 1,
        "name": "John Doe",
        "role": "Mine Supervisor",
        "completed_tasks": ["Reviewed safety procedures", "Checked machinery"],
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "role": "Safety Officer",
        "completed_tasks": ["Conducted safety training", "Monitored air quality"],
    },
]

smp_data = [
    {
        "smp_id": 1,
        "hazard": "Roof Falls",
        "control_measures": ["Regular inspections", "Proper bolting"],
        "consequences": 4,  # Severe injury
        "exposure": 4,      # High
        "probability": 3,   # Medium
    },
    {
        "smp_id": 2,
        "hazard": "Gas Explosion",
        "control_measures": ["Gas monitoring", "Proper ventilation"],
        "consequences": 5,  # Mass casualties
        "exposure": 5,      # Critical
        "probability": 2,   # Low
    },
]

# Dynamic IoT data
iot_data_template = [
    {"sensor_id": 1, "parameter": "Methane Level", "threshold": 4.5},
    {"sensor_id": 2, "parameter": "Temperature", "threshold": 40.0},
    {"sensor_id": 3, "parameter": "Air Quality Index", "threshold": 50},
]

# Function to generate random IoT data
def generate_iot_data():
    iot_data = []
    for sensor in iot_data_template:
        value = round(random.uniform(sensor["threshold"] * 0.5, sensor["threshold"] * 1.5), 2)
        status = "Normal" if value <= sensor["threshold"] else "Abnormal Spike" if value > sensor["threshold"] * 1.2 else "Unusually High"
        iot_data.append({
            "sensor_id": sensor["sensor_id"],
            "parameter": sensor["parameter"],
            "value": value,
            "threshold": sensor["threshold"],
            "status": status,
        })
    return iot_data

@app.route("/api/v1/shift", methods=["GET"])
def get_shift_info():
    return jsonify({"status": "success", "data": shift_data}), 200


@app.route("/api/v1/user", methods=["GET"])
def get_user_info():
    return jsonify({"status": "success", "data": user_data}), 200


@app.route("/api/v1/smp", methods=["GET"])
def get_smp_info():
    return jsonify({"status": "success", "data": smp_data}), 200


@app.route("/api/v1/iot", methods=["GET"])
def get_iot_info():
    def stream_data():
        count = 0
        while True:
            data = generate_iot_data()
            yield f"data: {json.dumps({'status': 'success', 'data': data})}\n\n"
            time.sleep(1)
            count += 1
            if count == 10:
                break

    return Response(stream_data(), content_type="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
