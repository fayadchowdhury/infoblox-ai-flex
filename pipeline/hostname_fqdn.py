from typing import List, Tuple, Dict

# ---------- TRIM ----------
def trim_dns_str(s: str) -> str:
    try:
        return s.strip()
    except AttributeError:
        return ""

# ---------- CORE HELPERS ----------
def _label_to_idna_ascii(label: str) -> Tuple[str, str]:
    """
    Convert a (possibly unicode) label to IDNA ASCII (xn--...).
    Returns (ascii_label, err_label). err_label == "" means OK.
    """
    try:
        ascii_label = label.encode("idna").decode("ascii")
        return ascii_label, ""
    except Exception:
        return label, "idna_encode_failed"

def _is_valid_label_ascii(label: str, allow_underscore: bool) -> str:
    """
    Validate an ASCII (already IDNA-encoded) DNS label per RFC 1123:
      - 1..63 chars
      - letters/digits/hyphen, optional underscore if allowed
      - cannot start or end with '-'
    Return "" if OK, else an error label.
    """
    if label == "":
        return "empty_label"
    if len(label) > 63:
        return "label_too_long"
    if label[0] == "-" or label[-1] == "-":
        return "label_starts_or_ends_with_hyphen"
    for ch in label:
        if ch.isalnum() or ch == "-" or (allow_underscore and ch == "_"):
            continue
        return "invalid_characters"
    return ""

# ---------- HOSTNAME (SINGLE LABEL) ----------
def validate_and_label_hostname_label(label: str, *, allow_underscore: bool = False) -> Tuple[str, str]:
    """
    Validate a single hostname label.
    Returns (normalized_label, 'ok') on success, or (original_input, '<error>') on failure.
    Normalization: IDNA → ASCII, then lowercase.
    """
    s = trim_dns_str(label)
    if s == "":
        return s, "empty_string"
    ascii_label, err = _label_to_idna_ascii(s)
    if err:
        return s, err
    ascii_label = ascii_label.lower()
    e = _is_valid_label_ascii(ascii_label, allow_underscore)
    if e:
        return s, e
    return ascii_label, "ok"

def classify_hostname_label(normalized_label: str, validation_label: str) -> str:
    """
    Return 'single_label' when validation_label == 'ok', else 'unclassified'.
    """
    return "single_label" if validation_label == "ok" else "unclassified"

# ---------- FQDN (ONE OR MORE LABELS, OPTIONAL TRAILING DOT) ----------
def validate_and_label_fqdn(
    name: str,
    *,
    allow_underscore: bool = False,
    require_at_least_two_labels: bool = False,
    forbid_numeric_tld: bool = False
) -> Tuple[str, str]:
    """
    Validate a hostname/FQDN (e.g., 'api.example.com' or 'api.example.com.').
    Returns (normalized_ascii, 'ok' | 'ok_absolute') on success, or (original_input, '<error>').

    Normalization:
      - Each label IDNA-encoded to ASCII and lowercased.
      - Trailing dot (absolute FQDN) is removed from the returned value; 'ok_absolute' signals it was present.

    Constraints:
      - Per-label rules per RFC 1123 (with optional underscores).
      - Total length (joined with dots, NO trailing dot) ≤ 253.
      - If require_at_least_two_labels=True, single-label names are rejected.
      - If forbid_numeric_tld=True, the last label cannot be all digits.
    """
    s = trim_dns_str(name)
    if s == "":
        return s, "empty_string"

    absolute = s.endswith(".")
    if absolute:
        s = s[:-1]  # strip for validation/length checks

    raw_labels = s.split(".")
    if any(lbl == "" for lbl in raw_labels):
        return name, "empty_label_in_sequence"

    ascii_labels: List[str] = []
    for lbl in raw_labels:
        a, err = _label_to_idna_ascii(lbl)
        if err:
            return name, err
        a = a.lower()
        e = _is_valid_label_ascii(a, allow_underscore)
        if e:
            return name, e
        ascii_labels.append(a)

    if require_at_least_two_labels and len(ascii_labels) < 2:
        return name, "requires_at_least_two_labels"

    if forbid_numeric_tld and ascii_labels and ascii_labels[-1].isdigit():
        return name, "numeric_tld_forbidden"

    joined = ".".join(ascii_labels)
    if len(joined) > 253:
        return name, "fqdn_too_long"

    return joined, ("ok_absolute" if absolute else "ok")

def classify_fqdn(normalized_name: str, validation_label: str) -> str:
    """
    Return:
      - 'absolute_fqdn' if validation_label == 'ok_absolute'
      - 'fqdn' if validation_label == 'ok' and there's at least one dot
      - 'single_label' if validation_label == 'ok' and no dots
      - 'unclassified' otherwise
    """
    if validation_label == "ok_absolute":
        return "absolute_fqdn"
    if validation_label == "ok":
        return "fqdn" if "." in normalized_name else "single_label"
    return "unclassified"

# ---------- OPTIONAL: AUTO-ROUTER (if your column may be either) ----------
def validate_and_label_dns_name(
    name: str,
    *,
    allow_underscore: bool = False,
    require_at_least_two_labels_for_fqdn: bool = False,
    forbid_numeric_tld: bool = False
) -> Tuple[str, str, str]:
    """
    Convenience: tries FQDN validation first (accepts single labels), returns
    (normalized_value, validation_label, kind)
      - kind in {'absolute_fqdn','fqdn','single_label','unclassified'}
    """
    normalized, label = validate_and_label_fqdn(
        name,
        allow_underscore=allow_underscore,
        require_at_least_two_labels=require_at_least_two_labels_for_fqdn,
        forbid_numeric_tld=forbid_numeric_tld,
    )
    kind = classify_fqdn(normalized, label)
    return normalized, label, kind

def process_hostname(hostname: str) -> Dict:
    steps = []
    notes = []
    hostname_normalized, hostname_label = validate_and_label_hostname_label(hostname)
    steps.append("hostname_normalize")
    steps.append("hostname_label")
    hostname_classification = classify_hostname_label(hostname_normalized, hostname_label)
    steps.append("hostname_classify")
    if hostname_label == "ok":
        hostname_out = hostname_normalized
        hostname_valid = "True"
        hostname_kind = hostname_classification
        hostname_issues = None
        hostname_recommended_action = None
    else:
        hostname_out = hostname
        hostname_valid = "False"
        hostname_kind = ""
        hostname_issues = hostname_label
        hostname_recommended_action = "Correct hostname or mark record for revision"
        steps.append(f"hostname_invalid_{hostname_issues}")
    return {
        "hostname_out": hostname_out,
        "hostname_valid": hostname_valid,
        "hostname_kind": hostname_kind,
        "hostname_issues": hostname_issues,
        "hostname_recommended_action": hostname_recommended_action,
        "hostname_normalization_steps": "|".join(steps)
    }

def process_fqdn(fqdn: str) -> Dict:
    steps = []
    notes = []
    fqdn_normalized, fqdn_label = validate_and_label_fqdn(fqdn)
    steps.append("fqdn_normalize")
    steps.append("fqdn_label")
    fqdn_classification = classify_fqdn(fqdn_normalized, fqdn_label)
    steps.append("fqdn_classify")
    if fqdn_label == "ok":
        fqdn_out = fqdn_normalized
        fqdn_valid = "True"
        fqdn_kind = fqdn_classification
        fqdn_issues = None
        fqdn_recommended_action = None
    else:
        fqdn_out = fqdn
        fqdn_valid = "False"
        fqdn_kind = ""
        fqdn_issues = fqdn_label
        fqdn_recommended_action = "Correct FQDN or mark record for revision"
        steps.append(f"fqdn_invalid_{fqdn_issues}")
    return {
        "fqdn_out": fqdn_out,
        "fqdn_valid": fqdn_valid,
        "fqdn_kind": fqdn_kind,
        "fqdn_issues": fqdn_issues,
        "fqdn_recommended_action": fqdn_recommended_action,
        "fqdn_normalization_steps": "|".join(steps)
    }