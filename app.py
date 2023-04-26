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
            # Construct the queue URL
            queue_url = sqs.get_queue_url(QueueName=os.environ.get('SQS_QUEUE_URL_PREFIX') + queue_name)['QueueUrl']

            # Send message to the queue with a 10-second delay
            response = sqs.send_message(
                QueueUrl=queue_url,
                DelaySeconds=10,
                MessageBody=json.dumps(bug_form)
            )

            return jsonify({'message': 'Bug information submitted successfully', 'MessageId': response['MessageId']}), 200

        except Exception as e:
            return jsonify({'error': 'Failed to submit bug information to the queue', 'details': str(e)}), 500

    else:
        return jsonify({'error': 'Invalid priority value', 'details': 'Priority value selected in the form is not valid'}), 400

@app.route('/createQueues', methods=['GET'])
def create_queues():
    # Create the High priority queue
    sqs.create_queue(QueueName='High')
    # Create the Medium/Low priority queue
    sqs.create_queue(QueueName='MediumLow')
    # Create the Dead Letter Queue (DLQ)
    sqs.create_queue(QueueName='DLQ')

    return jsonify({'message': 'Queues created successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
