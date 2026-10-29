#importiamo soliti moduli copia incolla 
import os
from pathlib import Path 
from dotenv import load_dotenv

#indiachiamo percorso della cartella principale del progetto.
BASE_DIR = Path(__file__).resolve().parent

#colegamento con i segreti dal file .env.
load_dotenv(BASE_DIR / ".env")


#es24 
#serve solo per fare collegamento con la chiave segreta per IA 
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "123456")

    #collegamento con il nostro ponte 
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        #scelto modello chatGPT 
        "openai/gpt-oss-20b",
    )
