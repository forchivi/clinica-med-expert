print("\033c", end="")
#importiamo solite moduli che ci servono 
from flask import Flask #flask  
from config import Config #dal file config del nostro porgetto 
from models.database import crea_database #dal file models la nostra funzione crea_database 
from controllers.controller import durka_route #da nostro controller prendiamo i nostri route 
#creamo programma come nel es. minishop(16), diamo un nome di fantasia per usare con route per la sicurezza
#сreaмо parola durka, carichiamo Config e avviamo il programma
def create_app():
    durka = Flask(__name__)
    durka.config.from_object(Config)
    crea_database()
    durka.register_blueprint(durka_route)
    return durka

durka = create_app()
# main per avviare programma 
if __name__ == "__main__":
    durka.run(debug=True)
