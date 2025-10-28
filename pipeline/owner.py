from pipeline.llm import GPTClient
from typing import Dict


def trim_owner_str(owner: str) -> str:
    try:
        return str(owner).strip()
    except Exception:
        return ""
    
def process_owner(owner: str, llm: GPTClient, owner_prompt: str, system_prompt: str) -> Dict:
    steps = []
    notes = []
    trimmed_owner = trim_owner_str(owner)
    steps.append("owner_trim")
    owner_prompt_augmented = owner_prompt + trimmed_owner
    owner = llm.generate(system_prompt, owner_prompt_augmented)
    steps.append("owner_parse")
    if any(v == "" for v in owner.values()):
        owner_issues = "Missing owner fields"
        owner_recommended_action = "Correct owner or mark record for revision"
        steps.append(f"owner_invalid_missing_owner_fields")
    else:
        owner_issues = None
        owner_recommended_action = None
    return {
        **owner,
        "owner_issues": owner_issues,
        "owner_recommended_action": owner_recommended_action,
        "owner_normalization_steps": "|".join(steps)
    }