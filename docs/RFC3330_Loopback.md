# RFC 3330 - Loopback Addresses

## Official IETF Document

[RFC 3330 - Special-Use IPv4 Addresses](https://tools.ietf.org/html/rfc3330)

## Description

The loopback address range 127.0.0.0/8 is reserved for communication within the same host. These addresses are not routable on the Internet and are used for internal host-to-host communication, typically for testing and diagnostics.

## Example CLI Output

```bash
$ lancalc 127.0.0.1/8 --json
{
  "Network": "127.0.0.0",
  "Prefix": "/8",
  "Netmask": "255.0.0.0",
  "Broadcast": "-*",
  "Hostmin": "-*",
  "Hostmax": "-*",
  "Hosts": "-*",
  "message": "Loopback - RFC3330"
}
```

## Notes

- Host-related fields show "-*" because loopback addresses are not used for traditional host addressing
- The entire 127.0.0.0/8 range is reserved, not just 127.0.0.1
- Commonly used for localhost communication and application testing