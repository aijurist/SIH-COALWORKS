import random
import time
from flask import Flask, jsonify, Response
import json

app = Flask(__name__)

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

shift_data = {
  "message": "Fetched shifts successfully!",
  "data": [
    {
      "shiftId": 1,
      "name": "Morning Shift",
      "startTime": "2024-12-09T08:00:00Z",
      "endTime": "2024-12-09T16:00:00Z",
      "isActive": True
    },
    {
        "shiftId": 2,
        "name": "Afternoon Shift",
        "startTime": "2024-12-09T16:00:00Z",
        "endTime": "2024-12-10T00:00:00Z",
        "isActive": False
    },
    {
        "shiftId": 3,
        "name": "Night Shift",
        "startTime": "2024-12-10T00:00:00Z",
        "endTime": "2024-12-10T08:00:00Z",
        "isActive": False
    }
  ]
}

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

@app.route("/api/v1/user", methods=["GET"])
def get_user_info():
    return jsonify({"status": "success", "data": user_data}), 200


@app.route("/api/v1/smp", methods=["GET"])
def get_smp_info():
    return jsonify({"status": "success", "data": smp_data}), 200

@app.route("/api/v1/shift", methods=["GET"])
def get_shift_info():
    return jsonify(shift_data), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
