import json
import pandas as pd
from kafka import KafkaConsumer
from time import sleep

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'iot-data',
    bootstrap_servers=['192.168.110.53:9093'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # Deserialize the incoming JSON message
)

# Initialize an empty DataFrame
columns = [
    "Node", "latitude", "longitude", "accelX", "accelY", "accelZ",
    "temperature", "pressure", "altitude", "methanePPM", 
    "carbonMonoxidePPM", "alert"
]
data_df = pd.DataFrame(columns=columns)

csv_file_counter = 1  # To keep track of CSV file numbering
print("Listening to Kafka topic 'iot-data'...")

try:
    while True:
        batch = []
        
        # Collect messages for a batch (adjust the size as needed)
        for _ in range(5):  # Process 5 messages for the current batch
            message = next(consumer)
            message_data = message.value  # Parse the message value
            
            # Append to batch
            batch.append(message_data)
        
        # Convert batch to DataFrame and append to main DataFrame
        batch_df = pd.DataFrame(batch)
        if not batch_df.empty:  # Ensure batch_df is not empty
            data_df = pd.concat([data_df, batch_df], ignore_index=True)
        
        # Check if DataFrame has 100 or more rows
        if len(data_df) >= 100:
            # Save the first 100 rows to a CSV file
            file_name = f"data/iot/iot_data_{csv_file_counter}.csv"
            data_df.iloc[:100].to_csv(file_name, index=False)
            print(f"Saved 100 rows to {file_name}")
            
            # Increment the CSV file counter
            csv_file_counter += 1
            
            # Drop the saved rows from the DataFrame
            data_df = data_df.iloc[100:].reset_index(drop=True)
        
        # Wait for a short period before processing more messages
        sleep(1)

except KeyboardInterrupt:
    print("\nStopped listening to Kafka.")
except Exception as e:
    print(f"Error occurred: {e}")