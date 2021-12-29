from os import linesep
import sqlite3 as lite
import time
from flask import Flask, config, request, render_template

DB_NAME = "database.db"
START_TIME = time.time()	# Heure du départ en seconde (depuis epoch soit le 1er janvier 1970, 00:00:00 (UTC))

app = Flask(__name__)


# Renvoi la date depuis le début du timer sous forme de cdc
def getDate():

	time_cmd = time.time() - START_TIME	# Ecart de temps entre lancement du site et la commande
	heures = int(time_cmd/3600)
	minutes = int((time_cmd/3600 - heures) * 60)
	secondes = int(time_cmd - heures*3600 - minutes*60)
	date = str(heures) + ":" + str(minutes) + ":" + str(secondes)	# Date en cdc

	return date

# Connexion à une base de donnée
# renvoie un objet Connect et un objet Cursor
def db_connect(db_name):
	
	con = lite.connect(db_name)
	con.row_factory = lite.Row
	cur = con.cursor()
	
	return con, cur


# Execute une requête SQL sans lecture avec un tuple de données
def db_execute(querry, data):
	con, cur = db_connect(DB_NAME)
	cur.execute(querry, data)
	con.commit()
	con.close()


# Execute une requête SQL avec lecture
def db_read(querry):
	con, cur = db_connect(DB_NAME)
	cur.execute(querry)
	lines = cur.fetchall()
	con.close()
	
	return lines


# Ajoute la commande client d'après un dictionnaire de données en paramètre
def db_addCmdClient(order_data):

	# Date de la commande
	date_cmd = getDate()
	#print(date_cmd)

	# Récupère le numéro de la dernière commande
	querry = "SELECT MAX(n_cmd) FROM CmdClient"
	n_cmd_prec = db_read(querry)[0][0]		# num cmd précédante
	if n_cmd_prec == None :					# Si pas de cmd précédente
		n_cmd = 1							# numéro de la commande à enregistrer
	else :
		n_cmd = n_cmd_prec + 1					

	# Modèle du véhicule
	ref_voiture = "C" + order_data['chassis'] + order_data['carrosserie']

	# Ajoute la commande à la base de données
	querry = "INSERT INTO CmdClient (n_cmd, ref_voiture, antenne, crochet, attache, date_reception) VALUES (?, ?, ?, ?, ?, ?)"
	values = (n_cmd, ref_voiture, order_data['options'][0], order_data['options'][1], order_data['options'][2], date_cmd)
	#print(values)
	db_execute(querry, values)


# Récupère la liste des commandes client depuis la bdd
def db_getCmdClient():

	querry = "SELECT * from CmdClient"
	lines = db_read(querry)

	return lines


##--------------PAGE D'ACCEUIL--------------

@app.route('/accueil')
def accueil():

	return render_template('accueil.html')


##--------------PAGE CLIENT--------------
# Afficher la page et les commandes en cours

@app.route('/order')  
def order():

		
	return render_template('order.html')


##--------------PAGE DE COMMANDE CLIENT A AGILEAN--------------

@app.route('/validate', methods=['GET'])
def validate():
	
	# Récupère les données du formulaire de commande
	# Les données spnt forcément complètes car les radio boutons de la page de commande ont des valeurs par défaut

	order_data = {}		# Données de commande

	if request.method == 'GET':

		order_data["chassis"] = request.args.get('chassis')				# Valeurs : C(court) ou L(long)
		order_data["carrosserie"] = request.args.get('carrosserie')		# Valeurs : O(ouvert) ou F(fermé)
		order_data["options"] = [0, 0, 0]									# [antenne?, crochet?, attache?]
		for i in range(3):
			order_data["options"][i] = request.args.get("option"+str(i), 0)
		#print(order_data)

		db_addCmdClient(order_data)			# Ajout de la commande à la base de donnée
	
	# Après avoir ajouté la cmd client à la bdd
	# On affiche un résumé des cmd du client

	lines = db_getCmdClient()
	
	return render_template('validate.html', cmds_client = lines)


##--------------PAGE DE GESTION DES COMMANDES CLIENT DE AGILEAN--------------

@app.route('/order_book_Agilean', methods=['GET'])
def order_book_Agilean():

	# Si une mise à jour de l'état d'une commande a été faite
	if request.method == 'GET':
		n_cmd = request.args.get("n_cmd")
		print(n_cmd)
		etat = request.args.get("maj_cmd_client")
		print(etat)

		if n_cmd != None :		# Pour ne pas lancer une requête SQL lorsqu'on ne met pas à jour une commande

			# En passant à l'état "Livré", on ajoute la date d'expédition/livraison (même chose dans le serious game)
			if etat == "Livrée":
				date_expedition = getDate()
				tuple=(date_expedition, etat, n_cmd)
				querry = "UPDATE CmdClient SET date_expedition=?, etat=? WHERE n_cmd=?"
			else:
				tuple=(etat, n_cmd)
				querry = "UPDATE CmdClient SET etat=? WHERE n_cmd=?"

			db_execute(querry,tuple)

	# Affiche le carnet de commande
	lines = db_getCmdClient()
	
	return render_template('order_book_Agilean.html', cmds_client = lines)
	

# Supprimer OREX-WEB.db et le remplacer par OREX-WEB_original.db (après l'avoir renommé)
@app.route('/reset_db')
def reset_db():
	contenu = ""
	
	return contenu
	
if __name__ == '__main__':
	app.run(debug=True, port=5678)
