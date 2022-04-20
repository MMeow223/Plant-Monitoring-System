import mysql.connector

host = "localhost"
user = "root"
password = ""
database = "plant_monitoring_system"

# if database not exist, create it
try:
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
except:
    print("Database not found, creating it...\n")
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )
    mycursor = mydb.cursor()

    mycursor.execute("CREATE DATABASE plant_monitoring_system")

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="plant_monitoring_system"
    )

mycursor = mydb.cursor()

# if table not exist, create it
mycursor.execute(
    "CREATE TABLE monitoring_data (id INT AUTO_INCREMENT PRIMARY KEY, timestamp DATETIME DEFAULT current_timestamp, footcandle float, moisture int(3), humidity int(3), temperature float(3))"
)

mycursor.execute(
    "CREATE TABLE fan_toggle (id INT AUTO_INCREMENT PRIMARY KEY, timestamp DATETIME DEFAULT current_timestamp, fan_status boolean)"
)

mycursor.execute(
    "CREATE TABLE lamp_toggle (id INT AUTO_INCREMENT PRIMARY KEY, timestamp DATETIME DEFAULT current_timestamp, lamp_status boolean)"
)

mycursor.execute(
    "CREATE TABLE pump_toggle (id INT AUTO_INCREMENT PRIMARY KEY, timestamp DATETIME DEFAULT current_timestamp, pump_status boolean)"
)

mycursor.execute("SHOW TABLES")

validation = False
required_tables = ['fan_toggle', 'lamp_toggle',
                   'monitoring_data', 'pump_toggle']
for x in mycursor:
    if(x[0] in required_tables):
        print("Check table " + x[0] + " exist - pass /")
        validation = True

    else:
        print("Check table " + x[0] + " exist - fail X")
        validation = False

if(validation):
    print("\nDatabase validation - pass /")
else:
    print("\nDatabase validation - fail X")
