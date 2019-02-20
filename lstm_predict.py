import pandas as pd
from numpy import array
from numpy import hstack
import numpy as np 
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import Dropout
from sklearn import preprocessing 


# split a multivariate sequence into samples
# ��Ʋ���Ϊ20��ʱ������
n_steps = 20
def create_dataset(sequences, n_steps):
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

#��ȡ����3D���н���¼
data = pd.read_csv('d:\\quantrading\\3D_record.csv')
data['date'] = pd.to_datetime(data['date'])
#ѡȡ����1000���н���¼��Ϊ����
data=data[4080:5080]

x=np.array(data['x'])
y=np.array(data['y'])
z=np.array(data['z'])    
#x,y,z��������ͨ����ʽ��
in_seq1 = x.reshape((len(x), 1))
in_seq2 = y.reshape((len(y), 1))
in_seq3 = z.reshape((len(z), 1))

#�ϲ��������������н���dataset
dataset = hstack((in_seq1, in_seq2, in_seq3))
#���������ݽ��б�׼������
scaler = preprocessing.MinMaxScaler() 
dataset = scaler.fit_transform(dataset.astype('float32')) 
# ��ȫ�����ݽ���4:1�������з֣�80%��������ѵ��������20%������������
train_size = int(len(dataset) * 0.8)
validation_size = len(dataset) - train_size
#��ȡѵ�����ݼ�train�Ͳ������ݼ���validation
train, validation = dataset[0: train_size, :], dataset[train_size: len(dataset), :]

# ���ල����ͨ��create_dataset()ת��Ϊ��������
X_train, y_train = create_dataset(train,n_steps)
X_validation, y_validation = create_dataset(validation,n_steps)


# configure network
# on line training (batch_size=1)
n_batch = 1
# ѵ�������趨Ϊ700
n_epoch = 700
# �񾭵�Ԫ����Ϊ40
n_neurons = 40
# design network
# �����Ʊ�н���¼��ʱ���ϴ���һ���ĺ���ӳ���ϵ�����Ը�����ʷ�н���¼Ԥ��δ���н���¼�����ģ�����Ϊʱ������ģ��
# ���Ϊ�����(ÿһ��������Ӧһ���н�����)����Ԥ�������LSTM����
# LSTM���Ա���״̬(state)������Stateless LSTM ֻ�ܱ���һ�������ڵ�״̬, Ϊ�˼�¼��ʱ���״̬���������Ϊstateful 
# ����Keras��stateful ��state���ݹ���Ϊ�����εĵ�i������״̬���ݸ������εĵ�i�������ĳ�ʼ״̬����˳������Ϊon line training(batch_size=1)
model = Sequential()
model.add(LSTM(n_neurons, batch_input_shape=(n_batch, X_train.shape[1], X_train.shape[2]), stateful=True, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(n_neurons, batch_input_shape=(n_batch, X_train.shape[1], X_train.shape[2]), stateful=True))
model.add(Dropout(0.2))
#Dense(3)�Ľ����Ԥ��ģ�������һ�ڵ���λ����3D�н�����
model.add(Dense(3))
#��ʧ����Ϊ������Ż��㷨��adam�ݶ��½�
model.compile(loss='mean_squared_error', optimizer='adam')

# fit ����������stateful LSTM��ѵ������shuffle�ֹ�����Ϊ�رգ�state��ÿ��epoch���������á�
for i in range(n_epoch):
    model.fit(X_train, y_train, epochs=1, batch_size=n_batch, verbose=2, shuffle=False)
    model.reset_states()

# Ԥ��1����������ѵ������Ԥ�⣬��ֱ�۹۲������н��ʼ��ߣ���һ��������������缫ǿ�ķ��������������
print('training dataset predict')
for i in range(X_train.shape[0]):
    testX = X_train[i]    
    testX = testX.reshape(1, X_train.shape[1], X_train.shape[2])
    yhat = model.predict(testX, batch_size=n_batch)
    testy = scaler.inverse_transform([y_train[i]])
    testy = testy.round()
    yhat = scaler.inverse_transform(yhat)
    yhat = yhat.round()
    print('expected : ',testy,end=' ') 
    print('predict :',yhat.squeeze())
# Ԥ��2������������������Ԥ�⣬��ֱ�۹۲�����һ���н���Ҳû�У���һ����������������(random walk)���ص㣬һö���ȵ�Ӳ�ҵ�Ͷ���������޷�Ԥ�⡣
# �мලѧϰ�Ļ���ԭ����ͨ��������Ԥ��ֵ������ֵ��ֵ����ʧ�����������Ż��㷨����ϳ��Ա����������֮��ĺ���ӳ�䣬��������������ݣ����ڲ�����ӳ�亯������˶��ڲ������ݵĽ���������������֡�
print('test dataset predict')
for i in range(X_validation.shape[0]):
    testX = X_validation[i]    
    testX = testX.reshape(1, X_validation.shape[1], X_validation.shape[2])
    yhat = model.predict(testX, batch_size=n_batch)
    testy = scaler.inverse_transform([y_validation[i]])
    testy = testy.round()
    yhat = scaler.inverse_transform(yhat)
    yhat = yhat.round()
    print('expected : ',testy,end=' ') 
    print('predict :',yhat.squeeze())
