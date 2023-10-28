import socket, mss, os

hôte ,port= "0.0.0.0",12345  
def setup():
    global serveur
    
    if not os.path.exists("dossiers_clients"):os.mkdir("dossiers_clients")
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind((hôte, port))
    serveur.listen()
    print(f"Serveur en écoute sur {hôte}:{port}")

def recevoir_capture_ecran(client, nom_machine, chemin_dossier_capture):
    try:
        with mss.mss() as sct:screenshot = sct.shot(output=os.path.join(chemin_dossier_capture, f"{nom_machine}_capture.png"));client.send(os.path.join(chemin_dossier_capture, f"{nom_machine}_capture.png").encode());return True
    except Exception as e:print(f"Erreur lors de la capture d'écran : {e}");return False



setup()

while True:
   
    client, adresse = serveur.accept()
    nom_machine = client.recv(1024).decode()
    
    os.makedirs(os.path.join(os.getcwd(), "dossiers_clients", nom_machine), exist_ok=True)
    os.makedirs(os.path.join(os.path.join(os.getcwd(), "dossiers_clients", nom_machine), "transfert"), exist_ok=True)
    os.makedirs(os.path.join("dossiers_clients", nom_machine), exist_ok=True)
    
    info, adresse_ip = client.recv(1024).decode(),client.recv(1024).decode()

    with open(os.path.join(os.path.join(os.getcwd(), "dossiers_clients", nom_machine), "info_du_systeme.txt"), 'w') as f:f.write(info)

    with open(os.path.join(os.path.join(os.getcwd(), "dossiers_clients", nom_machine), "adresse_ip.txt"), 'w') as f:f.write(f"Adresse IP du client : {adresse_ip}")

    with open(os.path.join(os.path.join(os.path.join(os.getcwd(), "dossiers_clients", nom_machine), "transfert"), "fichier_transfere.txt"), 'wb') as fichier:
        while True:
            morceau = client.recv(1024)
            if not morceau:break
            fichier.write(morceau)

    
    if recevoir_capture_ecran(client, nom_machine, os.path.join("dossiers_clients", nom_machine)):print(f"Capture d'écran reçue depuis {nom_machine} et sauvegardée dans le dossier de captures d'écran.")
    else:print(f"Échec de la capture d'écran depuis {nom_machine}.")

    print(f"Reçu depuis {nom_machine}. Dossier créé avec les informations du client et le fichier transféré dans le sous-dossier 'transfert'.")

    client.close()