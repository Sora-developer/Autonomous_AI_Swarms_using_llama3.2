import asyncio

from rich.console import Console
from rich.panel import Panel

from agents.base_agent import AgentExecutionError
from orchestrator import SwarmOrchestrator
from storage import save_specification

import argparse

console = Console()

# Maps orchestrator step roles -> (border color, default panel title)
STEP_STYLES = {
    "planner": ("green", "Agent A: Feature Planner"),
    "critic": ("red", "Agent B: Critic"),
    "critic_summary": ("magenta", "Agent B: Combined Critique"),
    "summarizer": ("blue", "Agent C: Final Specification"),
}


def render_step(role: str, title: str, content) -> None:
    """Callback passed into SwarmOrchestrator.run_swarm to render each agent turn live."""
    color, default_title = STEP_STYLES.get(role, ("white", role))
    display_title = title or default_title
    console.print(Panel(str(content), title=f"[bold {color}]{display_title}[/bold {color}]", border_style=color))


async def run_visual_swarm(idea: str, model_name: str = "llama3.2:1b", max_loops: int = 2) -> None:
    orchestrator = SwarmOrchestrator(model_name=model_name)

    console.print(
        Panel.fit(f"[bold white]Initiating Swarm for:[/bold white] [yellow]{idea}[/yellow]", border_style="cyan")
    )

    try:
        final_spec = await orchestrator.run_swarm(idea, max_loops=max_loops, on_step=render_step)
    except AgentExecutionError as e:
        console.print(f"\n[bold red]Swarm failed:[/bold red] {e}")
        console.print(
            "[dim]Check that Ollama is running and the model has been pulled "
            "(see README: `ollama pull llama3.2:1b`).[/dim]"
        )
        return

    saved_path = save_specification(idea, final_spec)
    console.print(f"\n[bold yellow]💾 Success! Specification saved to:[/bold yellow] {saved_path}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run a visual swarm for a given idea.")
    parser.add_argument("--idea", type=str, help="The idea to generate a specification for (e.g., 'A web app for tracking personal finances').", required=True)
    # parser.add_argument("--model", type=str, default="llama3.2:1b", help="The model to use for the swarm (default: 'llama3.2:1b').")
    parser.add_argument("--max-loops", type=int, default=2, help="The maximum number of loops for the swarm (default: 2).")

    args = parser.parse_args()

    asyncio.run(run_visual_swarm(args.idea, max_loops=args.max_loops))
