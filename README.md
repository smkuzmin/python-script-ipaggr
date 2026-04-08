```
IPAggr v1.16 - IPv4 Aggregator

Merges overlapping and adjacent IPv4 addresses and subnets into the minimum number
of networks, preserving and merging comments from the original list.

FEATURES:
  - Skips invalid lines without errors (empty lines, comments, text)
  - Automatically processes single IP addresses as /32
  - Outputs single addresses without /32 prefix
  - Automatic ascending sorting
  - Supports both CIDR prefixes and subnet masks (e.g., 192.168.1.0/24 or 192.168.1.0/255.255.255.0)
  - Preserves and merges comments from input lines
  - Fixed-width output format: "%-18s # %s"

INPUT FORMAT:
  192.168.1.1                  Single IP address
  192.168.1.0/24               Network with CIDR prefix
  192.168.1.0/255.255.255.0    Network with subnet mask

OUTPUT FORMAT:
  192.168.1.0/24     # comment1, comment2, ...
  192.168.1.1        # comment

USAGE:
  cat infile.lst | ipaggr
  ipaggr < infile.lst > outfile.lst
```
