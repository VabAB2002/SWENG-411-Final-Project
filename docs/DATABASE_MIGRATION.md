# Database Migration Guide: JSON to Supabase

This guide walks you through migrating your Penn State Course Recommendation System from JSON files to Supabase PostgreSQL database.

## Table of Contents
1. [Why Migrate?](#why-migrate)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Migration](#step-by-step-migration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [Rollback](#rollback)

---

## Why Migrate?

### Benefits of Supabase:
- **Better Data Management**: Update courses/programs without redeploying code
- **Scalability**: Database queries scale better than loading large JSON files
- **Real-time Capabilities**: Future features like live updates
- **Industry Standard**: PostgreSQL is production-ready
- **Matches Documentation**: Your design document specifies PostgreSQL

### What Won't Change:
- ✅ Performance stays the same (data is cached in memory)
- ✅ All recommendation logic remains identical
- ✅ API responses stay compatible
- ✅ Frontend requires no changes

---

## Prerequisites

Before starting, ensure you have:
- ✅ Completed packages installed (`supabase`, `python-dotenv`)
- ✅ A GitHub account (for Supabase signup)
- ✅ Stable internet connection
- ✅ 10-15 minutes of time

---

## Step-by-Step Migration

### Step 1: Create Supabase Account (2 minutes)

1. Go to https://supabase.com
2. Click **"Start your project"**
3. Sign up using your GitHub account
4. Verify your email if prompted

### Step 2: Create New Project (3 minutes)

1. Click **"New Project"**
2. Fill in project details:
   - **Name**: `penn-state-course-recommender` (or your preference)
   - **Database Password**: Generate a strong password (SAVE THIS!)
   - **Region**: Choose closest to you (e.g., US East)
   - **Pricing Plan**: Free tier is sufficient
3. Click **"Create new project"**
4. Wait 2-3 minutes for project to provision (you'll see a progress indicator)

### Step 3: Get Your Credentials (1 minute)

Once your project is ready:

1. Go to **Settings** (gear icon in left sidebar)
2. Click **"API"** in the settings menu
3. Copy these two values:

   **Project URL:**
   ```
   https://xxxxxxxxxxxxx.supabase.co
   ```

   **service_role key** (NOT the anon key):
   ```
   eyJxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx...
   ```

   ⚠️ **Important**: Use the `service_role` key, not the `anon` key. The service role key is needed for backend operations.

### Step 4: Update Environment Variables (1 minute)

1. Open `backend/.env` in your text editor
2. Replace the placeholder values:

   ```env
   SUPABASE_URL=https://your-actual-project-id.supabase.co
   SUPABASE_KEY=your_actual_service_role_key_here
   ```

3. Save the file

### Step 5: Execute Database Schema (2 minutes)

1. Go back to Supabase dashboard
2. Click **"SQL Editor"** in the left sidebar
3. Click **"New Query"**
4. Open `backend/scripts/create_schema.sql` on your computer
5. Copy the **entire contents** of the file
6. Paste into the Supabase SQL Editor
7. Click **"Run"** button (or press Cmd/Ctrl + Enter)
8. You should see: `Success. No rows returned`

**Verify tables were created:**
1. Click **"Table Editor"** in left sidebar
2. You should see 4 tables:
   - `programs`
   - `courses`
   - `course_equivalencies`
   - `prerequisite_config`

### Step 6: Run Data Migration (5 minutes)

Now migrate your JSON data to Supabase:

1. Open Terminal
2. Navigate to your project:
   ```bash
   cd "/Users/V-Personal/Desktop/SWENG PROJECTS/SWENG-411-Final-Project"
   ```

3. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

4. Run migration script:
   ```bash
   cd backend/scripts
   python3 migrate_to_supabase.py
   ```

5. You should see:
   ```
   📚 Migrating programs...
      ✓ Inserted batch 1: 500 programs
      ✓ Inserted batch 2: 312 programs
      ✅ Total programs migrated: 812
   
   📖 Migrating courses...
      ✓ Inserted batch 1: 500 courses
      ...
      ✅ Total courses migrated: 2847
   
   🔄 Migrating course equivalencies...
      ✅ Total equivalencies migrated: 156
   
   ⚙️  Migrating prerequisite configuration...
      ✅ Prerequisite config migrated
   
   🔍 Verifying migration...
      Programs: 812 rows
      Courses: 2847 rows
      Equivalencies: 156 rows
      Configs: 1 rows
   
   ✅ Migration completed successfully!
   ```

### Step 7: Verify in Supabase Dashboard (2 minutes)

1. Go to **"Table Editor"** in Supabase dashboard
2. Click on **`programs`** table
   - You should see 800+ rows
   - Click on a few to inspect data
3. Click on **`courses`** table
   - You should see 2,800+ rows
   - Verify prerequisites and GenEd attributes look correct
4. Check **`course_equivalencies`** table
   - Should have 150+ rows

---

## Verification

### Test the Backend (2 minutes)

1. Start your backend server:
   ```bash
   cd backend
   python3 app.py
   ```

2. You should see:
   ```
   📥 Loading data from Supabase...
      → Loading programs...
      ✓ Loaded 812 programs
      → Loading courses...
      ✓ Loaded 2847 courses
      → Loading course equivalencies...
      ✓ Loaded 156 equivalency mappings
      → Loading prerequisite configuration...
      ✓ Loaded prerequisite configuration
   ✅ Database load complete: 812 programs, 2847 courses
   ✓ Using Supabase database
   ✅ Server Ready! Loaded 35 majors.
   ```

3. Test the API:
   ```bash
   # In a new terminal
   curl http://localhost:5001/majors
   ```
   
   You should get a JSON list of majors.

### Test Frontend Integration (2 minutes)

1. Start your frontend:
   ```bash
   cd frontend
   npm run dev
   ```

2. Open http://localhost:5173 in your browser
3. Try a recommendation:
   - Select a major
   - Enter some courses: `CMPSC 121, MATH 140, ENGL 15`
   - Click "Analyze My Options"
4. Verify you get results (should work exactly as before)

---

## Troubleshooting

### Issue: "Supabase not configured" error

**Symptoms:**
```
⚠️  Supabase not configured: Please:
1. Create a Supabase project at https://supabase.com
...
```

**Solution:**
1. Check `backend/.env` file exists and has correct values
2. Make sure you used the `service_role` key, not `anon` key
3. Verify URL format: `https://xxxxx.supabase.co` (no trailing slash)

### Issue: Migration script fails with "Error inserting batch"

**Symptoms:**
```
❌ Error inserting batch 1: {...}
```

**Possible Causes:**
1. **Schema not created**: Go back to Step 5, execute `create_schema.sql`
2. **Wrong credentials**: Double-check your `.env` file
3. **Network issue**: Check your internet connection

**Solution:**
```bash
# Check if tables exist
# In Supabase SQL Editor, run:
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

You should see: `programs`, `courses`, `course_equivalencies`, `prerequisite_config`

### Issue: Backend falls back to JSON files

**Symptoms:**
```
⚠️  Supabase not configured: ...
⚠️  Falling back to JSON files...
✓ Using JSON files
```

**This is OK!** The system is designed to fallback gracefully. But to fix:
1. Verify `.env` file has correct credentials
2. Check Supabase project is active (go to dashboard)
3. Test connection:
   ```python
   from supabase import create_client
   import os
   from dotenv import load_dotenv
   load_dotenv('backend/.env')
   client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
   print("Connected!")
   ```

### Issue: "No module named 'supabase'"

**Solution:**
```bash
source venv/bin/activate
pip install supabase python-dotenv
```

---

## Rollback

If you need to revert to JSON files:

### Option 1: Quick Disable (Recommended for Testing)

Simply rename or delete `backend/.env`:
```bash
mv backend/.env backend/.env.backup
```

The system will automatically fall back to JSON files.

### Option 2: Remove Database Module

```bash
mv backend/database.py backend/database.py.backup
```

The system will use only JSON files.

### Option 3: Complete Rollback

```bash
# Backup Supabase files
mkdir backend/supabase_backup
mv backend/database.py backend/supabase_backup/
mv backend/.env backend/supabase_backup/
mv backend/scripts/migrate_to_supabase.py backend/supabase_backup/
mv backend/scripts/create_schema.sql backend/supabase_backup/
```

---

## Performance Comparison

| Metric | JSON Files | Supabase (Cached) |
|--------|-----------|-------------------|
| **Startup Time** | 2-3 seconds | 3-4 seconds |
| **Memory Usage** | ~50 MB | ~50 MB |
| **Recommendation Speed** | <1 second | <1 second |
| **Data Updates** | Requires code redeploy | Edit in dashboard |

**Verdict:** Supabase adds ~1 second to startup time but maintains runtime performance.

---

## Next Steps

After successful migration:

1. ✅ Update your documentation to reflect PostgreSQL database
2. ✅ Update README.md with Supabase setup instructions
3. ✅ Add database URL to your demo presentation
4. ✅ Consider adding Row Level Security (RLS) policies for production

---

## Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL JSON Functions](https://www.postgresql.org/docs/current/functions-json.html)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)

---

## Support

If you encounter issues not covered here:

1. Check Supabase project status: https://status.supabase.com
2. Review Supabase logs in dashboard (Logs section)
3. Check backend console output for detailed error messages
4. Verify all JSON files exist in `data/` directory

**Remember**: The system is designed to work with or without Supabase. If migration fails, your app will continue working with JSON files!

