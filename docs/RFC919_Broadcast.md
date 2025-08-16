# RFC 919 - Broadcast Address

## Official IETF Document

[RFC 919 - Broadcasting Internet Datagrams](https://tools.ietf.org/html/rfc919)

## Description

The limited broadcast address 255.255.255.255 is used to send packets to all hosts on the local network segment. This address is never forwarded by routers and is used for network-wide announcements and discovery protocols.

## Example CLI Output

```bash
$ lancalc 255.255.255.255/32 --json
{
  "Network": "255.255.255.255",
  "Prefix": "/32",
  "Netmask": "255.255.255.255",
  "Broadcast": "-*",
  "Hostmin": "-*",
  "Hostmax": "-*",
  "Hosts": "-*",
  "message": "Broadcast - RFC919"
}
```

## Notes

- Host-related fields show "-*" because the broadcast address is not used for individual host addressing
- Different from directed broadcast (network broadcast address) as this is the limited broadcast
- Used by protocols like DHCP, ARP, and Wake-on-LAN