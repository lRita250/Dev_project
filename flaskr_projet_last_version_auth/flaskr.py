import json
import logging
from pysnmp.hlapi import *
from equiepement_class import Equipement
import os
from flask import Flask, render_template, request, redirect, url_for, flash,  jsonify, session, flash
from datetime import datetime
import atexit
import time

from interoger_sonde import *
from apscheduler.schedulers.background import BackgroundScheduler

from werkzeug.security import check_password_hash, generate_password_hash
import json




app = Flask(__name__)
supervised_results = []
scheduler = BackgroundScheduler()
scheduler.start()
equipements = []
app.secret_key = 'toto'
CONFIG_FILE_NAME = "equipment_data.json"

Equipement.load_from_json(CONFIG_FILE_NAME)
# Retrieve the list of equipment instances
equipment_list = Equipement.equipements_list
##########################################################################################################################################################
################################################       Authentification                #################################################################
##########################################################################################################################################################



hashed_password = generate_password_hash('admin')
print(hashed_password)  # Vous utiliserez cette valeur hachée dans votre fichier users.json


# Route pour la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Tentative de connexion")  # Pour confirmer que la route est atteinte

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Nom d'utilisateur: {username}")  # Afficher le nom d'utilisateur saisi
        print(f"Mot de passe: {password}")  # Afficher le mot de passe saisi (Attention à la sécurité ici)

        # Vérification des identifiants
        if check_credentials(username, password):
            print("Identifiants valides")  # Confirmer que les identifiants sont valides
            session['username'] = username
            return redirect(url_for('index'))  # Assurez-vous que 'home' est la route de votre page d'accueil
        else:
            print("Identifiants invalides")  # Indiquer que les identifiants sont invalides
            #flash('Nom d\'utilisateur ou mot de passe incorrect')
            flash('Les informations saisies sont incorrectes', 'error')  # Envoie un message d'erreur

    return render_template('login.html')


# Route pour la déconnexion
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    # Supprimer l'utilisateur de la session
    session.pop('username', None)
    # Rediriger vers la page de connexion
    return redirect(url_for('login'))

# Fonction pour vérifier les identifiants d'utilisateur
def check_credentials(username, password):
    with open('users.json') as users_file:
        users = json.load(users_file)
        user_hashed_password = users.get(username)

    if user_hashed_password and check_password_hash(user_hashed_password, password):
        return True
    else:
        return False

#########################################################################################################################################################
""" 
@app.route('/')
def index():
    # Supposons que vous souhaitiez afficher la liste des équipements sur la page d'accueil.
    return render_template('index.html', equipements=equipements, supervised_results=supervised_results)
 """

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


###########################################################################
##########################       Equipements  #############################
###########################################################################

# Afficher les equipements
@app.route('/equipements')
def show_equipements():
    return render_template('equipements.html', equipements=equipment_list)


@app.route('/equipements/add', methods=['GET', 'POST'])
def ajouter_equipement():

    # Afficher le formulaire pour ajouter un equiepement
    if request.method == 'GET':
        return render_template('ajouter_equipement.html')
    
    elif request.method == 'POST':
        form_date = request.form.to_dict()
        Equipement(form_date["nom_equipement"], form_date["adresse_ip"],form_date["communaute_snmp"], form_date["interface"], form_date["oid"])
        return redirect('/equipements')

    

@app.route('/equipements/<id>/delete', methods=['POST'])
def supprimer_equipement(id):

    if request.method == "POST":
        Equipement.delete_equipment(id)
        return redirect('/equipements')


@app.route('/equipements/<id>/edit', methods=['GET', 'POST'])
def modifier_equipement(id):
    
    if request.method == "GET":
        equipement = Equipement.get_equipment_by_name(id).to_dict()
        return render_template('modifier_equipement.html', equipement=equipement)

    elif request.method == "POST":
        form_date = request.form.to_dict()
        found_equip = Equipement.get_equipment_by_name(id)

        if found_equip:
            # Update the equipment's attributes
            found_equip.update_equipment(form_date["adresse_ip"],form_date["communaute_snmp"], form_date["interface"], form_date["oid"])
            return redirect('/equipements')



###########################################################################
##########################       LOGS   #############################
###########################################################################


@app.route('/logs')
def display_log():
    log_lines = read_top_10_log_lines("app.log", 20)
    return render_template('logs.html', log_lines=log_lines)

def read_log_file(log_file):
    log_lines = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            log_lines = file.readlines()
    return log_lines

def read_top_10_log_lines(log_file, ligne=10, newest=True):
    log_lines = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            if newest:
                log_lines = list(reversed(file.readlines()))[:ligne]  # Get the top 10 newest lines
            else:
                log_lines = file.readlines()[-10:]  # Get the top 10 lines from the end (oldest)
    return log_lines

###########################################################################
##########################    Interoger SNMP  #############################
###########################################################################


@app.route('/interoger')
def interoger_snmp():
    
    global supervised_results
    supervised_results.clear()
    for equipement in equipment_list:
        logger.info(f"Supervision de l'équipement : {equipement.nom_equipement}")
        valeur_supervision = interroger_sonde(equipement)
        result = {'name': equipement.nom_equipement, 'value': valeur_supervision}
        supervised_results.append(result)
        print()
        print(valeur_supervision)
    
    logger.info(f"Résultats de supervision : {supervised_results}")
 #   #return render_template('index.html', supervised_results=supervised_results)


@app.route('/demarrer_supervision', methods=['POST'])
def demarrer_supervision():
    if not scheduler.get_job('SupervisionJob'):
        scheduler.add_job(id='SupervisionJob', func=interoger_snmp, trigger='interval', seconds=15)
    return redirect(url_for('index'))

@app.route('/arreter_supervision', methods=['POST'])
def arreter_supervision():
    if scheduler.get_job('SupervisionJob'):
        scheduler.remove_job('SupervisionJob')
    return redirect(url_for('index'))


@app.route('/get_supervised_results')
def get_supervised_results():
    if not scheduler.get_job('SupervisionJob'):
        return jsonify([])  # Aucun travail de supervision en cours, renvoyer une liste vide
    return jsonify(supervised_results)

# Register a function to save data to the JSON file on script exit
atexit.register(Equipement.save_to_json, 'equipment_data.json')

# Configuration de la journalisation
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(levelname)s] - %(message)s',handlers=[logging.FileHandler("app.log", 'a', 'utf-8'), logging.StreamHandler()])
logger = logging.getLogger()







app.run()
