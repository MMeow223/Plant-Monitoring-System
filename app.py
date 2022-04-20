from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import serial
import threading
import time
app = Flask(__name__)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="plant_monitoring_system"
)

thread_started = False


@app.route('/')
def index():
    global thread_started
    mycursor = mydb.cursor()

    if(thread_started == False):
        thread_started = True
        # ser = serial.Serial('COM3', 9600, timeout=1)
        thread2 = threading.Thread(
            target=save_data_to_database, args=(mycursor,))

        thread2.start()

    mycursor.execute("SELECT * FROM monitoring_data ORDER BY id DESC")

    result = mycursor.fetchall()

    return render_template('index.html', result=result,)


@app.route('/fan_operation')
def fan_operation():
    global thread_started
    mycursor = mydb.cursor()

    if(thread_started == False):
        thread_started = True
        ser = serial.Serial('COM3', 9600, timeout=1)
        thread2 = threading.Thread(
            target=save_data_to_database, args=(mycursor,))

        thread2.start()

    mycursor.execute("SELECT * FROM fan_toggle ORDER BY id DESC")

    result = mycursor.fetchall()

    return render_template('fan.operation.html', result=result,)


@app.route('/lamp_operation')
def lamp_operation():
    global thread_started
    mycursor = mydb.cursor()

    if(thread_started == False):
        thread_started = True
        # ser = serial.Serial('COM3', 9600, timeout=1)
        thread2 = threading.Thread(
            target=save_data_to_database, args=(mycursor))

        thread2.start()

    mycursor.execute("SELECT * FROM lamp_toggle ORDER BY id DESC")

    result = mycursor.fetchall()

    return render_template('lamp.operation.html', result=result,)


@app.route('/pump_operation')
def pump_operation():
    global thread_started
    mycursor = mydb.cursor()

    if(thread_started == False):
        thread_started = True
        # ser = serial.Serial('COM3', 9600, timeout=1)
        thread2 = threading.Thread(
            target=save_data_to_database, args=(mycursor))

        thread2.start()

    mycursor.execute("SELECT * FROM pump_toggle ORDER BY id DESC")

    result = mycursor.fetchall()

    return render_template('pump.operation.html', result=result,)


@app.route('/dashboard')
def dashboard():
    global thread_started
    mycursor = mydb.cursor()

    if(thread_started == False):
        thread_started = True
        thread2 = threading.Thread(
            target=save_data_to_database, args=(mycursor,))

        thread2.start()

    mycursor.execute("SELECT COUNT(*) FROM lamp_toggle WHERE lamp_status = 1")
    lightOnResult = mycursor.fetchall()

    mycursor.execute("SELECT COUNT(*) FROM lamp_toggle WHERE lamp_status = 0")
    lightOffResult = mycursor.fetchall()

    mycursor.execute("SELECT COUNT(*) FROM fan_toggle WHERE fan_status = 1")
    fanOnResult = mycursor.fetchall()

    mycursor.execute("SELECT COUNT(*) FROM fan_toggle WHERE fan_status = 0")
    fanOffResult = mycursor.fetchall()

    mycursor.execute("SELECT COUNT(*) FROM pump_toggle WHERE pump_status = 1")
    pumpOnResult = mycursor.fetchall()

    mycursor.execute("SELECT COUNT(*) FROM pump_toggle WHERE pump_status = 0")
    pumpOffResult = mycursor.fetchall()

    mycursor.execute(
        "SELECT * FROM monitoring_data WHERE DATE(timestamp) = CURDATE() ORDER BY `id` DESC LIMIT 24 ")
    monitoringResult = mycursor.fetchall()

    footcandleArray = []
    humidityArray = []
    moistureArray = []
    temperatureArray = []

    for row in monitoringResult:
        footcandleArray.append(row[2])
        moistureArray.append(row[3])
        humidityArray.append(row[4])
        temperatureArray.append(row[5])

    return render_template('dashboard.html', lightOnResult=lightOnResult, lightOffResult=lightOffResult, fanOnResult=fanOnResult, fanOffResult=fanOffResult, footcandleArray=footcandleArray, humidityArray=humidityArray, temperatureArray=temperatureArray, moistureArray=moistureArray, pumpOnResult=pumpOnResult, pumpOffResult=pumpOffResult)


@app.route('/action/<action>')
def control_actions(action):

    if action == "water_plant":
        print("Watering plant...")
        ser.write(b"1")
    if action == "toggle_lamp":
        print("Toggling lamp...")
        ser.write(b'2')
    if action == "toggle_fan":
        print("Toggling fan...")
        ser.write(b'3')
    if action == "toggle_auto_lamp":
        print("Toggling auto lamp...")
        ser.write(b'4')
    if action == "toggle_auto_fan":
        print("Toggling auto fan...")
        ser.write(b'5')
    if action == "toggle_auto_pump":
        print("Toggling auto pump...")
        ser.write(b'6')
    if action == "reset":
        print("Reset...")
        ser.write(b'7')

    return redirect('/dashboard')


def save_data_to_database(mycursor):

    while 1:
        line = ser.readline().decode('utf-8').rstrip()
        ser.reset_input_buffer()

        print("Line = " + line)
        # separate the string into list
        x = line.split("|")
        if(len(x) == 1):
            pass
        else:
            try:
                humidity = int(float(x[0]))
                temperature = float(x[1])
                footcandle = float(x[2])
                moisture = float(x[3])
                lampstatus = bool(0 if (x[4] == '1') else 1)
                fanstatus = bool(0 if (x[5] == '1') else 1)
                pumpstatus = bool(x[6])

                mycursor.execute(
                    "INSERT INTO monitoring_data (`id`,`timestamp`,`footcandle`,`moisture`,`humidity`,`temperature`) VALUES (NULL,DEFAULT,{0},{1},{2},{3})".format(footcandle, moisture, humidity, temperature))

                mycursor.execute(
                    "INSERT INTO lamp_toggle (`id`, `timestamp`, `lamp_status`) VALUES (NULL,DEFAULT,{0})".format(lampstatus))

                mycursor.execute(
                    "INSERT INTO `fan_toggle`(`id`, `timestamp`, `fan_status`) VALUES (NULL,DEFAULT,{0})".format(fanstatus))

                mycursor.execute(
                    "INSERT INTO `pump_toggle`(`id`, `timestamp`, `pump_status`) VALUES (NULL,DEFAULT,{0})".format(pumpstatus))

                mydb.commit()

            except:
                print("Error")
        time.sleep(10)


if __name__ == '__main__':
    ser = serial.Serial('COM3', 9600, timeout=1)
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
