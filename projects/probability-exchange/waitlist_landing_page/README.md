# Waitlist Landing Page

## Running Locally

The server is currently running in the background at:
- **http://localhost:3000/**

### To restart the server:
```bash
cd /home/billy/projects/probability exchange/waitlist_landing_page
nohup node express-server.js > server.log 2>&1 &
```

### To stop the server:
```bash
pkill -f "node express-server.js"
```

### View server logs:
```bash
tail -f server.log
```

## Troubleshooting 404 Errors

If you see a 404 error in your browser:

1. **Clear browser cache** (Ctrl+Shift+Del)
2. **Do a hard refresh** (Ctrl+F5)
3. **Try an incognito/private window**
4. **Verify server is running:**
   ```bash
   ps aux | grep "node express-server"
   curl http://localhost:3000/
   ```

## Deployment with Netlify (Recommended)

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Waitlist landing page"
   ```

2. **Push to GitHub**:
   - Create a new repository on github.com
   - Push your code to GitHub

3. **Deploy on Netlify**:
   - Go to netlify.com and sign up
   - Click "New site from Git"
   - Connect your GitHub repository
   - Netlify will automatically deploy your site
   - Your site will be live at a URL like `https://your-site-name.netlify.app`

**Note**: The netlify.toml file in this repository automatically configures Netlify to serve your static HTML site correctly.
