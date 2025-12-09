# Git Commands for Consensus Dashboard

Here are the exact Git commands to commit and push your consensus dashboard to GitHub:

## Step 1: Navigate to your project directory
```bash
cd "waitlist_landing_page"
```

## Step 2: Check current status
```bash
git status
```

## Step 3: Add the consensus dashboard files
```bash
git add ../consensus_dashboard/
```

## Step 4: Commit the consensus dashboard
```bash
git commit -m "Add consensus dashboard MVP

Features:
- Real-time cross-platform consensus analysis
- Signal detection with confidence scoring
- Professional UI with Probex branding
- Multiple analysis modes (Real-time, Historical, Signals, Risk)
- Advanced filtering and export capabilities
- Docker support and comprehensive documentation

Files added:
- consensus_dashboard/app.py (main dashboard)
- consensus_dashboard/config.py (configuration)
- consensus_dashboard/requirements.txt (dependencies)
- consensus_dashboard/README.md (documentation)
- consensus_dashboard/run_dashboard.py (launcher)
- consensus_dashboard/Dockerfile (container support)

This dashboard leverages existing prediction markets code and provides
unique cross-platform intelligence for Polymarket, Kalshi, and Manifold."
```

## Step 5: Push to GitHub
```bash
git push origin main
```

## Alternative: Create Separate Repository

If you prefer to keep the consensus dashboard separate:

```bash
cd ../consensus_dashboard
git init
git add .
git commit -m "Initial commit: Probex Consensus Dashboard MVP"
git remote add origin https://github.com/YOUR_USERNAME/probex-consensus-dashboard.git
git push -u origin main
```

## After Pushing

Once pushed to GitHub, you can:
1. Deploy to Streamlit Cloud
2. Set up CI/CD for automated testing
3. Configure environment variables for API keys
4. Share the repository with collaborators

The consensus dashboard is now ready for deployment and testing!