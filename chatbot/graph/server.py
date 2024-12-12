from flask import Flask, render_template, jsonify, request
import os
import re
import pandas as pd
from chatbot.agent.visualization.graph_plotter import chat2plot
import plotly.io as pio
import plotly.graph_objects as go

app = Flask(__name__)

# Global variables for DataFrame and chart
latest_file_path = None
df = None
plotter = None

# Step 1: Locate and load the latest CSV file
def load_latest_file():
    global latest_file_path, df, plotter

    folder_path = "data/iot"
    file_pattern = r"iot_data_(\d+)\.csv"  # Regex to extract the file number

    # Get all CSV files in the folder matching the pattern
    files = [f for f in os.listdir(folder_path) if re.match(file_pattern, f)]

    if not files:
        raise FileNotFoundError("No CSV files found in the specified folder.")

    # Extract the highest number `n` from the filenames
    latest_file = max(files, key=lambda x: int(re.search(file_pattern, x).group(1)))
    latest_file_path = os.path.join(folder_path, latest_file)

    print(f"Using latest file: {latest_file_path}")

    # Load the DataFrame
    df = pd.read_csv(latest_file_path, encoding='latin1')
    print("DataFrame Loaded:")
    print(df.head())

    # Initialize Chat2Plot instance
    plotter = chat2plot(df)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    global plotter

    query = request.json.get('query', "Create a chart showing some kind of simple relation in the data. Clean the data if required.")

    try:
        result = plotter(query, show_plot=False)
        
        if result.figure:
            # Convert the figure to a JSON format for Plotly
            figure_json = pio.to_json(result.figure)
            return jsonify({
                'status': 'success',
                'figure': figure_json,
                'config': result.config,
                'explanation': result.explanation
            })
        else:
            return jsonify({'status': 'failure', 'message': 'No chart could be generated.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    try:
        load_latest_file()
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error: {e}")