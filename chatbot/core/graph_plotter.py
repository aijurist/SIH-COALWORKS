import os
import re
import pandas as pd
from chatbot.agent.visualization.graph_plotter import chat2plot

folder_path = "data/iot"
file_pattern = r"iot_data_(\d+)\.csv"  
files = [f for f in os.listdir(folder_path) if re.match(file_pattern, f)]

latest_file = max(files, key=lambda x: int(re.search(file_pattern, x).group(1)))
latest_file_path = os.path.join(folder_path, latest_file)

print(f"Using latest file: {latest_file_path}")

df = pd.read_csv(latest_file_path, encoding='latin1')
print("DataFrame Loaded:")
print(df.head())
print("\n" + "-"*50 + "\n")

print("Step 3: Initializing ChartPlotter...")
plotter = chat2plot(df)
print("Chat2Plot instance created.")
print(f"Instance type: {type(plotter)}")
print("\n" + "-"*50 + "\n")

query = "Create a chart showing some kind of simple relation in the data. Clean the data if required."
print(f"Step 4: Querying ChartPlotter with: '{query}'")
result = plotter(query, show_plot=True)
print("Query executed. Result obtained.")
print("\n" + "-"*50 + "\n")

print("Step 5: Parsing and displaying LLM output...")
if result.config:
    print("Chart Configuration:")
    print(result.config)
else:
    print("No valid configuration returned.")

if result.explanation:
    print("\nExplanation from LLM:")
    print(result.explanation)

if result.figure:
    print("\nStep 6: Rendering the Chart...")
    result.figure.show()
else:
    print("No chart could be generated.")
