# RFC 1122 - Unspecified Addresses

## Official IETF Document

[RFC 1122 - Requirements for Internet Hosts -- Communication Layers](https://tools.ietf.org/html/rfc1122)

## Description

The unspecified address range 0.0.0.0/8 contains addresses that have special meaning in network protocols. The address 0.0.0.0 is used to indicate "this host on this network" and should not be used for regular host addressing. Note that 0.0.0.0/0 (the default route) is treated as normal unicast.

## Example CLI Output

```bash
$ lancalc 0.0.0.1/8 --json
{
  "Network": "0.0.0.0",
  "Prefix": "/8",
  "Netmask": "255.0.0.0",
  "Broadcast": "-*",
  "Hostmin": "-*",
  "Hostmax": "-*",
  "Hosts": "-*",
  "message": "Unspecified - RFC1122"
}
```

## Notes

- Host-related fields show "-*" because these addresses have special protocol meanings
- 0.0.0.0 is used in DHCP and routing protocols to indicate "this network"
- The default route 0.0.0.0/0 is treated as normal unicast, not unspecified