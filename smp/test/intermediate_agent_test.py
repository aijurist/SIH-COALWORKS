from langchain_google_genai import GoogleGenerativeAI 
from langchain_community.agent_toolkits import JsonToolkit, create_json_agent 
from langchain_community.tools.json.tool import JsonSpec 
from langchain.agents import AgentType 
import json  

def query_json(query, data):
    """
    Query user shift information using a JSON agent.
    
    Args:
        query (str): The query about user shift information
        data (dict): Dictionary containing user and shift information
    
    Returns:
        list: The agent's complete interaction steps
    """
    json_spec = JsonSpec(dict_=data, max_value_length=40000)
    json_toolkit = JsonToolkit(spec=json_spec)
    
    llm = GoogleGenerativeAI(model='gemini-1.5-pro', temperature=0.2)
    json_agent = create_json_agent(
        llm=llm, 
        toolkit=json_toolkit,
        verbose=True,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )
    
    # Capture the agent's complete interaction
    full_interaction = []
    
    # Flag to track if the final response has been captured
    final_response_captured = False
    
    for step in json_agent.iter(query):
        # Capture intermediate steps and thoughts
        if intermediate_step := step.get("intermediate_step"):
            action, value = intermediate_step[0]
            
            # Extract thought text
            thought_match = step.get("output", "").split("Thought:")
            if len(thought_match) > 1:
                thought = thought_match[1].split("Action:")[0].strip()
                print(f"Thought: {thought}")
                full_interaction.append({
                    "type": "thought", 
                    "content": thought
                })
            
            print(f"Action: {action.tool}")
            print(f"Action Input: {value}")
            full_interaction.append({
                "type": "action",
                "tool": action.tool,
                "input": value
            })
        
        # Capture final response
        if step.get("output") and not final_response_captured:
            # Check if this is the final response (no more intermediate steps)
            final_output = step.get("output", "")
            
            # Check for final thought
            final_thought_match = final_output.split("Thought:")
            if len(final_thought_match) > 1:
                final_thought = final_thought_match[1].split("Final Answer:")[0].strip()
                full_interaction.append({
                    "type": "final_thought", 
                    "content": final_thought
                })
            
            # Check for final answer
            final_answer_match = final_output.split("Final Answer:")
            if len(final_answer_match) > 1:
                final_answer = final_answer_match[1].strip()
                full_interaction.append({
                    "type": "final_answer", 
                    "content": final_answer
                })
            
            final_response_captured = True
        
        # Interactive continuation
        _continue = input("Should the agent continue (Y/n)?: ")
        if _continue.lower() != "y":
            break
    
    return full_interaction

# Example usage
data = {
    "data": [
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
        }
    ] 
}

question = 'Provide a detailed breakdown of works in the current shift, categorized as: Completed works, Half Completed, Unfinished works'
interaction = query_json(query=question, data=data)
print(interaction)