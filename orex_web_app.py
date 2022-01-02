import sqlite3 as lite
import time
import os
import shutil
from flask import Flask, config, request, render_template

DB_NAME = "database.db"
START_TIME = time.time()	# Heure du départ en seconde (depuis epoch soit le 1er janvier 1970, 00:00:00 (UTC))
PAUSE_TIME = 0

timer_paused = False
timer_stopped = True
timer = 0					# date en seconde
date = "00:00:00"			# date en cdc

app = Flask(__name__)


# Renvoi la date depuis le début du timer sous forme de cdc
def getDate():
	global date

	if timer_stopped:
		return "00:00:00"
	elif timer_paused:
		return date
	else:
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
# renvoie une liste de lignes
def db_read(querry):
	con, cur = db_connect(DB_NAME)
	cur.execute(querry)
	lines = cur.fetchall()
	con.close()
	
	return lines


# Execute une lecture SQL paramétrée 
# renvoie une liste de lignes 
def db_read_tuple(querry, tuple):
	con, cur = db_connect(DB_NAME)
	cur.execute(querry, tuple)
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


# Ajoute la commande de kits de Agilean à la bdd 
def db_addCmdAgilean(order_data):

	# Date de la commande
	date_cmd = getDate()

	# Récupère le numéro de la dernière commande
	querry = "SELECT MAX(n_cmd) FROM CmdAgilean"
	n_cmd_prec = db_read(querry)[0][0]		# num cmd précédante
	if n_cmd_prec == None :					# Si pas de cmd précédente
		n_cmd = 1							# numéro de la commande à enregistrer
	else :
		n_cmd = n_cmd_prec + 1					


	# Ajoute la commande à la base de données
	querry1 = "INSERT INTO CmdAgilean (n_cmd, date_emission) VALUES (?, ?)"
	values1 = (n_cmd, date_cmd)
	
	db_execute(querry1, values1)

	for i in range(1, int(len(order_data)/2)+1):		# On lit le numéro de commande à la quantité de chaque kit commandé
		
		if int(order_data["qte_cmd"+str(i)]) != 0:
			querry2 = "INSERT INTO CmdAgilean_contient_Kit (n_cmd, ref_kit, qte_cmd) VALUES (?, ?, ?)"
			values2 = (n_cmd, order_data["ref_kit"+str(i)], order_data["qte_cmd"+str(i)])

			db_execute(querry2, values2)


# Récupère la liste des commandes client depuis la bdd
def db_getCmdClient():

	querry = "SELECT * from CmdClient"
	lines = db_read(querry)

	return lines

# Récupère la liste des commandes de kit de Agilean depuis la bdd
def db_getCmdAgilean():

	querry = "SELECT * from CmdAgilean "
	lines = db_read(querry)

	return lines

# Récupère la liste détaillée des commandes de kit de Agilean depuis la bdd
def db_getDetailledCmdAgilean():

	querry = "SELECT * FROM CmdAgilean JOIN CmdAgilean_contient_Kit ON CmdAgilean.n_cmd = CmdAgilean_contient_Kit.n_cmd"
	lines = db_read(querry)

	return lines

# Récupère les stocks de kits chez Agilean
def db_getStocksKitAgilean():
	
	querry = "SELECT * from Kit"
	lines = db_read(querry)

	return lines

# Récupère le nombre de kits commandés mais pas encore livrés
def db_getEncoursKit():
	
	querry = "SELECT ref_kit, SUM(qte_cmd) As nb_encours FROM CmdAgilean JOIN CmdAgilean_contient_Kit ON CmdAgilean_contient_Kit.n_cmd = CmdAgilean.n_cmd WHERE CmdAgilean.etat != \"Livrée\" GROUP BY CmdAgilean_contient_Kit.ref_kit"
	lines = db_read(querry)

	return lines

# Historique des commandes de kits
def db_getHistoCmdsAgilean():

	querry = "SELECT CmdAgilean.n_cmd, CmdAgilean_contient_Kit.ref_kit, CmdAgilean_contient_Kit.qte_cmd ,CmdAgilean.date_emission, CmdAgilean.date_reception From CmdAgilean JOIN CmdAgilean_contient_Kit ON CmdAgilean_contient_Kit.n_cmd = CmdAgilean.n_cmd"
	lines = db_read(querry)

	return lines

# Nombre de kit référencés dans la bdd
def db_getNbKit():

	querry = "SELECT COUNT(DISTINCT ref) FROM Kit"
	lines = db_read(querry)

	return lines[0][0]

# Renvoi les références de kits contenues dans la commande en paramètre
def db_getKitInCmdAgilean(n_cmd):

	tuple = (n_cmd, )
	querry = "SELECT ref_kit, qte_cmd FROM CmdAgilean_contient_Kit WHERE n_cmd = ?"

	lines = db_read_tuple(querry, tuple)
	
	return lines

# Pour réinitialiser la base de donnée
def db_reset():
	dirname = os.getcwd()	# chemin absolu du dossier courant (racine du projet)
	init_db = os.path.join(dirname, "static/database_init.db")	# chemin aboslue de la bdd vierge à partir du chemin relatif
	work_db = os.path.join(dirname, "database.db")
	print(type(init_db))

	shutil.copy(init_db, work_db)


##--------------PAGE D'ACCEUIL--------------

@app.route('/accueil', methods=['GET'])
def accueil():
	global START_TIME
	global PAUSE_TIME
	global timer_stopped
	global timer_paused
	global date

	if request.method == 'GET':

		if request.args.get('submit') == "Start":
			START_TIME = time.time() - PAUSE_TIME	# On relance le timer avec un décalage du temps où on en était
			PAUSE_TIME = 0							# On reset la pause
			timer_paused = False
			timer_stopped = False
			date = getDate()
		elif request.args.get('submit') == "Pause":
			if timer_stopped == False:
				date = getDate()
				PAUSE_TIME = time.time() - START_TIME
				timer_paused = True
				
		elif request.args.get('submit') == "Stop":
			START_TIME = 0
			PAUSE_TIME = 0
			timer_stopped = True
			date="00:00:00"
		else:
			date = getDate()

		# Réinitialisation de la bdd
		if request.args.get('reset_button') == "Réinitialiser la base de donnée":
			db_reset()

	return render_template('accueil.html', time=date)


##--------------PAGE CLIENT--------------
# Afficher la page et les commandes en cours

@app.route('/order')  
def order():
	global date

	date = getDate()

	return render_template('order.html', time=date)


##--------------PAGE DE COMMANDE CLIENT A AGILEAN--------------

@app.route('/order_book_Client', methods=['GET'])
def order_book_Client():
	global date

	# Si on accède par redirection du formulaire de commande
	# Récupère les données du formulaire de commande
	# Les données sont forcément complètes car les radio boutons de la page de commande ont des valeurs par défaut

	if request.method == 'GET':

		if request.args.get('submit') == "Envoyer":

			order_data = {}		# Données de commande

			order_data["chassis"] = request.args.get('chassis')				# Valeurs : C(court) ou L(long)
			order_data["carrosserie"] = request.args.get('carrosserie')		# Valeurs : O(ouvert) ou F(fermé)
			order_data["options"] = [0, 0, 0]									# [antenne?, crochet?, attache?]
			for i in range(3):
				order_data["options"][i] = request.args.get("option"+str(i), 0)
			#print(order_data)

			db_addCmdClient(order_data)			# Ajout de la commande à la base de donnée

	# Qu'il y ai eu une commande ou non, on affiche un résumé des cmd du client
	lines = db_getCmdClient()
	date = getDate()
	
	return render_template('order_book_Client.html', cmds_client = lines, time = date)


##--------------PAGE DE GESTION DES COMMANDES CLIENT DE AGILEAN--------------

@app.route('/order_book_Agilean', methods=['GET'])
def order_book_Agilean():
	global date

	# Si une mise à jour de l'état d'une commande a été faite
	if request.method == 'GET':
		n_cmd = request.args.get("n_cmd")
		#print(n_cmd)
		etat = request.args.get("maj_cmd_client")
		#print(etat)

		if n_cmd != None :		# Pour ne pas lancer une requête SQL lorsqu'on ne met pas à jour une commande

			# En passant à l'état "Livré", on ajoute la date d'expédition/livraison (même chose dans le serious game)
			if etat == "Livrée":
				date_expedition = getDate()
				tuple=(date_expedition, etat, int(n_cmd))
				querry = "UPDATE CmdClient SET date_expedition=?, etat=? WHERE n_cmd=?"
			else:
				tuple=(etat, n_cmd)
				querry = "UPDATE CmdClient SET etat=? WHERE n_cmd=?"

			db_execute(querry,tuple)

	# Affiche le carnet de commande
	lines = db_getCmdClient()
	date = getDate()

	return render_template('order_book_Agilean.html', cmds_client = lines, time = date)
	

##--------------PAGE DE GESTION DES STOCKS DE KITS DE AGILEAN--------------

@app.route('/stocks_Agilean', methods=['GET'])
def stocks_Agilean():
	global date

	if request.method == "GET":

		data = {}

		# Met à jour les stocks de kits avec les valeurs entrées par l'utilisateur
		if request.args.get("MAJ") == "MAJ":

			data['ref_kit'] = int(request.args.get("ref_kit"))
			data['qte_stock'] = int(request.args.get("qte_stock"))

			querry = "UPDATE Kit SET qte_stock=? WHERE ref=?"
			tuple = (data["qte_stock"], data["ref_kit"])

			db_execute(querry, tuple)

		# Ajoute la commande de kits à la bdd
		if request.args.get("commander") == "Commander":
			
			for i in range(1, db_getNbKit()+1):
				data['ref_kit'+str(i)] = int(request.args.get('ref_kit'+str(i)))
				data['qte_cmd'+str(i)] = int(request.args.get('qte_cmd'+str(i)))

			db_addCmdAgilean(data)

	# Données pour afficher les tableaux de stocks et de commande de la page
	lines_cmdsAgilean = db_getStocksKitAgilean()
	lines_encours = db_getEncoursKit()
	lines_histo_cmds = db_getHistoCmdsAgilean()
	date = getDate()	# date pour le timer

	return render_template('stocks_Agilean.html', cmds_Agilean = lines_cmdsAgilean, cmds_Encours = lines_encours, histo_Agilean = lines_histo_cmds, time = date)


##--------------PAGE DE GESTION DES COMMANDES DE AGILEAN CHEZ AGILOG--------------

@app.route('/order_book_Agilog', methods=['GET'])
def order_book_Agilog():
	global date

	# Si une mise à jour de l'état d'une commande a été faite
	if request.method == 'GET':
		n_cmd = request.args.get("n_cmd")
		etat = request.args.get("maj_cmd_agilean")

		if n_cmd != None :		# Pour ne pas lancer une requête SQL lorsqu'on ne met pas à jour une commande

			# En passant à l'état "Livré", on ajoute la date de réception par Agilean (cmd livrée)
			# On ajoute également les en-cours au stocks de kits d'Agilean
			if etat == "Livrée":
				date_reception = getDate()
				tuple1 = (date_reception, etat, int(n_cmd))
				querry1 = "UPDATE CmdAgilean SET date_reception=?, etat=? WHERE n_cmd=?"
				db_execute(querry1,tuple1)

				# Maj des qtés en stock chez Agilean lorsque la cmd à été livrée	
				# On parcours la liste des qtés commandées pour chaque réf de la commande dont l'état vient d'être modifié
				lines = db_getKitInCmdAgilean(int(n_cmd))
				for line in lines:
					ref_kit = int(line['ref_kit'])
					ancien_stock = int(db_read_tuple("SELECT qte_stock FROM Kit WHERE ref = ?", (ref_kit,))[0][0])
					nouveau_stock = ancien_stock + int(line['qte_cmd'])

					tuple_maj_stock = (nouveau_stock, ref_kit)
					querry_maj_stock = "UPDATE Kit SET qte_stock = ? WHERE ref = ?"
					db_execute(querry_maj_stock, tuple_maj_stock)

			else:
				tuple = (etat, n_cmd)
				querry = "UPDATE CmdAgilean SET etat=? WHERE n_cmd=?"
				db_execute(querry, tuple)


	# Affiche le carnet de commandes
	cmds_lines = db_getCmdAgilean()
	det_lines = db_getDetailledCmdAgilean()
	date = getDate()

	return render_template('order_book_Agilog.html', cmds_Agilean = cmds_lines, det_cmds = det_lines, time = date)
	


if __name__ == '__main__':
	app.run(debug=True, port=5678)
