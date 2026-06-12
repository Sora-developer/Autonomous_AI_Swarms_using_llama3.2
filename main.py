from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from orchestrator import SwarmOrchestrator
from storage import save_specification

console = Console()

def run_visual_swarm(idea: str):
    orchestrator = SwarmOrchestrator(model_name="llama3.2:1b")
    
    console.print(Panel.fit(f"[bold white] Initiating Swarm for:[/bold white] [yellow]{idea}[/yellow]", border_style="cyan"))
    
    # 1. Initial Draft Generation
    console.print("[bold cyan]System:[/bold cyan] Planner is generating the initial architecture...")
    current_plan = orchestrator.planner.execute(f"Create a plan for: {idea}")
    orchestrator.global_history.append({"agent": "Planner", "turn": 0, "content": current_plan})
    
    # Display Planner Output in Green
    console.print(Panel(str(current_plan), title="[bold green]Agent A: Feature Planner[/bold green]", border_style="green"))
    
    # 2. The Discussion Loop (Max 2 Turns, can increase for more complex ideas or deeper refinement, but requires more compute)
    max_loops = 2
    for i in range(max_loops):
        console.print(f"\n[bold magenta]--- Loop Iteration {i + 1}/{max_loops} ---[/bold magenta]")
        
        # Critic analyzes
        console.print("[bold cyan]System:[/bold cyan] Critic is analyzing for flaws...")
        import json
        criticism = orchestrator.critic.execute(f"Review this plan and identify strict flaws: {json.dumps(current_plan)}")
        orchestrator.global_history.append({"agent": "Critic", "turn": i + 1, "content": criticism})
        
        # Display Critic Output in Red
        console.print(Panel(str(criticism), title="[bold red]Agent B: Critic[/bold red]", border_style="red"))
        
        # Planner refines
        console.print("[bold cyan]System:[/bold cyan] Planner is refining the architecture...")
        current_plan = orchestrator.planner.execute(f"Refine your plan based on these identified flaws: {json.dumps(criticism)}")
        orchestrator.global_history.append({"agent": "Planner", "turn": i + 1, "content": current_plan})
        
        # Display Updated Planner Output
        console.print(Panel(str(current_plan), title="[bold green]Agent A: Refined Plan[/bold green]", border_style="green"))

    # 3. The Finale
    console.print("\n[bold cyan]System:[/bold cyan] Summarizer is compiling the final document...")
    finale_prompt = (
        f"Here is the raw discussion log: {json.dumps(orchestrator.global_history)}. "
        "Strip out the chatter and output a clean, highly structured Markdown technical specification."
    )
    final_spec = orchestrator.summarizer.execute(finale_prompt)
    
    # Display Summarizer Output in Blue
    console.print(Panel(final_spec, title="[bold blue]Agent C: Final Specification[/bold blue]", border_style="blue"))
    
    # Save the file
    saved_path = save_specification(idea, final_spec)
    console.print(f"\n[bold yellow]💾 Success! Specification saved to:[/bold yellow] {saved_path}")

if __name__ == "__main__":
    test_idea = "Build a local markdown note-taking app with tag-based search."
    run_visual_swarm(test_idea)