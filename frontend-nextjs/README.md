# Penn State Degree Optimizer - Next.js Frontend

Modern, TypeScript-powered frontend for the Penn State Degree Optimizer. Built with Next.js 14, React, and Tailwind CSS.

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ (20.12.2 tested)
- npm or yarn
- Flask backend running on port 5001

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on `http://localhost:3000`

---

## 📁 Project Structure

```
frontend-nextjs/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout (Header + Footer)
│   ├── page.tsx                 # Home page (search & results)
│   ├── globals.css              # Tailwind + custom styles
│   └── program/
│       └── [programId]/
│           └── page.tsx         # Program detail page
├── components/                   # React components (10 total)
│   ├── Header.tsx               # Navigation header
│   ├── SearchForm.tsx           # Main search form
│   ├── FileUpload.tsx           # PDF transcript upload
│   ├── FilterButtons.tsx        # Program type filters
│   ├── ResultsSection.tsx       # Results container
│   ├── ProgramCard.tsx          # Individual program card
│   ├── CourseChip.tsx           # Course status chips
│   ├── PrerequisiteModal.tsx    # Prerequisite viewer
│   ├── PrerequisiteTree.tsx     # Prerequisite tree
│   └── LoadingSpinner.tsx       # Loading animation
├── services/
│   └── api.ts                   # API service layer
├── types/
│   └── index.ts                 # TypeScript type definitions
├── .env.local                   # Environment variables (dev)
└── .env.example                 # Environment variables template
```

---

## 🛠️ Available Scripts

```bash
# Development
npm run dev              # Start dev server on port 3000

# Production
npm run build            # Build for production
npm start                # Start production server

# Linting
npm run lint             # Run ESLint
```

---

## 🎨 Features

### User Features
- **Smart Search** - Find minors and certificates based on completed courses
- **PDF Upload** - Upload Penn State transcript for automatic course extraction
- **Real-time Filtering** - Filter results by program type
- **Triple Dip Detection** - Find courses that satisfy multiple requirements
- **Prerequisite Trees** - Visual prerequisite dependency graphs
- **Progress Tracking** - See completion status and credits needed

### Technical Features
- **TypeScript** - Full type safety
- **Server-Side Rendering** - Fast initial page load
- **Responsive Design** - Mobile, tablet, desktop support
- **Animations** - Smooth Framer Motion animations
- **Penn State Branding** - Official colors and styling

---

## 🔧 Configuration

### Environment Variables

Create `.env.local` file:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://127.0.0.1:5001
```

For production deployment, update to your backend URL:
```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## 🌐 Backend Connection

The frontend expects a Flask backend running with these endpoints:

- `GET /majors` - List of available majors
- `POST /recommend` - Get program recommendations
- `POST /upload_transcript` - Upload PDF transcript
- `GET /courses` - Get course data for prerequisites

**Backend should be running on `http://127.0.0.1:5001` by default.**

---

## 🎯 Component Overview

### Layout Components
- **Header** - Sticky navigation with Penn State branding
- **LoadingSpinner** - Animated loading state

### Form Components
- **SearchForm** - Main input form with validation
- **FileUpload** - Drag-and-drop PDF uploader

### Results Components
- **ResultsSection** - Results container with filtering
- **FilterButtons** - Program type filter buttons
- **ProgramCard** - Individual program display
- **CourseChip** - Course status badges

### Modal Components
- **PrerequisiteModal** - Course prerequisite viewer
- **PrerequisiteTree** - Interactive prerequisite tree

---

## 📦 Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.0.3 | React framework |
| React | 18.3.1 | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Styling |
| Framer Motion | 11.11.17 | Animations |
| Axios | 1.7.7 | API calls |
| React Icons | 5.3.0 | Icons |

---

## 🚀 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Set root directory to `frontend-nextjs`
4. Add environment variable: `NEXT_PUBLIC_API_URL`
5. Deploy!

See `docs/DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## 📊 Build Output

Production build generates:
- Static HTML for homepage
- Server-rendered dynamic routes
- Optimized JavaScript bundles
- Minified CSS

Build time: ~2 seconds  
Build size: Optimized for production

---

## 🔍 Development Tips

### Hot Reload
Save any file to see changes instantly. No page refresh needed!

### TypeScript
- All components are fully typed
- Use `@/` for absolute imports
- Check `types/index.ts` for type definitions

### Styling
- Tailwind utility classes
- Penn State theme colors: `penn-blue`, `penn-navy`, etc.
- Custom classes in `globals.css`

---

## 🐛 Troubleshooting

### Port 3000 in use
```bash
lsof -ti:3000 | xargs kill -9
```

### Backend connection error
- Ensure Flask backend is running on port 5001
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is enabled in Flask

### Build fails
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

---

## 📝 Migration Notes

This frontend was migrated from Vite + React to Next.js 14. See `docs/NEXTJS_MIGRATION.md` for details.

**Key Changes:**
- Vite → Next.js 14 with App Router
- JavaScript → TypeScript
- React Router → Next.js routing
- All functionality preserved

---

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Build successfully
5. Submit pull request

---

## 📄 License

Penn State Degree Optimizer
Copyright © 2024

---

## 📞 Support

For issues or questions:
- Check `docs/DEPLOYMENT_GUIDE.md`
- Check `docs/NEXTJS_MIGRATION.md`
- Review component source code

---

## ✅ Checklist for New Developers

- [ ] Node.js 16+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] `.env.local` created with backend URL
- [ ] Flask backend running on port 5001
- [ ] Dev server starts (`npm run dev`)
- [ ] Can access `http://localhost:3000`
- [ ] Form loads and majors populate
- [ ] Can submit form and see results

---

**Ready to optimize your Penn State degree! 🎓**
