#!/usr/bin/python3
import socket, io, json, binascii, sys, errno, argparse

colors = {
    "black"          : "\033[38;2;0;0;0;m",       #00 00 00   0   0   0
    "dark_blue"      : "\033[38;2;0;0;170;m",     #00 00 aa   0   0   170
    "dark_green"     : "\033[38;2;0;170;0;m",     #00 aa 00   0   170 0
    "dark_aqua"      : "\033[38;2;0;170;170;m",   #00 aa aa   0   170 170
    "dark_red"       : "\033[38;2;170;0;0;m",     #aa 00 00   170 0   0
    "dark_purple"    : "\033[38;2;170;0;170;m",   #aa 00 aa   170 0   170
    "gold"           : "\033[38;2;255;170;0;m",   #ff aa 00   255 170 0
    "gray"           : "\033[38;2;170;170;170;m", #aa aa aa   170 170 170
    "dark_gray"      : "\033[38;2;55;85;85;m",    #55 55 55   85  85  85
    "blue"           : "\033[38;2;55;85;255;m",   #55 55 ff   85  85  255
    "green"          : "\033[38;2;55;255;85;m",   #55 ff 55   85  255 85
    "aqua"           : "\033[38;2;55;255;255;m",  #55 ff ff   85  255 255
    "red"            : "\033[38;2;255;85;85;m",   #ff 55 55   255 85  85
    "light_purple"   : "\033[38;2;255;85;255;m",  #ff 55 ff   255 85  255
    "yellow"         : "\033[38;2;255;255;85;m",  #ff ff 55   255 255 85
    "white"          : "\033[38;2;255;255;255;m", #ff ff ff   255 255 255
    "reset"          : "\033[0m",
    "obfuscated"     : "\033[8m",
    "bold"           : "\033[1m",
    "strikethrough"  : "\033[9m",
    "underline"      : "\033[4m",
    "italic"         : "\033[3m"
}

seen = {
    "translate" : str,
    "with" : [str],
    "description" : {
        "extra" : [
            {
                "color" : str,
                "bold" : bool,
                "italic" : bool,
                "text" : str
           }
        ],
        "text" : str
        },
    "players" : {
        "max" : int,
        "online" : int,
        "sample" : [
            {
                "id" : str,
                "name" : str
            }
        ]
    },
    "version" : {
        "name" : str,
        "protocol" : int
    },
    "favicon" : str,
    "modinfo" : {
        "type" : str,
        "modList" : list
    }
}

print_raw_json = False
raw_json_file = False
print_json_key_structure = False
check_new_json_keys = True
text_color_formatting = True

def recieveResponse(s: socket) -> bytes:
    data = bytearray()
    while True:
        buff = bytearray(1460)
        byteCount = s.recv_into(buff)
        if len(data) == 0 and byteCount < 6:
            print("Recieved unknown data before server response: 0x" + buff[0:byteCount].hex())
            continue
        data += buff[0:byteCount]
        if byteCount < 1460:
            return data

def printKeys(data, indent=0):
    indentStr = ""
    for i in range(indent):
        indentStr += "\t"
    if isinstance(data,list):
        if len(data) > 0:
            print(indentStr + str(data[0]) + " " + str(type(data[0])))
            if isinstance(data[0], (dict, list)):
                printKeys(data[0], indent+1)
    else:
        for key in data.keys():
            if isinstance(data[key], list) and len(data[key]) > 0:
                print(indentStr + key + " " + str(type(data[key])) + " " + str(type(data[key][0])))
                if isinstance(data[key][0], (dict, list)):
                    printKeys(data[key][0], indent+1)
            else:
                print(indentStr + key + " " + str(type(data[key])))
                if isinstance(data[key], dict):
                    printKeys(data[key], indent+1)
    if indent == 0:
        print()

def checkHasSeen(data, s=seen, indent=0):
    indentStr = ""
    foundNew = False
    for i in range(indent):
        indentStr += "\t"
    for key in data.keys():
        if key in s.keys():
            if isinstance(data[key], dict):
                if isinstance(s[key], dict):
                    r = checkHasSeen(data[key], s[key], indent + 1)
                elif len(s[key]) > 0:
                    r = checkHasSeen(data[key], s[key][0], indent + 1)
                if r:
                    if indent == 0:
                        if not foundNew:
                            print("Found new json key(s):\n")
                        print(key + " " + str(type(data[key])) + "\n" + r)
                        foundNew = True
                    else:
                        return indentStr + key + " " + str(type(data[key])) + "\n" + r
            elif isinstance(data[key], list):
                if len(data[key]) > 0:
                    if isinstance(s[key], dict):
                        r = checkHasSeen(data[key][0], s[key], indent + 1)
                    elif len(s[key]) > 0:
                        r = checkHasSeen(data[key][0], s[key][0], indent + 1)
                    if r:
                        if indent == 0:
                            if not foundNew:
                                print("Found new json key(s):\n")
                            print(key + " " + str(type(data[key])) + "\n" + r)
                            foundNew = True
                        else:
                            return indentStr + key + " " + str(type(data[key])) + "\n" + r
        else:
            if indent == 0:
                if not foundNew:
                    print("Found new json key(s):\n")
                print(key + " " + str(type(data[key])))
                foundNew = True
            else:
                return indentStr + key + " " + str(type(data[key]))
    if indent == 0 and foundNew:
        print()

def parseAndPrint(jsonStr: str):
    if print_raw_json:
        print(jsonStr)
        return
    data = json.loads(jsonStr)
    if check_new_json_keys:
        checkHasSeen(data)
    if print_json_key_structure:
        printKeys(data)
    if "translate" in data:
        print(data["translate"])
        if "with" in data:
            for d in data["with"]:
                print(d)
        return
    if isinstance(data["description"],str):
        print(data["description"])
    else:
        if "extra" in data["description"]:
            for d in data["description"]["extra"]:
                if text_color_formatting:
                    if "color" in d:
                        print(colors[d["color"]], end='')
                    if "bold" in d and d["bold"]:
                        print(colors["bold"],end='')
                    if "italic" in d and d["italic"]:
                        print(colors["italic"],end='')
                    if "strikethrough" in d and d["strikethrough"]:
                        print(colors["strikethrough"],end='')
                    if "underline" in d and d["underline"]:
                        print(colors["underline"],end='')
                    if "obfuscated" in d and d["obfuscated"]:
                        print(colors["obfuscated"],end='')
                    if "reset" in d and d["reset"]:
                        print(colors["reset"],end='')
                print(d["text"],end="")
                if text_color_formatting:
                    print(colors["reset"],end='')
            print()
        else:
            if "text" in data["description"]:
                print(data["description"]["text"])
    print("Players Online " + str(data["players"]["online"]) + "/" + str(data["players"]["max"]))
    if "sample" in data["players"]:
        print(*[d["name"] for d in data["players"]["sample"]],sep=", ")
    print("Version: " + data["version"]["name"] + "\nProtocol: " + str(data["version"]["protocol"]))
    if "modinfo" in data:
        if "type" in data["modinfo"]:
            print("Mod Loader: " + data["modinfo"]["type"])
        if "modList" in data["modinfo"]:
            if len(data["modinfo"]["modList"]) > 0:
                print("Mods: ",end='')
                print(data["modinfo"]["modList"],sep=", ")
            else:
                print("No mods installed")

def getRequestHex(hostname:str, port:int):
    hexstr = '00c204'
    hexstr += hex(len(hostname))[2:].zfill(2)
    hexstr += bytearray(hostname, encoding='ascii').hex()
    hexstr += hex(port)[2:]
    hexstr += '01'
    hexstr = hex(len(bytearray.fromhex(hexstr)))[2:].zfill(2) + hexstr
    return hexstr

def main(host:str, port=25565):
    requestHex = getRequestHex(host, port)
    requestEndHex = '0100'
    ackHex = '0901000000000050c91c'
    request = bytearray.fromhex(requestHex)
    requestEnd = bytearray.fromhex(requestEndHex)
    acknowledge = bytearray.fromhex(ackHex)

    try:
        s = socket.create_connection((host,port))
    except socket.gaierror as e:
        if port == 25565:
            print("\nCouldn't connect to " + host + " Can't get address info")
            return
        else:
            print("\nCouldn't connect to " + host + ":" + str(port) + " gaierror")
            return
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED:
            if port == 25565:
                print("\nCouldn't connect to " + host + " Connection refused.")
                return
            else:
                print("\nCouldn't connect to " + host + ":" + str(port) + " Connection refused.")
                return
        elif e.errno == errno.ETIMEDOUT:
            print(e)
            if port == 25565:
                print("\nCouldn't connect to " + host + " Connection timeout")
                return
            else:
                print("\nCouldn't connect to " + host + ":" + str(port) + " Connection timeout")
                return
        else:
            raise e

    s.sendall(request)
    s.sendall(requestEnd)

    print("\n" + host + ":\n")
    response = recieveResponse(s)
    parseAndPrint(response[response.find(b'{"'):].decode(encoding="ascii",errors="ignore"))

    s.sendall(acknowledge)

    serverAck = s.recv(1024)
    s.close()

parser = argparse.ArgumentParser(description="Gets date from a Minecraft Server's public API. Such as motd, Player counts, version and favicon.\nBy: Fírnen")
parser.add_argument("-r", "--raw", help="Print the raw JSON to stdin and exit.", action="store_true")
parser.add_argument("-f", "--file", help="Output raw JSON to a file and exit. Default name = <hostname>.json", action="store_true")
parser.add_argument("-k", "--keys", help="Print the JSON key structure.", action="store_true")
parser.add_argument("-n", "--new", help="Disable the new keys check.", action="store_false")
parser.add_argument("-c", "--color", help="Disable text formating.", action="store_false")
parser.add_argument("hostname", action="append",type=str, nargs='+', help="Hostname of the server. <host>[:<port>]", metavar="<host>[:<port>]")

args = parser.parse_args()

print_raw_json = args.raw
raw_json_file = args.file
print_json_key_structure = args.keys
check_new_json_keys = args.new
text_color_formatting = args.color

for hostname in args.hostname[0]:
    if ":" in hostname:
        host = hostname[0:hostname.find(":")]
        port = hostname[hostname.find(":") + 1:]
        main(host,int(port))
    else:
        main(hostname)