import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='',
    db='novamind',
    port=3306
)
print("Connected!", conn)
conn.close()
