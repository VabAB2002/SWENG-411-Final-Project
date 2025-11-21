# Penn State World Campus Course Recommendation System

A comprehensive web application that helps Penn State World Campus students discover optimal academic programs (minors, majors, certificates) based on their completed coursework and GenEd requirements.

## 🌟 Features

- **Intelligent Course Analysis**: Analyzes student transcripts to identify completed courses
- **Smart Recommendations**: Suggests programs with minimal additional coursework required
- **Prerequisite Intelligence**: 
  - Tier 1: Exact course matching
  - Tier 2: Course equivalencies (e.g., CMPSC 121 ≈ CMPSC 131)
  - Tier 3: Hierarchical course rules (higher-level courses satisfy lower prerequisites)
- **GenEd Optimization**: Identifies "triple-dip" opportunities where courses satisfy program + GenEd requirements
- **Recursive Cost Calculation**: Automatically calculates prerequisite chains
- **PDF Transcript Parsing**: Automatically extracts courses from Penn State transcript PDFs
- **Real-Time Filtering**: Filter by program type (Minors, Majors, Certificates)
- **Modern UI**: Beautiful, responsive React interface with Tailwind CSS

## 📁 Project Structure

```
project_root/
├── backend/                          # Flask API backend
│   ├── app.py                       # Main Flask application
│   ├── recommendation_engine.py     # Core recommendation logic
│   ├── transcript_parser.py         # PDF parsing utilities
│   ├── config/
│   │   └── prerequisite_config.json # Prerequisite matching configuration
│   └── uploads/                     # Temporary PDF upload storage
│
├── data/                            # JSON data files
│   ├── academic_programs_rules.json           # Program requirements (800+ programs)
│   ├── world_campus_courses_master.json       # World Campus course catalog
│   ├── gened_supplementary.json               # Additional GenEd courses
│   ├── course_equivalencies.json              # Course equivalency mappings
│   ├── gened_courses_golden_record.json       # GenEd attributes database
│   ├── duplicate_conflicts.json               # Data quality report
│   └── old/                                   # Legacy data files
│
├── scripts/                         # Utility scripts
│   ├── generate_optimized_data.py   # Builds optimized course databases
│   ├── generate_equivalencies.py    # Creates equivalency mappings
│   ├── enrich_data.py              # Enriches course data
│   ├── build_rules.py              # Builds program rules
│   └── scraping/                   # Web scraping utilities
│       ├── scraper.py              # Course catalog scraper
│       ├── test_parser.py          # Parser testing
│       └── Transformation.py       # Data transformation
│
├── frontend/                        # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx                 # Main application component
│   │   ├── components/             # Reusable UI components
│   │   ├── services/               # API service layer
│   │   └── styles/                 # CSS styles
│   ├── public/                     # Static assets
│   └── vite.config.js              # Vite configuration
│
├── docs/                            # Documentation
│   ├── FRONTEND_SETUP.md           # Frontend setup instructions
│   └── PREREQUISITE_LOGIC_SUMMARY.md # Prerequisite matching documentation
│
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **pip** (Python package manager)

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd "SWE FINAL"
```

#### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Navigate to backend directory
cd backend
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Running the Application

#### Start Backend Server

```bash
# From project root, activate virtual environment
source venv/bin/activate

# Navigate to backend
cd backend

# Run Flask server
python app.py
```

The backend API will be available at `http://localhost:5001`

#### Start Frontend Development Server

```bash
# In a new terminal, navigate to frontend
cd frontend

# Start Vite dev server
npm run dev
```

The frontend will be available at `http://localhost:5173` (or next available port)

### Building for Production

```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/dist/
```

## 📊 Data Management

### Regenerating Optimized Data

If you update `academic_programs_rules.json` or `gened_courses_golden_record.json`, regenerate the optimized data files:

```bash
# From project root
cd scripts
python generate_optimized_data.py
```

This script:
1. Extracts all courses from academic programs
2. Deduplicates and detects conflicts
3. Enriches with GenEd attributes
4. Creates `world_campus_courses_master.json` and `gened_supplementary.json`

### Data Files Overview

| File | Purpose | Size |
|------|---------|------|
| `academic_programs_rules.json` | Program requirements for 800+ programs | ~17K lines |
| `world_campus_courses_master.json` | Primary course lookup (World Campus) | ~9K lines |
| `gened_supplementary.json` | Fallback GenEd courses | ~20K lines |
| `course_equivalencies.json` | Course equivalency mappings | ~1K lines |
| `prerequisite_config.json` | Prerequisite matching rules | Small config |

## 🔧 Configuration

### Prerequisite Matching Configuration

Edit `backend/config/prerequisite_config.json`:

```json
{
  "hierarchy_rules": {
    "enabled": true,
    "same_department_higher_level": true,
    "minimum_level_difference": 0
  }
}
```

- **enabled**: Enable/disable hierarchical prerequisite matching
- **same_department_higher_level**: Allow higher-level courses to satisfy lower prereqs
- **minimum_level_difference**: Minimum level difference required (0 = same level ok)

### Frontend API Configuration

Edit `frontend/src/services/api.js` to change the backend URL:

```javascript
const API_BASE_URL = import.meta.env.DEV 
  ? 'http://127.0.0.1:5001'
  : '';
```

## 🧪 Testing

### Test Transcript Parsing

```bash
cd backend
python transcript_parser.py
```

### Test Recommendation Engine

```python
from recommendation_engine import load_data, calculate_program_gap

PROGRAMS, COURSES, EQUIV_MAP, PREREQ_CONFIG = load_data()
# Test with sample data
```

## 📚 API Documentation

### Endpoints

#### `GET /majors`
Returns list of available majors.

**Response:**
```json
["AEROSPACE ENGINEERING", "COMPUTER SCIENCE", ...]
```

#### `POST /upload_transcript`
Uploads and parses a Penn State transcript PDF.

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "status": "success",
  "courses": ["CMPSC 131", "MATH 140", ...]
}
```

#### `POST /recommend`
Gets program recommendations based on completed courses.

**Request:**
```json
{
  "history": ["CMPSC 131", "MATH 140"],
  "major": "COMPUTER SCIENCE",
  "gen_ed_needs": ["GN", "GS"],
  "interest_filter": "Minor"
}
```

**Response:**
```json
{
  "status": "success",
  "count": 15,
  "recommendations": [
    {
      "program_name": "MATHEMATICS",
      "gap_credits": 12.0,
      "missing_courses": [...],
      "optimizations": [...],
      "optimization_count": 3
    }
  ]
}
```

## 🎨 Tech Stack

### Backend
- **Flask**: Web framework
- **pypdf**: PDF parsing
- **Flask-CORS**: Cross-origin resource sharing

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client

## 🔍 How It Works

### Recommendation Algorithm

1. **Parse User Input**: Extract completed courses from transcript or manual entry
2. **Load Program Database**: Load 800+ academic programs with requirements
3. **Calculate Gaps**: For each program:
   - Check required courses against user history
   - Apply equivalency rules
   - Calculate recursive prerequisite chains
   - Account for major overlap (courses that count for both)
4. **Find Optimizations**: Identify courses that satisfy multiple requirements
5. **Rank Results**: Sort by lowest gap credits and most optimizations
6. **Return Top 15**: Return best recommendations

### Prerequisite Intelligence

The system uses a three-tier prerequisite matching system:

**Tier 1: Exact Match**
```
Required: MATH 140
User has: MATH 140 ✓
```

**Tier 2: Equivalency Map**
```
Required: CMPSC 121
User has: CMPSC 131 ✓ (equivalent)
```

**Tier 3: Hierarchical Rules**
```
Required: MATH 140 (140-level)
User has: MATH 230 ✓ (higher level in same department)
```

### Course Cost Calculation

The system recursively calculates the true cost of taking a course:

```
Cost(CMPSC 311) = 3 credits + Cost(CMPSC 221 OR CMPSC 121)
                = 3 + min(Cost(CMPSC 221), Cost(CMPSC 121))
                = 3 + 3 = 6 credits
```

## 🐛 Troubleshooting

### Backend won't start
- Ensure virtual environment is activated
- Check Python version: `python --version` (needs 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend won't start
- Check Node version: `node --version` (needs 16+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### API connection errors
- Verify backend is running on port 5001
- Check CORS configuration in `backend/app.py`
- Verify API URL in `frontend/src/services/api.js`

### Transcript parsing issues
- Ensure PDF is a genuine Penn State transcript
- Check PDF is not password-protected
- Verify transcript format matches expected structure

## 📈 Future Enhancements

- [ ] User accounts and saved recommendations
- [ ] Course scheduling optimization
- [ ] Integration with official Penn State APIs
- [ ] Mobile app version
- [ ] Export recommendations to PDF
- [ ] Semester-by-semester planning
- [ ] Cost estimation (tuition calculator)

## 📄 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

## 📞 Support

For questions or issues, please [open an issue](link-to-issues) or contact [your-email].

---

**Built with ❤️ for Penn State World Campus students**

