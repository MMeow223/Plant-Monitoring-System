import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)
mycursor = mydb.cursor()

mycursor.execute("DROP DATABASE plant_monitoring_system")

print("Database Drop Success! ")
