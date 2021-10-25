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
	contenu += "<a href='/template_get?prenom=toi'>Lien direct</a><br/><br/>"
	
	contenu += "<form method='get' action='template_get'>"
	contenu += "<input type='text' name='prenom' value=''>"
	contenu += "<input type='submit' value='Envoyer'>"
	contenu += "</form><br/>"

	return contenu;
 

@app.route('/template_get', methods=['GET'])  
def template_html():
	return render_template('hello.html', prenom=request.args.get('prenom', ''))

# ---------------------------------------
# pour lancer le serveur web local Flask
# ---------------------------------------

if __name__ == '__main__':
	app.run(debug=True, port=5678)
