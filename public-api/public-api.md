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
0x20   01
```

The packet starts with the length of the packet as one unsigned byte. 

The next 3 bytes ( 0x01 to 0x03 ) are constant and are always ```00 c2 04```, This is probably some identifier.
The byte at 0x05 is the length of the server's hostname in ascii, this is followed by the hostname in ascii encoding.
The packet is terminated by ```01```.

The two or three bytes after the hostname and before the terminator is one of the following in my test cases:
```
63 dd
2e 55 f3
2e 63 dd
```
I'm not sure what these bytes are yet.

In order for this protocol to be valid the client must send another packet only consisting of ```01 00```, if the client fails to do this the server will not send a response.
