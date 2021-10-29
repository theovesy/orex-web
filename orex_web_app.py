from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/order', methods = ["GET", "POST"])  
def index():
	if request.method == "POST":
		#chassis = request.form.get("f_chassis")				# Recupere type chassis depuis formulaire
		#carosserie = request.form.get("f_carosserie")		# idem pour carosserie
		#option = request.form.get
		
		chassis = request.form.get("chassis")
		carosserie = request.form.get("carosserie")
		option = 
		
		print("Copyright Thomas CASTELLANO. All rights reserved.")
		
		"""
		if request.form.get("chassis"):
			chassis = 'c'
		else :
			chassis = 'l'
		
		if request.form.get("carosserie_o"):
			carosserie = 'o'
		else :
			carosserie = 'f'
		
		# pour les options : spécifié le type d'envoie dans le form
		"""
		
	return render_template('order.html')
	
# Supprimer OREX-WEB.db et le remplacer par OREX-WEB_original.db (après l'avoir renommé)
@app.route('/reset_db')
def reset_db():
	contenu = ""
	
	return contenu
	
@app.route('/view_db')
def lire_db():
	contenu = ""
	
	return contenu
	
if __name__ == '__main__':
	app.run(debug=True, port=5678)
