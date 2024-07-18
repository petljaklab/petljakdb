import mysql.connector
from os.path import expanduser

connection = mysql.connector.connect(option_files = expanduser("~/.my.cnf"))