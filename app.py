from flask import Flask, request, render_template, jsonify
import json
import os
from flask_cors import CORS


app = Flask(__name__, template_folder='.')

CORS(app)

@app.route("/")
def home():
    return render_template('upload_form.html')


@app.route('/api/handle_information', methods=['POST'])
def handle_information():
    name = request.form.get('bug')
    priority = request.form.get('priority')
    additional_info = request.form.get('additional_info')

    # Validate form data
    bug_form = {
        'bug': name,
        'priority': priority,
        'additional_info': additional_info
    }

    # Map priority values from form to filenames
    priority_mapping = {
        'high_priority': 'high_priority.json',
        'medium_priority': 'medium_priority.json',
        'low_priority': 'low_priority.json'
    }

    # Get the filename based on priority
    filename = priority_mapping.get(priority)

    if filename is not None:
        # Append the JSON data to the appropriate file
        with open(filename, 'a') as file:
            json.dump(bug_form, file)
            file.write('\n')  # Add newline to separate JSON objects

        # SEND INFORMATION TO ANOTHER API?????
        return jsonify({'message':f'Your bug form has been accepted, Thank you'}), 200
    else:
        return jsonify({'error': 'Invalid priority value'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=80)
