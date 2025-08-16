# RFC 5771 - Multicast Addresses

## Official IETF Document

[RFC 5771 - IANA Guidelines for IPv4 Multicast Address Assignments](https://tools.ietf.org/html/rfc5771)

## Description

The multicast address range 224.0.0.0/4 (224.0.0.0 - 239.255.255.255) is reserved for IP multicast communication. These addresses are used to send data to multiple hosts simultaneously and are not intended for traditional unicast host addressing.

## Example CLI Output

```bash
$ lancalc 224.0.0.1/4 --json
{
  "Network": "224.0.0.0",
  "Prefix": "/4",
  "Netmask": "240.0.0.0",
  "Broadcast": "-*",
  "Hostmin": "-*",
  "Hostmax": "-*",
  "Hosts": "-*",
  "message": "Multicast - RFC5771"
}
```

## Notes

- Host-related fields show "-*" because multicast addresses are not used for individual host identification
- Used for protocols like IGMP, streaming media, and group communication
- Different from broadcast as they require explicit group membership