#controller serve per nascondere tutti route e funzioni 
#es.25 importiamo solite dati copia incolla
import sqlite3 #per riconoscere l'errore di username gia esistente
from datetime import datetime #per la chat
from flask import Blueprint, render_template, request, redirect, url_for, session, flash #il nostro ponte
from groq import Groq #ponte per IA 
from config import Config #per le nostre chiavi
#qua portiamo tutti nostri route e funzione che fanno passare dati in questi rooute 
#es.16
from models.database import (
    registra_utente,
    login_utente,
    leggi_utenti,
    trova_utente,
    modifica_utente,
    elimina_utente,
    inserisce_paziente,
    leggi_paziente,
    trova_paziente,
    modifica_paziente,
    elimina_paziente,
    inserisci_servizio,
    leggi_servizi,
    trova_servizio,
    modifica_servizio,
    elimina_servizio,
    inserisci_appuntamento,
    trova_appuntamento,
    modifica_appuntamento,
    elimina_appuntamento,
    inserisci_dottore,
    leggi_dottori,
    trova_dottore,
    modifica_dottore,
    elimina_dottore,
    leggi_informazione,
    leggi_esami,
    leggi_reparti,
    salva_conversazione,
    ultime_conversazioni
)

#inseriamo parola senza sinificato e collegiamo con route e bluprint per la sicurezza dei dati.
durka_route = Blueprint("durka_route", __name__)
#collegiamo al nostro lending e facciamo capire quale la directori principale
@durka_route.route("/")
def index():
    return render_template("landing.html")
#funzione della registrazione utenti
@durka_route.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        conferma = request.form.get("conferma", password)

        if password != conferma:
            flash("Le due password non coincidono.", "error")
            return render_template("register.html", username=username)

        #username e UNIQUE nella tabella utenti: se esiste gia, SQLite da IntegrityError
        try:
            registra_utente(username, password)
        except sqlite3.IntegrityError:
            flash("Questo username è già in uso. Scegline un altro.", "error")
            return render_template("register.html", username=username)

        #dopo la registrazione l'utente entra subito, come dopo il login
        utente = login_utente(username, password)
        session["utente_id"] = utente[0]
        session["username"] = utente[1]
        session["ruolo"] = utente[2]
        return redirect(url_for("durka_route.benvenuto"))
    return render_template("register.html")

#pagina di registrazione completata
@durka_route.route("/benvenuto")
def benvenuto():
    if "utente_id" not in session:
        return redirect(url_for("durka_route.login"))
    return render_template("registrazione_ok.html", nome_utente=session["username"])
#funzione login 
@durka_route.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        utente = login_utente(username, password) #16(140)
        if utente:
            session["utente_id"] = utente[0]
            session["username"] = utente[1]
            #sessione per passagio dati sensibile 16(150)
            session["ruolo"] = utente[2] #indiachiamo ruolo cosi admin entra nella sessione particolare
            return redirect(url_for("durka_route.profilo"))
        #elaboriamo errore come es.25(102) del login sbagliato
        flash("Username o password errati", "error")
    return render_template("login.html")
#logout per chiudere sessione 
@durka_route.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("durka_route.index"))
#controlliamo se sessione è aperta
@durka_route.route("/profilo")
def profilo():
    if "utente_id" not in session:
        return redirect(url_for("durka_route.login"))
    utente= trova_utente(session["utente_id"])
    return render_template("profilo.html", utente=utente)
#se sessione non è aperta mandiamo alla pagina login
@durka_route.route("/profilo/modifica", methods=["GET", "POST"])
def modifica_profilo():
    if "utente_id" not in session:
        return redirect(url_for("durka_route.login"))
    id = session["utente_id"]
    if request.method == "POST":
        username = request.form["username"].strip()
        password= request.form["password"]
        try:
            modifica_utente(id, username, password)
        except sqlite3.IntegrityError:
            flash("Questo username è già in uso. Scegline un altro.", "error")
            return redirect(url_for("durka_route.profilo"))
        session["username"] = username
        flash("Dati aggiornati.", "success")
        return redirect(url_for("durka_route.profilo"))
    return redirect(url_for("durka_route.profilo")) #16(183)

#questi dati sono visibile solo ad admin es.16(212)
@durka_route.route("/admin/utenti") #16(212)
def utenti():
    if session.get("ruolo") != "admin": #solo per admin
        return redirect(url_for("durka_route.profilo"))
    utenti = leggi_utenti()
    return render_template("utenti.html", utenti=utenti)

@durka_route.route("/admin/utenti/elimina/<int:id>") #sempre solo per admin 16(255)
def elimina_utente_admin(id):
   #ho fatto elimanzione semplice, perche non ho capito come si fa con numeri buleani 
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    if id == session["utente_id"]:
        return redirect(url_for("durka_route.utenti"))
    elimina_utente(id)
    return redirect(url_for("durka_route.utenti"))

#inserimento paziente solo admin 
@durka_route.route("/paziente", methods=["POST"])
def paziente(): 
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    nome = request.form["nome"]
    cognome = request.form["cognome"]
    data_nascita = request.form["data_nascita"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    indirizzo = request.form["indirizzo"]
    filiale = request.form.get("filiale")
    allergie = request.form.get("allergie")
    dottori_id = request.form.get("dottori_id")
    note = request.form.get("note")
    id_paziente = inserisce_paziente(nome, cognome, data_nascita, email, telefono, indirizzo, filiale, allergie, note, dottori_id)
    return redirect(url_for("durka_route.scheda", id=id_paziente))

@durka_route.route("/paziente/<int:id>") #visualizziamo paziente 
def scheda(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    paziente = trova_paziente(id)
    return render_template("scheda.html", paziente=paziente)

@durka_route.route("/select") #selizioniamo paziente sempre solo admin 
def select():
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    paziente = leggi_paziente()
    dottori = leggi_dottori()
    return render_template("select.html", paziente = paziente, dottori = dottori)

@durka_route.route("/update/<int:id>", methods=["POST"]) #aggiorna 
def update(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    nome= request.form["nome"]
    cognome= request.form["cognome"]
    data_nascita= request.form["data_nascita"]
    email= request.form["email"]
    telefono= request.form["telefono"]
    indirizzo= request.form["indirizzo"]
    filiale= request.form.get("filiale")
    allergie= request.form.get("allergie")
    note= request.form.get("note")
    modifica_paziente(id, nome, cognome, data_nascita, email, telefono, indirizzo, filiale, allergie, note)
    return redirect(url_for("durka_route.scheda", id=id))

@durka_route.route("/delete/<int:id>") #elimina
def delete_paziente(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    elimina_paziente(id)
    return redirect(url_for("durka_route.select"))

@durka_route.route("/servizio", methods=["POST"]) #creare servizi solo admin 
def reparto():
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    nome = request.form["nome"]
    descrizione = request.form["descrizione"]
    prezzo = request.form["prezzo"]
    durata = request.form["durata"]
    inserisci_servizio(nome, descrizione, prezzo, durata)
    return redirect(url_for("durka_route.servizi"))

@durka_route.route("/servizi")
def servizi():
    if "utente_id" not in session:
        return redirect(url_for("durka_route.login"))
    servizi = leggi_servizi()
    return render_template("servizi.html", servizi=servizi)

@durka_route.route("/update_servizio/<int:id>", methods=["POST"])
def update_servizio(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    nome = request.form["nome"]
    descrizione = request.form["descrizione"]
    prezzo= request.form["prezzo"]
    durata=request.form["durata"]
    modifica_servizio(id, nome, descrizione, prezzo, durata)
    return redirect(url_for("durka_route.servizi"))

@durka_route.route("/delete_servizio/<int:id>")
def delete_servizio(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    elimina_servizio(id)
    return redirect(url_for("durka_route.servizi"))

@durka_route.route("/appuntamento", methods=["POST"]) #per tutti utenti registrati pg.16
def appuntamento():
    if "utente_id" not in session:
        return redirect(url_for("durka_route.login"))
    id_paziente = request.form["id_paziente"]
    id_dottore = request.form["id_dottore"]
    data_ora = request.form["data_ora"]
    reparto = request.form["reparto"]
    inserisci_appuntamento(id_paziente, id_dottore, data_ora, reparto)
    if session["ruolo"] == "admin":
        return redirect(url_for("durka_route.scheda", id=id_paziente))
    return redirect(url_for("durka_route.prenota"))  

@durka_route.route("/prenota")
def prenota():
    if "utente_id" not in session:
        return redirect(url_for("durka_route.login"))
    dottori = leggi_dottori()
    return render_template("appuntamento.html", dottori=dottori)

@durka_route.route("/appuntamento/<int:id>") #visualizzza appuntamenti 
def vedi_appuntamento(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    appuntamento = trova_appuntamento(id)
    dottori = leggi_dottori()
    return render_template("appuntamento.html", appuntamento=appuntamento, dottori=dottori)

@durka_route.route("/update_appuntamento/<int:id>", methods=["POST"]) #modifica solo admin 
def update_appuntamento(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    id_paziente = request.form["id_paziente"]
    id_dottore = request.form["id_dottore"]
    data_ora = request.form["data_ora"]
    reparto = request.form["reparto"]
    modifica_appuntamento(id, id_paziente, id_dottore, data_ora, reparto)
    return redirect(url_for("durka_route.prenota"))

@durka_route.route("/delete_appuntamento/<int:id>") #elimina solo admin 
def delete_appuntamento(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    elimina_appuntamento(id)
    return redirect(url_for("durka_route.prenota"))

#CRUD per dottori solo admin 
@durka_route.route("/dottore", methods=["POST"])  
def dottore():
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    nome = request.form["nome"]
    cognome = request.form["cognome"]
    specializzazione = request.form["specializzazione"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    inserisci_dottore(nome, cognome, specializzazione, email, telefono)
    return redirect(url_for("durka_route.dottori"))


@durka_route.route("/dottori")
def dottori():
    if "utente_id" not in session:
        return redirect(url_for("durka_route.login"))
    dottori = leggi_dottori()
    return render_template("dottori.html", dottori=dottori)

@durka_route.route("/update_dottore/<int:id>", methods=["POST"])
def update_dottore(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    nome = request.form["nome"]
    cognome = request.form["cognome"]
    specializzazione = request.form["specializzazione"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    modifica_dottore(id, nome, cognome, specializzazione, email, telefono)
    return redirect(url_for("durka_route.dottori"))

@durka_route.route("/delete_dottore/<int:id>")
def delete_dottore(id):
    if session.get("ruolo") != "admin":
        return redirect(url_for("durka_route.profilo"))
    elimina_dottore(id)
    return redirect(url_for("durka_route.dottori"))


#assistente statico es.23
@durka_route.route("/assistente", methods=["GET", "POST"])
def assistente():
    nome_clinica = leggi_informazione("nome_clinica")
    scelta = None
    titolo = ""
    righe = []
    lista = []
    messaggio = ""
    uscita = False

    if request.method == "POST":
        #scelta 1 
        scelta = request.form.get("scelta", "").strip()
        if scelta == "1":
            titolo = "Informazioni generali"
            righe = [
                ("Nome", leggi_informazione("nome_clinica")),
                ("Indirizzo", leggi_informazione("indirizzo")),
                ("Telefono", leggi_informazione("telefono")),
                ("Email", leggi_informazione("email"))
            ]

        #scelta 2 
        elif scelta == "2":
            titolo = "Orari di apertura"
            righe = [
                ("Lunedì - Venerdì", leggi_informazione("orario_settimana")),
                ("Sabato", leggi_informazione("orario_sabato")),
                ("Domenica", leggi_informazione("orario_domenica"))
            ]
            messaggio = "Per richieste particolari, contatta la reception."

        #scelta 3
        elif scelta == "3":
            titolo = "Orari di prelievi, visite e ricoveri"
            righe = [
                ("Centro prelievi", leggi_informazione("orario_prelievi")),
                ("Visite", leggi_informazione("orario_visite")),
                ("Ricoveri", leggi_informazione("orario_ricoveri"))
            ]

        #scelta 4
        elif scelta == "4":
            titolo = "Tempi per avere i risultati degli esami"
            messaggio = leggi_informazione("tempi_esami")

        #scelta 5
        elif scelta == "5":
            titolo = "Prezzi indicativi degli esami"
            righe = [
                (nome, f"{prezzo:g} euro")
                for nome, prezzo in leggi_esami()
            ]
            righe.append(("Pagamenti", leggi_informazione("pagamenti")))
            messaggio = (
                "I prezzi sono indicativi. "
                "Per il prezzo esatto contatta direttamente la reception."
            )

        #scelta 6
        elif scelta == "6":
            titolo = "Reparti della clinica"
            lista = [
                reparto[0]
                for reparto in leggi_reparti()
            ]

        #scelta 7
        elif scelta == "7":
            titolo = "Contatta la reception"
            righe = [
                ("Telefono", leggi_informazione("telefono")),
                ("Email", leggi_informazione("email")),
                ("Indirizzo", leggi_informazione("indirizzo"))
            ]

        #uscita
        elif scelta == "0":
            uscita = True
            titolo = "Grazie per averci contattato!"
            messaggio = f"Grazie per aver contattato {nome_clinica}. A presto!"

        #gestione errore
        else:
            titolo = "Attenzione"
            messaggio = "Opzione non valida. Seleziona un numero compreso tra 0 e 7."

    return render_template(
        "assistente.html",
        nome_clinica=nome_clinica,
        scelta=scelta,
        titolo=titolo,
        righe=righe,
        lista=lista,
        messaggio=messaggio,
        uscita=uscita
    )


#assistente IA con ponte Groq modello chatGPT come indicato nella config

MODELLO_IA = Config.GROQ_MODEL

#creamo collegamneto con groq es.17 
def crea_client_ia():
    if not Config.GROQ_API_KEY:
        return None
    return Groq(api_key=Config.GROQ_API_KEY)

#impostiamo ruolo 
ruolo = (
    "Sei un assistente virtuale della clinica privata italiana Med.Expert. "
    "Rispondi nella lingua in cui ti scrive il paziente: italiano, inglese, russo, arabo o cinese. "
    "Spiega ogni argomento in modo semplice. "
    "Usa esempi pratici e risposte brevi. "
    "Sii gentile e paziente, dai supporto morale e rafforza la sicurezza del paziente. "
    "Parli con anziani che non sono pratici nell'usare il computer: dai riferimenti concreti. "
    "Non usare le solite frasi fatte da assistente virtuale, parla come una persona reale, "
    "madrelingua nella lingua scelta. "
    "Non fai diagnosi e non prescrivi farmaci: per problemi di salute consiglia di prenotare una visita. "
    "Tieni conto dei messaggi precedenti della conversazione."
)

#apriamo nuova conversazione es.25
def nuova_conversazione():
    return [
        {
            "role": "system",
            "content": ruolo,
        }
    ]


@durka_route.route("/chat", methods=["GET", "POST"])
def chat():
    #chat assistnete con IA es.25 copia incolla 

    if "utente_id" not in session:
        return redirect(url_for("durka_route.login"))

    nome_utente = session["username"]
    conversazione = session.get("conversazione", nuova_conversazione())

    storico = ultime_conversazioni(nome_utente, limite=10)
    risposta_ultima = None

    if request.method == "POST":
        domanda = request.form.get("domanda", "").strip()
        comando = domanda.lower()

        #aggiungere parole per la chiusura della sessione
        if comando in ["esci", "fine", "stop"]:
            session.clear()
            flash("Sessione terminata. Arrivederci!", "success")
            return redirect(url_for("durka_route.index"))

        #per stampare storico
        if comando == "storico":
            return redirect(url_for("durka_route.storico"))

        if not domanda:
            flash("Inserisci una domanda prima di inviare.", "error")

            return render_template(
                "chat.html",
                nome_utente=nome_utente,
                conversazione=conversazione[1:],
                storico=storico,
                risposta_ultima=None,
                modello=MODELLO_IA,
            )

        client = crea_client_ia()

        if client is None:
            flash(
                "Chiave GROQ_API_KEY mancante. "
                "Configurala nel file .env.",
                "error",
            )

            return render_template(
                "chat.html",
                nome_utente=nome_utente,
                conversazione=conversazione[1:],
                storico=storico,
                risposta_ultima=None,
                modello=MODELLO_IA,
            )

        #aggiungere domanda 
        conversazione.append(
            {"role": "user", "content": domanda}
        )

        try:
            risultato = client.chat.completions.create(
                model=MODELLO_IA,
                messages=conversazione,
                max_completion_tokens=500, #modificare sercondo esigenze 
            )
            # 0 in questo caso è stesso resultato che viene fornito da AI 
            testo_risposta = risultato.choices[0].message.content

            if not testo_risposta or not testo_risposta.strip():
                conversazione.pop()

                flash(
                    "L'assistente non ha restituito una risposta.",
                    "error",
                )

            else:
                conversazione.append( #inseriamo la ripsosta nel database
                    {
                        "role": "assistant",
                        "content": testo_risposta,
                    }
                )

                data_ora = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                #salva la risposta inserite nel database
                salva_conversazione(
                    nome_utente,
                    domanda,
                    testo_risposta,
                    data_ora,
                )

                risposta_ultima = testo_risposta

        except Exception:
            if (
                conversazione
                and conversazione[-1]["role"] == "user"
            ):
                conversazione.pop()

            flash(
                "Errore durante la richiesta IA. Riprova più tardi.",
                "error",
            )

        session["conversazione"] = conversazione

        storico = ultime_conversazioni(
            nome_utente,
            limite=10,
        )

    return render_template(
        "chat.html",
        nome_utente=nome_utente,
        conversazione=session.get("conversazione", [])[1:],
        storico=storico,
        risposta_ultima=risposta_ultima,
        modello=MODELLO_IA,
    )

#per visualizzare storico, es.25
@durka_route.route("/storico") 
def storico():

    if "utente_id" not in session:
        return redirect(url_for("durka_route.login"))

    nome_utente = session["username"]
    risultati = ultime_conversazioni(nome_utente, limite=10)

    return render_template(
        "storico.html",
        nome_utente=nome_utente,
        risultati=risultati,
    )

#riconminica la conversazione 
@durka_route.route("/nuova-chat", methods=["POST"])
def nuova_chat():

    if "utente_id" in session:
        session["conversazione"] = nuova_conversazione()

    return redirect(url_for("durka_route.chat"))
