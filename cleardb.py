import TinyDB as ty

ty.createdb()
table = ty.createtable()
ty.cleartable(table)
ty.closedb()