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

## 📦 Deploy to Netlify

Once your code is on GitHub:

1. Go to [netlify.com](https://netlify.com) and sign in with GitHub
2. Click **"Add new site"** → **"Import an existing project"**
3. Select your GitHub repository: `noob123ii/Anti-Cheat`
4. Netlify will auto-detect the configuration from `netlify.toml`
5. Click **"Deploy site"**

Your app will be live at: `https://your-project-name.netlify.app` or a custom domain

## ⚠️ Important Notes

### File Storage on Netlify

- JSON files (config, banned accounts, etc.) are stored in `/tmp` which is **temporary**
- Data will **NOT persist** between deployments or function invocations
- For production, consider:
  - **Supabase** - Free PostgreSQL database
  - **MongoDB Atlas** - Free MongoDB database
  - **Netlify Functions** with external storage
  - **Environment Variables** - For configuration (set in Netlify Dashboard)

### Update API URLs

After deploying to Netlify, update your CloudScript API URLs to:
```
https://your-project-name.netlify.app
```

## 🔧 Environment Variables (Optional)

You can set these in Netlify Dashboard → Site settings → Environment variables:

- `BAN_WEBHOOK_URL` - Discord webhook for bans
- `ALLOWED_WEBHOOK_URL` - Discord webhook for allowed devices
- `DEBUG_MODE` - Enable/disable debug mode

Click "Add variable" for each one, then redeploy your site.

