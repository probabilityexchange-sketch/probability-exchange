# Market Pulse Dashboard - Deployment Guide

Complete deployment guide for the Market Pulse Dashboard on Netlify and Vercel platforms.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Netlify Deployment](#netlify-deployment)
- [Vercel Deployment](#vercel-deployment)
- [Backend API Configuration](#backend-api-configuration)
- [Production Build Testing](#production-build-testing)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

## Prerequisites

- Node.js 18.x or higher
- npm 9.x or higher
- Git repository connected to GitHub/GitLab/Bitbucket
- Netlify or Vercel account

## Environment Configuration

### Environment Variables

The dashboard requires minimal configuration. Create a `.env.production` file if you need custom settings:

```bash
# API Backend URL (optional - defaults to /api proxy)
VITE_API_URL=https://your-backend-api.com

# Analytics (optional)
VITE_GA_ID=G-XXXXXXXXXX

# Feature Flags (optional)
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG=false
```

### Required Environment Variables by Platform

**Netlify:**
- `NODE_VERSION`: 18 (set in netlify.toml)
- `VITE_API_URL`: Your backend API URL (set in Netlify dashboard)

**Vercel:**
- `NODE_VERSION`: 18 (set in vercel.json)
- `VITE_API_URL`: Your backend API URL (set in Vercel dashboard)

## Netlify Deployment

### Option 1: Deploy via Netlify UI (Recommended for First-Time Setup)

1. **Connect Repository**
   - Log in to [Netlify](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Connect your Git provider (GitHub, GitLab, or Bitbucket)
   - Select the `market-pulse-dashboard` repository

2. **Configure Build Settings**
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Node version: 18 (auto-detected from netlify.toml)

3. **Set Environment Variables**
   - Go to Site settings → Build & deploy → Environment
   - Add environment variables:
     ```
     VITE_API_URL=https://your-backend-api.com
     ```

4. **Deploy**
   - Click "Deploy site"
   - Netlify will automatically build and deploy your site
   - Your site will be available at: `https://[site-name].netlify.app`

### Option 2: Deploy via Netlify CLI

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify**
   ```bash
   netlify login
   ```

3. **Initialize Site (First Time Only)**
   ```bash
   cd /home/billy/projects/probability\ exchange/market-pulse-dashboard
   netlify init
   ```
   Follow the prompts to:
   - Create a new site or link to existing
   - Configure build settings
   - Set deployment branch

4. **Set Environment Variables**
   ```bash
   netlify env:set VITE_API_URL "https://your-backend-api.com"
   ```

5. **Deploy**
   ```bash
   npm run deploy:netlify
   ```
   Or manually:
   ```bash
   npm run build
   netlify deploy --prod
   ```

### Option 3: Continuous Deployment (Recommended for Production)

1. **Enable Automatic Deploys**
   - In Netlify dashboard, go to Site settings → Build & deploy
   - Under "Continuous Deployment", connect your Git repository
   - Set production branch (usually `main` or `master`)

2. **Configure Deploy Contexts**
   - Production deploys: `main` branch
   - Deploy previews: Pull requests
   - Branch deploys: Other branches (optional)

3. **Push to Deploy**
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```
   Netlify will automatically build and deploy on every push

## Vercel Deployment

### Option 1: Deploy via Vercel UI (Recommended for First-Time Setup)

1. **Connect Repository**
   - Log in to [Vercel](https://vercel.com)
   - Click "Add New..." → "Project"
   - Import your Git repository
   - Select the `market-pulse-dashboard` repository

2. **Configure Project**
   - Framework Preset: Vite (auto-detected)
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `dist` (auto-detected)
   - Install Command: `npm install` (auto-detected)

3. **Set Environment Variables**
   - Add environment variables:
     ```
     VITE_API_URL=https://your-backend-api.com
     ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your site
   - Your site will be available at: `https://[project-name].vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd /home/billy/projects/probability\ exchange/market-pulse-dashboard
   npm run deploy:vercel
   ```
   Or manually:
   ```bash
   vercel --prod
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add VITE_API_URL
   ```
   When prompted, enter: `https://your-backend-api.com`

### Option 3: Continuous Deployment (Recommended for Production)

1. **Automatic Setup**
   - After initial deployment, Vercel automatically sets up continuous deployment
   - Every push to `main` branch triggers production deployment
   - Pull requests get preview deployments

2. **Push to Deploy**
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

## Backend API Configuration

The dashboard requires a backend API for real-time market data. Configure the API endpoint:

### Development (Local)
The dashboard uses a proxy configuration in `vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

### Production

**Option 1: Environment Variable (Recommended)**
Set `VITE_API_URL` environment variable in your deployment platform:
```bash
VITE_API_URL=https://api.marketpulse.com
```

**Option 2: Netlify Redirects**
Uncomment the API redirect section in `netlify.toml`:
```toml
[[redirects]]
  from = "/api/*"
  to = "https://your-backend-api.com/api/:splat"
  status = 200
  force = true
```

**Option 3: Vercel Rewrites**
Add to `vercel.json`:
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-api.com/api/:path*"
    }
  ]
}
```

### CORS Configuration
Ensure your backend API allows requests from your deployment domain:
```
Access-Control-Allow-Origin: https://your-dashboard.netlify.app
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## Production Build Testing

Before deploying, test the production build locally:

1. **Build the Application**
   ```bash
   npm run build:production
   ```

2. **Analyze Bundle Size**
   ```bash
   npm run build:analyze
   ```
   This generates a visual report of your bundle composition

3. **Preview Production Build**
   ```bash
   npm run preview
   ```
   Access at: http://localhost:4173

4. **Test Production Build**
   - Verify all features work correctly
   - Check network tab for API calls
   - Test responsive design
   - Verify performance (Lighthouse score)
   - Check console for errors

5. **Performance Benchmarks**
   Target metrics:
   - First Contentful Paint (FCP): < 1.8s
   - Largest Contentful Paint (LCP): < 2.5s
   - Time to Interactive (TTI): < 3.8s
   - Cumulative Layout Shift (CLS): < 0.1
   - Total Bundle Size: < 500KB (gzipped)

## Troubleshooting

### Build Failures

**Issue: TypeScript errors during build**
```bash
# Run type check to identify issues
npm run type-check

# Fix errors and rebuild
npm run build
```

**Issue: Out of memory during build**
```bash
# Increase Node.js memory limit
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

**Issue: Missing dependencies**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Deployment Issues

**Issue: 404 on page refresh**
- Ensure SPA redirect is configured:
  - Netlify: Check `netlify.toml` redirects
  - Vercel: Check `vercel.json` rewrites

**Issue: API calls failing**
- Check `VITE_API_URL` environment variable
- Verify CORS configuration on backend
- Check network tab for actual URLs being called

**Issue: Static assets not loading**
- Verify `dist` directory is being deployed
- Check asset paths in browser console
- Ensure base URL is correct in `vite.config.ts`

**Issue: Environment variables not working**
- Ensure variables are prefixed with `VITE_`
- Rebuild after changing environment variables
- Verify variables are set in deployment platform

### Performance Issues

**Issue: Large bundle size**
```bash
# Analyze bundle
npm run build:analyze

# Check for large dependencies
npm ls --depth=0

# Consider code splitting for large components
```

**Issue: Slow initial load**
- Enable lazy loading for routes
- Optimize images and assets
- Check network waterfall in DevTools
- Enable compression on hosting platform

### Runtime Errors

**Issue: "Cannot read property" errors**
- Check browser console for stack trace
- Enable source maps: Set `sourcemap: true` in `vite.config.ts`
- Deploy and test again

**Issue: API data not displaying**
- Check network tab for API responses
- Verify API endpoint is accessible
- Check CORS headers
- Verify data format matches expected schema

## Performance Optimization

### Pre-Deployment Checklist

- [ ] Run production build locally
- [ ] Test all critical user paths
- [ ] Check Lighthouse score (target: 90+)
- [ ] Verify bundle size < 500KB gzipped
- [ ] Test on mobile devices
- [ ] Verify API integration works
- [ ] Check error tracking is configured
- [ ] Verify analytics are working
- [ ] Test SEO meta tags
- [ ] Verify security headers

### Post-Deployment

1. **Monitor Performance**
   - Set up Vercel/Netlify Analytics
   - Configure error tracking (Sentry, LogRocket, etc.)
   - Monitor Core Web Vitals

2. **Set Up Alerts**
   - Deploy notifications (Slack, email)
   - Error rate monitoring
   - Performance degradation alerts

3. **Regular Maintenance**
   - Update dependencies monthly
   - Review bundle size regularly
   - Monitor user feedback
   - Update documentation

## Custom Domain Setup

### Netlify Custom Domain

1. Go to Site settings → Domain management
2. Click "Add custom domain"
3. Enter your domain name
4. Follow DNS configuration instructions
5. Enable HTTPS (automatic via Let's Encrypt)

### Vercel Custom Domain

1. Go to Project settings → Domains
2. Enter your domain name
3. Follow DNS configuration instructions
4. Vercel automatically provisions SSL certificate

## Rollback Procedure

### Netlify Rollback
1. Go to Deploys tab
2. Find the previous working deploy
3. Click "Publish deploy"

### Vercel Rollback
1. Go to Deployments tab
2. Find the previous working deployment
3. Click "..." → "Promote to Production"

## Support and Resources

- **Netlify Documentation**: https://docs.netlify.com
- **Vercel Documentation**: https://vercel.com/docs
- **Vite Documentation**: https://vitejs.dev
- **React Documentation**: https://react.dev

## Deployment Status

After deployment, your dashboard will be available at:
- **Netlify**: `https://[site-name].netlify.app`
- **Vercel**: `https://[project-name].vercel.app`
- **Custom Domain**: `https://your-domain.com`

For questions or issues, refer to the platform-specific documentation or contact support.
