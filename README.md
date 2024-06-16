# NacaHelper

This application is a helper for NacaBattle to connect AComs to websites if using a website that is not compatible with the Web Serial standard.

## How it works

When opened, the application launches a small flask web server. This web server then can be used to interact with the JavaScript code of NacaBattle. By default this web server runs on localhost at port 5000, but this can be changed in the main.py file for your implementation.

## Building

To build this application, you need to run the following commands:
    
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pyinstaller --onefile --windowed main.py
```

the resulting file can be found under `dist/main` if built under Linux or `dist/main.exe` if built under Windows. Technically this application is compatible with macOS, but I don't have a Mac to test it.

## Running

You can also run the application without building it by running the following command:

```bash
python main.py
```

Important to have done the previous steps to have the dependencies installed.

## Usage

Usage is very simple, when opened, the application will ask for the COM port where your ACom is connected. Select it and then hit "Connect to serial". After that, on NacaBattle choose the NacaHelper option and you will be able to use the website as if you were using the Web Serial standard.

## Modifications

To modify this application to suit your website, look in the main.py file for the following lines:

```python
flask_cors.CORS(
    app, 
    # IF YOU WANT TO IMPLEMENT IT IN YOUR SITE, CHANGE THESE ORIGINS
    origins=["https://battle.nacatech.es", "https://nacatests.mainframe.home"], 
    methods=["GET", "POST"]
)
```

and modify the line that says origin, then put your website. This is due to the CORS policy this server enforces. It is also possible to enforce all websites, but that is not recommended.

## API

There are three endpoints in this web server:

- `/`: This is just a status endpoint, you can use this to see if the application is running or if there is a serial port attached.
- `/write`: This endpoint accepts a GET request with the DigiROM in question sent as a url parameter. This will write the DigiROM to the ACom. Example: `http://localhost:5000/write?d=<DigiROM>`. Returns a JSON object with a status, that can be `ok` or `error`.
- `/read`: This endpoint accepts a GET request and will return the resulting serial communication from the ACom without being altered. This endpoint will lock up until a valid result is found. Same as in ``/write``, returns a JSON object with a status, that can be `ok` or `error`. If the status is `ok`, the result will be in the `data` key.

### Errors
If any errors occur during the communication, the status key will be `error` and the error message will be in the `error` key.

## Example library

I have also added a small example library that can be used to interact with the NacaHelper. This library is written in JavaScript. To use it you can use the following example code:

```javascript
let nh = new NacaHelper("http://localhost:5000");
nh.writeData("V2-FC03").then(() => {
    console.log("Success reading data");
    nh.readData().then((data) => {
        console.log("Data read:")
        console.log(data);
    });
}).catch((err) => {
    console.error(err);
});
```

Remember, if you are going to use NacaHelper in your project, you need to change the origin in the main.py file to your website, otherwise CORS will block the request.
