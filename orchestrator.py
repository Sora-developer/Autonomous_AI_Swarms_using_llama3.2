import asyncio
import json
from typing import Any, Callable, Dict, List, Optional

from agents.base_agent import AgentExecutionError, BaseAgent
from prompts import (
    CRITIC_SCALABILITY_PROMPT,
    CRITIC_SECURITY_PROMPT,
    CRITIC_UX_PROMPT,
    PLANNER_PROMPT,
    SUMMARIZER_PROMPT,
)
from schemas import CriticOutput, PlannerOutput

# Signature: on_step(role, title, content) -> None
StepCallback = Callable[[str, str, Any], None]

_SEVERITY_RANK = {"Low": 0, "Medium": 1, "High": 2}


def _merge_critic_outputs(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Combines the independent Security/Scalability/UX critic results into a
    single criticism object for the Planner to respond to."""
    merged_flaws: List[str] = []
    merged_fixes: List[str] = []
    top_severity = "Low"

    for result in results:
        merged_flaws.extend(result.get("identified_flaws", []))
        merged_fixes.extend(result.get("suggested_fixes", []))
        severity = result.get("severity_level", "Low")
        if _SEVERITY_RANK.get(severity, 0) > _SEVERITY_RANK.get(top_severity, 0):
            top_severity = severity

    return {
        "identified_flaws": merged_flaws,
        "severity_level": top_severity,
        "suggested_fixes": merged_fixes,
    }


class SwarmOrchestrator:
    def __init__(self, model_name: str = "llama3.2:1b"):
        # A single model powers every agent — the "swarm" comes from running
        # several specialized personas of that same model concurrently, not
        # from mixing different models.
        self.planner = BaseAgent(
            name="Planner",
            model=model_name,
            system_prompt=PLANNER_PROMPT,
            require_json=True,
            response_schema=PlannerOutput,
        )

        # Three critic personas, each with its own isolated chat history, all
        # targeting the same model, invoked concurrently every loop.
        self.critics: List[BaseAgent] = [
            BaseAgent(
                name="Critic-Security",
                model=model_name,
                system_prompt=CRITIC_SECURITY_PROMPT,
                require_json=True,
                response_schema=CriticOutput,
            ),
            BaseAgent(
                name="Critic-Scalability",
                model=model_name,
                system_prompt=CRITIC_SCALABILITY_PROMPT,
                require_json=True,
                response_schema=CriticOutput,
            ),
            BaseAgent(
                name="Critic-UX",
                model=model_name,
                system_prompt=CRITIC_UX_PROMPT,
                require_json=True,
                response_schema=CriticOutput,
            ),
        ]

        self.summarizer = BaseAgent(
            name="Summarizer",
            model=model_name,
            system_prompt=SUMMARIZER_PROMPT,
            require_json=False,
        )

        self.global_history: List[Dict[str, Any]] = []

    async def _run_critics_concurrently(
        self, current_plan: Any, loop_index: int, emit: Callable[[str, str, Any], None]
    ) -> Dict[str, Any]:
        """Fires all critic personas at Ollama at the same time and merges
        whichever ones succeed. A single critic failing doesn't abort the loop.

        NOTE: asyncio.as_completed() does not guarantee it hands back the exact
        task objects you passed in (this changed across Python versions), so we
        can't key a dict by task identity. Instead each wrapped coroutine
        carries its own critic reference in its return value.
        """

        async def run_one(critic: BaseAgent):
            try:
                result = await critic.aexecute(
                    f"Review this plan and identify strict flaws: {json.dumps(current_plan)}"
                )
                return critic, result, None
            except AgentExecutionError as e:
                return critic, None, e

        tasks = [asyncio.create_task(run_one(critic)) for critic in self.critics]

        results: List[Dict[str, Any]] = []
        for finished in asyncio.as_completed(tasks):
            critic, result, error = await finished
            if error is not None:
                print(f"[{critic.name}] failed this loop, skipping its input: {error}")
                continue

            self.global_history.append({"agent": critic.name, "turn": loop_index, "content": result})
            emit("critic", f"Agent B: {critic.name}", result)
            results.append(result)

        if not results:
            raise AgentExecutionError(
                f"All {len(self.critics)} critics failed in loop {loop_index}; aborting swarm."
            )

        return _merge_critic_outputs(results)

    async def run_swarm(
        self,
        user_idea: str,
        max_loops: int = 2,
        on_step: Optional[StepCallback] = None,
    ) -> str:
        """
        Runs the full Planner -> [Critic swarm, concurrent] -> Planner -> ... -> Summarizer loop.

        `on_step`, if provided, is called after every agent turn as
        on_step(role, title, content) so a caller (e.g. main.py's rich TUI)
        can render progress without duplicating this control flow.
        """

        def emit(role: str, title: str, content: Any) -> None:
            if on_step:
                on_step(role, title, content)

        print(f'\nInitiating Swarm for: "{user_idea}"\n')

        # 1. Initial Draft Generation
        print("[Planner] Generating functional architecture draft...")
        current_plan = await self.planner.aexecute(f"Create a plan for: {user_idea}")
        self.global_history.append({"agent": "Planner", "turn": 0, "content": current_plan})
        emit("planner", "Agent A: Feature Planner", current_plan)

        # 2. The Discussion Loop
        for i in range(max_loops):
            print(f"\n--- Loop {i + 1}/{max_loops} (Security/Scalability/UX critics running concurrently) ---")

            merged_criticism = await self._run_critics_concurrently(current_plan, i + 1, emit)
            emit("critic_summary", "Agent B: Combined Critique", merged_criticism)

            print("[Planner] Refining the plan based on combined Critic feedback...")
            current_plan = await self.planner.aexecute(
                f"Refine your plan based on these identified flaws: {json.dumps(merged_criticism)}."
            )
            self.global_history.append({"agent": "Planner", "turn": i + 1, "content": current_plan})
            emit("planner", f"Agent A: Refined Plan (Loop {i + 1})", current_plan)

            self.planner.prune_context()
            for critic in self.critics:
                critic.prune_context()

        # 3. Final Summarization
        print("\n[Summarizer] Compiling the final technical specification...")

        final_prompt = (
            f"Here is the raw discussion log between the Planner and Critics: {json.dumps(self.global_history)}. "
            "Strip out the chatter and write a clean, highly structured Markdown technical specification."
        )

        final_spec = await self.summarizer.aexecute(final_prompt)
        emit("summarizer", "Agent C: Final Specification", final_spec)
        return final_spec
