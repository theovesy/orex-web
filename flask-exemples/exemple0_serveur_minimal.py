from flask import Flask

app = Flask(__name__)

# placer les fonctions route/vue de l'application Flask ici
@app.route('/')
def index():
	return 'OK !'

# se lance avec http://localhost:5678
if __name__ == '__main__':
	app.run(debug=True, port=5678)