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
	contenu += "<a href='/afficher_personnes'>Affichage des personnes de la BDD</a><br/><br/>"
	return contenu;
  

@app.route('/afficher_personnes', methods=['GET'])
def afficher_personnes():
	
	con = lite.connect('exemples.db')
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("SELECT nom, prenom, role FROM personnes")
	lignes = cur.fetchall()
	con.close()
	return render_template('affichage_personnes.html', personnes = lignes)
	
# ---------------------------------------
# pour lancer le serveur web local Flask
# ---------------------------------------

if __name__ == '__main__':
	app.run(debug=True, port=5678)
