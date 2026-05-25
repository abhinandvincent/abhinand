import os
import django
import importlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product.settings')
django.setup()

m = importlib.import_module('adminapp.models')
from django.db import connection

print('db_table', m.Product._meta.db_table)
with connection.cursor() as c:
    c.execute('SHOW TABLES')
    print('tables', c.fetchall())
    try:
        c.execute('SHOW COLUMNS FROM adminapp_product')
        print('columns', c.fetchall())
    except Exception as e:
        print('columns error', repr(e))
