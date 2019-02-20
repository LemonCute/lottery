from numpy import array
from numpy import hstack
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from sklearn import preprocessing 
import pandas as pd
import numpy as np 

# split a multivariate sequence into samples
def split_sequences(sequences, n_steps):
    X, y = list(), list()
    for i in range(len(sequences)):
        # find the end of this pattern
        end_ix = i + n_steps
        # check if we are beyond the dataset
        if end_ix > len(sequences)-1:
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = sequences[i:end_ix, :], sequences[end_ix, :]
        X.append(seq_x)
        y.append(seq_y)
    return array(X), array(y)

# ��ȡ����3D���н���¼
data = pd.read_csv('d:\\quantrading\\3D_record.csv')
data['date'] = pd.to_datetime(data['date'])
# ѡȡ����1000���н���¼��Ϊ����
data=data[4080:5080]

#x,y,z��������ͨ����ʽ��
x=np.array(data['x'])
y=np.array(data['y'])
z=np.array(data['z'])    

in_seq1 = x.reshape((len(x), 1))
in_seq2 = y.reshape((len(y), 1))
in_seq3 = z.reshape((len(z), 1))

# �ϲ��������������н���dataset
dataset = hstack((in_seq1, in_seq2, in_seq3))
# ��ȫ�����ݽ���4:1�������з֣�80%��������ѵ��������20%������������
train_size = int(len(dataset) * 0.8)
validation_size = len(dataset) - train_size
#��ȡѵ�����ݼ�train�Ͳ������ݼ���validation
train, validation = dataset[0: train_size, :], dataset[train_size: len(dataset), :]
# �н��������ݲ�������Ϊ20
n_steps = 20
# �����ݽ��в�֣�����ѵ�����ݼ��Ͳ������ݼ�
X_train, y_train = split_sequences(train,n_steps)
X_validation, y_validation = split_sequences(validation,n_steps)

n_features = X_train.shape[2]
# ������������ģ��
# ���������һά���(Ӧ����NLP)����ά���(Ӧ����ͼƬ����)����ά���(Ӧ������Ƶ����)
# �˴�����һά���Conv1D�����Ʊ�н���������
model = Sequential()
model.add(Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(n_steps, n_features)))
model.add(MaxPooling1D(pool_size=2))
model.add(Flatten())
model.add(Dense(50, activation='relu'))
# Dense(n_features)�Ľ����Ԥ��ģ�������һ�ڵ���λ����3D�н�����
model.add(Dense(n_features))
model.compile(optimizer='adam', loss='mse')
# ģ��ѵ��2400��
model.fit(X_train, y_train, epochs=2400, verbose=2)

# Ԥ��1����������ѵ������Ԥ�⣬��ֱ�۹۲������н��ʼ��ߣ���һ��������������缫ǿ�ķ��������������
print('predict training dataset')
for i in range(X_train.shape[0]):
    testX = X_train[i]    
    testX = testX.reshape(1, n_steps, n_features)
    yhat = model.predict(testX, verbose=0)
    yhat = yhat.round()
    testy = y_train[i]
    testy = testy.round()   
    print('training expected : ',testy,end=' ') 
    print('training predict :',yhat.squeeze())
# Ԥ��2������������������Ԥ�⣬��ֱ�۹۲�����һ���н���Ҳû�У���һ����������������(random walk)���ص㣬һö���ȵ�Ӳ�ҵ�Ͷ���������޷�Ԥ�⡣
print('predict test dataset')
for i in range(X_validation.shape[0]):
    testX = X_validation[i]    
    testX = testX.reshape(1, n_steps, n_features)
    yhat = model.predict(testX, verbose=0)
    yhat = yhat.round()
    testy = y_validation[i]
    testy = testy.round()
    print('expected : ',testy,end=' ') 
    print('predict :',yhat.squeeze())
