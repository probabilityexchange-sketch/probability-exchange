# Quick Start Guide

## Prerequisites

1. **Backend API Running**: Ensure the FastAPI backend is running at `http://localhost:8000`
2. **Node.js**: Version 18 or higher

## Start Development Server

```bash
# Navigate to project directory
cd "/home/billy/projects/probability exchange/market-pulse-dashboard"

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

The dashboard will be available at: **http://localhost:3000**

## Verify Setup

1. **Type Checking**: Run `npm run lint` to verify TypeScript compilation
2. **Build Test**: Run `npm run build` to test production build
3. **Preview Build**: Run `npm run preview` to test production bundle

## Backend Requirements

Ensure your FastAPI backend has these endpoints:

- `GET /api/v1/markets` - List markets
- `GET /api/v1/markets/{id}` - Market details
- `GET /api/v1/status` - API health check
- `WS /api/v1/ws/markets` - Real-time updates

## Project Structure Overview

```
src/
├── components/       # React UI components
├── hooks/           # Custom React hooks
├── lib/             # API client & WebSocket manager
├── types/           # TypeScript type definitions
├── App.tsx          # Main application
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## Development Workflow

1. **Make changes** to components in `src/components/`
2. **Hot reload** will automatically refresh the browser
3. **Type check** with `npm run lint` before committing
4. **Build** with `npm run build` to verify production readiness

## Common Tasks

### Add a new component
```bash
# Create component file
touch src/components/NewComponent.tsx
```

### Add a new hook
```bash
# Create hook file
touch src/hooks/useNewHook.ts
```

### Update types
```bash
# Edit types file
nano src/types/market.ts
```

## Troubleshooting

### Port already in use
If port 3000 is in use, Vite will automatically use the next available port.

### API connection errors
Ensure the backend is running at `http://localhost:8000` and check CORS settings.

### TypeScript errors
Run `npm run lint` to see detailed error messages and fix them.

### WebSocket not connecting
Verify the WebSocket endpoint at `ws://localhost:8000/api/v1/ws/markets` is accessible.

## Next Steps

See [README.md](README.md) for full documentation and feature roadmap.
