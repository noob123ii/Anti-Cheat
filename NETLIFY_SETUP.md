# Netlify Build Settings Configuration

## Build Settings Page Configuration

Fill out the Netlify build settings page as follows:

### Runtime
- **Select:** Leave as default (or select Python if available)
- Netlify will automatically detect Python from your `runtime.txt` file

### Base directory
- **Value:** `/`
- This is where Netlify installs dependencies and runs your build command

### Package directory
- **Value:** `/`
- Leave as default unless you're using a monorepo

### Build command
- **Value:** `echo 'No build step required'`
- Or leave empty - your `netlify.toml` already specifies this

### Publish directory
- **Value:** `/`
- This is where your static files are published (not needed for serverless functions)

### Functions directory
- **Value:** `netlify/functions`
- This tells Netlify where to find your serverless functions
- This should match what's in your `netlify.toml` file

### Deploy log visibility
- **Choose:** Public logs or Private logs (your preference)

### Build status
- **Choose:** Active builds (to auto-deploy on Git push)

## Important Notes

1. **Functions Directory:** Make sure `netlify/functions` is set correctly
2. **No Build Command Needed:** Since we're using serverless functions, no build step is required
3. **Environment Variables:** Don't forget to set `NETLIFY_DATABASE_URL` in:
   - Site settings → Environment variables

## After Configuration

1. Click **"Save"** on the build settings page
2. Trigger a new deploy (or wait for auto-deploy)
3. Check the deploy logs to verify the function is detected

