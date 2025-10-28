from typing import Tuple, Dict

def trim_ip_str(ip: str) -> str:
    try:
        return ip.strip()
    except AttributeError:
        return ""
    
def validate_and_label_ipv4(ip: str) -> Tuple[str, str]:
    if ip == "":
        return ip, "empty_string"
    if ":" in ip:
        return ip, "ipv6_or_mixed_non_ipv4"
    if "." not in ip:
        return ip, "no_octet_separation"
    parts = ip.split(".")
    if len(parts) != 4:
        return ip, "wrong_part_count"
    canonical_parts = []
    for part in parts:
        part = part.strip()
        if part == "":
            return ip, "empty_octet"
        if not (part.lstrip("+").isdigit() and not part.startswith("-")):
            return ip, "non_numeric_or_negative"
        try:
            v = int(part, 10)
        except ValueError:
            return ip, "non_decimal_format"
        if v < 0 or v > 255:
            return ip, "octet_out_of_range"
        canonical_parts.append(str(v))
    return '.'.join(canonical_parts), "ok"

def determine_reverse_ptr_ipv4(ip: str, validation_label: str) -> str:
    if validation_label != "ok":
        return ""
    parts = ip.split(".")
    reversed_parts = parts[::-1]
    return ".".join(reversed_parts) + ".in-addr.arpa"

def classify_ipv4(ip: str, validation_label: str) -> str:
    if validation_label != "ok":
        return "unclassified"
    a, b, c, d = list(map(int, ip.split(".")))
    classification = ""
    if ip == "0.0.0.0" :
        classification = "unspecified"
    elif ip == "255.255.255.255":
        classification = "limited_broadcast"
    elif a == 127:
        classification = "loopback"
    elif a == 169 and b == 254:
        classification = "link_local_apipa"
    elif 224 <= a <= 239:
        classification = "multicast"
    elif 240 <= a <= 255 and ip != "255.255.255.255":
        classification = "reserved"
    elif a == 10 or (a == 172 and 16 <= b <= 31) or (a == 192 and b == 168):
        classification = "private"
    else:
        classification = "public_or_other"
    return classification

def determine_subnet(ip: str, classification: str) -> str:
    if classification == "unclassified":
        return ""
    if classification in ["limited_broadcast", "unspecified", "unclassified", "multicast", "reserved"]:
        return ""
    elif classification == "loopback":
        mask = "8"
        subnet_ip = f"{'.'.join(ip.split(".")[:3])}.0/{mask}"
        return subnet_ip
    elif classification == "private":
        mask = "24"
        subnet_ip = f"{ip}/{mask}"
        return subnet_ip
    elif classification == "link_local_apipa":
        mask = "16"
        subnet_ip = f"{'.'.join(ip.split(".")[:2])}.0.0/{mask}"
        return subnet_ip
    else:
        return ""
    
def process_ipv4(ip: str) -> Dict:
    steps = []
    notes = []
    trimmed_ip = trim_ip_str(ip)
    steps.append("ip_trim")
    trimmed_ip, validation_label = validate_and_label_ipv4(trimmed_ip)
    if validation_label == "ok":
        steps.append("ip_parse")
        steps.append("ip_normalize")
        reverse_ptr = determine_reverse_ptr_ipv4(trimmed_ip, validation_label)
        steps.append("ip_reverse_ptr_determine")
        classification = classify_ipv4(trimmed_ip, validation_label)
        steps.append("ip_classify")
        subnet = determine_subnet(trimmed_ip, classification)
        steps.append("ip_subnet_determine")
        ip_out = trimmed_ip
        ip_valid = "True"
        ip_version = "4"
        ip_reverse_ptr = reverse_ptr
        ip_classification = classification
        subnet_cidr = subnet
        ip_issues = None
        ip_recommended_action = None
    else:
        ip_out = str(ip).strip()
        ip_classification = ""
        ip_valid = "False"
        ip_version = ""
        ip_reverse_ptr = ""
        ip_classification = ""
        subnet_cidr = ""
        ip_issues = validation_label
        ip_recommended_action = "Correct IP or mark record for revision"
        steps.append(f"ip_invalid_{validation_label}")
    return {
        "ip_out": ip_out,
        "ip_valid": ip_valid,
        "ip_version": ip_version,
        "ip_reverse_ptr": ip_reverse_ptr,
        "ip_classification": ip_classification,
        "subnet_cidr": subnet_cidr,
        "ip_issues": ip_issues,
        "ip_recommended_action": ip_recommended_action,
        "ip_normalization_steps": "|".join(steps),
    }