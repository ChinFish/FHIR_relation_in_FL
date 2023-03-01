import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
import pandas as pd

'''Training'''
# load the boston dataset
data_url = "http://lib.stat.cmu.edu/datasets/boston"
raw_df = pd.read_csv(data_url, sep="\s+", skiprows=22, header=None)
data = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
target = raw_df.values[1::2, 2]
# defining feature matrix(X) and response vector(y)
X = data
y = target

# splitting X and y into training and testing sets

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4,
                                                    random_state=1)

# create linear regression object
reg = LinearRegression()

# train the model using the training sets
reg.fit(X_train, y_train)

# regression coefficients
# print('Coefficients: ', reg.coef_)

# variance score: 1 means perfect prediction
# print('Variance score: {}'.format(reg.score(X_test, y_test)))

'''load model test'''
# save model
pickle.dump(reg, open('model.sav', 'wb'))
# load model
load_model = pickle.load(open('model.sav', 'rb'))
print(load_model.score(X_test,y_test))


# update model parameters(coefficient and interpretation)
load_model.coef_ *= 2
# print(load_model.coef_)
# print(load_model.score(X_test, y_test))
