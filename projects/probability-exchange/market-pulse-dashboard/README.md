# MarketPulse Pro Dashboard

Production-grade real-time prediction markets dashboard built with Vite + React 19 + TypeScript.

## Status

✅ **Production Ready** - Optimized build, deployment configured, fully documented

- Bundle Size: 233.73 KB (gzipped) - Well under 500 KB target
- Build Time: ~16 seconds
- Security: Headers configured, XSS protection enabled
- Performance: Code splitting, optimized caching

## Quick Links

- **[Deployment Guide](DEPLOYMENT.md)** - Complete deployment instructions for Netlify/Vercel
- **[Deployment Summary](DEPLOYMENT_SUMMARY.md)** - Quick start deployment guide
- **[Build Report](BUILD_REPORT.md)** - Detailed bundle analysis
- **[Quick Start](QUICKSTART.md)** - Fast development setup

## Tech Stack

- **Frontend Framework**: React 19 with TypeScript
- **Build Tool**: Vite 7
- **State Management**: TanStack Query (React Query)
- **Styling**: Tailwind CSS 3
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Charts**: Recharts
- **WebSocket**: Native WebSocket API

## Project Structure

```
market-pulse-dashboard/
├── src/
│   ├── components/          # React components
│   │   ├── Header.tsx       # Dashboard header with branding
│   │   ├── StatusBar.tsx    # Connection status indicators
│   │   ├── SearchBar.tsx    # Search and filter controls
│   │   ├── MarketCard.tsx   # Individual market card
│   │   └── MarketGrid.tsx   # Grid layout for markets
│   ├── lib/                 # Utilities and clients
│   │   ├── api-client.ts   # REST API client
│   │   └── websocket.ts    # WebSocket manager
│   ├── types/               # TypeScript type definitions
│   │   └── market.ts       # Market-related types
│   ├── hooks/               # Custom React hooks
│   │   ├── useMarkets.ts   # Market data fetching
│   │   └── useWebSocket.ts # WebSocket connection
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # Application entry point
│   └── index.css           # Global styles
├── public/                  # Static assets
├── index.html              # HTML entry point
├── vite.config.ts          # Vite configuration (optimized)
├── tailwind.config.js      # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
├── netlify.toml            # Netlify deployment config
├── vercel.json             # Vercel deployment config
└── package.json            # Dependencies
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running at http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at http://localhost:3000

### Build for Production

```bash
# Type check and build
npm run build

# Preview production build
npm run preview
```

## Deployment

### Quick Deploy to Netlify

```bash
npm install -g netlify-cli
netlify login
netlify init
netlify deploy --prod
```

### Quick Deploy to Vercel

```bash
npm install -g vercel
vercel login
vercel --prod
```

### Environment Variables

Set `VITE_API_URL` in your deployment platform:

```bash
VITE_API_URL=https://your-backend-api.com
```

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete deployment instructions.

## Features

- Real-time market updates via WebSocket
- Search and filter markets by category
- Responsive grid layout
- Live price change indicators
- Connection status monitoring
- Auto-reconnection on disconnect
- Dark mode optimized UI
- Optimized bundle with code splitting

## API Endpoints

The dashboard connects to the following backend endpoints:

- `GET /api/v1/markets` - Fetch markets list
- `GET /api/v1/markets/{id}` - Get market details
- `GET /api/v1/status` - API health check
- `WS /api/v1/ws/markets` - Real-time market updates

## Development

### Available Scripts

```bash
npm run dev              # Start dev server on :3000
npm run build           # Production build
npm run build:production # Production build with optimizations
npm run build:analyze   # Build with bundle analysis
npm run preview         # Preview production build on :4173
npm run lint            # TypeScript type checking
npm run deploy:netlify  # Build and deploy to Netlify
npm run deploy:vercel   # Deploy to Vercel
```

### Type Checking

```bash
npm run lint
```

### Configuration

- **API Proxy**: Configured in `vite.config.ts` to proxy `/api` requests to `http://localhost:8000`
- **TypeScript**: Strict mode enabled with comprehensive type checking
- **Tailwind**: Custom color scheme and dark mode configuration
- **Build**: Optimized with code splitting, minification, and caching

## Performance

### Bundle Analysis

- **Total Size**: 233.73 KB (gzipped)
- **Code Splitting**: 7 optimized chunks
- **Caching**: 1-year cache for static assets
- **Target Metrics**:
  - First Contentful Paint: < 1.8s
  - Time to Interactive: < 3.8s
  - Lighthouse Score: > 90

### Browser Support

- Chrome 51+
- Firefox 54+
- Safari 10+
- Edge 15+
- Modern mobile browsers

## Security

- XSS protection enabled
- Frame options configured
- Content type sniffing disabled
- Referrer policy set
- Permissions policy configured
- HTTPS enforced (automatic on Netlify/Vercel)

## Documentation

### Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide (Netlify/Vercel)
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Quick start deployment
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Pre/post deployment checklist
- **[BUILD_REPORT.md](BUILD_REPORT.md)** - Bundle analysis and optimization

### Development
- **[QUICKSTART.md](QUICKSTART.md)** - Fast development setup
- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Design system documentation
- **[DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)** - Architecture decisions

## Troubleshooting

### Build Fails
```bash
# Clean and rebuild
rm -rf node_modules dist
npm install
npm run build
```

### Environment Variables Not Working
- Ensure variables start with `VITE_`
- Rebuild after changing variables
- Check deployment platform dashboard

### API Calls Failing
- Check CORS configuration on backend
- Verify `VITE_API_URL` is set correctly
- Check network tab in browser DevTools

See **[DEPLOYMENT.md](DEPLOYMENT.md)** troubleshooting section for more help.

## Next Steps

### Immediate
1. ✅ Production build configured
2. ✅ Deployment ready
3. Deploy to chosen platform
4. Configure custom domain
5. Set up monitoring

### Future Enhancements
1. Implement detailed market view modal
2. Add price history charts
3. Implement advanced filtering options
4. Add user preferences/favorites
5. Implement market comparison view
6. Add export/share functionality

## License

ISC
