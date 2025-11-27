const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Determine file path
  let filePath = path.join(__dirname, '..', req.url === '/' ? 'index.html' : req.url);

  // Check if file exists
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    // Serve the file
    const content = fs.readFileSync(filePath);
    const ext = path.extname(filePath);
    
    // Set content type
    let contentType = 'text/html';
    if (ext === '.js') contentType = 'application/javascript';
    else if (ext === '.css') contentType = 'text/css';
    else if (ext === '.png') contentType = 'image/png';
    else if (ext === '.jpg' || ext === '.jpeg') contentType = 'image/jpeg';
    else if (ext === '.gif') contentType = 'image/gif';
    else if (ext === '.svg') contentType = 'image/svg+xml';
    else if (ext === '.json') contentType = 'application/json';
    
    res.setHeader('Content-Type', contentType);
    res.status(200).send(content);
  } else {
    // For routes without extensions, serve index.html (for client-side routing)
    if (!req.url.includes('.')) {
      const indexPath = path.join(__dirname, '..', 'index.html');
      const content = fs.readFileSync(indexPath);
      res.setHeader('Content-Type', 'text/html');
      res.status(200).send(content);
    } else {
      res.status(404).send('Not found');
    }
  }
};
