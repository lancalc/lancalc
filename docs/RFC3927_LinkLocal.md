# RFC 3927 - Link-Local Addresses

## Official IETF Document

[RFC 3927 - Dynamic Configuration of IPv4 Link-Local Addresses](https://tools.ietf.org/html/rfc3927)

## Description

The link-local address range 169.254.0.0/16 is used for automatic IP address configuration when no DHCP server is available. These addresses are not routable beyond the local network segment and are typically assigned automatically by the operating system.

## Example CLI Output

```bash
$ lancalc 169.254.1.1/16 --json
{
  "Network": "169.254.0.0",
  "Prefix": "/16",
  "Netmask": "255.255.0.0",
  "Broadcast": "-*",
  "Hostmin": "-*",
  "Hostmax": "-*",
  "Hosts": "-*",
  "message": "Link-local - RFC3927"
}
```

## Notes

- Host-related fields show "-*" because link-local addresses have special automatic assignment behavior
- Commonly seen on Windows systems when DHCP fails (APIPA - Automatic Private IP Addressing)
- Used for local communication only, not routable through gateways