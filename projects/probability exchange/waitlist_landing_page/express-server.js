const express = require('express');
const path = require('path');

const app = express();
const port = 3000;

// Serve static files from the current directory
app.use(express.static(__dirname));

// For any request, serve the index.html file
app.use((req, res, next) => {
  console.log(`Request: ${req.method} ${req.url}`);
  // If the request is for a file that exists, let express-static handle it
  // Otherwise, serve index.html
  if (!req.url.includes('.')) {
    res.sendFile(path.join(__dirname, 'index.html'));
  } else {
    next();
  }
});

// Static files handler must come after the above middleware
app.use(express.static(__dirname));

app.listen(port, '0.0.0.0', () => {
  console.log(`\nServer running at http://localhost:${port}/`);
  console.log(`Open your browser at http://localhost:${port}/`);
  console.log(`\nIf localhost doesn't work, try one of these:`);
  
  const os = require('os');
  const networkInterfaces = os.networkInterfaces();
  Object.values(networkInterfaces).forEach(iface => {
    iface.forEach(iface => {
      if (!iface.internal && iface.family === 'IPv4') {
        console.log(`  http://${iface.address}:${port}/`);
      }
    });
  });
  console.log('\nPress Ctrl+C to stop the server');
});