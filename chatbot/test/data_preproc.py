from chatbot.utils.autoclean import AutoClean
import pandas as pd

df = pd.read_csv('chatbot/test/data.csv', encoding='latin1')
print(df.head())
pipeline = AutoClean(df)

print("Cleaned Output")
print(pipeline.output)