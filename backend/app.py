import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import recommendation_engine as engine
import transcript_parser
import traceback

app = Flask(__name__)
CORS(app)

# Configuration for Uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

print("⏳ Starting Server...")
try:
    PROGRAMS, COURSES, EQUIV_MAP, PREREQ_CONFIG = engine.load_data()
    MAJOR_LIST = sorted([p['id'] for p in PROGRAMS if p['type'] == 'Majors'])
    print(f"✅ Server Ready! Loaded {len(MAJOR_LIST)} majors.")
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    PROGRAMS, COURSES, EQUIV_MAP, PREREQ_CONFIG, MAJOR_LIST = [], {}, {}, {}, []

@app.route('/majors', methods=['GET'])
def get_majors():
    return jsonify(MAJOR_LIST)

@app.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    """
    Receives a PDF file, parses it, and returns the list of courses.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Parse the PDF
        courses = transcript_parser.parse_transcript_pdf(filepath)
        
        # Clean up (optional: delete file after parsing)
        try:
            os.remove(filepath)
        except:
            pass
            
        return jsonify({"status": "success", "courses": courses})

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        if not data: return jsonify({"error": "No data"}), 400

        user_history = [engine.normalize_code(c) for c in data.get('history', [])]
        user_major = data.get('major', '')
        user_gen_ed_needs = data.get('gen_ed_needs', [])
        interest_filter = data.get('interest_filter', 'Minor')

        major_courses = engine.get_prescribed_major_courses(user_major, PROGRAMS)
        combined_history = list(set(user_history + major_courses))
        
        print(f"🔎 Analyzing {len(user_history)} completed + {len(major_courses)} major courses.")

        results = []
        for prog in PROGRAMS:
            if interest_filter.lower() not in prog['type'].lower(): continue
            
            gap, missing = engine.calculate_program_gap(prog, combined_history, COURSES, major_courses, EQUIV_MAP, PREREQ_CONFIG)
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
            "status": "success",
            "count": len(results),
            "recommendations": results[:15]
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)