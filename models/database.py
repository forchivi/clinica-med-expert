print("\033c", end="")
#importiamo con coppia incolla moduli che servono per le tabelle di database 
import sqlite3
import os
import hashlib
#diciamo dove database, che lavoriamo nella cartella models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)
DATABASE = os.path.join(MODELS_DIR, "database.db")
#cominciamo con conessione e creazione delle tabelle 
def conessione():
    conn=sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn 
#creamo le tabelli che ci servono 
def crea_database():
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            ruolo TEXT NOT NULL DEFAULT 'user'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pazienti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            data_nascita TEXT NOT NULL,
            email TEXT NOT NULL,
            telefono TEXT NOT NULL,
            indirizzo TEXT NOT NULL,
            filiale TEXT,
            allergie TEXT,
            note TEXT,
            dottori_id INTEGER NOT NULL,
            FOREIGN KEY (dottori_id)
            REFERENCES dottori(id)
            ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servizi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descrizione TEXT NOT NULL,
            prezzo REAL NOT NULL,
            durata TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appuntamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paziente INTEGER NOT NULL,
            id_dottore INTEGER NOT NULL,
            data_ora TEXT NOT NULL,
            reparto TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dottori (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cognome TEXT NOT NULL,
        specializzazione TEXT NOT NULL,
        email TEXT NOT NULL,
        telefono TEXT NOT NULL
        )
    """)
    #assistente statico es 23
    #tabella informazioni (chiave, valore) per le risposte dell'assistente statico
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS informazioni (
            chiave TEXT PRIMARY KEY,
            valore TEXT NOT NULL
        )
    """)
    #assistente con api es 25 
    #tabella conversazioni dove la chat IA salva domanda, risposta e data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversazioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utente TEXT NOT NULL,
            domanda TEXT NOT NULL,
            risposta TEXT NOT NULL,
            data_ora TEXT NOT NULL
        )
    """)
    #es.23 dizionario con INSERT OR IGNORE (non duplica se esiste gia)
    informazioni = {
        "nome_clinica": "Clinica Privata Med.Expert",
        "indirizzo": "Via Roma 100, Milano",
        "telefono": "+39 02 1234567",
        "email": "info@medexpert.it",
        "orario_settimana": "08:00 - 19:00",
        "orario_sabato": "08:00 - 13:00",
        "orario_domenica": "Chiuso",
        "orario_prelievi": "dalle 06:30 alle 13:00",
        "orario_visite": "dalle 08:30 alle 19:00",
        "orario_ricoveri": "dalle 11:00 alle 16:30",
        "tempi_esami": (
            "I tempi sono indicati nella ricevuta e nella delega: "
            "da 3 giorni per gli esami base fino a 7 giorni per gli esami preparto."
        ),
        "pagamenti": (
            "Contanti e carte di credito Visa, Mastercard, American Express. "
            "Siamo accreditati con il Servizio Sanitario Nazionale (SSN)."
        )
    }
    for chiave, valore in informazioni.items():
        cursor.execute("""
            INSERT OR IGNORE INTO informazioni
            (chiave, valore)
            VALUES (?, ?)
        """, (chiave, valore))
    #creamo tabella esami con i prezzi es.21b
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS esami (
            nome TEXT PRIMARY KEY,
            prezzo REAL NOT NULL
        )
    """)
    esami = [
        ("Esame del sangue base", 80),
        ("Esame del sangue per diabete", 120),
        ("Esami preparto", 160)
    ]
    for nome, prezzo in esami:
        cursor.execute("""
            INSERT OR IGNORE INTO esami (nome, prezzo)
            VALUES (?, ?)
        """, (nome, prezzo))
   
    #creamo tabella reparti
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reparti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        )
    """)
    reparti = [
        "Cardiologia",
        "Ortopedia",
        "Dermatologia",
        "Centro prelievi"
    ]
    #ciclo for per inserire nuovi reparti
    for reparto in reparti:
        cursor.execute("""
            INSERT OR IGNORE INTO reparti (nome)
            VALUES (?)
        """, (reparto,))
    conn.commit()
    conn.close()

# per leggere informaizone dalla tabella, una alla volta 
def leggi_informazione(chiave):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT valore FROM informazioni WHERE chiave = ?", (chiave,))
    risultato = cursor.fetchone()
    conn.close()
    return risultato[0] if risultato else "Non disponibile"

#per visualizzare esame con prezzo - tutte le righe
def leggi_esami():
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, prezzo FROM esami ORDER BY prezzo")
    esami = cursor.fetchall()
    conn.close()
    return esami

#per visualizzare reparti tutti 
def leggi_reparti():
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM reparti ORDER BY id")
    reparti = cursor.fetchall()
    conn.close()
    return reparti

#per salvare conversazioni con chat IA con data e ora 
def salva_conversazione(utente, domanda, risposta, data_ora):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversazioni
        (utente, domanda, risposta, data_ora)
        VALUES (?, ?, ?, ?)
    """, (utente, domanda, risposta, data_ora))
    conn.commit()
    conn.close()

#per visuaoizzare conversazione dal piu recente (DESC)
def ultime_conversazioni(utente, limite=10):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, domanda, risposta, data_ora
        FROM conversazioni
        WHERE utente = ?
        ORDER BY id DESC
        LIMIT ?
    """, (utente, limite))
    conversazioni = cursor.fetchall()
    conn.close()
    return conversazioni

#per salvare dati utenti
def registra_utente(username, password):
    password = hashlib.sha256(password.encode()).hexdigest()
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO utenti (username, password)
        VALUES (?, ?)
    """, (username, password))
    conn.commit()
    conn.close()

def login_utente(username, password):
    password = hashlib.sha256(password.encode()).hexdigest()
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, ruolo FROM utenti WHERE username = ? AND password = ?", (username, password))
    utente = cursor.fetchone()
    conn.close()
    return utente

#per visualizzare elenco utenti
def leggi_utenti():
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, ruolo FROM utenti ORDER BY id")
    utenti = cursor.fetchall()
    conn.close()
    return utenti

def trova_utente(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, ruolo FROM utenti WHERE id = ?", (id,))
    utente = cursor.fetchone()
    conn.close()
    return utente

def modifica_utente(id, username, password):
    password = hashlib.sha256(password.encode()).hexdigest()
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE utenti
        SET username = ?, password = ?
        WHERE id = ?
    """, (username, password, id))
    conn.commit()
    conn.close()

def elimina_utente(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM utenti WHERE id = ?", (id,))
    conn.commit()
    conn.close()    

def inserisce_paziente(nome, cognome, data_nascita, email, telefono, indirizzo, filiale, allergie, note, dottori_id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pazienti
        (nome, cognome, data_nascita, email, telefono, indirizzo, filiale, allergie, note, dottori_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, cognome, data_nascita, email, telefono, indirizzo, filiale, allergie, note, dottori_id))
    conn.commit()
    id_paziente = cursor.lastrowid 
    conn.close()
    return id_paziente
#fatto collegamento con dottori per visualizzare nella tabella paziente che dottore li seguino 
def leggi_paziente():
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            pazienti.id,
            pazienti.nome,
            pazienti.cognome,
            pazienti.data_nascita,
            pazienti.email,
            pazienti.telefono,
            pazienti.indirizzo,
            pazienti.filiale,
            pazienti.allergie,
            pazienti.note,
            dottori.nome,
            dottori.cognome,
            dottori.specializzazione
        FROM pazienti 
        JOIN dottori
        ON pazienti.dottori_id = dottori.id
    """)
    paziente = cursor.fetchall()
    conn.close()
    return paziente

def trova_paziente(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pazienti WHERE id =?", (id,))
    paziente = cursor.fetchone()
    conn.close()
    return paziente
    
def modifica_paziente(id, nome, cognome, data_nascita, email, telefono, indirizzo, filiale, allergie, note):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE pazienti
        SET nome = ?, cognome = ?, data_nascita = ?, email = ?, telefono = ?, indirizzo = ?, filiale = ?, allergie = ?, note = ?
        WHERE id = ?
    """, (nome, cognome, data_nascita, email, telefono, indirizzo, filiale, allergie, note, id))
    conn.commit()
    conn.close()

def elimina_paziente(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pazienti WHERE id = ?", (id,))
    conn.commit()
    conn.close()  

def inserisci_servizio(nome, descrizione, prezzo, durata):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO servizi
        (nome, descrizione, prezzo, durata)
        VALUES (?, ?, ?, ?)
    """, (nome, descrizione, prezzo, durata))
    conn.commit()
    conn.close()

def leggi_servizi():
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM servizi")
    servizi = cursor.fetchall()
    conn.close()
    return servizi

def trova_servizio(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM servizi WHERE id = ?", (id,))
    servizio = cursor.fetchone()
    conn.close()
    return servizio 

def modifica_servizio(id, nome, descrizione, prezzo, durata):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE servizi
        SET nome = ?, descrizione = ?, prezzo = ?, durata = ?
        WHERE id = ?
    """, (nome, descrizione, prezzo, durata, id))
    conn.commit()
    conn.close()

def elimina_servizio(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servizi WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def inserisci_appuntamento(id_paziente, id_dottore, data_ora, reparto):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appuntamento
        (id_paziente, id_dottore, data_ora, reparto)
        VALUES (?, ?, ?, ?)
    """, (id_paziente, id_dottore, data_ora, reparto))
    conn.commit()
    conn.close()

def leggi_appuntamenti():
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appuntamento")
    appuntamenti = cursor.fetchall()
    conn.close()
    return appuntamenti

def trova_appuntamento(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appuntamento WHERE id = ?", (id,))
    appuntamento = cursor.fetchone()
    conn.close()
    return appuntamento

def modifica_appuntamento(id, id_paziente, id_dottore, data_ora, reparto):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appuntamento 
        SET id_paziente = ?, id_dottore = ?, data_ora = ?, reparto = ?
        WHERE id = ?
    """, (id_paziente, id_dottore, data_ora, reparto, id))
    conn.commit()
    conn.close()

def elimina_appuntamento(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appuntamento WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def inserisci_dottore(nome, cognome, specializzazione, email, telefono):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO dottori
        (nome, cognome, specializzazione, email, telefono)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, cognome, specializzazione, email, telefono))
    conn.commit()
    conn.close()

def leggi_dottori():
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SElECT * FROM dottori")
    dottori = cursor.fetchall()
    conn.close()
    return dottori


def trova_dottore(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dottori WHERE id = ?", (id,))
    dottore = cursor.fetchone()
    conn.close()
    return dottore

def modifica_dottore(id, nome, cognome, specializzazione, email, telefono):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE dottori 
        SET nome = ?, cognome = ?, specializzazione = ?, email = ?, telefono = ?
        WHERE id = ?
    """, (nome, cognome, specializzazione, email, telefono, id))
    conn.commit()
    conn.close()

def elimina_dottore(id):
    conn = conessione()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dottori WHERE id = ?", (id,))
    conn.commit()
    conn.close()