import TinyDB as ty

ty.createdb('db.json')
table = ty.createtable('raw_data_test')
ty.cleartable(table)
ty.closedb()