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

sport.on('data', function(data){
  console.log(data.toString());
  io.emit('arduino:data', {
    data:data.toString()
  });
});

let connectedSocket = null;
function onConnection(socket){
    connectedSocket = socket;
}
io.on('connection', onConnection);

server.on("connection", (socket) => {
  console.log(`Cliente conectado`);

//	Command to force a slide change
		io.emit('arduino:data',{data:"6"});

		const { spawn } = require ('child_process');
		const dummyOutput = [];

		const pyCatcher = spawn('python', ['dummy.py']);
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
