import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import recommendation_engine as engine
import transcript_parser
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configuration for Uploads
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

print("⏳ Starting Server...")
try:
    # Now loads the enriched file defined in the engine
    PROGRAMS, COURSES = engine.load_data()
    MAJOR_LIST = sorted([p['id'] for p in PROGRAMS if p['type'] == 'Majors'])
    print(f"✅ Server Ready! Loaded {len(MAJOR_LIST)} majors.")
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    PROGRAMS, COURSES, MAJOR_LIST = [], {}, []

@app.route('/majors', methods=['GET'])
def get_majors():
    return jsonify(MAJOR_LIST)

@app.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        courses = transcript_parser.parse_transcript_pdf(filepath)
        try: os.remove(filepath)
        except: pass
        return jsonify({"status": "success", "courses": courses})

# VALIDATION ENDPOINT
@app.route('/api/student/input', methods=['POST'])
def process_student_input():
    try:
        data = request.json
        if not data: return jsonify({"status": "invalid", "errors": ["No data provided"]}), 400

        raw_history = data.get('courseList', []) 
        user_major = data.get('major', '')
        
        normalized_history = []
        invalid_courses = []
        
        for raw_code in raw_history:
            norm_code = engine.normalize_code(raw_code)
            # Check existence in Universe (COURSES)
            if engine.get_course_credits(norm_code, COURSES) > 0:
                normalized_history.append(norm_code)
            else:
                invalid_courses.append(raw_code)

        if invalid_courses:
            return jsonify({
                "status": "invalid",
                "errors": [f"Course not found: {c}" for c in invalid_courses],
                "suggestions": "Please check course codes."
            }), 200 

        user_gen_ed_needs = data.get('gen_ed_needs', [])
        interest_filter = data.get('interest_filter', 'Minor')

        major_courses = engine.get_prescribed_major_courses(user_major, PROGRAMS)
        combined_history = list(set(normalized_history + major_courses))
        
        results = []
        for prog in PROGRAMS:
            if interest_filter.lower() not in prog['type'].lower(): continue
            
            gap, missing = engine.calculate_program_gap(prog, combined_history, COURSES, major_courses)
            triple_dips = engine.find_triple_dips(prog, user_gen_ed_needs, COURSES)
            
            results.append({
                "id": prog['id'],
                "program_name": prog['id'],
                "program_url": prog.get('url', '#'),
                "gap_credits": gap,
                "missing_courses": missing,
                "optimizations": triple_dips,
                "optimization_count": len(triple_dips)
            })

        results.sort(key=lambda x: (x['gap_credits'], -x['optimization_count']))

        return jsonify({
            "status": "valid",
            "studentData": { "history_count": len(normalized_history) },
            "recommendations": results[:15]
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)