from agents.base_agent import BaseAgent
from prompts import PLANNER_PROMPT, CRITIC_PROMPT, SUMMARIZER_PROMPT
from orchestrator import SwarmOrchestrator

# Used to test the BaseAgent's ability to maintain isolated chat history.

# def test_infrastructure():
#     print("Initializing test agent on local hardware foundation...")
    
#     # Initialize a test agent using the 1B parameter model [cite: 5, 14]
#     test_agent = BaseAgent(
#         name="Tester",
#         model="llama3.2:1b",
#         system_prompt="You are a helpful, minimalist assistant. Keep answers to one short sentence."
#     )
    
#     # Turn 1
#     print("\n--- Sending Turn 1 ---")
#     reply_1 = test_agent.execute("Hello! Introduce yourself briefly.")
#     print(f"Agent Reply: {reply_1}")
    
#     # Turn 2 (Testing chat history state isolation) 
#     print("\n--- Sending Turn 2 ---")
#     reply_2 = test_agent.execute("What was the very first thing I asked you to do?")
#     print(f"Agent Reply: {reply_2}")

# This test checks if the agent generates valid JSON output when the require_json flag is set to True
# def test_json_output():
#     print("Initializing Planner Agent...")
    
#     planner = BaseAgent(
#         name="Planner",
#         model="llama3.2:1b", # or qwen2.5:1.5b
#         system_prompt=PLANNER_PROMPT,
#         require_json=True
#     )
    
#     print("\n--- Generating Architecture ---")
#     response = planner.execute("Build a simple local to-do list application.")
    
#     # Because it returns parsed JSON, we can interact with it like a dictionary
#     if response:
#         print(f"Feature: {response.get('feature_name')}")
#         print(f"Components: {response.get('core_components')}")
#     else:
#         print("Model failed to output valid JSON.")

def main():
    # Initialize the swarm with your optimized 1B model
    orchestrator = SwarmOrchestrator(model_name="llama3.2:1b")
    
    # The user enters an idea
    idea = "Build a local markdown note-taking app with tag-based search."
    
    # Run the state machine
    final_markdown_spec = orchestrator.run_swarm(user_idea=idea, max_loops=2)
    
    print("\n==================================================")
    print(" FINAL TECHNICAL SPECIFICATION ")
    print("==================================================\n")
    print(final_markdown_spec)

if __name__ == "__main__":
    # test_infrastructure()
    # test_json_output()
    main()