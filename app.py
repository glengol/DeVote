from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import matplotlib.pyplot as plt
import numpy as np
import os
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection string
client = MongoClient("mongodb://root:root@mongo:27017/votes_collection?authSource=admin")
db = client.votes_collection 
votes_collection = db.votes 
comment_collection = db.comment
UPLOAD_FOLDER = 'static/uploads'  # Define the folder to save chart images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dictionary to hold cloud providers and their services
cloud_services = {
    "AWS": ["EC2", "S3", "Lambda", "RDS", "DynamoDB", "ECS", "CloudFront", "Route 53", "SQS", "SNS"],
    "GCP": ["Compute Engine", "Cloud Storage", "Cloud Functions", "Cloud SQL", "BigQuery", "App Engine", "Pub/Sub", "Cloud Run", "Kubernetes Engine", "Cloud Spanner"],
    "Azure": ["Virtual Machines", "Blob Storage", "Functions", "SQL Database", "Cosmos DB", "App Services", "Service Bus", "Kubernetes Service", "Front Door", "Event Grid"],
    "Alibaba Cloud": ["ECS", "OSS", "Function Compute", "RDS", "Table Store", "Container Service", "CDN", "DNS", "Message Service", "MQTT"],
    "Oracle Cloud": ["Compute", "Object Storage", "Functions", "Autonomous Database", "NoSQL Database", "Kubernetes Engine", "API Gateway", "Load Balancer", "Streaming", "Data Integration"]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    name = request.form.get('name')
    if votes_collection.count_documents({"name": name}) > 0 or votes_collection.count_documents({"name": name}) > 0:
        return render_template('index.html', already_voted=True)

    return render_template('vote_cloud.html', name=name, cloud_providers=list(cloud_services.keys()))


@app.route('/vote_cloud', methods=['POST'])
def vote_cloud():
    name = request.form.get('name')
    cloud = request.form.get('choice_Which cloud provider do you prefer?')
    if cloud in cloud_services:
        services = cloud_services[cloud]
        return render_template('vote_services.html', name=name, cloud=cloud, services=services)
    else:
        return redirect(url_for('index'))

@app.route('/submit_cloud_vote', methods=['POST'])
def submit_cloud_vote():
    name = request.form.get('name')
    cloud = request.form.get('cloud')
    selected_services = request.form.getlist('services')
    comment = request.form.get('comment')
    is_public = request.form.get('public') == 'true'

    for service in selected_services:
        vote = {
            "name": name,
            "cloud": cloud,
            "service": service,
        }
        votes_collection.insert_one(vote) 

    comment = {
        "name": name,
        "comment": comment,
        "is_public": is_public,
        "services": selected_services,
    }
    comment_collection.insert_one(comment) 
    return redirect(url_for('results'))

@app.route('/results')
def results():
    # Calculate vote results
    results = {}
    for cloud, services in cloud_services.items():
        results[cloud] = {service: votes_collection.count_documents({"cloud": cloud, "service": service}) for service in services}
        # Ensure all services have a count, even if zero
        for service in services:
            if service not in results[cloud]:
                results[cloud][service] = 0
    
    # Generate and save pie charts
    chart_paths = {}
    for cloud, result in results.items():
        items = [(label,value) for label, value in result.items() if value > 0]
        labels = [label for label, _ in items]
        values = [value for _, value in items]


        # Check for NaN values in values list
        if not all(isinstance(val, (int, float)) and not np.isnan(val) for val in values):
            continue  # Skip generating chart if any NaN values are present
        #return str(values) + str(labels)
        fig = plt.figure()
        plt.pie(values,labels=labels)#, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')

        # Save chart to file
        chart_filename = f"{cloud.replace(' ', '_')}_chart.png"
        chart_path = os.path.join(app.config['UPLOAD_FOLDER'], chart_filename)
        plt.savefig(chart_path)
        plt.close(fig)

        chart_paths[cloud] = chart_filename
    
    
    
    # Fetch last 10 public comments
    public_comments = comment_collection.find({"is_public": True}).sort("_id", -1).limit(10)
    
    return render_template('results.html', results=results, chart_paths=chart_paths, comments=public_comments)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
