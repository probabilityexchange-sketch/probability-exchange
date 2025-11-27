const http = require('http');
const fs = require('fs');
const path = require('path');

const port = 3000;
const directory = __dirname; // Current directory (waitlist_landing_page)

const server = http.createServer((req, res) => {
  console.log(`Request: ${req.method} ${req.url}`);
  let filePath = path.join(directory, req.url === '/' ? 'index.html' : req.url);

  // Handle /public directory for assets
  if (req.url.startsWith('/public/')) {
    filePath = path.join(directory, req.url);
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('404 Not Found');
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('500 Internal Server Error');
      }
    } else {
      let contentType = 'text/html';
      if (filePath.endsWith('.js')) {
        contentType = 'application/javascript';
      } else if (filePath.endsWith('.css')) {
        contentType = 'text/css';
      } else if (filePath.endsWith('.png')) {
        contentType = 'image/png';
      } else if (filePath.endsWith('.jpg') || filePath.endsWith('.jpeg')) {
        contentType = 'image/jpeg';
      }
      // Add more content types as needed

      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    }
  });
});

server.listen(port, '0.0.0.0', () => {
  const os = require('os');
  const networkInterfaces = os.networkInterfaces();
  const ips = Object.values(networkInterfaces)
    .flat()
    .filter(iface => !iface.internal && iface.family === 'IPv4')
    .map(iface => iface.address);
  
  console.log(`Server running at:`);
  console.log(`  http://localhost:${port}/`);
  ips.forEach(ip => console.log(`  http://${ip}:${port}/`));
  console.log(`Directory: ${directory}`);
});
