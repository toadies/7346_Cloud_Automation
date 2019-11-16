
import os
# inFile = open('/tmp/bucket/requirements.txt')
# for line in inFile:
# 	os.system('pip install ${line}')


from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split	

import pandas

#train_loc = "c:/users/blaine.brewer/documents/python/cloudcomputingbctv/iris_train.csv"
#test_loc = "c:/users/blaine.brewer/documents/python/cloudcomputingbctv/iris_test.csv"

train_loc = "/tmp/bucket/iris_train.csv"
test_loc = "/tmp/bucket/iris_test.csv"

#Load the data set
train_data = pandas.read_csv(train_loc)
test_data = pandas.read_csv(test_loc)

# X = feature values, all the columns except the last column
x_train = train_data.iloc[:, 1:]
x_test = test_data.iloc[:, 1:]

print("xtrain dims ", x_train.shape)
print("xtest dim", x_test.shape)

# y = target values, last column of the data frame
y_train = train_data.iloc[:, 0]
y_test = test_data.iloc[:, 0]
# #Train the model
model = LogisticRegression()
model.fit(x_train, y_train) #Training the model


#Test the model
predictions = model.predict(x_test)
pred_frame = {'Predictions':predictions}
pred_df = pandas.DataFrame(pred_frame)

# csv_path = "c:/users/blaine.brewer/documents/python/cloudcomputingbctv/predictions.csv"
csv_path = "/tmp/output/predictions.csv"

pred_df.to_csv(csv_path)

# txt_path = "c:/users/blaine.brewer/documents/python/cloudcomputingbctv/prediction_accuracy.txt"
txt_path = "/tmp/output/prediction_accuracy.txt"
pa_file = open(txt_path,"w")
print(classification_report(y_test, predictions))
pa_file.write(classification_report(y_test, predictions))
pa_file.close()
  