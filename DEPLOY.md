# Deployment Guide

## 🚀 Push to GitHub

Your repository is ready! Follow these steps to push to GitHub:

### Option 1: Create a New Repository on GitHub

1. Go to [github.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Name your repository (e.g., `AntiCheat` or `anticheat-api`)
4. **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

### Option 2: Use GitHub CLI (if installed)

```bash
gh repo create AntiCheat --public --source=. --remote=origin --push
```

### Option 3: Manual Push

After creating the repository on GitHub, run these commands:

```bash
# Add your GitHub repository as remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/cpatt/AntiCheat.git
git branch -M main
git push -u origin main
```

## 📦 Deploy to Vercel

Once your code is on GitHub:

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect the Python configuration
5. Click **"Deploy"**

Your app will be live at: `https://your-project-name.vercel.app`

## ⚠️ Important Notes

### File Storage on Vercel

- JSON files (config, banned accounts, etc.) are stored in `/tmp` which is **temporary**
- Data will **NOT persist** between deployments or function invocations
- For production, consider:
  - **Vercel KV** (Redis) - `vercel kv`
  - **Supabase** - Free PostgreSQL database
  - **MongoDB Atlas** - Free MongoDB database
  - **Environment Variables** - For configuration

### Update API URLs

After deploying to Vercel, update your CloudScript API URLs to:
```
https://your-project-name.vercel.app
```

## 🔧 Environment Variables (Optional)

You can set these in Vercel Dashboard → Settings → Environment Variables:

- `BAN_WEBHOOK_URL` - Discord webhook for bans
- `ALLOWED_WEBHOOK_URL` - Discord webhook for allowed devices
- `DEBUG_MODE` - Enable/disable debug mode

