# Penn State Course Recommendation System

**Group 9**

**Team Members:**
- Vishal Bidari
- Sylvan Adams
- Noah Blumenstock
- David Leija

---

## Software Design Specification Document

**Version:** 2.0
**Date:** 12/17/2025

---

# Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 [Goals and Objectives](#11-goals-and-objectives)
   - 1.2 [Statement of System Scope](#12-statement-of-system-scope)
   - 1.3 [Reference Material](#13-reference-material)
   - 1.4 [Definitions and Acronyms](#14-definitions-and-acronyms)

2. [Architectural Design](#2-architectural-design)
   - 2.1 [System Architecture](#21-system-architecture)
   - 2.2 [Design Rationale](#22-design-rationale)

3. [Key Functionality Design](#3-key-functionality-design)
   - 3.1 [Upload and Parse Transcript](#31-upload-and-parse-transcript)
   - 3.2 [Generate Course Recommendations](#32-generate-course-recommendations)
   - 3.3 [View Program Details](#33-view-program-details)
   - 3.4 [Filter Recommendations by Type](#34-filter-recommendations-by-type)
   - 3.5 [Calculate Prerequisite Chains](#35-calculate-prerequisite-chains)

4. [User Interface Design](#4-user-interface-design)
   - 4.1 [Interface Design Rules](#41-interface-design-rules)
   - 4.2 [Description of User Interface](#42-description-of-the-user-interface)

5. [Restrictions, Limitations, and Constraints](#5-restrictions-limitations-and-constraints)

6. [Testing Issues](#6-testing-issues)

7. [Appendices](#7-appendices)

---

# 1. Introduction

This document describes the complete design of the Penn State Course Recommendation System. We built this system to help Penn State World Campus students make smarter decisions about choosing minors, certificates, and general education courses that align with their major.

Instead of manually comparing hundreds of courses across different programs, students can now get personalized recommendations in just a few minutes. The system analyzes which courses overlap between the student's major and other programs, helping students graduate faster and take fewer extra courses.

## 1.1 Goals and Objectives

We created this system with five main goals:

**Goal 1: Save Students Time and Money**

Students shouldn't waste hours manually comparing course requirements across programs. Our system automatically calculates which programs have the most overlap with courses they've already completed or will take for their major. More overlap means fewer additional courses, which means less time and money spent on extra credits.

**Goal 2: Provide Intelligent, Personalized Recommendations**

Every student's situation is unique. The system analyzes each student's specific major and completed courses, then ranks all available minors, certificates, and Gen Ed options by how well they fit. A Computer Science major will get completely different recommendations than a Business major because their course histories are different.

**Goal 3: Show Clear, Transparent Requirements**

Students hate surprises when it comes to degree requirements. We show exactly:
- How many courses overlap between their major and each program
- Which additional courses they'll need to complete
- What prerequisites those courses require
- Total additional credits needed

There are no hidden requirements or confusing prerequisites.

**Goal 4: Work Anywhere, Anytime**

Whether students are on their phone during a lunch break or on their laptop at midnight, the system works smoothly. It's a web application - no downloads, no special software, just a browser and internet connection.

**Goal 5: Support Academic Advisors**

Academic advisors spend significant time answering routine questions like "What minor should I choose?" and "How many courses do I need?" Our system handles these basic questions automatically, freeing advisors to focus on complex academic planning that truly needs human expertise.

## 1.2 Statement of System Scope

The Penn State Course Recommendation System helps World Campus students discover which minors, certificates, and general education courses best complement their major by automatically calculating course overlap and providing ranked recommendations.

### What the System Does:

The system retrieves course and program data from a Supabase PostgreSQL database (with JSON file fallback for offline development) and generates personalized recommendations based on student input. Specifically:

**Data Management:**
- Maintains a database of 800+ Penn State World Campus programs (majors, minors, certificates)
- Stores detailed course information including prerequisites, credits, and Gen Ed attributes
- Manages course equivalency mappings (e.g., CMPSC 121 ≈ CMPSC 131)

**Input Processing:**
- Accepts student's major selection from a dropdown menu
- Allows manual entry of completed courses via text input
- Supports PDF transcript upload with automatic course extraction
- Validates all course codes against Penn State's course catalog

**Recommendation Engine:**
- Calculates course overlap between student's major and all available programs
- Applies three-tier prerequisite matching:
  - Tier 1: Exact course code match
  - Tier 2: Course equivalency mappings
  - Tier 3: Hierarchical rules (higher-level courses satisfy lower prerequisites)
- Identifies "triple-dip" opportunities where courses satisfy major + program + Gen Ed requirements
- Ranks all programs by total additional credits needed
- Returns top 15 recommendations sorted by best fit

**Results Display:**
- Shows program name, type, total overlap, and additional credits needed
- Provides filtering by program type (Minors, Certificates, Gen Ed)
- Displays detailed course lists with completion status
- Shows prerequisite chains for uncompleted courses
- Calculates recursive prerequisite costs (prerequisites of prerequisites)

**Web Interface:**
- Delivers responsive Next.js web interface accessible on desktop and mobile
- Works on any modern web browser without requiring installation
- Provides real-time results without page refreshes

### What the System Does NOT Do:

The system will **NOT**:
- Connect to Penn State's official systems (LionPATH, Canvas, official registrar databases)
- Automatically import student transcripts from Penn State servers
- Store user data between sessions or require user accounts/login
- Register students for courses or check real-time course availability/waitlists
- Handle financial aid calculations, tuition estimates, or payment processing
- Replace academic advisors or provide official degree audits
- Send email notifications or track student progress over time
- Guarantee course availability in any given semester
- Provide academic advising or career counseling

### System Boundaries:

This is a **standalone planning tool** that operates independently from Penn State's official infrastructure. Students use it to explore options and make informed decisions, then work with their academic advisor and official university systems (LionPATH) to implement their actual course registration and degree plan.

### Performance Requirements:

- Generate recommendations within **5 seconds** after receiving student input
- Support at least **50 concurrent users** without performance degradation
- Work on any modern web browser (Chrome, Firefox, Safari, Edge)
- Maintain 99% uptime during academic planning periods
- Handle transcript PDFs up to 10 MB in size

### Data Requirements:

- Store and process data for 800+ academic programs
- Maintain course catalog with 5,000+ course definitions
- Update course equivalency mappings as Penn State modifies curriculum
- Cache data in memory for fast access during recommendation generation

## 1.3 Use Case Diagram

The following diagram shows the main interactions between users and the system:

```
┌─────────────────────────────────────────────────────────────┐
│                Penn State Recommendation System             │
│                                                             │
│  ┌──────────────────┐                                      │
│  │                  │                                      │
│  │    Student       │─────► Enter Major                    │
│  │                  │                                      │
│  │                  │─────► Enter Completed Courses        │
│  │                  │                                      │
│  │                  │─────► Upload PDF Transcript          │
│  └──────────────────┘                                      │
│          │                                                  │
│          │                                                  │
│          ▼                                                  │
│  ┌──────────────────┐                                      │
│  │   Get            │                                      │
│  │   Recommendations│◄────── Calculate Overlap             │
│  └──────────────────┘                                      │
│          │                                                  │
│          │                                                  │
│          ▼                                                  │
│  ┌──────────────────┐                                      │
│  │   View Results   │                                      │
│  └──────────────────┘                                      │
│          │                                                  │
│     ┌────┴────┬─────────┬────────────┐                    │
│     │         │         │            │                    │
│     ▼         ▼         ▼            ▼                    │
│  Filter   View      Check     Calculate                   │
│  by Type  Details   Prereqs   Gap                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Main Use Cases:

1. **Enter Academic Information**: Student selects major and enters completed courses
2. **Upload Transcript**: Student uploads PDF transcript for automatic course extraction
3. **Get Recommendations**: System calculates and displays ranked program recommendations
4. **Filter Recommendations**: Student filters results by program type (Minor/Certificate/Gen Ed)
5. **View Program Details**: Student views detailed course requirements for a program
6. **Check Prerequisites**: Student views prerequisite chains for required courses
7. **Calculate Gap**: System calculates total additional credits needed

## 1.4 Reference Material

The following documents and resources were used in designing this system:

**Penn State Official Sources:**
- Penn State Course Bulletin (https://bulletins.psu.edu/) - Source for course codes, titles, credits, and prerequisites
- Penn State World Campus Academic Planning Pages - Source for major, minor, and certificate requirements
- Penn State Undergraduate Degree Programs Database - Complete program requirements

**Project Documentation:**
- Software Requirements Specification (SRS) - Penn State Course Recommendation System (Team document, September 2025)
- Version 1 Design Document - Initial design with preliminary architecture (November 2025)

**Technical References:**
- IEEE Software Design Document Template - Structure for organizing this design document
- UML 2.5 Specification (Object Management Group) - Reference for creating UML diagrams
- PlantUML Documentation - Tool for generating diagrams from text
- Flask Documentation (https://flask.palletsprojects.com/) - Python web framework reference
- Next.js Documentation (https://nextjs.org/docs) - React framework for production
- Supabase Documentation (https://supabase.com/docs) - PostgreSQL database platform
- React Documentation (https://react.dev/) - Frontend UI library

**Development Tools:**
- Python 3.8+ Documentation - Backend programming language
- PostgreSQL 14+ Documentation - Database system
- Tailwind CSS Documentation - Utility-first CSS framework

## 1.5 Definitions and Acronyms

### Academic Terms:

**Gen Ed**: General Education requirements that all Penn State students must complete regardless of major. Includes categories like GN (Natural Sciences), GS (Social Sciences), GH (Humanities), etc.

**Overlap**: Courses that satisfy requirements for multiple programs simultaneously. For example, a course that counts toward both a student's major and a minor, reducing total credits needed.

**Prerequisites**: Courses that must be completed before enrolling in a higher-level course. For example, MATH 140 (Calculus I) is a prerequisite for MATH 141 (Calculus II).

**Triple-Dip**: A course that simultaneously satisfies three requirements: the student's major, a program (minor/certificate), AND a Gen Ed category. These are highly valuable for efficiency.

**Course Equivalency**: Two different courses that satisfy the same requirement. For example, CMPSC 121 (Introduction to Programming) and CMPSC 131 (Programming and Computation I) are equivalent for most purposes.

**Hierarchical Prerequisites**: Rule where higher-level courses in the same department automatically satisfy lower-level prerequisites. For example, MATH 230 satisfies the MATH 140 prerequisite.

### Penn State Systems:

**LionPATH**: Penn State's official student information system for registration, grades, and academic records. Our system does NOT connect to LionPATH.

**World Campus**: Penn State's online education platform for distance learners. All programs in our database are available through World Campus.

### Technical Terms:

**API**: Application Programming Interface - Allows different software components to communicate. Our Flask backend exposes a REST API that the Next.js frontend calls.

**REST API**: Representational State Transfer API - Architectural style for web services. Uses HTTP methods (GET, POST) to transfer data in JSON format.

**JSON**: JavaScript Object Notation - Lightweight data format used for storing and transferring data. Example: `{"course": "CMPSC 131", "credits": 3}`

**PostgreSQL**: Open-source relational database system used to store our course and program data (via Supabase).

**Supabase**: Cloud-hosted PostgreSQL database platform that provides an easy-to-use interface and API for database operations.

**Next.js**: React framework for building production-ready web applications with server-side rendering and optimized performance.

**Flask**: Lightweight Python web framework used for building our backend API server.

**CORS**: Cross-Origin Resource Sharing - Security feature that allows our Next.js frontend (running on one port) to communicate with our Flask backend (running on a different port).

**Responsive Design**: Web design approach that automatically adjusts layout and styling based on screen size, ensuring the app works well on phones, tablets, and desktops.

**UML**: Unified Modeling Language - Standardized notation for creating software design diagrams (use case, sequence, class, activity diagrams).

**SSR**: Server-Side Rendering - Next.js feature that renders pages on the server for faster initial load and better SEO.

### System-Specific Terms:

**Recommendation Engine**: Core backend component that calculates course overlap, applies prerequisite logic, and ranks programs by best fit.

**Overlap Count**: Number of courses that satisfy both the student's major requirements AND another program's requirements.

**Gap Credits**: Total additional credits a student needs to complete a program after accounting for overlap with their major.

**Recursive Prerequisites**: The full chain of courses needed, including prerequisites of prerequisites. For example, to take CMPSC 311, you need CMPSC 221, which needs CMPSC 121, which needs MATH 140.

**Normalized Course Code**: Course codes converted to a standard format (uppercase, no spaces) for consistent comparison. Example: "CMPSC 131" and "cmpsc 131" both normalize to "CMPSC131".

---

# 2. Architectural Design

## 2.1 System Architecture

Our system uses a **three-tier architecture** with clear separation between presentation, business logic, and data storage. This design allows each layer to be developed, tested, and modified independently.

### Architecture Overview:

```
┌──────────────────────────────────────────────────────────────┐
│                     TIER 1: PRESENTATION                     │
│                    (Next.js Frontend)                        │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Pages     │  │  Components  │  │  API Client  │      │
│  ├─────────────┤  ├──────────────┤  ├──────────────┤      │
│  │ HomePage    │  │ SearchForm   │  │ axios HTTP   │      │
│  │ DetailPage  │  │ ProgramCard  │  │ client       │      │
│  │             │  │ FilterButtons│  │              │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/JSON (REST API)
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   TIER 2: BUSINESS LOGIC                     │
│                     (Flask Backend)                          │
│                                                              │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  API Routes │  │ Core Modules     │  │ Data Access   │  │
│  ├─────────────┤  ├──────────────────┤  ├───────────────┤  │
│  │ /majors     │  │ recommendation_  │  │ database.py   │  │
│  │ /recommend  │  │    engine.py     │  │ (Supabase     │  │
│  │ /upload_    │  │ transcript_      │  │  connector)   │  │
│  │  transcript │  │    parser.py     │  │               │  │
│  │ /courses    │  │                  │  │ OR            │  │
│  │             │  │                  │  │ JSON files    │  │
│  └─────────────┘  └──────────────────┘  └───────────────┘  │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │ SQL Queries / JSON I/O
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                    TIER 3: DATA LAYER                        │
│              (Supabase PostgreSQL / JSON Files)              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Programs    │  │   Courses    │  │ Equivalencies│      │
│  │  Table       │  │   Table      │  │  Table       │      │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤      │
│  │ 800+ programs│  │ 5000+ courses│  │ Equivalency  │      │
│  │ (Majors,     │  │ (credits,    │  │ mappings     │      │
│  │  Minors,     │  │  prereqs,    │  │              │      │
│  │  Certs)      │  │  GenEd)      │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  Fallback: JSON files in /data directory                    │
└──────────────────────────────────────────────────────────────┘
```

### Tier 1: Presentation Layer (Next.js Frontend)

**Technology**: Next.js 14 with React 18, Tailwind CSS

**Responsibilities:**
- Render user interface components (forms, buttons, cards, modals)
- Handle user interactions (clicks, text input, file uploads)
- Validate user input on the client side (check for empty fields, invalid formats)
- Send HTTP requests to backend API using axios
- Display loading states while waiting for server responses
- Show recommendations and detailed program information
- Support responsive layouts for mobile, tablet, and desktop

**Key Components:**
- **Pages**: HomePage (main search page), DetailPage (program details)
- **Components**: SearchForm, FilterButtons, ProgramCard, PrerequisiteTree, LoadingSpinner
- **API Client**: Axios HTTP client configured to communicate with Flask backend

**Benefits of Next.js:**
- Server-side rendering for faster initial page loads
- Automatic code splitting for smaller bundle sizes
- Built-in routing system
- Optimized production builds
- Better SEO than pure client-side React apps

### Tier 2: Business Logic Layer (Flask Backend)

**Technology**: Python 3.8+ with Flask framework

**Responsibilities:**
- Expose REST API endpoints for frontend to consume
- Receive and validate incoming requests
- Load and cache program/course data in memory at startup
- Execute recommendation algorithm (calculate overlap, rank programs)
- Parse PDF transcripts to extract course codes
- Apply prerequisite matching logic (exact, equivalency, hierarchical)
- Calculate recursive prerequisite chains
- Return JSON responses to frontend

**Core Modules:**

1. **app.py** (135 lines)
   - Main Flask application
   - Defines API routes: `/majors`, `/recommend`, `/upload_transcript`, `/courses`
   - Handles CORS (Cross-Origin Resource Sharing) to allow Next.js communication
   - Manages data loading (tries Supabase first, falls back to JSON files)

2. **recommendation_engine.py** (467 lines)
   - Core recommendation algorithm
   - Calculates course overlap between major and programs
   - Applies three-tier prerequisite matching
   - Finds triple-dip optimization opportunities
   - Ranks programs by gap credits
   - Recursively calculates prerequisite chains

3. **transcript_parser.py** (74 lines)
   - Parses PDF transcript files
   - Extracts course codes using regular expressions
   - Returns list of normalized course codes

4. **database.py** (266 lines)
   - Connects to Supabase PostgreSQL database
   - Loads all data into memory at startup for fast access
   - Provides caching layer to maintain performance
   - Falls back to JSON files if Supabase not configured

**API Endpoints:**

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| `/majors` | GET | Get list of all majors | None | JSON array of major names |
| `/recommend` | POST | Get program recommendations | Major, completed courses, GenEd needs | Top 15 ranked recommendations |
| `/upload_transcript` | POST | Parse PDF transcript | PDF file (multipart) | List of extracted course codes |
| `/courses` | GET | Get all course data | None | Full course catalog (for prereq trees) |

### Tier 3: Data Layer (Supabase PostgreSQL)

**Technology**: Supabase (hosted PostgreSQL 14+) with JSON file fallback

**Primary Storage: Supabase PostgreSQL**

Tables:
- **programs** - Stores 800+ academic programs with requirements
- **courses** - Stores 5000+ course definitions with credits, prerequisites, GenEd attributes
- **course_equivalencies** - Maps equivalent courses (e.g., CMPSC 121 ≈ CMPSC 131)
- **prerequisite_config** - Stores configuration for prerequisite matching rules

**Fallback Storage: JSON Files**

Located in `/data` directory:
- `academic_programs_rules.json` - Program requirements (17K lines)
- `world_campus_courses_master.json` - Primary course catalog (9K lines)
- `course_equivalencies.json` - Equivalency mappings (1K lines)
- `prerequisite_config.json` - Prerequisite matching configuration

**Data Loading Strategy:**

```python
# Startup sequence in app.py
1. Try to import database.py (Supabase connector)
2. If successful, try to connect to Supabase and load data
3. If Supabase connection fails, fall back to JSON files
4. If database.py doesn't exist, use JSON files directly
5. Cache all data in memory for fast access during runtime
```

This hybrid approach ensures the system works in both production (with Supabase) and development (with local JSON files) without code changes.

### Key Architectural Patterns:

**1. Three-Tier Separation**
- Clear boundaries between presentation, logic, and data
- Each tier can be modified independently
- Frontend team can work on UI while backend team works on algorithms

**2. In-Memory Caching**
- All data loaded into RAM at startup
- Eliminates database query latency during recommendations
- Trades memory for speed (acceptable for our dataset size)

**3. Hybrid Data Access**
- Primary: Supabase (for production deployment with easy updates)
- Fallback: JSON files (for development and offline work)
- Abstracted through `database.py` module

**4. REST API Communication**
- Stateless HTTP requests between frontend and backend
- JSON data format for easy parsing
- Standard HTTP status codes (200, 400, 500)

**5. Modular Backend**
- Each Python module has single responsibility
- `app.py` handles routing
- `recommendation_engine.py` handles algorithm
- `transcript_parser.py` handles PDF parsing
- `database.py` handles data access

## 2.2 Design Rationale

### Why We Chose This Architecture

**Decision 1: Three-Tier Instead of Two-Tier**

We considered having Next.js directly query the database using Supabase's JavaScript client, eliminating the Flask backend entirely.

**Why we rejected it:**
- Complex recommendation algorithm is better suited for Python (rich libraries, easier math)
- Prerequisite matching logic requires recursive calculations (cleaner in Python)
- PDF parsing requires server-side processing (can't be done in browser)
- Separating business logic from presentation makes testing easier
- Backend can serve multiple frontends (web, mobile app, CLI) in the future

**Trade-off:** Added network latency between Next.js and Flask, but performance is still acceptable (<1 second for recommendations).

**Decision 2: Next.js Instead of Plain React with Vite**

We considered using React with Vite (simpler build tool) instead of Next.js.

**Why Next.js is better:**
- Server-side rendering improves initial page load (critical for SEO and user experience)
- Built-in routing eliminates need for react-router configuration
- Automatic code splitting reduces bundle size
- API routes feature (though we're using Flask instead)
- Production-ready optimizations out of the box
- Better developer experience with hot module replacement

**Trade-off:** Next.js has a steeper learning curve, but the performance and DX benefits justify it.

**Decision 3: Supabase Primary, JSON Fallback**

We considered three options:
1. JSON files only (simplest)
2. Direct PostgreSQL connection
3. Supabase with JSON fallback (chosen)

**Why Supabase with fallback:**
- Supabase provides hosted PostgreSQL with easy setup (no server management)
- Built-in API and authentication if we add user accounts later
- Dashboard for easy data updates without coding
- JSON fallback allows development without internet or database setup
- Fallback ensures system works even if Supabase has downtime
- Migration path: Start with JSON files, move to Supabase when ready

**Trade-off:** Added complexity of supporting two data sources, but the flexibility is worth it.

**Decision 4: In-Memory Caching Instead of Per-Request Queries**

We load all data into RAM at startup instead of querying the database for every recommendation request.

**Why in-memory caching:**
- Our dataset is small enough to fit in memory (800 programs, 5000 courses ≈ 50 MB)
- Eliminates database query latency (from ~100ms to <1ms per lookup)
- Simplifies code (no need for complex database queries)
- Reduces database costs (fewer queries = lower Supabase bills)
- Provides consistent performance regardless of database load

**Trade-off:** Data updates require server restart to refresh cache, but program requirements rarely change.

**Decision 5: Flask Instead of FastAPI or Django**

We considered three Python web frameworks:
- Flask (chosen)
- FastAPI (modern, async)
- Django (full-featured)

**Why Flask:**
- Lightweight and simple (perfect for a small API)
- Team is already familiar with Flask
- Excellent documentation and community support
- Easy to add CORS support with flask-cors
- No unnecessary features (Django's ORM, admin panel not needed)
- Fast enough for our use case (async not required for our workload)

**Trade-off:** Less built-in features than Django, but we don't need them.

**Decision 6: Monolithic Backend Instead of Microservices**

We considered splitting the backend into separate microservices (Recommendation Service, Transcript Service, etc.).

**Why monolithic:**
- Our system is small enough that microservices add unnecessary complexity
- All services share the same data (programs, courses), so separation doesn't help
- Easier deployment (one Flask app vs. managing multiple services)
- Simpler development (no need to coordinate between services)
- Better performance (no network calls between services)
- Team size doesn't justify microservices overhead

**Trade-off:** If the system grows significantly, we might need to split it later, but that's not a concern now.

### Alternatives Considered and Rejected

**Alternative 1: Full-Stack Next.js (API Routes + Frontend)**

Use Next.js API routes for backend instead of separate Flask server.

**Why we rejected it:**
- Next.js API routes use JavaScript/TypeScript, but our algorithm is better suited for Python
- PDF parsing libraries are more mature in Python (pypdf)
- Recommendation engine uses complex recursion (easier in Python)
- Team has stronger Python skills than Node.js
- Mixing frontend and backend in one codebase can get messy

**Alternative 2: Client-Side Only (No Backend)**

Load all data in the browser and calculate recommendations entirely in JavaScript.

**Why we rejected it:**
- Sending 50 MB of course data to every user's browser is wasteful
- Slower performance on mobile devices
- Recommendation algorithm would run slower in JavaScript
- No way to parse PDF transcripts (requires server-side processing)
- Security risk (exposes all data to users, including unpublished programs)

**Alternative 3: GraphQL Instead of REST**

Use GraphQL API instead of REST endpoints.

**Why we rejected it:**
- Our API is simple (only 4 endpoints), GraphQL is overkill
- REST is easier to understand and test
- No complex nested queries that would benefit from GraphQL
- Team is more familiar with REST
- GraphQL adds learning curve without clear benefits for our use case

### Critical Design Decisions

**Decision 1: Three-Tier Prerequisite Matching**

The prerequisite matching system uses three tiers of intelligence instead of just exact matching:
1. Exact match (MATH 140 = MATH 140)
2. Equivalency map (CMPSC 121 = CMPSC 131)
3. Hierarchical rules (MATH 230 satisfies MATH 140 requirement)

**Rationale:** Students often take different but equivalent courses, or higher-level courses that should satisfy lower prerequisites. Without this intelligence, the system would incorrectly flag satisfied prerequisites as missing.

**Decision 2: Recursive Prerequisite Calculation**

When calculating the true cost of a course, we recursively include prerequisites of prerequisites.

**Example:**
```
CMPSC 311 requires:
  - CMPSC 221 (which requires CMPSC 121 (which requires MATH 140))

Total cost: 3 + 3 + 3 + 4 = 13 credits (not just 3)
```

**Rationale:** Students need to know the full commitment, not just the immediate course. Without recursive calculation, recommendations would be misleading.

**Decision 3: Startup Data Loading**

Load all data into memory at Flask startup, not on-demand.

**Rationale:**
- Provides instant responses to users (no database query delays)
- Simplifies code (no async database calls)
- Reduces costs (fewer database queries)
- Acceptable trade-off since data changes infrequently

**Decision 4: Hybrid Supabase/JSON Approach**

Support both database and JSON files simultaneously.

**Rationale:**
- Allows development without setting up database
- Provides disaster recovery (fallback if database fails)
- Eases deployment (works in any environment)
- Migration path from prototype to production

This architecture balances simplicity, performance, and maintainability while providing a clear path for future enhancements.

---

# 3. Key Functionality Design

This section describes the design for our system's five major use cases. For each use case, we provide detailed descriptions, sequence diagrams showing how components interact, structural design showing the modules involved, activity diagrams showing the workflow, and interface specifications.

## 3.1 Upload and Parse Transcript

### 3.1.1 Use Case Description

**Use Case Name**: Upload and Parse PDF Transcript

**Primary Actor**: Student

**Preconditions**:
- Student has accessed the system homepage
- Student has a Penn State transcript PDF file available

**Main Success Scenario**:
1. Student clicks "Upload Transcript" button on search form
2. System displays file picker dialog
3. Student selects PDF transcript file and confirms upload
4. Next.js frontend sends PDF file to Flask backend via HTTP POST to `/upload_transcript`
5. Flask receives file and saves it to temporary `uploads/` directory
6. Flask calls `transcript_parser.parse_transcript_pdf()` function
7. Transcript parser reads PDF using pypdf library
8. Parser extracts course codes using regular expression pattern matching
9. Parser returns list of normalized course codes (e.g., ["CMPSC131", "MATH140", "ENGL15"])
10. Flask deletes temporary PDF file
11. Flask returns JSON response with extracted courses to frontend
12. Frontend populates "Completed Courses" text field with extracted codes
13. Student reviews extracted courses and can edit if needed

**Alternative Flows**:
- **4a**: PDF file too large (>10MB) → System rejects upload and shows error message
- **6a**: PDF is password-protected → Parser fails, system asks student to remove password
- **8a**: PDF doesn't match Penn State format → Parser returns empty list, system warns student
- **8b**: Some course codes malformed → Parser extracts valid codes, skips invalid ones

**Postconditions**:
- Student's completed courses field is populated with extracted course codes
- Student can proceed to get recommendations or manually edit the list
- Temporary PDF file is cleaned up from server

**Success Criteria**:
- At least 90% of course codes correctly extracted from standard Penn State transcripts
- Processing completes in under 3 seconds for typical transcript (1-2 pages)
- No temporary files left on server after processing

### 3.1.2 Sequence Diagram

```
Student    Next.js      Flask        transcript_      File
  |       Frontend     Backend        parser        System
  |          |            |              |             |
  |--Click Upload-------->|              |             |
  |          |            |              |             |
  |<--Show File Picker----|              |             |
  |          |            |              |             |
  |--Select PDF---------->|              |             |
  |          |            |              |             |
  |          |--POST /upload_transcript->|             |
  |          |    (multipart/form-data)  |             |
  |          |            |              |             |
  |          |            |--save(pdf)------------------>|
  |          |            |              |             |
  |          |            |--parse_transcript_pdf()---->|
  |          |            |              |             |
  |          |            |              |--read PDF--->|
  |          |            |              |             |
  |          |            |              |<--PDF data--|
  |          |            |              |             |
  |          |            |              |--regex extract
  |          |            |              |  course codes
  |          |            |              |             |
  |          |            |<--["CMPSC131","MATH140"]---|
  |          |            |              |             |
  |          |            |--delete(pdf)--------------->|
  |          |            |              |             |
  |          |<--{"status":"success",    |             |
  |          |    "courses":["CMPSC131"]}|             |
  |          |            |              |             |
  |<--Populate Form-------|              |             |
  |  (courses displayed)  |              |             |
  |          |            |              |             |
```

### 3.1.3 Structural Design

**Python Modules and Functions Involved**:

```python
# app.py (Flask Backend)
@app.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    """
    Receives PDF file, parses it, returns course list.

    Input: PDF file (multipart/form-data)
    Output: JSON {"status": "success", "courses": [...]}
    """
    # 1. Validate file exists in request
    # 2. Save file to uploads/ directory
    # 3. Call transcript_parser.parse_transcript_pdf()
    # 4. Delete temporary file
    # 5. Return JSON response

# transcript_parser.py
def parse_transcript_pdf(filepath):
    """
    Extract course codes from Penn State transcript PDF.

    Args:
        filepath (str): Path to PDF file

    Returns:
        list: Normalized course codes (e.g., ["CMPSC131", "MATH140"])

    Algorithm:
        1. Open PDF using pypdf.PdfReader
        2. Extract text from each page
        3. Use regex to find course codes: r"([A-Z]{2,5}\s+\d{1,4}[A-Z]?)"
        4. Normalize codes (remove spaces, uppercase)
        5. Deduplicate and return sorted list
    """

def normalize_code(code):
    """
    Normalize course code to standard format.

    Args:
        code (str): Raw course code (e.g., "CMPSC 131" or "cmpsc 131")

    Returns:
        str: Normalized code (e.g., "CMPSC131")
    """
    return code.replace(" ", "").replace("\xa0", "").upper()
```

**Data Structures**:

```python
# Request (multipart/form-data)
{
    "file": <binary PDF data>
}

# Response (JSON)
{
    "status": "success",
    "courses": ["CMPSC131", "MATH140", "ENGL15", ...]
}

# Error Response (JSON)
{
    "error": "No file part"  # or other error message
}
```

### 3.1.4 Activity Diagram

```
┌─ START: Student Has Transcript PDF ─┐
│                                      │
▼                                      │
[Student Clicks Upload Button]        │
│                                      │
▼                                      │
[System Shows File Picker]            │
│                                      │
▼                                      │
[Student Selects PDF File]            │
│                                      │
▼                                      │
<Is File Size < 10MB?>────NO────>│[Show Error: File Too Large]──┐
│ YES                              │                              │
▼                                  │                              │
[Frontend Sends PDF to Backend]    │                              │
│                                  │                              │
▼                                  │                              │
[Backend Saves File to uploads/]   │                              │
│                                  │                              │
▼                                  │                              │
[Call transcript_parser Module]    │                              │
│                                  │                              │
▼                                  │                              │
[Open PDF with pypdf Library]      │                              │
│                                  │                              │
▼                                  │                              │
<Is PDF Readable?>─────NO─────────>│[Return Empty List + Warning]─┤
│ YES                              │                              │
▼                                  │                              │
[Extract Text from All Pages]      │                              │
│                                  │                              │
▼                                  │                              │
[Apply Regex to Find Course Codes] │                              │
│                                  │                              │
▼                                  │                              │
[Normalize Codes (Uppercase, No Spaces)]                          │
│                                  │                              │
▼                                  │                              │
[Deduplicate Course Codes]         │                              │
│                                  │                              │
▼                                  │                              │
[Delete Temporary PDF File]        │                              │
│                                  │                              │
▼                                  │                              │
[Return Course List to Frontend]   │                              │
│                                  │                              │
▼                                  │                              │
[Frontend Populates Text Field]    │                              │
│                                  │                              │
▼                                  │                              │
[Student Reviews Extracted Courses]│                              │
│                                  │                              │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
                   [END: Courses Ready for Recommendations]
```

### 3.1.5 Software Interface

**Input Interface**:

```
HTTP POST /upload_transcript
Content-Type: multipart/form-data

Field "file": Binary PDF data
```

**Output Interface**:

```javascript
// Success Response
{
  "status": "success",
  "courses": [
    "CMPSC131",
    "MATH140",
    "ENGL15",
    "ECON102",
    ...
  ]
}

// Error Response (HTTP 400)
{
  "error": "No file part"
}

// Error Response (HTTP 400)
{
  "error": "No selected file"
}
```

**Dependencies**:
- **Frontend**: Next.js FormData API for file upload, axios for HTTP request
- **Backend**: Flask `request.files` for receiving upload, `os` module for file operations
- **Library**: `pypdf` (Python PDF parsing library)

**Error Handling**:
- Missing file → HTTP 400, JSON error response
- Invalid PDF format → Return empty list with warning flag
- File system errors → Try to delete temp file in finally block, return error response

---

## 3.2 Generate Course Recommendations

### 3.2.1 Use Case Description

**Use Case Name**: Calculate and Display Program Recommendations

**Primary Actor**: System (triggered by student's input submission)

**Preconditions**:
- Student has selected a major from dropdown
- Student has entered completed courses (manually or via transcript upload)
- All course codes have been validated

**Main Success Scenario**:
1. Student clicks "Get Recommendations" button
2. Next.js frontend collects form data (major, completed courses, Gen Ed needs)
3. Frontend sends HTTP POST to `/recommend` with JSON payload
4. Flask backend receives request and extracts parameters
5. Backend loads cached program and course data from memory
6. Backend calls `recommendation_engine.get_prescribed_major_courses()` to get student's major courses
7. Backend combines completed courses + major courses into full history
8. Backend loops through all programs in database
9. For each program:
   - Call `calculate_program_gap()` → returns additional credits needed
   - Call `find_triple_dips()` → returns Gen Ed optimization opportunities
   - Call `calculate_overlap_count()` → returns number of overlapping courses
10. Backend creates recommendation object for each program with all calculated metrics
11. Backend sorts programs by gap credits (lowest first), then by overlap count (highest first)
12. Backend returns top 15 recommendations as JSON array
13. Frontend receives recommendations and renders results in ProgramCard components
14. Student views ranked recommendations with overlap and gap information

**Alternative Flows**:
- **4a**: Invalid major selected → Return HTTP 400 error
- **4b**: Empty course history → Still generate recommendations (all programs will have high gaps)
- **9a**: Program type doesn't match interest filter → Skip program, don't include in results

**Postconditions**:
- Student sees top 15 recommended programs sorted by best fit
- Each recommendation shows program name, type, overlap count, and gap credits
- Student can click any recommendation to view details

**Success Criteria**:
- Recommendations generated in under 5 seconds for full program database
- Results accurately reflect course overlap (verified against manual calculation)
- Programs with more overlap ranked higher than those with less

### 3.2.2 Sequence Diagram

```
Student   Next.js    Flask    recommendation_    Supabase/
  |      Frontend   Backend      engine          JSON Files
  |         |          |             |                |
  |--Click Get Recommendations------>|                |
  |         |          |             |                |
  |         |--POST /recommend------>|                |
  |         |   {major, courses,     |                |
  |         |    genEd, filter}      |                |
  |         |          |             |                |
  |         |          |--PROGRAMS (from memory cache)|
  |         |          |--COURSES  (loaded at startup)|
  |         |          |--EQUIV_MAP                   |
  |         |          |             |                |
  |         |          |--get_prescribed_major_courses()
  |         |          |             |                |
  |         |          |<--[major courses list]-------|
  |         |          |             |                |
  |         |          |--combine(completed + major)  |
  |         |          |             |                |
  |         |          |--FOR each program in PROGRAMS|
  |         |          |             |                |
  |         |          |--calculate_program_gap()---->|
  |         |          |             |                |
  |         |          |             |--check each required course
  |         |          |             |--apply prerequisite logic
  |         |          |             |--calculate recursive costs
  |         |          |             |                |
  |         |          |<--{gap: 12.0, missing: [...]}|
  |         |          |             |                |
  |         |          |--find_triple_dips()--------->|
  |         |          |             |                |
  |         |          |             |--match GenEd attributes
  |         |          |             |--find overlaps
  |         |          |             |                |
  |         |          |<--[optimization opportunities]|
  |         |          |             |                |
  |         |          |--calculate_overlap_count()-->|
  |         |          |             |                |
  |         |          |<--{overlap: 5, courses: [...]}
  |         |          |             |                |
  |         |          |--END FOR each program        |
  |         |          |             |                |
  |         |          |--sort(gap ASC, overlap DESC) |
  |         |          |             |                |
  |         |          |--slice(top 15 results)       |
  |         |          |             |                |
  |         |<--{"status":"success",  |                |
  |         |    "recommendations":[...]               |
  |         |          |             |                |
  |<--Display Results--|             |                |
  |  (ProgramCards)    |             |                |
  |         |          |             |                |
```

### 3.2.3 Structural Design

**Key Python Functions**:

```python
# recommendation_engine.py

def get_prescribed_major_courses(major_name, programs_db):
    """
    Get all required courses for a student's major.

    Args:
        major_name (str): Student's major (e.g., "SOFTWARE ENGINEERING")
        programs_db (list): List of all program dictionaries

    Returns:
        list: Normalized course codes required for major
    """

def calculate_program_gap(program, user_history, courses_db,
                         major_courses, equiv_map, prereq_config):
    """
    Calculate additional credits needed to complete a program.

    Args:
        program (dict): Program requirements dictionary
        user_history (list): Student's completed courses
        courses_db (dict): Course catalog
        major_courses (list): Courses from student's major
        equiv_map (dict): Course equivalency mappings
        prereq_config (dict): Prerequisite matching rules

    Returns:
        tuple: (gap_credits, missing_courses_list)

    Algorithm:
        1. Get all required courses from program
        2. For each required course:
           a. Check if student has it (exact match)
           b. Check equivalency map
           c. Check hierarchical rules
           d. If not satisfied, mark as missing
        3. For each missing course:
           a. Get credit value
           b. Recursively check prerequisites
           c. Calculate total cost (course + prerequisites)
        4. Sum all costs, return total gap
    """

def find_triple_dips(program, gen_ed_needs, courses_db, user_history):
    """
    Find courses that satisfy major + program + GenEd requirements.

    Args:
        program (dict): Program being evaluated
        gen_ed_needs (list): GenEd categories student still needs
        courses_db (dict): Course catalog with GenEd attributes
        user_history (list): Courses student has completed

    Returns:
        list: Triple-dip opportunities with explanations
    """

def calculate_overlap_count(program, user_history, major_courses):
    """
    Count courses that satisfy both major and program requirements.

    Args:
        program (dict): Program being evaluated
        user_history (list): Student's completed courses
        major_courses (list): Courses from student's major

    Returns:
        tuple: (overlap_count, overlap_course_list)
    """

def course_satisfies_prerequisite(required_code, user_history,
                                 equiv_map, prereq_config):
    """
    Three-tier intelligent prerequisite checking.

    Tier 1: Exact match
    Tier 2: Equivalency map
    Tier 3: Hierarchical rules (higher-level satisfies lower)

    Returns:
        bool: True if prerequisite satisfied
    """
```

**Data Structures**:

```python
# Recommendation Object
{
    "id": "MATHEMATICS",
    "program_name": "MATHEMATICS",
    "program_type": "Minor",
    "program_url": "https://bulletins.psu.edu/...",
    "gap_credits": 12.0,
    "missing_courses": [
        {
            "code": "MATH 311",
            "title": "Concepts of Discrete Mathematics",
            "credits": 3.0,
            "total_cost": 3.0,
            "prerequisites": []
        },
        ...
    ],
    "optimizations": [
        "STAT 200 counts for your major, this minor, AND GQ Gen Ed"
    ],
    "optimization_count": 1,
    "overlap_count": 5,
    "overlap_courses": ["MATH 140", "MATH 141", ...]
}
```

### 3.2.4 Activity Diagram

```
┌─ START: Student Submits Form ─┐
│                                │
▼                                │
[Extract Form Data]              │
(major, courses, GenEd needs)    │
│                                │
▼                                │
[Send POST to /recommend]        │
│                                │
▼                                │
[Backend Receives Request]       │
│                                │
▼                                │
[Load Cached Data from Memory]   │
(PROGRAMS, COURSES, EQUIV_MAP)   │
│                                │
▼                                │
[Get Major Required Courses]     │
│                                │
▼                                │
[Combine: Completed + Major Courses]
│                                │
▼                                │
[Initialize Results List]        │
│                                │
▼                                │
┌─────[FOR EACH PROGRAM]─────────┤
│   │                            │
│   ▼                            │
│   <Matches Interest Filter?>───NO─┐(Skip)
│   │ YES                        │   │
│   ▼                            │   │
│   [Calculate Gap Credits]      │   │
│   (check each required course) │   │
│   │                            │   │
│   ▼                            │   │
│   [Find Triple-Dip Opportunities]  │
│   (match GenEd attributes)     │   │
│   │                            │   │
│   ▼                            │   │
│   [Calculate Overlap Count]    │   │
│   (courses in both major & program)│
│   │                            │   │
│   ▼                            │   │
│   [Create Recommendation Object]   │
│   │                            │   │
│   ▼                            │   │
│   [Add to Results List]        │   │
│   │                            │   │
└───[END FOR]◄──────────────────────┘
    │
    ▼
[Sort Results]
(by gap ASC, overlap DESC)
    │
    ▼
[Take Top 15 Results]
    │
    ▼
[Return JSON Response]
    │
    ▼
[Frontend Renders ProgramCards]
    │
    ▼
[END: Student Views Recommendations]
```

### 3.2.5 Software Interface

**Input Interface**:

```javascript
// POST /recommend
{
  "history": ["CMPSC131", "MATH140", "ENGL15"],  // completed courses
  "major": "SOFTWARE ENGINEERING",                 // selected major
  "gen_ed_needs": ["GN", "GS", "GH"],             // GenEd categories needed
  "interest_filter": "Minor"                       // filter: "Minor"/"Certificate"/"All"
}
```

**Output Interface**:

```javascript
// Success Response
{
  "status": "success",
  "count": 15,
  "recommendations": [
    {
      "id": "MATHEMATICS",
      "program_name": "MATHEMATICS",
      "program_type": "Minor",
      "program_url": "https://bulletins.psu.edu/...",
      "gap_credits": 12.0,
      "missing_courses": [...],
      "optimizations": ["STAT 200 counts for major + minor + GQ GenEd"],
      "optimization_count": 1,
      "overlap_count": 5,
      "overlap_courses": ["MATH140", "MATH141", "MATH230", ...]
    },
    // ... 14 more recommendations
  ]
}
```

**Dependencies**:
- Cached data: PROGRAMS, COURSES, EQUIV_MAP, PREREQ_CONFIG (loaded at startup)
- Python modules: `recommendation_engine.py` for all calculations
- Flask: `request.json` for parsing JSON body

**Performance Constraints**:
- Must complete in under 5 seconds for all 800+ programs
- Achieved through in-memory caching (no database queries during calculation)

---

