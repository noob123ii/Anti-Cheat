# Netlify Build Settings Configuration

## Exact Settings to Use

Fill out your Netlify build settings page with these **exact values**:

### ✅ Runtime
- **Set to:** `Not set` (leave empty/deselect)
- Netlify will auto-detect Python from your files

### ✅ Base directory
- **Set to:** `/`
- This is the root of your repository

### ✅ Package directory
- **Set to:** `Not set` (leave empty)
- Only needed for monorepos

### ✅ Build command
- **Set to:** `Not set` (leave empty)
- No build step needed for serverless functions

### ✅ Publish directory
- **Set to:** `Not set` (leave empty)
- Not needed for serverless-only deployments

### ✅ Functions directory
- **Set to:** `netlify/functions`
- **This is the most important one!** This tells Netlify where your Python function is located

### ✅ Deploy log visibility
- **Set to:** `Logs are public`
- Or choose "Private" if you prefer

### ✅ Build status
- **Set to:** `Active`
- This enables automatic deployments on Git push

## Summary

The **only field you need to fill** is:
- **Functions directory:** `netlify/functions`

All other fields should be left empty/not set.

## After Saving

1. Click **"Save"** button
2. Netlify will automatically trigger a new deploy
3. Check the deploy logs - you should now see the function being detected and bundled
4. Your site will be live at your Netlify URL

## Important

Make sure your function file is at: `netlify/functions/server.py`
This file should contain the `handler` function for Netlify to detect it.

