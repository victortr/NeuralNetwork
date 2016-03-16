import theano
from theano import tensor as T
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams
import numpy as np
from load import mnist
from itertools import izip

srng = RandomStreams()

def adagrad(cost, parameters ,rho=0.9 ,eps=1e-6):
    #As said before, I don't remember how this works, but it works
    gradients = T.grad(cost=cost, wrt=parameters)

    gradients_sq = [ create_shared(np.zeros(p.get_value().shape)) for p in parameters ]
    deltas_sq = [ create_shared(np.zeros(p.get_value().shape)) for p in parameters ]

    gradients_sq_new = [ rho*g_sq + (1-rho)*(g**2) for g_sq,g in izip(gradients_sq,gradients) ]
    deltas = [ (T.sqrt(d_sq+eps)/T.sqrt(g_sq+eps))*grad for d_sq,g_sq,grad in izip(deltas_sq,gradients_sq_new,gradients) ]
    deltas_sq_new = [ rho*d_sq + (1-rho)*(d**2) for d_sq,d in izip(deltas_sq,deltas) ]
    gradient_sq_updates = zip(gradients_sq,gradients_sq_new)
    deltas_sq_updates = zip(deltas_sq,deltas_sq_new)
    parameters_updates = [ (p,p - d) for p,d in izip(parameters,deltas) ]
    return gradient_sq_updates + deltas_sq_updates + parameters_updates

def floatX(X):
    return np.asarray(X, dtype=theano.config.floatX)

def init_weights(shape):
    return theano.shared(floatX(np.random.randn(*shape) * 0.01))

def create_shared(array, dtype=theano.config.floatX, name=None):
    return theano.shared(
            value = np.asarray(
                array,
                dtype = dtype
            ),
            name = name,
        )

def rectify(X):
    return T.maximum(X, 0.)

def softmax(X):
    e_x = T.exp(X - X.max(axis=1).dimshuffle(0, 'x'))
    return e_x / e_x.sum(axis=1).dimshuffle(0, 'x')

def RMSprop(cost, params, lr=0.001, rho=0.9, epsilon=1e-6):
    grads = T.grad(cost=cost, wrt=params)
    updates = []
    for p, g in zip(params, grads):
        acc = theano.shared(p.get_value() * 0.)
        acc_new = rho * acc + (1 - rho) * g ** 2
        gradient_scaling = T.sqrt(acc_new + epsilon)
        g = g / gradient_scaling
        updates.append((acc, acc_new))
        updates.append((p, p - lr * g))
    return updates

def dropout(X, p=0.):
    if p > 0:
        retain_prob = 1 - p
        X *= srng.binomial(X.shape, p=retain_prob, dtype=theano.config.floatX)
        X /= retain_prob
    return X

def model(X, w_h, w_h2, w_o, p_drop_input, p_drop_hidden):
    X = dropout(X, p_drop_input)
    h = T.dot(X, w_h)
    #h = rectify(T.dot(X, w_h))
    #h = T.nnet.sigmoid(T.dot(X, w_h))

    h = dropout(h, p_drop_hidden)
    h2 = T.dot(h, w_h2)
    #h2 = rectify(T.dot(h, w_h2))
    #h2 = T.nnet.sigmoid(T.dot(h, w_h2))

    h2 = dropout(h2, p_drop_hidden)
    py_x = T.dot(h2, w_o)
    return h, h2, py_x

trX = [[-0.10 , -0.126146445 , -0.070842698],[-0.13 , -0.070842698 , -0.091556409],[-0.07 , -0.091556409 , -0.092151275],[-0.09 , -0.092151275 , -0.055807894],[-0.09 , -0.055807894 , -0.073318059],[-0.06 , -0.073318059 , -0.069078388],[-0.07 , -0.069078388 , 0.011747354],[-0.07 , 0.011747354 , 0.025933861],[0.01 , 0.025933861 , 0.062879096],[0.03 , 0.062879096 , 0.105180336],[0.06 , 0.105180336 , 0.027002413],[0.11 , 0.027002413 , 0.04344488],[0.03 , 0.04344488 , -0.016646764],[0.04 , -0.016646764 , -0.010518442],[-0.02 , -0.010518442 , -0.062511153],[-0.01 , -0.062511153 , 0.010093805],[-0.06 , 0.010093805 , 0.017511964],[0.01 , 0.017511964 , 0.002657991],[0.02 , 0.002657991 , 0.018688508],[0.00 , 0.018688508 , -0.077876653],[0.02 , -0.077876653 , 0.044948858],[-0.08 , 0.044948858 , 0.109134973],[0.04 , 0.109134973 , 0.125899654],[0.11 , 0.125899654 , 0.119043843],[0.13 , 0.119043843 , 0.137227792],[0.12 , 0.137227792 , 0.145275726],[0.14 , 0.145275726 , 0.158878008],[0.15 , 0.158878008 , 0.173466291],[0.16 , 0.173466291 , 0.132946033],[0.17 , 0.132946033 , 0.175753601],[0.13 , 0.175753601 , 0.160196729],[0.18 , 0.160196729 , 0.154343139],[0.16 , 0.154343139 , 0.095273421],[0.15 , 0.095273421 , 0.051958695],[0.10 , 0.051958695 , 0.179383486],[0.05 , 0.179383486 , 0.210920934],[0.18 , 0.210920934 , 0.187673822],[0.21 , 0.187673822 , 0.193525742],[0.19 , 0.193525742 , 0.168068066],[0.19 , 0.168068066 , 0.080588181],[0.17 , 0.080588181 , 0.171808466],[0.08 , 0.171808466 , 0.2114158],[0.17 , 0.2114158 , 0.196858698],[0.21 , 0.196858698 , 0.178679602],[0.20 , 0.178679602 , 0.164166337],[0.18 , 0.164166337 , 0.164189996],[0.16 , 0.164189996 , 0.147364748],[0.16 , 0.147364748 , 0.14437703],[0.15 , 0.14437703 , 0.166019497],[0.14 , 0.166019497 , 0.141900901],[0.17 , 0.141900901 , 0.120109758],[0.14 , 0.120109758 , 0.167546802],[0.12 , 0.167546802 , 0.188262492],[0.17 , 0.188262492 , 0.178859728],[0.19 , 0.178859728 , 0.199985402],[0.18 , 0.199985402 , 0.183562759],[0.20 , 0.183562759 , 0.145447742],[0.18 , 0.145447742 , 0.180972086],[0.15 , 0.180972086 , 0.183669452],[0.18 , 0.183669452 , 0.181534514],[0.18 , 0.181534514 , 0.2166329],[0.18 , 0.2166329 , 0.317038072],[0.22 , 0.317038072 , 0.330619494],[0.32 , 0.330619494 , 0.34431028],[0.33 , 0.34431028 , 0.333042573],[0.34 , 0.333042573 , 0.292678199],[0.33 , 0.292678199 , 0.323298092],[0.29 , 0.323298092 , 0.321478272],[0.32 , 0.321478272 , 0.327058103],[0.32 , 0.327058103 , 0.336915086],[0.33 , 0.336915086 , 0.339398807],[0.34 , 0.339398807 , 0.341036337],[0.34 , 0.341036337 , 0.338217777],[0.34 , 0.338217777 , 0.377690076],[0.34 , 0.377690076 , 0.380994889],[0.38 , 0.380994889 , 0.293831442],[0.38 , 0.293831442 , 0.369508288],[0.29 , 0.369508288 , 0.352116368],[0.37 , 0.352116368 , 0.374883278],[0.35 , 0.374883278 , 0.394537685],[0.37 , 0.394537685 , 0.398945072],[0.39 , 0.398945072 , 0.414807124],[0.40 , 0.414807124 , 0.375134125],[0.41 , 0.375134125 , 0.392869693],[0.38 , 0.392869693 , 0.399520525],[0.39 , 0.399520525 , 0.375745362],[0.40 , 0.375745362 , 0.36293138],[0.38 , 0.36293138 , 0.410043942],[0.36 , 0.410043942 , 0.400411496],[0.41 , 0.400411496 , 0.392913799],[0.40 , 0.392913799 , 0.367517459],[0.39 , 0.367517459 , 0.33673333],[0.37 , 0.33673333 , 0.356830905],[0.34 , 0.356830905 , 0.429575811],[0.36 , 0.429575811 , 0.407188507],[0.43 , 0.407188507 , 0.402311386],[0.41 , 0.402311386 , 0.385247855],[0.40 , 0.385247855 , 0.422508746],[0.39 , 0.422508746 , 0.435899517],[0.42 , 0.435899517 , 0.447110059],[0.44 , 0.447110059 , 0.443542158],[0.45 , 0.443542158 , 0.456332442],[0.44 , 0.456332442 , 0.469182826],[0.46 , 0.469182826 , 0.448513687],[0.47 , 0.448513687 , 0.428465183],[0.45 , 0.428465183 , 0.454212365],[0.43 , 0.454212365 , 0.490791945],[0.45 , 0.490791945 , 0.505029048],[0.49 , 0.505029048 , 0.530681386],[0.51 , 0.530681386 , 0.529141585],[0.53 , 0.529141585 , 0.541816776],[0.53 , 0.541816776 , 0.50271969],[0.54 , 0.50271969 , 0.50793],[0.50 , 0.50793 , 0.541719847],[0.51 , 0.541719847 , 0.566953167],[0.54 , 0.566953167 , 0.56651237],[0.57 , 0.56651237 , 0.563354914],[0.57 , 0.563354914 , 0.573371773],[0.56 , 0.573371773 , 0.571409573],[0.57 , 0.571409573 , 0.586161878],[0.57 , 0.586161878 , 0.599521797],[0.59 , 0.599521797 , 0.636018253],[0.60 , 0.636018253 , 0.632985135],[0.64 , 0.632985135 , 0.611028741],[0.63 , 0.611028741 , 0.619432989],[0.61 , 0.619432989 , 0.637556702],[0.62 , 0.637556702 , 0.571887285],[0.64 , 0.571887285 , 0.572133043],[0.57 , 0.572133043 , 0.647711498],[0.57 , 0.647711498 , 0.717685304],[0.65 , 0.717685304 , 0.673176365],[0.72 , 0.673176365 , 0.626245434],[0.67 , 0.626245434 , 0.638404545]]


teX = [[0.63 , 0.638404545 , 0.61854384],[0.64 , 0.61854384 , 0.634380558],[0.62 , 0.634380558 , 0.684519105],[0.63 , 0.684519105 , 0.6351438],[0.68 , 0.6351438 , 0.61774209],[0.64 , 0.61774209 , 0.654367924],[0.62 , 0.654367924 , 0.657384913],[0.65 , 0.657384913 , 0.719624672],[0.66 , 0.719624672 , 0.741644961],[0.72 , 0.741644961 , 0.75319176],[0.74 , 0.75319176 , 0.732981045],[0.75 , 0.732981045 , 0.641416078],[0.73 , 0.641416078 , 0.592886784],[0.64 , 0.592886784 , 0.614976011],[0.59 , 0.614976011 , 0.606363764],[0.61 , 0.606363764 , 0.598154196],[0.61 , 0.598154196 , 0.582372337],[0.60 , 0.582372337 , 0.516861241],[0.58 , 0.516861241 , 0.586739305],[0.52 , 0.586739305 , 0.612916511],[0.59 , 0.612916511 , 0.661287646],[0.61 , 0.661287646 , 0.619651393],[0.66 , 0.619651393 , 0.592750764],[0.62 , 0.592750764 , 0.467903481],[0.59 , 0.467903481 , 0.521471321],[0.47 , 0.521471321 , 0.574342146],[0.52 , 0.574342146 , 0.658489017],[0.57 , 0.658489017 , 0.561186959],[0.66 , 0.561186959 , 0.585948491],[0.56 , 0.585948491 , 0.650539731],[0.59 , 0.650539731 , 0.638247457],[0.65 , 0.638247457 , 0.640836238],[0.64 , 0.640836238 , 0.661643115],[0.64 , 0.661643115 , 0.614698453],[0.66 , 0.614698453 , 0.64551001],[0.61 , 0.64551001 , 0.666834954],[0.65 , 0.666834954 , 0.68496405],[0.67 , 0.68496405 , 0.723743177],[0.68 , 0.723743177 , 0.768587617],[0.72 , 0.768587617 , 0.788058762],[0.77 , 0.788058762 , 0.83264223],[0.79 , 0.83264223 , 0.856997912],[0.83 , 0.856997912 , 0.885718188],[0.86 , 0.885718188 , 0.85823717],[0.89 , 0.85823717 , 0.964440986],[0.86 , 0.964440986 , 0.943044156],[0.96 , 0.943044156 , 0.912798991],[0.94 , 0.912798991 , 0.89565573],[0.91 , 0.89565573 , 0.881054076],[0.90 , 0.881054076 , 0.892440863],[0.88 , 0.892440863 , 0.881817173],[0.89 , 0.881817173 , 0.937662509],[0.88 , 0.937662509 , 1],[0.94 , 1 , 0.879490397],[1.00 , 0.879490397 , 0.890217292],[0.88 , 0.890217292 , 0.863132185],[0.89 , 0.863132185 , 0.985106579],[0.86 , 0.985106579 , 0.841844842]]

trY = [[-0.091556409,-0.092151275,-0.055807894,-0.073318059,-0.069078388,0.011747354,0.025933861,0.062879096,0.105180336,0.027002413,0.04344488,-0.016646764,-0.010518442,-0.062511153,0.010093805,0.017511964,0.002657991,0.018688508,-0.077876653,0.044948858,0.109134973,0.125899654,0.119043843,0.137227792,0.145275726,0.158878008,0.173466291,0.132946033,0.175753601,0.160196729,0.154343139,0.095273421,0.051958695,0.179383486,0.210920934,0.187673822,0.193525742,0.168068066,0.080588181,0.171808466,0.2114158,0.196858698,0.178679602,0.164166337,0.164189996,0.147364748,0.14437703,0.166019497,0.141900901,0.120109758,0.167546802,0.188262492,0.178859728,0.199985402,0.183562759,0.145447742,0.180972086,0.183669452,0.181534514,0.2166329,0.317038072,0.330619494,0.34431028,0.333042573,0.292678199,0.323298092,0.321478272,0.327058103,0.336915086,0.339398807,0.341036337,0.338217777,0.377690076,0.380994889,0.293831442,0.369508288,0.352116368,0.374883278,0.394537685,0.398945072,0.414807124,0.375134125,0.392869693,0.399520525,0.375745362,0.36293138,0.410043942,0.400411496,0.392913799,0.367517459,0.33673333,0.356830905,0.429575811,0.407188507,0.402311386,0.385247855,0.422508746,0.435899517,0.447110059,0.443542158,0.456332442,0.469182826,0.448513687,0.428465183,0.454212365,0.490791945,0.505029048,0.530681386,0.529141585,0.541816776,0.50271969,0.50793,0.541719847,0.566953167,0.56651237,0.563354914,0.573371773,0.571409573,0.586161878,0.599521797,0.636018253,0.632985135,0.611028741,0.619432989,0.637556702,0.571887285,0.572133043,0.647711498,0.717685304,0.673176365,0.626245434,0.638404545,0.61854384]]
 
teY = [[0.634380558,0.684519105,0.6351438,0.61774209,0.654367924,0.657384913,0.719624672,0.741644961,0.75319176,0.732981045,0.641416078,0.592886784,0.614976011,0.606363764,0.598154196,0.582372337,0.516861241,0.586739305,0.612916511,0.661287646,0.619651393,0.592750764,0.467903481,0.521471321,0.574342146,0.658489017,0.561186959,0.585948491,0.650539731,0.638247457,0.640836238,0.661643115,0.614698453,0.64551001,0.666834954,0.68496405,0.723743177,0.768587617,0.788058762,0.83264223,0.856997912,0.885718188,0.85823717,0.964440986,0.943044156,0.912798991,0.89565573,0.881054076,0.892440863,0.881817173,0.937662509,1,0.879490397,0.890217292,0.863132185,0.985106579,0.841844842]]

trY, teY = np.array(trY).T, np.array(teY).T

for i in range(len(trX)): #feature expansion
 trX[i].append(trX[i][2] - trX[i][1])
 trX[i].append(trX[i][1] - trX[i][0])
 trX[i].append( sum(trX[i][:3])/3. )

for i in range(len(teX)):
 teX[i].append(teX[i][2] - teX[i][1])
 teX[i].append(teX[i][1] - teX[i][0])
 teX[i].append( sum(teX[i][:3])/3. )

X = T.fmatrix()
Y = T.fmatrix()

w_h = init_weights((6, 1000))
w_h2 = init_weights((1000, 1000))
w_o = init_weights((1000, 1))

noise_h, noise_h2, noise_py_x = model(X, w_h, w_h2, w_o, 0., 0.)
h, h2, py_x = model(X, w_h, w_h2, w_o, 0., 0.)
y_x = py_x

cost = T.mean((noise_py_x - Y) ** 2)
#params = [w_h, w_h2, w_o] 	#mlp
params = [w_o]			#elm

#updates = adagrad(cost, params)
updates = RMSprop(cost, params, lr=0.001)

train = theano.function(inputs=[X, Y], outputs=cost, updates=updates, allow_input_downcast=True)
predict = theano.function(inputs=[X], outputs=y_x, allow_input_downcast=True)

for i in range(1000):
    for start, end in zip(range(0, len(trX), 20), range(20, len(trX), 20)):
        cost = train(trX[start:end], trY[start:end])
    print cost

print predict(teX)
print teY
