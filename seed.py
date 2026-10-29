#questo script serve per creare admin. Ci sono gia password e login 
#altri registrati dalla pagina html sarano solo utenti. Admin non si puo cancellare. 
#importiamo hashlib per criptare la password 
from models.database import conessione
import hashlib

username = "admin"
password = "admin123"


password = hashlib.sha256(
    password.encode()
).hexdigest()

#inseriamo dati di admin nella tabella utenti
conn = conessione()

conn.execute("""
    INSERT INTO utenti
    (username, password, ruolo)
    VALUES (?, ?, 'admin')
""", (
    username,
    password
))
#ogni collegamento deve essere sempre salvato e chiuso, mai lasciare collegamento aperto 
conn.commit()
conn.close()

print("Admin creato!")
print("Username:", username)
print("Password:", "admin123")
