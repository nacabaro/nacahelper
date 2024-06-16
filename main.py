import flask
import flask_cors
import threading
import time
from tkinter import *
from tkinter import ttk
import os
import re
import serial
import sys
import glob

serial_line = ""
ser = None
ser_port = ""

# I found this in stackoverflow, it lists all the available serial ports
# don't ask me how it does it, it works at least
def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
        
    return result

# Initialize the serial port with the selected port
def init_serial():
    global ser
    if ser is not None: ser.close()
    ser = serial.Serial(ser_port, 9600)

# Write the data to the serial port
# also reset the input and output buffer
def write_serial_data():
    global ser
    ser.reset_input_buffer()
    ser.reset_output_buffer() 
    ser.write(bytearray(serial_line + "\r\n", 'utf-8'))

# Read the data from the serial port
# Will get stuck until a digirom is found in the communication
def read_serial_data():
    global ser
    global serial_line
    regex_pattern = re.compile(r'r:([A-F0-9]*)')
    while True:
        serial_line = ser.readline()
        match_data = regex_pattern.findall(serial_line.decode('utf-8'))
        if match_data:
            break       

# Web server thread
def thread_webapp():
    ## Create the web server and enable CORS
    app = flask.Flask(__name__)
    flask_cors.CORS(
        app, 
        # IF YOU WANT TO IMPLEMENT IT IN YOUR SITE, CHANGE THESE ORIGINS
        origins=["https://battle.nacatech.es", "https://nacatests.mainframe.home"], 
        methods=["GET", "POST"]
    )
    
    # Small info page to know if it is workking
    @app.route('/')
    def index():
        return 'NacaHelper running...<br>Serial port: ' + ("none" if ser_port == "" else ser_port) + '\n'
    
    # Read the serial port. Will get stuck until a digirom is found in the communication
    @app.route('/read')
    def data():
        response = {}
        # status can be ok or error, if error check the "error" param, otherwise check the "data" param
        # to get the digirom in the serial form as output by the acom
        response["status"] = 'error'
        
        # Useful to check if the serial port is running or not
        global ser
        if ser is None:
            response["error"] = 'Serial port not connected'
            return flask.jsonify(response), 200
        
        # Spin up a thread to handle the serial read, then lock this thread until the read is done
        # might generate problems if the acom is not sending the digirom
        pyserial_thread = threading.Thread(target=read_serial_data)
        pyserial_thread.start()
        pyserial_thread.join()
        
        # Return the data read from the serial port
        global serial_line
        response["status"] = 'ok'
        response["data"] = serial_line.decode('utf-8')
        
        return flask.jsonify(response), 200

    # Write to the serial port
    @app.route('/write')
    def write():
        response = {}
        # Same as read, status can be ok or error, if error check the "error" param
        # Useful to check if the serial port is running or not
        response["status"] = 'error'
        
        global ser
        if ser is None:
            response["error"] = 'Serial port not connected'
            return flask.jsonify(response), 200
        
        # Check if data was sent to the acom
        request_data = flask.request.args.get('d')
        if request_data is None:
            response["error"] = 'No data provided'
            return flask.jsonify(response), 200
        
        # Spin up a thread to handle the serial write, then lock this thread until the write is done
        global serial_line
        serial_line = request_data
        pyserial_thread = threading.Thread(target=write_serial_data)
        pyserial_thread.start()
        pyserial_thread.join()
        
        response["status"] = 'ok'
        return flask.jsonify(response), 200
    
    # Run the web server
    app.run(debug=False, host='127.0.0.1', port=5000)

def ui_thread():
    # Close the serial port and then kill everything
    def cleanup():
        global ser
        if ser is not None: ser.close()
        os._exit(0)

    # Set the serial port to the selected one
    # then init the serial device selected
    def set_serial_port():
        global ser
        global ser_port
        ser_port = clicked.get()
        init_serial()

    # Create the app's main window
    root = Tk()
    root.title("NacaHelper")
    
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    
    # Get the available serial ports
    ports = serial_ports()

    # Create serial port dropdown menu
    clicked = StringVar()
    clicked.set(ports[0])
    ttk.OptionMenu(frm, clicked, *ports).grid(column=0, row=0)
    
    # Connect serial and then quit buttons
    ttk.Button(frm, text="Connect to serial", command=set_serial_port).grid(column=1, row=0)
    ttk.Button(frm, text="Quit", command=cleanup).grid(column=2, row=0)
    
    # Start the UI
    root.mainloop()

if __name__ == '__main__':
    # Start the web server thread
    t_webApp = threading.Thread(target=thread_webapp)
    t_webApp.daemon = True  # Important it is a daemon thread, otherwise the app won't die
    t_webApp.start()
    
    # Start the UI thread
    t_UI = threading.Thread(target=ui_thread)
    t_UI.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        os._exit(0)     # Forcefully kill the app with control + c
