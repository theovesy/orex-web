from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
	
	contenu = ""
	contenu = "<h1/>Agi[lean|log] Web-app</h1>"
	contenu += "<br/>"
	contenu += "<a href='/reset_db'>Réinitialiser la base de données</a>"
	
	return contenu;
	
@app.route('/reset_db')
def reset_db():
	contenu = ""
	
	return contenu
	
@app.route('/view_db')
def lire_db():
	contenur = ""
	
	return contenu
	
if __name__ == '__main__':
	app.run(debug=True, port=5678)
