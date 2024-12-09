import pandas as pd
from chatbot.components.visualization.graph_plotter import chat2plot

# Step 1: Create and display a sample DataFrame
print("Step 1: Creating the DataFrame...")

df = pd.read_csv('chatbot/test/data.csv', encoding='latin1')
print("DataFrame Created:")
print(df)
print("\n" + "-"*50 + "\n")

# Step 2: Create a chat2plot instance
print("Step 2: Initializing ChartPlotter...")
plotter = chat2plot(df)
print("Chat2Plot instance created.")
print(f"Instance type: {type(plotter)}")
print("\n" + "-"*50 + "\n")

# Step 3: Query the LLM to generate the bar chart
query = "Create a chart showing some kind of simple relation in the data. clean the data if required"
print(f"Step 3: Querying ChartPlotter with: '{query}'")
result = plotter(query, show_plot=True)
print("Query executed. Result obtained.")
print("\n" + "-"*50 + "\n")

# Step 4: Display LLM Output
print("Step 4: Parsing and displaying LLM output...")
if result.config:
    print("Chart Configuration:")
    print(result.config)
else:
    print("No valid configuration returned.")

if result.explanation:
    print("\nExplanation from LLM:")
    print(result.explanation)

# Step 5: Display the Chart
if result.figure:
    print("\nStep 5: Rendering the Chart...")
    result.figure.show()
else:
    print("No chart could be generated.")


# Guide to use graphPlotter:
#     step 1: read df
#     step 2: initialize chat2plot instance
#         plotter = chat2plot(df)
#     step 3: query chat2plot with a question
#         result = plotter("Create a bar chart showing the relationship between 'x' and 'y'", show_plot=True)
#     step 4: result.config -> returns vegaFusion-Lite configuration code
#             result.explanation -> gives llm reply to the request
#             result.figure -> returns matplotlib figure object
#             result.figure.show() -> returns the figure object in form of localhost