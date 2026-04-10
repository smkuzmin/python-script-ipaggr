```
IPAggr v1.18 - IPv4 Aggregator

Merges overlapping and adjacent IPv4 addresses and subnets into the minimum number
of networks, preserving and merging comments from the original list.

FEATURES:
  - Rounds input networks to the specified CIDR prefix before aggregation
  - Supports both CIDR prefixes and subnet masks (e.g., 192.168.1.0/24 or 192.168.1.0/255.255.255.0)
  - Skips invalid lines without errors (empty lines, comments, text)
  - Preserves and merges comments from input lines
  - Automatically treats individual IP addresses as /32 networks
  - Outputs single addresses without /32 prefix
  - Automatically sorts output in ascending order
  - Uses fixed-width formatting: "%-18s # %s"

INPUT FORMAT:
  192.168.1.1                  Single IP address
  192.168.1.0/24               Network with CIDR prefix
  192.168.1.0/255.255.255.0    Network with subnet mask

OUTPUT FORMAT:
  192.168.1.0/24     # comment1, comment2, ...
  192.168.1.1        # comment

USAGE:
  cat infile.lst | ipaggr OPTIONS
  ipaggr OPTIONS < infile.lst > outfile.lst

OPTIONS:
  -p, --prefix=CIDR_PREFIX    Aggregation with rounding to the specified CIDR prefix
```
