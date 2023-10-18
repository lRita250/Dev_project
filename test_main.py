import json
import logging
from pysnmp.hlapi import *
from classes import Equipement, Sonde
from flask import Flask, render_template,request
import os

app = Flask(__name__)

equipements = []

#Afficher  la liste des équipements
@app.route('/')
def index():
    return render_template('equipements.html', equipements=equipements)

# ajouter un nouveau equipement
@app.route('/equipements/add', methods=['GET', 'POST'])
def ajouter_equipement():

    # Si le request est HTTP POST il faut ajouter le nouveau equiepemnt dans le fichier json
    # Il faut ajouter le nouveau equipement dans le tableau de equiepments[] et quand le programe s'arrete
    # mis à jour les fichier json
    #if request.method == 'POST':
    #    data = request.form.to_dict()

        #nom_equipement = data['']

    
    # If request is HTTP GET afficher le page formulaire d'ajouter l'equipement
    return render_template('ajouter_equipement.html')


# Configuration de la journalisation
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] - %(message)s',
                    handlers=[logging.FileHandler("app.log", 'a', 'utf-8'), logging.StreamHandler()])
logger = logging.getLogger()



def load_data():
    # Charger les équipements
    with open("equipments.json", "r") as file:
        data = json.load(file)
        for item in data["equipments"]:
            equipements.append(Equipement(item["nom_equipement"], item["adresse_ip"], item["communaute_snmp"]))
    logger.info('Equipements chargés.')

    # Charger les sondes et les associer aux équipements
    with open("sondes.json", "r") as file:
        data = json.load(file)
        for item in data["sondes"]:
            equipement = next(e for e in equipements if e.nom_equipement == item["nom_equipement"])
            for s in item.get("sondes", []):  # Use get to avoid KeyError
                sonde = Sonde(s["name"], s["oid"])
                equipement.sondes.append(sonde)
    logger.info('Sondes chargées et associées aux équipements.')

def interroger_sonde(equipement, sonde):
    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                CommunityData(equipement.communaute_snmp),
                UdpTransportTarget((equipement.adresse_ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(sonde.oid)))
        )
        if errorIndication:
            logger.error(f"Erreur lors de l'interrogation de la sonde SNMP à {equipement.adresse_ip}: {errorIndication}")
        elif errorStatus:
            logger.error(f"Réponse d'erreur de la sonde SNMP à {equipement.adresse_ip}: {errorStatus} à l'index {errorIndex}")
        else:
            for varBind in varBinds:
                logger.info(f"Réponse de la sonde SNMP à {equipement.adresse_ip}: {varBind.prettyPrint()}")
    except Exception as e:
        logger.error(f"Une erreur s'est produite lors de l'interrogation de la sonde: {e}")

if __name__ == "__main__":
    load_data()

    # Interroger toutes les sondes pour chaque équipement
    for equipement in equipements:
        logger.info(f"Supervision de l'équipement : {equipement.nom_equipement}")
        for sonde in equipement.sondes:
            logger.info(f"Supervision de la sonde : {sonde.name}")
            interroger_sonde(equipement, sonde)
    
    app.run(debug=True)
