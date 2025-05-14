'''
SECRET_KEY = 'yasmine'
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'novamind'
'''
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_pwd')
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_DB = os.environ.get('MYSQL_DB', 'novamind')