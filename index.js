const express = require('express');
const app = express();
const SerialPort = require('serialport');

let connAttemptFailTime; // Variable to register when a connection attempt failed
let connAttemptFailFlag = 0; // Flag to indicate whether a connection failure happened


const server = app.listen(3000, function () {
  console.log('Listo el puerto 3000!');
});
const io = require('socket.io')(server);

app.use(express.json());

app.get('/test', function (req, res) {
  res.send('Hola mundo!');
});

app.use(express.static('public'));

//const sport = new SerialPort('/dev/ttyACM0', () => { ///dev/ttyACM0
  const sport = new SerialPort('/dev/ttyUSB0', () => { ///dev/ttyACM0
  console.log('Puerto abierto');
});

/* Original sport.on function. Modified below  
sport.on('data', function(data){
  console.log(data.toString());
  io.emit('arduino:data', {
    data:data.toString()
  });
}); */


/* The routine for sport.on below is handles the input from Arduino, deriving the value to index.html 
and to siges_ArduinoHandler.py. 

Arduino can send the following values: 1: pag QR. 2: pag llenado. 4:incr cuenta botellas. 6: pag insertar 
contenedor. 0: pag inicio con contador reiniciado. The siges_ArduinoHandler acts only on 0, 1 and 4: 0 to 
reinitiate bottle counter; 4 to increment counter; 1 to send accumulation intention.
The Siges Python script returns a value indicating whether the accumuation request failed or succeded (success
is a value in the 200s).In case the accumulation request fails, instead of the QR page the system currently
shows the bottle counter page with an error message on top. Then the system holds this state for 3 minutes. 

This is a temporary solution. The final solutionis to show a new slide with an image indicating the bottles 
total and a message to contact personnel on site to do the transaction manually. 
		
Variable arduinoData holds the value reported by Arduino, which is passed to python
*/

sport.on('data', function(data){
  
  arduinoData=data.toString();
  
  console.log("ArduinoData: ");
  console.log(arduinoData);

// Spawing the python script to send the accumulation intention request
// if Arduino data is applicable. First, must check if 3 minutes elapsed
// since a connection attempt failure. 

  console.log("conn times ");
  console.log(connAttemptFailTime);
  console.log(`Curr time ${Date.now()}`);

  if (connAttemptFailFlag==0) {

    if (arduinoData=="0" || arduinoData=="1" || arduinoData=="4"){
      const { spawn } = require ('child_process');
      const pyOutput = [];

      const pyCatcher = spawn('python', ['siges_ArduinoInputHandler.py', arduinoData]);
      pyCatcher.stdout.on('data', function(data) {
        pyOutput.push(parseFloat(data));
        console.log(pyOutput);
        if (pyOutput<"200" || pyOutput>"299"){
          console.log("Bad code");
        
          connAttemptFailFlag = 1;
          connAttemptFailTime = Date.now();

          // console.log(connAttemptFailTime);
          io.emit('arduino:data', {data:"9"});  // Sending error code to index.html
        }
        else {
        io.emit('arduino:data',{data:arduinoData}); // Sending data to index.html
        }
      });
    }
    else {
      io.emit('arduino:data',{data:arduinoData}); // Sending data to index.html
    }
  }
  else if (Date.now() - connAttemptFailTime > 180000){
    connAttemptFailFlag = 0; // resets the flag if more than 3 minutes elapsed
  }
});


let connectedSocket = null;
function onConnection(socket){
    connectedSocket = socket;
}
io.on('connection', onConnection);

server.on("connection", (socket) => {
  console.log(`Cliente conectado`);
});

const parsers = SerialPort.parsers;
const parser = new parsers.Readline({
  delimiter: '\n'
});


function com2Arduino(){
	io.emit('arduino:data', {data:"0"});
	console.log("2 to Arduino from within function");
}


   	
var i = 0 ;
sport.pipe(parser);
parser.on('data', (data) => {
  console.log(data);
  i = i + 1;
  io.emit('data', { data: data });
  console.log(i);
  });
