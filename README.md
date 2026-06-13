#  Autonomous AI Agent Swarms (Simulated OS Environment)   

Local multi-agent system engineered to execute entirely within a strict 4GB VRAM ceiling.

By optimizing 1B parameter quantized models (like Llama 3.2 1B or Qwen 2.5 1.5B) via Ollama, this project bypasses bloated, memory-heavy frameworks like LangChain or CrewAI. Instead, it utilizes a custom, lightweight state machine orchestrator and structured JSON outputs to force deterministic behavior from small models in a simulated OS console stream.

<!-- ## 🎥 Demo

> **Note:** (Upload an MP4 or GIF here showing the rich console UI and the three agents firing off sequentially.) -->

##  The Architecture
Running massive models simultaneously easily freezes standard hardware. Because 1B models have a tiny footprint, we can run multiple agent abstractions concurrently on a 4GB GPU without crashing the system.  

This swarm consists of three distinct personas:

- **Agent A (Feature Planner):** Creative and systematic, this agent takes a raw idea and breaks it down into functional architectural components.
- **Agent B (Critic):** Hyper-focused on edge cases, scaling limits, security flaws, and execution bottlenecks. It relentlessly analyzes the Planner's proposals.
- **Agent C (Summarizer):** An objective, structured compiler that combines the raw conversation between the Planner and Critic into a final, clean specification document.

##  Key Technical Features

- **Zero-Overhead Foundation:** Built using raw Python, Pydantic for type-safe configurations, and the official Ollama library, completely eliminating unnecessary middleware overhead.
- **Deterministic Multi-Agent Orchestration:** Utilizes Ollama's Structured Outputs (JSON Schema mode) to force structural compliance, effectively taming the 1B model from wandering and eliminating hallucinations.
- **Custom State Machine:** The centralized `SwarmOrchestrator` dynamically routes inputs, outputs, and isolated agent contexts, strictly limiting loop iterations to safeguard the finite context window.
- **Context-Pruning Middleware:** A dynamic mechanism that truncates non-essential chat history to maintain real-time conversational loops without memory overflow.
- **Simulated OS Console Stream:** A real-time Console based Text User Interface (TUI) powered by the Python `rich` library streams agent outputs live into custom-colored containers.
- **Persistence Layer:** Automatically saves the Summarizer's final compiled technical specification as an exported `.md` file inside an organized `/workspace` directory.

## 🛠️ Installation & Setup
Before running the application, ensure all heavy background applications (web browsers, games, heavy IDE indexing) are closed to dedicate your GPU entirely to the multi-turn exchange.

**1. Install Ollama**
Download and install Ollama for your operating system.

**2. Pull the Quantized Models**
Open your terminal and pull the compact models designed for resource-constrained execution:

```bash
ollama pull llama3.2:1b
ollama pull qwen2.5:1.5b
```

**3. Clone & Install Dependencies**

```bash
git clone https://github.com/Sora-developer/Autonomous_AI_Swarms_using_llama3.2.git
cd Autonomous_AI_Swarms_using_llama3.2
pip install -r requirements.txt
```

(Dependencies: `ollama>=0.2.0`, `pydantic>=2.0.0`, `rich>=13.0.0`) 

## 💻 Usage
To initialize the multi-agent swarm, run the main orchestrator script:

```bash
python main.py
```

1. The script will initialize the **Planner** to draft a functional architecture.
2. The **Critic** will review the JSON output, identify flaws, and send them back to the Planner for a maximum of 2 loops.
3. The **Summarizer** compiles the raw discussion log into a clean Markdown document.
4. The final specification is automatically saved locally in the `/workspace` folder.
