// temperature-listener.js

const { spawn } = require('child_process');
const temperatures = [];

const sensor = spawn('python', ['sensor.py']);
sensor.stdout.on('data', function(data) {
	temperatures.push(parseFloat(data));
	console.log(temperatures);
});
