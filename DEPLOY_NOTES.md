# Deployment Notes for Probability Exchange

## Current Setup (December 10, 2025)

### What's Deployed
The site now deploys the **Market Pulse Dashboard** - a complete prediction markets dashboard built with Vite + React.

**Live URL**: https://probability-exchange.vercel.app

### Repository Structure

```
probability-exchange/
├── public/                          # Deployed static site (built dashboard)
│   ├── index.html                   # Main entry point
│   ├── assets/                      # JS, CSS bundles
│   └── favicon-*.svg                # Branding icons
├── vercel.json                      # Vercel configuration
├── packages/market-pulse-dashboard/ # Original build location
│   └── dist/                        # Source of deployed files
└── projects/probability exchange/
    ├── PROBEX_STYLE_GUIDE.md       # Complete branding/design specs
    └── market-pulse-dashboard/
        └── src/lib/                 # Utility functions (API client, websocket, utils)
```

### Branding & Design

**Located at**: `projects/probability exchange/PROBEX_STYLE_GUIDE.md`

#### Key Brand Elements
- **Logo**: P(E) symbol with "probex.markets" wordmark
- **Primary Colors**:
  - Dark Background: `#0a0f16`
  - Surface Background: `#141b26`
  - Brand Blue: `#00B3FF`
  - Neon Cyan: `#2EFFFA`
  - Terminal Gray: `#7a8a99`
  - UI Red: `#FF3366`

#### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 400, 500, 600, 700
- **Style**: Terminal-inspired, monospace feel

#### Component Style
- **Cards**: Dark surface (#141b26) with cyan border glow
- **Buttons**: Primary uses #00B3FF
- **Inputs**: Dark with cyan focus states
- **Grid Pattern**: Subtle 60px terminal grid overlay

### Dashboard Components

The deployed dashboard includes:
1. **Hero Section** - Main headline and CTA
2. **Market Cards** - Prediction market displays with probability charts
3. **Ticker** - Scrolling market updates (if implemented)
4. **What to Watch** - Sidebar with featured markets (if implemented)
5. **News Feed** - AI-powered analysis (if implemented)

**Note**: The current deployment is the built version. Some features may be stubbed or using mock data.

### Key Files & Paths

#### Dashboard Components (if source exists)
- Look in: `projects/probability exchange/market-pulse-dashboard/src/`
- Currently only found: `src/lib/` with utility functions

#### Branding & Assets
- Style Guide: `projects/probability exchange/PROBEX_STYLE_GUIDE.md`
- Favicons: `public/favicon-*.svg` (16px to 256px)

#### Configuration
- Vercel Config: `vercel.json` (at root)
- API Client: `projects/probability exchange/market-pulse-dashboard/src/lib/api-client.ts`
- WebSocket: `projects/probability exchange/market-pulse-dashboard/src/lib/websocket.ts`

### Editing the Site

#### To Update Branding
1. Edit `PROBEX_STYLE_GUIDE.md` for reference
2. Source React components are not currently in repo (only built version exists)
3. To make changes, you'll need to:
   - Rebuild the dashboard from source (if available elsewhere)
   - Or manually edit the built files in `public/` (not recommended)

#### To Update Market Data
- Mock data configuration may be in the bundled JS
- For real data: Configure API endpoints in environment variables
- API client at: `projects/probability exchange/market-pulse-dashboard/src/lib/api-client.ts`

#### To Update AI Analysis Copy
- Built into the bundled React app
- Would require rebuilding from source

### What Was Disabled/Stubbed

Based on the build:
- **Real-time Data**: May be using mock/static data
- **Live WebSocket**: WebSocket client exists but may not be connected
- **External APIs**: No API keys configured in deployment

### Deployment Process

#### Current Workflow
1. Changes to `public/` folder
2. Commit and push to GitHub
3. Vercel auto-deploys from the `public/` directory

#### Manual Deploy
```bash
# From repo root
vercel --prod
```

### Local Development

Since we only have the built version:

```bash
# Serve the public folder locally
npx serve public
# Or
python3 -m http.server 8000 --directory public
```

**Note**: You cannot run `npm run dev` for hot-reloading since the source React app is not in the repo.

### Missing/TODO

1. **Source Code**: The React source for the dashboard is not committed
   - Only the built version (`dist/`) exists
   - Original source may be elsewhere or lost

2. **Real API Integration**:
   - Polymarket API
   - Kalshi API
   - DFlow API (mentioned in commits)
   - AI/LLM for market analysis

3. **Environment Variables**: Need to configure in Vercel:
   - API keys for market data providers
   - AI/LLM API keys
   - WebSocket endpoints

4. **Testing**: No test suite found in repo

### Restoring Full Development

To enable full development (editing React components):
1. Locate the original dashboard source code
2. Set up a proper Vite project structure
3. Configure build pipeline to output to `public/`
4. Set up development scripts in `package.json`

### Support & Troubleshooting

**If deployment fails:**
1. Check Vercel build logs
2. Verify `public/index.html` exists
3. Ensure `vercel.json` is at root

**If dashboard doesn't load:**
1. Check browser console for errors
2. Verify asset paths in `index.html`
3. Check Vercel headers/rewrites configuration

**If you need to rebuild:**
1. Find the original Vite project source
2. Run `npm install && npm run build`
3. Copy `dist/` contents to `public/`

### Long-term Fixes

1. **Restore Source Control**: Commit the full React source
2. **Automated Builds**: Set up Vercel to build from source
3. **Environment Configuration**: Proper env var management
4. **Documentation**: Component-level docs for developers
5. **Testing**: Add test suite for components

---

## Quick Commands

```bash
# Check what's deployed
ls -la public/

# View Vercel config
cat vercel.json

# View style guide
cat "projects/probability exchange/PROBEX_STYLE_GUIDE.md"

# Deploy manually
vercel --prod
```

---

**Last Updated**: December 10, 2025
**Deployment**: Vercel (probability-exchange.vercel.app)
**Status**: ✅ Dashboard deployed, using built version from `packages/market-pulse-dashboard/dist/`
