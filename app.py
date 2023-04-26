from flask import Flask, request, render_template, jsonify
import json
import os
import boto3

app = Flask(__name__, template_folder='.')

# Create an SQS client
sqs = boto3.client('sqs', region_name='eu-north-1')

@app.route("/")
def home():
    return render_template('upload_form.html')

@app.route('/createQueues', methods=['GET'])
def create_queues():
    # Create the High priority queue
    sqs.create_queue(QueueName='High')
    # Create the Medium/Low priority queue
    sqs.create_queue(QueueName='MediumLow')
    # Create the Dead Letter Queue (DLQ)
    sqs.create_queue(QueueName='DLQ')

    return jsonify({'message': 'Queues created successfully'}), 200

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
    priority_mapping = {
        'high_priority': 'High',
        'medium_priority': 'MediumLow',
        'low_priority': 'MediumLow'
    }

    # Get the queue name based on priority
    queue_name = priority_mapping.get(priority)

    if queue_name is not None:
        # Send the JSON data to the appropriate SQS queue
        sqs.send_message(
            QueueUrl=f'https://sqs.{os.environ.get("AWS_REGION", "eu-north-1")}.amazonaws.com/301073929141/{queue_name}',
            MessageBody=json.dumps(bug_form)
        )

        # SEND INFORMATION TO ANOTHER API?????
        return jsonify({'message': 'Your bug form has been accepted. Thank you'}), 200
    else:
        return jsonify({'error': 'Invalid priority value'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
