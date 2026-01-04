# server.py
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from threading import Lock

DATA_FILE = 'users.txt'  # UID:stato => 04A2BB01:0
                         #                       ^ 0 = Assente
                         #                         1 = Presente
LOCK = Lock()
app = Flask(__name__, static_folder='.')
CORS(app)

def normalize_UID(UID: str) -> str:
    return UID.replace(':','').replace('-','').upper() if UID else UID

# ######################## #
#      __                  #
#     |__)_ _  _| /\ ||    #
#     | \(-(_|(_|/--\||    #
#                          #
# ######################## #

def read_all():
    # Crea il file se non esiste
    if not os.path.exists(DATA_FILE):
        return {}
    d = {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line: 
                continue
            UID, st = line.split(':', 1)
            d[UID.strip().upper()] = st.strip()
    return d

# ------------------------------------------------------------------------
def update(UID, new_state):

# Crea il file se non esiste
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(f'{UID}:{new_state}\n')
        return
    
    # Leggi tutte le righe
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Cerca e aggiorna la riga specifica
    found = False
    for i, line in enumerate(lines):
        if ':' in line:
            file_UID = line.split(':', 1)[0].strip().upper()
            if file_UID == UID:
                lines[i] = f'{UID}:{new_state}\n'
                found = True
                break
    
    # Se non trovato, aggiungi in fondo
    if not found:
        lines.append(f'{UID}:{new_state}\n')
    
    # Riscrivi il file
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# ------------------------------------------------------------------------
@app.route('/nfc', methods=['POST'])
def nfc():
    
    payload = request.get_json(silent=True)
    # Errori
    if not payload:
        return jsonify({'error': 'E! Json'}), 400
    raw_UID = payload.get('UID')
    if not raw_UID:
        return jsonify({'error': 'E! No UID'}), 400
    UID = normalize_UID(raw_UID)
    if not UID:
        return jsonify({'error': 'E! UID'}), 400

#   Bussa il file
    try:
        with LOCK:
            data = read_all()
            
#           Alterna stato
            if cur is None:
                new_state = '1'
            else:
                new_state = '0' if cur == '1' else '1'
            
#           Aggiorna solo la riga specifica
            update(UID, new_state)
            
#           Legge Dopo
            confirmed = read_all().get(UID)
        
#       Restituisce json { UID + PRIMA + DOPO } 
        return jsonify({'UID': UID, 'DOPO': confirmed}), 200
    except Exception as e:
        return jsonify({'error': 'E! Server', 'detail': str(e)}), 500

# ------------------------------------------------------------------------
@app.route('/')
def root():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
