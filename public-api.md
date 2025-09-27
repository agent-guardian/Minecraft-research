# Public API
I decided a good place to start is the information that you're shown on the server list in the main menu of Minecraft. It seems like the easiest information to access and there's clearly a way to get this information, server list websites appear to have this information.

I'm going to try to gather the following information:
- Server Online
- Server type (vanilla/spigot/etc)
- Number of online players
- Online player usernames
- Server MOTD
- Server icon
- Server version
- Any other information I manage to find

I'm going to start by using [Wireshark](https://www.wireshark.org/#download) to look at the packets exchanged by the client when opening the muliplay menu.

I recorded all the packets going through my ethernet card with Wireshark and used a display filter after recording to only show packets between my ip and a server ip and had some data sent with the packet, this is to ignore the TCP setup packets and irrelevant network traffic.

Our first packet going to the server contains the server's hostname (so I'm going to cencor that, but I'll keep the size the same) a long with some addition bytes before and after the hostname.

```
0x00   20 00 c2 04 19 XX XX XX XX XX XX XX XX XX XX XX
0x10   XX XX XX XX XX XX XX XX XX XX XX XX XX XX 63 dd
0x20   01                                                .                                                .
```

With just a bit of counting we can discover that the byte at 0x04 is the length of the hostname in ascii. Following this (starting at 0x05) is the hostname. The packet ends with 0x63 dd 01, this appears to be the same in all of these request packets, so this is probably a request terminator.
