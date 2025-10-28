from pipeline.llm import GPTClient
from typing import Dict

def trim_device_type_str(device_type: str) -> str:
    try:
        return str(device_type).strip()
    except Exception:
        return ""
    
def process_device(device: str, hostname: str, notes: str, llm: GPTClient, device_prompt: str, system_prompt: str) -> Dict:
    steps = []
    notes = []
    steps.append("device_trim")
    device_prompt_augmented = device_prompt + f"Hostname: {hostname} Device Type: {trim_device_type_str(device)} Notes: {notes}"
    device = llm.generate(system_prompt, device_prompt_augmented)
    steps.append("device_parse")
    if any(v == "" for v in device.values()):
        device_issues = "Missing device fields"
        device_recommended_action = "Correct device or mark record for revision"
        steps.append(f"device_invalid_missing_device_fields")
    else:
        device_issues = None
        device_recommended_action = None
    return {
        **device,
        "device_issues": device_issues,
        "device_recommended_action": device_recommended_action,
        "device_normalization_steps": "|".join(steps)
    }