from flask import Flask, request, json
import boto3
import joblib
from io import BytesIO
BUCKET_NAME = 'iris-train-12746b8f-be9f-4ef8-8c06-38323c33c122'
MODEL_FILE_NAME = 'model/iris-rf.pkl'
LABEL_FILE_NAME = 'model/iris-labels.pkl'

def load_model(key):    
    # Load model from S3 bucket
    response = S3.get_object(Bucket=BUCKET_NAME, Key=key)
    # Load pickle model
    model_str = response['Body'].read()   
    model = joblib.load(BytesIO(model_str)) 
    
    return model

app = Flask(__name__)

S3 = boto3.client('s3')

@app.route('/', methods=['POST'])
def index():    
    # Parse request body for model input 
    body_dict = request.get_json(force=True)
    data = body_dict['data']     
    
    # Load model
    model = load_model(MODEL_FILE_NAME)
    le = load_model(LABEL_FILE_NAME)
# Make prediction 
    prediction = model.predict(data).tolist()
# Respond with prediction result
    result = {'prediction': le.inverse_transform(prediction).tolist()}    
   
    return json.dumps(result)

if __name__ == '__main__':    
    # listen on all IPs 
    app.run(host='0.0.0.0')
