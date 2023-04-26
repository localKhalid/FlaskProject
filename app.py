from flask import Flask, render_template, request, jsonify
import os
import boto3
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/handle_information', methods=['POST'])
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

    # Map priority values to queue names
    queue_names = {
        'high_priority': 'High',
        'medium_priority': 'MediumLow',
        'low_priority': 'MediumLow'
    }

    # Send message to the appropriate queue
    queue_name = queue_names.get(priority)
    if queue_name:
        try:
            # Create an SQS client
            sqs = boto3.client('sqs', region_name='eu-north-1')

            # Send message to the queue
            response = sqs.send_message(
                QueueUrl=os.environ.get('SQS_QUEUE_URL_PREFIX') + queue_name,
                MessageBody=json.dumps(bug_form)
            )

            return jsonify({'message': 'Bug information submitted successfully', 'MessageId': response['MessageId']}), 200

        except Exception as e:
            return jsonify({'error': 'Failed to submit bug information to the queue', 'details': str(e)}), 500

    else:
        return jsonify({'error': 'Invalid priority value', 'details': 'Priority value selected in the form is not valid'}), 400

if __name__ == '__main__':
    app.run(debug=True)
