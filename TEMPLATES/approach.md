# approach.md (Template)

Explain your pipeline (rules → LLM), constraints, and how to reproduce end‑to‑end.

## Overall pipeline

Read raw data into Pandas DataFrame -> Set index to source_row_id -> Normalize IP -> Normalize MAC -> Normalize site -> Normalize hostname -> Normalize FQDN -> Normalize owner -> Normalize device -> Generate anomalies -> Clean up final dataframe -> Output cleaned dataframe and anomalies JSON

## Individual processes

### Normalize IP

<ol>
<li>Trim IP string if possible, return empty string if not</li>
<li>Validate IP string based on octets, return valid IP and a label to show whether IP was valid or not</li>
<li>Determine reverse_ptr as reversed octets + ".in-addr.arpa" if valid IP</li>
<li>Classify IP address into "unspecified", "unclassified", "limited_broadcast", "loopback", "link_local_apipa", "multicast", "reserved", "private" or "public_or_other" based on RFC1918 if valid IP</li>
<li>Determine subnet mask based on classification</li>
<li>Add processing steps and recommended actions if there are issues (based on validation label)</li>
</ol>

### Normalize MAC

<ol>
<li>Trim MAC string if possible, return empty string if not</li>
<li>Validate MAC string based on parts separated by separator (reject if multiple separators like ":" and "-" and "."), return canonicalized MAC and a label to show whether MAC was valid or not</li>
<li>Classify MAC address into "eui48", "eui64" or  "unclassified" based on count of MAC address parts</li>
<li>Add processing steps and recommended actions if there are issues (based on validation label)</li>
</ol>

### Normalize site

<ol>
<li>Trim site string if possible, return empty string if not</li>
<li>Replace common abbreviations with their full forms (Bldg to Building)</li>
<li>Remove unnecessary whitespaces and hyphens</li>
<li>Capitalize site names</li>
<li>Add processing steps and recommended actions if there are issues (based on validation label)</li>
</ol>

### Normalize hostname

<ol>
<li>Trim hostname string if possible, return empty string if not</li>
<li>Convert to IDNA and then to ASCII and check for validity (1-63 characters, only letters, digits and optional underscores, cannot start or end with "-")</li>
<li>Classify into "single-label" or "unclassified" based on validation label</li>
<li>Add processing steps and recommended actions if there are issues (based on validation label)</li>
</ol>

### Normalize FQDN

<ol>
<li>Trim FQDN string if possible, return empty string if not</li>
<li>Convert to IDNA and then to ASCII and remove trailiing dot</li>
<li>Classify into "absolute_fqdn", "fqdn", "single-label" or "unclassified" based on validation label</li>
<li>Add processing steps and recommended actions if there are issues (based on validation label)</li>
</ol>

### Normalize owner

<ol>
<li>Trim owner string if possible, return empty string if not</li>
<li>Parse owner name, email and team based on LLM call (prompt specified in prompts.md)</li>
<li>Add processing steps and recommended actions if there are issues (based on validation label)</li>
</ol>

### Normalize device

<ol>
<li>Trim device type string if possible, return empty string if not</li>
<li>Parse device based on LLM call (prompt specified in prompts.md)</li>
<li>Add processing steps and recommended actions if there are issues (based on validation label)</li>
</ol>

### Generate anomalies

<ol>
<li>Iterate over rows</li>
<li>For columns with names ending in "_issues", extract the issue field, type and value</li>
<li>For columns with names ending in "_recommended_action", extract the recommended action</li>
<li>Combine into single JSON entry for each row</li>
</ol>

### Clean up final dataframe

<ol>
<li>Gather and concatenate normalization steps from all columns with names ending in "_normalization_steps"</li>
<li>Retain only the columns of interest and rename them as required</li>
</ol>

### Output cleaned dataframe and anomalies JSON

Save dataframe to inventory_clean.csv and anomalies to anomalies.json

## Setup

```
python3 -m venv venv
source venv/bin/activate (adapt for non-Unix systems)
pip3 install -R requirements.txt
```

## Run

```
python3 run.py
```

## Constraints

Other than the cons mentioned in cons.md:

<ul>
<li>Dependent on external libraries (openai, pandas, numpy, dotenv, jupyter)</li>
<li>Specific to the provided dataset</li>
<li>No informative logging, slow process hard to tell where it is at</li>
</ul>
