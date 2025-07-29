# Vercel Deployment Guide

## Quick Setup Steps

1. **Environment Variables in Vercel Dashboard:**
   - LINE_ACCESS_TOKEN: Your LINE access token
   - LINE_CHANNEL_SECRET: Your LINE channel secret  
   - GEMINI_API_KEY: Your Google AI API key
   - DATABASE_URL: PostgreSQL connection string

2. **Deploy to Vercel:**
   ```bash
   npm install -g vercel
   vercel login
   vercel --prod
   ```

3. **Update LINE Webhook:**
   - Go to LINE Developers Console
   - Set webhook URL: https://your-app.vercel.app/webhook

## Database Options

### Option 1: Vercel Postgres (Recommended)
1. Go to Vercel Dashboard → Storage → Create Postgres
2. Copy the DATABASE_URL to environment variables

### Option 2: External Database (Neon/Supabase)  
1. Create PostgreSQL database at Neon.tech or Supabase
2. Copy connection string to DATABASE_URL

## Testing
- Health check: https://your-app.vercel.app/health
- Frontend: https://your-app.vercel.app/
- API: https://your-app.vercel.app/api/users

## Troubleshooting
- Check logs: `vercel logs --follow`
- Local testing: `vercel dev`
- Environment check: `vercel env ls`