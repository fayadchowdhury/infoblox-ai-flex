# prompts.md

### Overall system prompt

```
You specialize in network analytics
```

Constraints: None

Output format: Not applicable

Rationale: Because this task was grounded in cleaning up data from network interactions, it made sense to prepare the LLM to be an expert at network analytics. This way, it could contextualize data better, especially the device type. There were no constraints or output formats specified because this was a system prompt

### Prompt to parse device_type

```
Given the following string, I want you to parse it to extract:
- Device Type (based on Hostname and Device Type and Notes)
- Confidence score (low, high, mid) based on your classification, be very critical of this

I want you to return the response to me in a JSON format containing:
- device_out
- device_type_confidence

I want only the JSON and nothing else

Wherever impossible to do so, return empty strings within the JSON fields

String:
```

Constraints: Other than system prompt to prepare it for network analytics, its classification of device type would be grounded in hostname, device type and associated notes

Output format:

```json
{
  "device_out": "name/type of device; empty if impossible to do so",
  "device_type_confidence": "low/mid/high depending on how confidently it classified device; empty if impossible to do so"
}
```

Rationale: The base prompt did pretty well initially with just the device type passed to the LLM. However, upon inspection, there could be more enriching information present in the notes and the hostname, which is why these were passed along with the device type. Initially, the confidence score was a number ranging from 0 to 1 but that results in some randomness given that the LLM would sometimes output 0.9 and sometimes 0.95 for the same record. To incorporate more determinism, the confidence was switched to low/mid/high

### Prompt to parse owner

```
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
```

Constraints: Other than system prompt to prepare it for network analytics, its parsing of the owner was based entirely on the owner field with the name of the owner sometimes parsed from the email address

Output format:

```json
{
  "owner_out": "name of owner; empty if impossible to do so",
  "owner_email": "email address of owner; empty if impossible to do so",
  "owner_team": "team of owner; empty if impossible to do so"
}
```

Rationale: The initial prompt was successfully able to parse owner names and email addresses where present. However, in the case of `priya (platform) priya@corp.example.com`, it was missing out on the team name, and in the case of `jane@corp.example.com`, it was missing out on the owner name (`Jane`). This prompt is successfully able to parse and extract all the required information.
