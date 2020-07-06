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
