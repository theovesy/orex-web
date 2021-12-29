from flask import Flask, url_for

# ------------------
# application Flask
# ------------------

app = Flask(__name__)

# ---------------------------------------
# les différentes pages (fonctions VUES)
# ---------------------------------------

# une page index avec un lien vers une page exemple
@app.route('/')
def index():
	
	contenu = ""
	contenu = "Index du site !<br/>"
	contenu += "<a href='/hello'>hello</a>"
	return contenu;

# une page avec du texte
@app.route('/hello')  
def hello():
	
	contenu = ""
	contenu += "<a href='/'>retour à l'index</a><br/><br/>"
	contenu += "Hello, World !"
	return contenu
	
if __name__ == '__main__':
	app.run(debug=True, port=5678)
