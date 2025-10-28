import re

def normalize_site_name(name: str) -> str:
    steps = []
    if not name or not isinstance(name, str):
        return {
            "site_out": "",
            "site_normalization_steps": "site_invalid_missing_site"
        }

    # Mapping of common abbreviations to full forms
    replacements = {
        r"\bBldg\b": "Building",
        r"\bBLR\b": "Bangalore",
        r"\bDC\b": "Datacenter",
        r"\bHQ\b": "Headquarters",
        r"\bLab\b": "Laboratory",
        r"\bCampus\b": "Campus",  # keep capitalization consistent
    }

    s = name.strip()

    # Apply replacements (case-insensitive)
    for pattern, full in replacements.items():
        s = re.sub(pattern, full, s, flags=re.IGNORECASE)

    steps.append("site_replace_common_abbreviations")
    # Replace spaces/underscores with hyphens
    s = re.sub(r"[ _]+", "-", s)
    steps.append("site_replace_common_abbreviations")
    
    # Remove duplicate hyphens
    s = re.sub(r"-{2,}", "-", s)
    steps.append("site_replace_whitespace_with_hypen")

    # Normalize capitalization (title case or upper depending on your style)
    s = s.title()
    steps.append("site_capitalize")

    if s == "":
        site_issues = "Missing site fields"
        site_recommended_action = "Correct site or mark record for revision"
        steps.append("site_invalid_missing_site_fields")
    else:
        site_issues = None
        site_recommended_action = None

    return {
        "site_out": s,
        "site_issues": site_issues,
        "site_recommended_action": site_recommended_action,
        "site_normalization_steps": "|".join(steps)
    }