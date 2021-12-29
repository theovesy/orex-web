from flask import Flask, url_for, request, render_template, redirect
import sqlite3 as lite

# ------------------
# application Flask
# ------------------

app = Flask(__name__)

# ---------------------------------------
# les différentes pages (fonctions VUES)
# ---------------------------------------

# une page index avec des liens vers les différentes pages d'exemple d'utilisation de Flask
@app.route('/')
def index():
	
	contenu = ""
	contenu += "<a href='/hello_get?prenom=toi'>Lien direct</a><br/><br/>"
	
	contenu += "<form method='get' action='hello_get'>"
	contenu += "<input type='text' name='prenom' value=''>"
	contenu += "<input type='submit' value='Envoyer'>"
	contenu += "</form><br/><br/>"
	
	return contenu

# une page avec du texte dynamique envoyé par HTTP/GET
@app.route('/hello_get', methods=['GET'])  
def hello_get_prenom():
	
	contenu = ""
	contenu += "<a href='/'>retour à l'index</a><br/><br/>"
	contenu += "Hello, " + request.args.get('prenom', 'une valeur par défaut de la req') + " !"
	
	return contenu
	
# ---------------------------------------
# pour lancer le serveur web local Flask
# ---------------------------------------

if __name__ == '__main__':
	app.run(debug=True, port=5678)
