# REGISTRAZIONE ACCESSI VIA WEB NFC

Il dispositivo Android si collega al Server, fornendogli un UID (codice univoco del tag NFC) ed ottenendo lo stato da aggiornare nel tag.

Il Server quando contattato cerca nel file di Registro l'UID, ne aggiorna lo stato e restituisce il nuovo valore al dispositivo.

## SERVER 

### Funzioni
#### normalize_UID(UID)
Pulisce l'id Utente rimuovendo ":" e "-"

#### read_all()
- Restituisce un dizionario {UID: stato} del file Registro
- Salta righe vuote o senza :

#### update(UID, new_state)
Aggiorna il file di Registro con il nuovo stato dell'Utente

#### /nfc (POST)
Riceve un UID, ne restituisce lo stato dopo l'aggiornamento

Se l'utente viene trovato, ne inverte il stato (0→1 o 1→0)
Se l'utente è nuovo, lo registra come presente (1)

+ Thread-safe grazie al LOCK
-  Nessuna autenticazione (chiunque può inviare richieste)

## WEB NFC

