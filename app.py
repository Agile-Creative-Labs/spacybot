from flask import Flask, request, jsonify, session, render_template
import spacy

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the Spacy model
nlp = spacy.load('en_core_web_sm')

# Define conversation flow
conversation_flow = [
    {"key": "name", "message": "Nice to meet you, ! Can you tell me about your skills?"},
    {"key": "skills", "message": "Great! Now, could you describe your work experience?"},
    {"key": "experience", "message": "Thanks! Finally, what is your educational background?"},
    {"key": "education", "message": "Thank you! Here's a summary of the information you've provided:"}
]

def extract_entities(text):
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ == "DATE":
            entities['EXPERIENCE'] = ent.text
        elif ent.label_ == "ORG":
            entities['EDUCATION'] = ent.text
        elif ent.label_ == "SKILLS":
            entities['SKILLS'] = ent.text
    return entities

@app.route('/')
def index():
    session.clear()
    #session['step_index'] = 0
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_step():
    user_input = request.json.get('user_input', '').strip()
    step_index = session.get('step_index', 0)
    
    # Initialize response_message
    response_message = ""
    
    # Get current step message
    step_key = conversation_flow[step_index]["key"]
    entities = extract_entities(user_input)
    
    if step_key == "name":
        session['name'] = user_input
        response_message = conversation_flow[step_index]["message"]
    
    elif step_key == "skills":
        session['skills'] = entities.get('SKILLS', user_input)
        response_message = conversation_flow[step_index]["message"]
    
    elif step_key == "experience":
        session['experience'] = entities.get('EXPERIENCE', user_input)
        response_message = conversation_flow[step_index]["message"]
    
    elif step_key == "education":
        session['education'] = entities.get('EDUCATION', user_input)
        # Build summary string after the last step
        summary_text = (
            "Thank you! Here's a summary of the information you've provided:\n\n"
            f"**Name:** {session.get('name', 'N/A')}\n"
            f"**Skills:** {session.get('skills', 'N/A')}\n"
            f"**Experience:** {session.get('experience', 'N/A')}\n"
            f"**Education:** {session.get('education', 'N/A')}"
        )
        response_message = summary_text
        session.clear()  # Clear session after summary

    # Set up next step if not at the end
    if step_index + 1 < len(conversation_flow) and step_key != "education":
        session['step_index'] = step_index + 1
    
    return jsonify({"summary": response_message})

if __name__ == '__main__':
    app.run(debug=True)
