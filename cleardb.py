from tinydb import TinyDB

# Apri il database
db = TinyDB('db.json')

# Ottieni la tabella che vuoi pulire
table = db.table('raw_data_test')

# Elimina tutti i documenti dalla tabella
table.purge()

# Chiudi il database
db.close()