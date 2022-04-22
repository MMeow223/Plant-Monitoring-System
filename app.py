from flask import Flask, make_response, render_template, request, redirect
from mysql.connector import Error
import mysql.connector
import serial
import threading
import time
import json

app = Flask(__name__)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="plant_monitoring_system"
)
mydb.reconnect()
mycursor = mydb.cursor()
mycursor.execute('set global max_allowed_packet=67108864')
mycursor.close()

thread_started = False
humidity = ""
temperature = ""
footcandle = ""
moisture = ""
lampstatus = ""
fanstatus = ""
pumpstatus = ""
autolamp = True
autofan = True
autopump = True


def thread_start():
    global thread_started

    if(thread_started == False):
        # mycursor = mydb.cursor()
        thread_started = True
        thread2 = threading.Thread(
            target=save_data_to_database, args=())
        thread2.start()


@app.route('/')
def index():
    # global thread_started
    # mycursor = mydb.cursor()

    # if(thread_started == False):
    #     thread_started = True
    #     # ser = serial.Serial('COM3', 9600, timeout=1)
    #     thread2 = threading.Thread(
    #         target=save_data_to_database, args=(mycursor,))

    #     thread2.start()
    thread_start()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM monitoring_data ORDER BY id DESC")

    result = mycursor.fetchall()
    mycursor.close()

    return render_template('index.html', result=result,)


@app.route('/fan_operation')
def fan_operation():
    # global thread_started
    # mycursor = mydb.cursor()

    # if(thread_started == False):
    #     thread_started = True
    #     # ser = serial.Serial('COM3', 9600, timeout=1)
    #     thread2 = threading.Thread(
    #         target=save_data_to_database, args=(mycursor,))

    #     thread2.start()
    thread_start()

    mydb.reconnect()

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM fan_toggle ORDER BY id DESC")

    result = mycursor.fetchall()
    mycursor.close()
    return render_template('fan.operation.html', result=result,)


@app.route('/lamp_operation')
def lamp_operation():
    # global thread_started
    # mycursor = mydb.cursor()

    # if(thread_started == False):
    #     thread_started = True
    #     # ser = serial.Serial('COM3', 9600, timeout=1)
    #     thread2 = threading.Thread(
    #         target=save_data_to_database, args=(mycursor))

    #     thread2.start()
    thread_start()
    mydb.reconnect()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM lamp_toggle ORDER BY id DESC")

    result = mycursor.fetchall()
    mycursor.close()
    return render_template('lamp.operation.html', result=result,)


@app.route('/pump_operation')
def pump_operation():
    # global thread_started
    # mycursor = mydb.cursor()

    # if(thread_started == False):
    #     thread_started = True
    #     # ser = serial.Serial('COM3', 9600, timeout=1)
    #     thread2 = threading.Thread(
    #         target=save_data_to_database, args=(mycursor))

    #     thread2.start()
    thread_start()
    mydb.reconnect()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM pump_toggle ORDER BY id DESC")

    result = mycursor.fetchall()
    mycursor.close()

    return render_template('pump.operation.html', result=result,)


@app.route('/dashboard')
def dashboard():
    # global thread_started
    global humidity
    global temperature
    global footcandle
    global moisture
    global lampstatus
    global fanstatus
    global pumpstatus
    global autolamp
    global autofan
    global autopump

    # mycursor = mydb.cursor()

    # if(thread_started == False):
    #     thread_started = True
    #     thread2 = threading.Thread(
    #         target=save_data_to_database, args=(mycursor,))

    #     thread2.start()
    thread_start()
    mydb.reconnect()
    mycursor = mydb.cursor()

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

    mycursor.close()

    # set default value of 0 to the variable below
    if ser.in_waiting:

        line = ser.readline().decode('utf-8').rstrip()
        ser.reset_input_buffer()
        x = line.split("|")

        if(len(x) == 10):
            humidity = x[0]
            temperature = x[1]
            footcandle = x[2]
            moisture = x[3]
            lampstatus = 0 if (x[4] == '1') else 1
            fanstatus = 0 if (x[5] == '1') else 1
            pumpstatus = x[6]
            autolamp = x[7]
            autofan = x[8]
            autopump = x[9]

    footcandleArray = []
    humidityArray = []
    moistureArray = []
    temperatureArray = []

    for row in monitoringResult:
        footcandleArray.append(row[2])
        moistureArray.append(row[3])
        humidityArray.append(row[4])
        temperatureArray.append(row[5])

    templateData = {
        'lightOnResult': lightOnResult,
        'lightOffResult': lightOffResult,
        'fanOnResult': fanOnResult,
        'fanOffResult': fanOffResult,

        'pumpOnResult': pumpOnResult,
        'pumpOffResult': pumpOffResult,

        'footcandleArray': footcandleArray,
        'humidityArray': humidityArray,
        'moistureArray': moistureArray,
        'temperatureArray': temperatureArray,

        'humidity': humidity,
        'moisture': moisture,
        'temperature': temperature,
        'footcandle': footcandle,
        'lampstatus': lampstatus,
        'fanstatus': fanstatus,
        'pumpstatus': pumpstatus,

        'autolamp': autolamp,
        'autofan': autofan,
        'autopump': autopump,

    }
    return render_template('dashboard.html', **templateData)
    # return render_template('dashboard.html', lightOnResult=lightOnResult, lightOffResult=lightOffResult, fanOnResult=fanOnResult, fanOffResult=fanOffResult, footcandleArray=footcandleArray, humidityArray=humidityArray, temperatureArray=temperatureArray, moistureArray=moistureArray, pumpOnResult=pumpOnResult, pumpOffResult=pumpOffResult)


@app.route('/api/get-data', methods=['POST', 'GET'])
def get_data():
    # global thread_started
    global humidity
    global temperature
    global footcandle
    global moisture
    global lampstatus
    global fanstatus
    global pumpstatus
    global autolamp
    global autofan
    global autopump

    # mycursor = mydb.cursor()

    # if(thread_started == False):
    #     thread_started = True
    #     thread2 = threading.Thread(
    #         target=save_data_to_database, args=(mycursor,))

    #     thread2.start()
    thread_start()
    if ser.in_waiting:

        # set default value of 0 to the variable below
        line = ser.readline().decode('utf-8').rstrip()
        ser.reset_input_buffer()
        x = line.split("|")

        if(len(x) == 10):
            humidity = x[0]
            temperature = x[1]
            footcandle = x[2]
            moisture = x[3]
            lampstatus = 0 if (x[4] == '1') else 1
            fanstatus = 0 if (x[5] == '1') else 1
            pumpstatus = x[6]
            autolamp = x[7]
            autofan = x[8]
            autopump = x[9]

    data = [humidity, temperature, footcandle, moisture, lampstatus,
            fanstatus, autolamp, autofan, autopump]

    response = make_response(json.dumps(data))
    response.content_type = 'application/json'

    return response


@ app.route('/action/<action>')
def control_actions(action):

    if action == "water_plant":
        ser.write("1001".encode())
    if action == "toggle_lamp":
        ser.write('1002'.encode())
    if action == "toggle_fan":
        ser.write('1003'.encode())
    if action == "toggle_auto_lamp":
        ser.write('1004'.encode())
    if action == "toggle_auto_fan":
        ser.write('1005'.encode())
    if action == "toggle_auto_pump":
        ser.write('1006'.encode())
    if action == "reset":
        ser.write('1007'.encode())

    # return dashboard()

    return redirect('/dashboard')


@ app.route('/setting', methods=['POST'])
def setting():
    preferredLight = request.form.get('preferredLight')
    preferredTemperature = request.form.get(
        'preferredTemperature')
    preferredMoisture = request.form.get('preferredMoisture')
    preferredPump = request.form.get('preferredPump')

    # put those value into array
    temparray = [preferredLight, preferredTemperature,
                 preferredMoisture, preferredPump]
    default = [4, 30, 50, 1]

    for i in range(len(temparray)):
        if temparray[i] == "":
            temparray[i] = default[i]
            # convert the value to string
        temparray[i] = str(temparray[i])
        # check how many character is in the string
        while len(temparray[i]) < 3:
            temparray[i] = "0" + temparray[i]

    print("20"+temparray[0]+temparray[1] +
          temparray[2]+temparray[3])

    ser.write(("20"+temparray[0]+temparray[1] +
              temparray[2]+temparray[3]).encode())

    return redirect('/dashboard')


def save_data_to_database():

    while 1:
        mydb.reconnect()
        mycursor = mydb.cursor()
        if ser.in_waiting:  # Or: if serialport.inWaiting():
            line = ser.readline().decode('utf-8').rstrip()
            ser.reset_input_buffer()
            print("Line = " + line)
            x = line.split("|")

            if(len(x) == 1):
                pass
            else:
                try:
                    humidity = int(float(x[0]))
                    temperature = float(x[1])
                    footcandle = float(x[2])
                    moisture = int(x[3])
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

                    mycursor.close()
                    mydb.commit()

                except Error as e:
                    print("Error: " + e)
        mycursor.close()
        time.sleep(10)


if __name__ == '__main__':
    ser = serial.Serial('COM3', 9600, timeout=1)
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
