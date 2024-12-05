from tinydb import TinyDB

# Var
db = None

def createdb(dbname):
    global db
    db = TinyDB(dbname)

def closedb():
    db.close()

def createtable(tablename):
    return db.table(tablename)

def insert(table, elem):
    table.insert(elem)

def printtable(table):
    for sample in table.all():
        print(sample)

def cleartable(table):
    table.purge()