# 7346_Cloud_Automation

### ML Models to deploy and run in Cloud
* `ml_code\malware\train.py`
    * Create a pkl file in models directory

How to access your enviornment variable
```
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

print(os.getenv("AWS_ACCESS_ID"))
print(os.getenv("AWS_SECRET_ACCESS_KEY"))
```