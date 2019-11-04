#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# before running the following code it is necessary to create a google cloud project
# it is also necessary to create a service account and associate with above project.  Save the key to your machine
# console.cloud.google.com/iam-admin/serviceaccounts


import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/blaine.brewer/Documents/Python/CloudComputingBCTV/GoogleCloud/Keys/cloudcomputingbctv-b548c53b3cf0.json'
print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])


# In[25]:


import google.cloud
from google.cloud import storage

def create_bucket(project_name, bucket_name):
    client = storage.Client(project = project_name)
    bucket = client.create_bucket(bucket_name)


# In[28]:


create_bucket('CloudComputingBCTV', 'bctv-test-bucket')


# In[37]:


project_name = 'CloudComputingBCTV'
client = storage.Client(project = project_name)
bucket = client.get_bucket('bctv-test-bucket')

print(dir(storage.Blob))

#print(dir(bucket))


# In[29]:


from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


# In[38]:


from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_file_name):
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_file_name)
    
    blob.upload_from_filename(source_file_name)


# In[39]:


upload_blob('bctv-test-bucket', 'C:/Users/blaine.brewer/Documents/Python/CloudComputingBCTV/beta_derivative.py', 'testPython.py')

