# Deployment Guide - Penn State Degree Optimizer

Complete guide for deploying the Penn State Degree Optimizer with Next.js frontend on Vercel and Flask backend on Render.

---

## Architecture Overview

**Frontend (Next.js)** → **Vercel** (Free Tier)  
**Backend (Flask)** → **Render** (Free Tier)

---

## Part 1: Deploy Backend to Render

### Step 1: Prepare Backend for Deployment

1. Ensure your backend has all required files:
   - `backend/app.py` - Flask application
   - `backend/recommendation_engine.py` - Core logic
   - `backend/transcript_parser.py` - PDF parsing
   - `backend/database.py` - Supabase integration
   - `requirements.txt` - Python dependencies

2. Verify `requirements.txt` contains all dependencies:
```txt
flask>=2.3.0
flask-cors>=4.0.0
pypdf>=3.0.0
supabase>=2.0.0
python-dotenv>=1.0.0
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended for easy deployment)

### Step 3: Deploy Backend

1. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

2. **Configure Service**
   - **Name**: `penn-state-optimizer-backend` (or your choice)
   - **Region**: US East (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

3. **Environment Variables** (if using Supabase)
   - Click "Advanced" → "Add Environment Variable"
   - Add the following:
     - `SUPABASE_URL`: Your Supabase project URL
     - `SUPABASE_KEY`: Your Supabase anon/public key
     - `PYTHON_VERSION`: `3.11.0` (or your preferred version)

4. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Note your backend URL (e.g., `https://penn-state-optimizer-backend.onrender.com`)

### Step 4: Test Backend

Test your backend endpoints:
```bash
curl https://your-backend-url.onrender.com/majors
```

Should return a JSON array of majors.

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Prepare Frontend for Deployment

Your Next.js frontend is already configured for deployment!

### Step 2: Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub (recommended)

### Step 3: Deploy Frontend

1. **Import Project**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Vercel will auto-detect Next.js

2. **Configure Project**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend-nextjs`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

3. **Environment Variables**
   - Click "Environment Variables"
   - Add the following:
     - **Key**: `NEXT_PUBLIC_API_URL`
     - **Value**: `https://your-backend-url.onrender.com` (from Part 1, Step 3)
     - Select: Production, Preview, Development

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your app will be live at `https://your-project.vercel.app`

### Step 4: Test Deployment

1. Visit your Vercel URL
2. Test the following:
   - ✅ Page loads with header
   - ✅ Majors dropdown populates
   - ✅ Form submission works
   - ✅ Results display correctly
   - ✅ Navigation to detail page works

---

## Part 3: Custom Domain (Optional)

### Vercel Custom Domain

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed by Vercel

### Render Custom Domain

1. Go to your service → Settings → Custom Domain
2. Add your custom domain
3. Configure DNS records as instructed by Render

---

## Part 4: Environment-Specific Configuration

### Development
```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:5001
```

### Production
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## Troubleshooting

### Frontend Issues

**Issue**: API calls fail with CORS error  
**Solution**: Ensure Flask backend has `flask-cors` enabled:
```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
```

**Issue**: Environment variables not working  
**Solution**: 
- Variables must start with `NEXT_PUBLIC_` for client-side access
- Redeploy after adding new environment variables
- Clear browser cache

**Issue**: Build fails  
**Solution**:
```bash
# Test build locally first
cd frontend-nextjs
npm run build
```

### Backend Issues

**Issue**: Backend service crashes on startup  
**Solution**: Check Render logs for Python errors:
- Verify all dependencies in `requirements.txt`
- Check Python version compatibility

**Issue**: Slow cold starts (Free tier)  
**Solution**: Render free tier spins down after 15 mins of inactivity
- First request after inactivity takes ~30 seconds
- Consider upgrading to paid tier for 24/7 availability

**Issue**: File uploads not working  
**Solution**: Render ephemeral filesystem - files deleted on restart
- Current implementation deletes uploaded PDFs after parsing (good)
- Don't rely on persistent file storage on free tier

### General Issues

**Issue**: Changes not reflecting  
**Solution**:
- Vercel: Push to GitHub → auto-deploys
- Render: Push to GitHub → auto-deploys
- Both platforms have automatic deployments on git push

---

## Monitoring & Logs

### Vercel Logs
- Go to your project → Deployments → Click deployment → Runtime Logs
- Real-time logs for debugging

### Render Logs
- Go to your service → Logs tab
- Real-time Python/Flask logs

---

## Cost Breakdown

### Free Tier Limits

**Vercel (Frontend)**
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Global CDN
- **Perfect for this project**

**Render (Backend)**
- ✅ 750 hours/month (enough for 1 service 24/7)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ ~30 second cold start
- ✅ Automatic HTTPS
- **Good for development/portfolio projects**

**Upgrade Recommendations:**
- If you need 24/7 uptime → Render Starter ($7/month)
- If you need faster cold starts → Consider Render paid tier

---

## Continuous Deployment

Both platforms support automatic deployment:

1. **Push to GitHub**
```bash
git add .
git commit -m "Update feature"
git push origin main
```

2. **Auto-Deploy**
   - Vercel: Deploys frontend automatically
   - Render: Deploys backend automatically
   - Takes 2-5 minutes

3. **Preview Deployments** (Vercel)
   - Every pull request gets a preview URL
   - Test before merging to main

---

## Security Best Practices

1. **Environment Variables**
   - Never commit `.env` files
   - Use Vercel/Render dashboards for secrets
   - Rotate API keys regularly

2. **CORS Configuration**
   - Only allow your frontend domain in production
   - Update Flask CORS settings:
```python
CORS(app, origins=['https://your-frontend.vercel.app'])
```

3. **Rate Limiting**
   - Consider adding rate limiting to backend API
   - Prevent abuse on free tier

---

## Backup & Rollback

### Vercel
- Click "Deployments" → Select previous deployment → "Promote to Production"

### Render
- Click "Manual Deploy" → Select previous commit
- Or use "Rollback" button in dashboard

---

## Next Steps

1. ✅ Test all features in production
2. ✅ Monitor logs for errors
3. ✅ Set up custom domain (optional)
4. ✅ Configure analytics (Vercel Analytics free)
5. ✅ Set up uptime monitoring (UptimeRobot free tier)

---

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs
- **Next.js Deployment**: https://nextjs.org/docs/deployment

---

## Summary

🎉 **You now have a fully deployed, production-ready application!**

**Your URLs:**
- Frontend: `https://your-project.vercel.app`
- Backend: `https://your-backend.onrender.com`

**Deployment Time:**
- Backend: ~10 minutes
- Frontend: ~5 minutes
- **Total: ~15 minutes**

**Cost: $0/month** (Free tier for both services)

---

## Quick Reference Commands

```bash
# Test backend locally
cd backend
python app.py

# Test frontend locally
cd frontend-nextjs
npm run dev

# Build frontend locally
cd frontend-nextjs
npm run build

# Check frontend env vars
cd frontend-nextjs
cat .env.local

# View frontend build output
cd frontend-nextjs
npm run build && npm start
```

Ready to deploy! 🚀

