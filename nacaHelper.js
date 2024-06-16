class NacaHelper {
    constructor(nh_url) {
        this.nh_url = nh_url;
    }

    writeData(rom) {
        return new Promise((resolve, reject) => {
            fetch(`${this.nh_url}/write?d=${rom}`).then(response => response.json().then(data => {
                if (data["status"] === "ok") {
                    resolve();
                } else {
                    reject(data["error"]);
                }
            }))
        });
    }

    readData(processing = true) {
        return new Promise((resolve, reject) => {
            fetch(`${this.nh_url}/read`).then(response => response.json().then(data => {
                if (data["status"] === "ok") {
                    if (processing) {
                        let rom = processSerialLine(data["data"]);
                        resolve(rom.join("-"));
                    } else {
                        resolve(data["data"]);
                    }
                } else {
                    reject(data["error"]);
                }
            }))
        })
    }
}


function checkIfNacaHelperIsRunning() {
    return new Promise((resolve, reject) => {
        fetch("http://localhost:5000/").then(response => {
            if (response.ok) {
                resolve();
            } 
            throw new Error("NacaHelper is not running");
        }).catch(error => {
            reject();
        })
    });
}
