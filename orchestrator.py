import json
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from prompts import PLANNER_PROMPT, CRITIC_PROMPT, SUMMARIZER_PROMPT

class SwarmOrchestrator:
    def __init__(self, model_name : str = "llama3.2:1b"):
        # Initialize the three different personas
        self.planner = BaseAgent(
            name="Planner",
            model=model_name,
            system_prompt=PLANNER_PROMPT,
            require_json=True
        )

        self.critic = BaseAgent(
            name = "Critic", 
            model = model_name,
            system_prompt = CRITIC_PROMPT,
            require_json = True
        )
        self.summarizer = BaseAgent(
            name = "Summarizer",
            model = model_name,
            system_prompt = SUMMARIZER_PROMPT,
            require_json = False
        )

        self.global_history : List[Dict[str, Any]] = []  # To track the entire conversation across agents

    def run_swarm(self, user_idea: str, max_loops: int = 2) -> str:
        print(f'\nInitiating Swarm for: "{user_idea}"\n')

        # 1. Initial Draft Generation
        print("[Planner] Generating functional architecture draft...")
        current_plan = self.planner.execute(f"Create a plan for : {user_idea}")
        self.global_history.append({"agent": "Planner", "turn" : 0, "content": current_plan})

        # 2. The Discussion Loop
        for i in range(max_loops):
            print(f'\n--- Loop {i+1}/{max_loops} ---')

            # Critic analyzes the current plan
            print("[Critic] Analyzing the Planner's proposal...")
            criticism = self.critic.execute(f'Review this plan and identify strict flaws: {json.dumps(current_plan)}')
            self.global_history.append({"agent": "Critic", "turn" : i+1, "content": criticism})
            # print(f"Identified Flaws {i+1}: {criticism.get('identified_flaws', [])}")

            # Planner refines the plan based on criticism
            print("[Planner] Refining the plan based on Critic's feedback...")
            current_plan = self.planner.execute(f"Refine your plan based on these identified flaws: {json.dumps(criticism)}.")
            self.global_history.append({"agent": "Planner", "turn" : i+1, "content": current_plan})
            # print(f"Refined Plan {i+1}: {current_plan.get('feature_name', 'N/A')} with components {current_plan.get('core_components', [])}")

            self.planner.prune_context()
            self.critic.prune_context()
        
        # 3. Final Summarization
        print("\n[Summarizer] Compiling the final technical specification...")

        final_prompt = (
            f"Here is the raw discussion log between the Planner and Critic: {json.dumps(self.global_history)}. "
            "Strip out the chatter and output a clean, highly structured Markdown technical specification."
        )

        final_spec = self.summarizer.execute(final_prompt)
        return final_spec