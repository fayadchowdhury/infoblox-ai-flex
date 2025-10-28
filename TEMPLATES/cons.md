# cons.md (Template)

List at least 3 concrete limitations and tradeoffs of your approach.

## Con 1: Ignored IPv6 addresses

The data presents IPv6 addresses as well ("fe80::1%eth0") which are completely ignored in this pipeline. A more robust solution would rely on the `ipaddress` library to parse all kinds of valid IP addresses and then route to different processing functions based on whether it is IPv4 or IPv6.

## Con 2: Incomplete context

While the LLM (`gpt-4o-mini`) is fairly adept at this cleaning task, some more context such as the source of the dataset could possibly allow it to be used to parse sites, device types etc.

## Con 3: Only basic recommendations

If a more fine-tuned LLM were used, it would be able to generate better recommendations for each of the issues with IP addresses, MAC addresses etc. As of this implementation, it only recommends to either correct or mark the record for revision
