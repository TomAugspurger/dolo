from __future__ import division
from itertools import product

import numpy
from numpy import array, zeros, floor, cumprod, column_stack, reshape


def multilinear_interpolation( smin, smax, orders, x, y):

    '''
    :param smin: dx1 array : lower bounds
    :param smax: dx1 array : upper bounds
    :param orders: dx1 array : number of points in each dimension
    :param x: Nxd array : values on the grid
    :param y: Mxd array : points where to interpolate
    :return: Mxd array : interpolated values
    '''

    d = len(orders)

    n_x, N = x.shape
    n_s, M = y.shape

    assert(d == n_s)

    qq = zeros( (d,M) )
    mm = zeros( (d,M) )

    for i in range(n_s):
        s = (y[i,:]-smin[i])/(smax[i]-smin[i])
        n = orders[i]
        delta = 1/(n-1)
        r = s/delta
        q = floor(r)
        q = (q<0) * 0 + (q>=n-2)*(n-2) + (0<=q)*(q<n-2)*q
        m = r-q
        mm[i,:] = m
        qq[i,:] = q

    [b,g] = index_lookup( x, qq, orders )

    z = b + recursive_evaluation(d,tuple([]),mm[:,numpy.newaxis,:], g)

    return z

def recursive_evaluation(d,ind,mm,g):
    if len(ind) == d:
        return g[ind]
    else:
        j = len(ind)
        ind1 = ind + (0,)
        ind2 = ind + (1,)
        return (1-mm[j,:]) * recursive_evaluation(d,ind1,mm,g) + mm[j,:] * recursive_evaluation(d,ind2,mm,g)


def index_lookup(a, q, dims):
    '''

    :param a: (l1*...*ld)*n_x array
    :param q: k x M array
    :param dims: M: array
    :return: 2**k array (nx*2*...*2)
    '''

    M = q.shape[1]
    n_x = a.shape[0]

    d = len(dims)

    cdims  = (cumprod(dims[::-1]))
    cdims = cdims[::-1]

    q = array(q,dtype=numpy.int)

    lin_q = q[d-1,:]

    for i in reversed(range(d-1)):
        lin_q += q[i,:] * cdims[i+1]

    cart_prod = column_stack( [e for e in product(*[(0,1)]*d)] )

    lin_cp = cart_prod[d-1,:]
    for i in reversed(range(d-1)):
        lin_cp += cart_prod[i,:] * cdims[i+1]

    b = a[:,lin_q]

    g = zeros( (cart_prod.shape[1], n_x, M) )

    for i in range(cart_prod.shape[1]):
        t = a[:,lin_q + lin_cp[i]] - b
        g[i,:,:] = t


    g = reshape(g, (2,)*d + (n_x,M))

    return [b,g]

#
#try:
#    print("using compiled linear interpolator (on gpu)")
#    from multilinear_gpu import multilinear_interpolation
#except Exception as e:
#    print('Failback')
#    pass


try:
    print("using compiled linear interpolator")
    from dolo.numeric.interpolation.multilinear_cython import multilinear_interpolation
except Exception as e:
    print('Failback')
    pass


class MultilinearInterpolator:

    def __init__(self, smin, smax, orders):
        d = len(orders)
        self.smin = numpy.array( smin, dtype=numpy.double )
        self.smax = numpy.array( smax, dtype=numpy.double )
        self.orders = numpy.array( orders, dtype=numpy.int )
        self.d = d
        self.grid = column_stack( [e for e in product(*[numpy.linspace(smin[i],smax[i],orders[i]) for i in range(d)])])
        self.grid = numpy.ascontiguousarray(self.grid)


    def set_values(self,values):
        self.values = values

    def interpolate(self,s):
        a = multilinear_interpolation(self.smin,self.smax,self.orders,self.values,s)
#        from multilinear_c import multilinear_c
#        b = multilinear_c(self.smin,self.smax,self.orders,self.values,s)
#        test = abs(b-a).max()
#        print('Error : {}'.format(test))
        return a

    def __call__(self,s):
        return self.interpolate(s)
