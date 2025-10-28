import pandas as pd
import json
from typing import Dict, List
from pipeline.ip import process_ipv4
from pipeline.hostname_fqdn import process_hostname, process_fqdn
from pipeline.site import normalize_site_name
from pipeline.mac import process_mac
from pipeline.device import process_device
from pipeline.owner import process_owner
from pipeline.llm import GPTClient

system_prompt = '''
You specialize in network analytics
'''
device_prompt = '''
Given the following string, I want you to parse it to extract:
- Device Type (based on Hostname and Device Type and Notes)
- Confidence score (low, high, mid) based on your classification, be very critical of this

I want you to return the response to me in a JSON format containing:
- device_out
- device_type_confidence

I want only the JSON and nothing else

Wherever impossible to do so, return empty strings within the JSON fields

String:
'''
owner_prompt = '''
Given the following string, I want you to parse it to extract:
- An email address
- A name
- A team name

I want you to return the response to me in a JSON format containing:
- owner_out (Capitalize owner name if possible, may be possible to obtain from email address too)
- owner_email
- owner_team

I want only the JSON and nothing else

Wherever impossible to do so, return empty strings within the JSON fields

String:
'''

def apply_and_expand(df: pd.DataFrame, func, input_cols: list[str], **kwargs) -> pd.DataFrame:
    
    # Apply the function row-wise, passing in the specified columns
    result_df = (
        df[input_cols]
        .apply(lambda row: func(*row, **kwargs), axis=1)
        .apply(pd.Series)
    )

    # Join results back to the original DataFrame
    return df.join(result_df)

def collect_anomalies(df: pd.DataFrame) -> List[Dict]:
    anomaly_records = []
    for _, row in df.iterrows():
        source_row_id = row.name

        issues = []
        for col in row.index:
            if col.endswith("issues"):
                issue_val = row[col]
                if pd.notna(issue_val) and str(issue_val).strip().lower() != "none":
                    issue_field = col[:col.index("_issues")]
                    issues.append(
                        {
                            "field": issue_field,
                            "type": issue_val,
                            "value": row[f"{issue_field}_out"] if pd.notna(row[f"{issue_field}_out"]) else ""
                        }
                    )
        recommended_actions = []
        for col in row.index:
            if col.endswith("recommended_action"):
                recommended_action = row[col]
                if pd.notna(recommended_action) and str(recommended_action).strip().lower() != "none":
                    recommended_actions.append(recommended_action)
        
        anomaly_records.append(
            {
                "source_row_id": source_row_id,
                "issues": issues,
                "recommended_actions": recommended_actions
            }
        )

    return anomaly_records

def generate_anomalies_json(output_file: str, anomaly_records: Dict) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(anomaly_records, f, ensure_ascii=False, indent=2)

def main():
    # Load input data
    raw_data = pd.read_csv("inventory_raw.csv")
    raw_data = raw_data.set_index("source_row_id")

    llm_client = GPTClient()

    # Process each field
    ip_norm_df = apply_and_expand(raw_data, process_ipv4, input_cols=["ip"])
    mac_norm_df = apply_and_expand(ip_norm_df, process_mac, input_cols=["mac"])
    site_norm_df = apply_and_expand(mac_norm_df, normalize_site_name, input_cols=["site"])
    hostname_norm_df = apply_and_expand(site_norm_df, process_hostname, input_cols=["hostname"])
    fqdn_norm_df = apply_and_expand(hostname_norm_df, process_fqdn, input_cols=["fqdn"])
    owner_norm_df = apply_and_expand(fqdn_norm_df, process_owner, input_cols=["owner"], llm=llm_client, system_prompt=system_prompt, owner_prompt=owner_prompt)
    device_norm_df = apply_and_expand(owner_norm_df, process_device, ["hostname", "device_type", "notes"], llm=llm_client, system_prompt=system_prompt, device_prompt=device_prompt)

    # # Save enriched DataFrame to CSV
    # device_norm_df.to_csv("inventory_enriched.csv", index=False)

    # Collect anomalies
    anomalies = collect_anomalies(device_norm_df)

    # Generate anomalies JSON file
    generate_anomalies_json("anomalies.json", anomalies)

    # Clean up dataframe
    normalization_steps_columns = [c for c in device_norm_df.columns if c.endswith("normalization_steps")]
    device_norm_df["normalization_steps"] = device_norm_df[normalization_steps_columns].fillna("").agg("|".join, axis=1)
    columns_of_interest = [
        'notes',
        'ip_out',
        'ip_valid',
        'ip_version',
        'ip_reverse_ptr',
        'ip_classification',
        'subnet_cidr',
        'mac_out',
        'mac_valid',
        'mac_kind',
        'site_out',
        'hostname_out',
        'hostname_valid',
        'hostname_kind',
        'fqdn_out',
        'fqdn_valid',
        'fqdn_kind',
        'owner_out',
        'owner_email',
        'owner_team',
        'device_out',
        'device_type_confidence',
    ]
    clean_df = device_norm_df[columns_of_interest]
    clean_df.rename(
        columns = {
            col: col[:col.index("_out")] for col in clean_df.columns if col.endswith("_out")
        }, inplace=True
    )
    clean_df.to_csv("inventory_clean.csv", index=True)

if __name__ == "__main__":
    main()