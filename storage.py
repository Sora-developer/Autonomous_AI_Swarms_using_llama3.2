import os 
from datetime import datetime

def save_specification(idea: str, markdown_content: str):
    """Saves the final technical specification to a local worksace directory"""

    #Create the workspace directory if it doesn't exists
    workspace_dir = "workspace"
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
    

    # Create a safe filename based on the idea and timestamp
    safe_idea = "".join([c if c.isalnum() else "_" for c in idea])[:20]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{workspace_dir}/spec_{safe_idea}_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    return filename
