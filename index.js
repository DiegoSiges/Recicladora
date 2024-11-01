const express = require('express');
const app = express();
const SerialPort = require('serialport');

const server = app.listen(3000, function () {
  console.log('Listo el puerto 3000!');
});
const io = require('socket.io')(server);

app.use(express.json());

app.get('/test', function (req, res) {
  res.send('Hola mundo!');
});

app.use(express.static('public'));

const sport = new SerialPort('/dev/ttyACM0', () => { ///dev/ttyACM0
  console.log('Puerto abierto');
});

/* Original sport.on function. Modified below */
sport.on('data', function(data){
  console.log(data.toString());
  io.emit('arduino:data', {
    data:data.toString()
  });
});


/*
sport.on('data', function(data){
  inputData=data.toString();
  
  console.log(inputdata);
  io.emit('arduino:data', {
    data:inputdata
  });

  const { spawn } = require ('child_process');
  const dummyOutput = [];

  const pyCatcher = spawn('python', ['dummy2.py', inputData]);
  pyCatcher.stdout.on('data', function(data) {
    dummyOutput.push(parseFloat(data));
    console.log(dummyOutput);
  });

}); */


let connectedSocket = null;
function onConnection(socket){
    connectedSocket = socket;
}
io.on('connection', onConnection);

server.on("connection", (socket) => {
  console.log(`Cliente conectado`);

//	Command to force a slide change

// data=1: pag QR. =2:pag llenado. =4:incr cuenta botellas. =6: pag insertar 
// contenedor. =0: pag inicio con contador reiniciado
// Data passed to Siges Python script: 0 to reinitiate bottle counter; 4 to increment counter; 
// 1 to send accumulation intention
// The Siges Python script will have to return a value indicating success or failure sending the 
// accumulation request. What to do then? A new page may have to be shown indicating the total #
// of bottles that could not be reported (?) 
		
// Variable arduinoData holds the value reported by Arduino, which is passed to
//index.html and to python
const arduinoData="1" 


io.emit('arduino:data',{data:arduinoData});


    const { spawn } = require ('child_process');
		const dummyOutput = [];

		const pyCatcher = spawn('python', ['pointAccumulationRequest.py', arduinoData]);
		pyCatcher.stdout.on('data', function(data) {
			dummyOutput.push(parseFloat(data));
			console.log(dummyOutput);
		});

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
//io.emit('arduino:data',"2");
//console.log("Enviando 2 a Arduino inicio");
parser.on('data', (data) => {
  console.log(data);
  i = i + 1;
  io.emit('data', { data: data });
  console.log(i);
  });
console.log("Executes?");
//setTimeout (com2Arduino, 7000);
