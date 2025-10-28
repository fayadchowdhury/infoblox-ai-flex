from typing import Dict, Tuple

def trim_mac_str(mac: str) -> str:
    try:
        return str(mac).strip()
    except Exception:
        return ""
    
def is_valid_hex(s: str) -> bool:
    HEX = set("01223456789abcdefABCDEF")
    return s != "" and all(c in HEX for c in s)

def validate_and_label_mac(mac: str) -> Tuple[str, str]:
    """
    Returns (canonical_mac, label).
      - On success: ('aa:bb:cc:dd:ee:ff', 'ok') or EUI-64 equivalent.
      - On failure: (original_input, '<error_label>').
    Canonical form: lowercase, colon-separated. Accepts:
      - aa:bb:cc:dd:ee:ff  | aa-bb-cc-dd-ee-ff
      - aabb.ccdd.eeff     | aabb.ccdd.eeff.gghh
      - aabbccddeeff       | aabbccddeeffgghh
    """
    if mac is None:
        return "", "missing"
    s = trim_mac_str(mac)
    if s == "":
        return s, "empty_string"

    has_colon = ":" in s
    has_dash  = "-" in s
    has_dot   = "." in s

    # reject mixed separators
    if sum([has_colon, has_dash, has_dot]) > 1:
        return s, "mixed_separators"

    octets = []

    if has_colon or has_dash:
        sep = ":" if has_colon else "-"
        parts = s.split(sep)
        if len(parts) not in (6, 8):
            return s, "wrong_group_count"
        for p in parts:
            p = p.strip()
            if len(p) != 2 or not is_valid_hex(p):
                return s, "bad_octet_hex"
            octets.append(p.lower())

    elif has_dot:
        # Cisco-style: aabb.ccdd.eeff(.gghh)
        parts = s.split(".")
        if len(parts) not in (3, 4):
            return s, "wrong_group_count_dot"
        for grp in parts:
            grp = grp.strip()
            if len(grp) != 4 or not is_valid_hex(grp):
                return s, "bad_group_hex_dot"
            octets.extend([grp[0:2].lower(), grp[2:4].lower()])

    else:
        # No separators: 12 (EUI-48) or 16 (EUI-64) hex chars
        if not is_valid_hex(s):
            return s, "non_hex_chars"
        if len(s) not in (12, 16):
            return s, "wrong_length_no_separators"
        octets = [s[i:i+2].lower() for i in range(0, len(s), 2)]

    if len(octets) not in (6, 8):
        return s, "not_6_or_8_octets"

    canonical = ":".join(octets)
    return canonical, "ok"

def classify_mac(mac: str, validation_label: str) -> str:
    """
    Only returns 'eui48' or 'eui64' (or 'unclassified' if not ok).
    """
    if validation_label != "ok":
        return "unclassified"
    count = len(mac.split(":"))
    if count == 6:
        return "eui48"
    if count == 8:
        return "eui64"
    return "unclassified"

def process_mac(mac: str) -> Dict:
    steps = []
    notes = []
    trimmed_mac = trim_mac_str(mac)
    steps.append("mac_trim")
    trimmed_mac, validation_label = validate_and_label_mac(trimmed_mac)
    if validation_label == "ok":
        steps.append("mac_parse")
        steps.append("mac_normalize")
        classification = classify_mac(trimmed_mac, validation_label)
        steps.append("mac_classify")
        mac_out = trimmed_mac
        mac_valid = "True"
        mac_kind = classification
        mac_issues = None
        mac_recommended_action = None
    else:
        mac_out = str(mac).strip()
        mac_valid = "False"
        mac_kind = ""
        mac_issues = validation_label
        mac_recommended_action = "Correct MAC or mark record for revision"
        steps.append(f"mac_invalid_{validation_label}")
    return {
        "mac_out": mac_out,
        "mac_valid": mac_valid,
        "mac_kind": mac_kind,
        "mac_issues": mac_issues,
        "mac_recommended_action": mac_recommended_action,
        "mac_normalization_steps": "|".join(steps),
    }