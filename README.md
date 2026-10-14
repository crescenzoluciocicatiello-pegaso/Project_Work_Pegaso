# Prenotazione digitale di prestazioni sanitarie

Applicazione full-stack API-based che permette a un paziente di registrarsi, inserire una ricetta elettronica (NRE), scegliere un orario libero e prenotare le prestazioni prescritte, con resoconto stampabile.

Progetto realizzato per il project work del corso di laurea in **Informatica per le aziende digitali (L-31)** – Università Telematica Pegaso.
Tema 1 “La digitalizzazione dell’impresa”, Traccia 16.

Autore: **Crescenzo Lucio Cicatiello**

---

## Funzionalità

- Registrazione e accesso del paziente (password salvate come hash bcrypt)
- Inserimento di una ricetta con NRE, medico, date di emissione e scadenza e prestazioni prescritte
- Elenco degli slot liberi di una prestazione, raggruppati per giorno
- Prenotazione e annullamento di una prestazione, con aggiornamento dello stato dello slot
- Dashboard con ricette, prenotazioni e prossimo appuntamento
- Resoconto della prenotazione stampabile

## Tecnologie

| Livello  | Strumenti |
|----------|-----------|
| Backend  | Python, FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic 2, Passlib (bcrypt), python-dotenv |
| Database | PostgreSQL |
| Frontend | Nuxt 3, Vue 3, TypeScript, Nuxt UI 3, Zod |

## Struttura del repository

```
backend/
├── app/
│   ├── main.py        # crea l'applicazione, registra i router, configura CORS
│   ├── db.py          # connessione al database e sessioni
│   ├── models.py      # modelli SQLAlchemy (tabelle)
│   ├── schemas.py     # schemi Pydantic di richiesta e risposta
│   ├── crud.py        # funzioni di accesso ai dati
│   └── routers/       # endpoint REST divisi per risorsa
├── requirements.txt
└── .env.example
frontend/
├── pages/             # accesso, registrazione, dashboard, prenotazione, resoconto
├── composables/       # funzione unica per le chiamate al backend
└── package.json
```

## Requisiti

- Python 3.10 o superiore
- Node.js 18 o superiore
- PostgreSQL

## Avvio del progetto

### 1. Database

Creare un database vuoto in PostgreSQL, ad esempio `db_prenotazioni`.
Le tabelle vengono create automaticamente all’avvio del backend.

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # su macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Copiare il file `.env.example` in `.env` e inserire i dati di connessione al proprio database:

```
DATABASE_URL=postgresql://utente:password@localhost:5432/db_prenotazioni
```

Avviare il server:

```bash
uvicorn app.main:app --reload
```

L’API è disponibile su `http://localhost:8000`.
La documentazione interattiva si trova su `http://localhost:8000/docs` (Swagger UI) e `http://localhost:8000/redoc`.

### 3. Frontend

In un secondo terminale:

```bash
cd frontend
npm install
npm run dev
```

L’applicazione è disponibile su `http://localhost:3000`.

## Principali endpoint

| Metodo | Endpoint | Funzione |
|--------|----------|----------|
| POST | `/utenti_pazienti/login` | Accesso con username e password |
| POST | `/utenti_pazienti/` | Registrazione di un nuovo paziente |
| GET | `/medici/` | Elenco dei medici |
| GET | `/prestazioni/` | Elenco delle prestazioni |
| POST | `/ricette/` | Creazione di una ricetta |
| POST | `/ricetta-prestazione/` | Collegamento di una prestazione a una ricetta |
| GET | `/ricette/paziente/{id}` | Ricette di un paziente |
| GET | `/ricetta-prestazione/{id_ricetta}` | Prestazioni di una ricetta con stato di prenotazione |
| GET | `/slot/disponibili-by-codice-prestazione` | Slot liberi di una prestazione |
| POST | `/prenotazioni/` | Creazione di una prenotazione |
| GET | `/prenotazioni/paziente/{id}` | Prenotazioni dettagliate di un paziente |
| DELETE | `/prenotazioni/ricetta-prestazione/{id}` | Annullamento di una prenotazione |

L’elenco completo è nella documentazione interattiva.
