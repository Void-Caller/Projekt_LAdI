import math
import numpy





def expm(A):
    """
        Compute the matrix exponential.
        Parameters
        ----------
        A : (2, 2) array_like or sparse matrix
            Matrix to be exponentiated.
        Returns

        -------
        expm: (2, 2) ndarray
            Matrix exponential of `A`.
        References

        ----------
        https://en.wikipedia.org/wiki/Matrix_exponential

        Examples

        ----------

        array([[ 0.42645930+1.89217551j, -2.13721484-0.97811252j],
           [ 1.06860742+0.48905626j, -1.71075555+0.91406299j]])


    In mathematics, the matrix exponential is a matrix function on
    square matrices analogous to the ordinary exponential function.
    It is used to solve systems of linear differential equations.
    In the theory of Lie groups, the matrix exponential gives the connection between
    a matrix Lie algebra and the corresponding Lie group.

    Let X be an n×n real or complex matrix. The exponential of X, denoted by eX or exp(X),
     is the n×n matrix given by the power series

    In mathematics a Padé approximant is the "best" approximation of a
    function by a rational function of given order – under this technique,
    the approximant's power series agrees with the power series of the function it is approximating.
    The technique was developed around 1890 by Henri Padé, but goes back to Georg Frobenius,
    who introduced the idea and investigated the features of rational approximations of power series.

    """
    rozmiar = 2
    m2 = numpy.copy(A)
    # CREATE A MATRIX TO OPERATE
    exp = numpy.copy(A)
    # TWO FIRST STEP OF SERIES #

    # CHECKING THE IDENTITY MATRIX #
    if exp[0][0] != 0 or exp[0][1] != 0 or exp[1][0] != 0 or exp[1][1] != 1:
        exp[0][0] = exp[0][0] + 1
        exp[1][1] = exp[1][1] + 1


    # THE MAIN LOOP COUNTING THE SERIES #
    k = 1
    while 1:
        k = k + 1
        # COUNTING THE POWER OF MATRIX
        for q in range(2, k+1):
            m3 = []
            for w in range(rozmiar):
                m3.append([])
                for p in range(rozmiar):
                    element = 0
                    for i in range(rozmiar):
                        element += A[w][i] * m2[i][p]
                    m3[-1].append(element)
            m2 = numpy.copy(m3)

        # COUNTING FACTOIRAL OF SERIES

        z = 1/math.factorial(k)
        # CHECKING THE FINISH STEP, END OF THE LOOP #
            # IF VALUESS IN MATRIX NOT GROW UP #
        if abs(m2[0][0] * z) <  abs(10e-15):
            if abs(m2[0][1] * z) < abs(10e-15):
                if abs(m2[1][0] * z) < abs(10e-15):
                    if abs(m2[1][1] * z) < abs(10e-15):
                        break
        # SUM OF SERIES #
        for r in range(rozmiar):
            for u in range(rozmiar):
                exp[r][u] = exp[r][u] + (m2[r][u] * z)
        # LAST STEP, GOING BACK TO THE BEGINING #
        m2 = numpy.copy(A)
    # END OF THE LOOP, EXP(A) IS RETURNING

    return exp

A = [[1.0, 0.0], [0.0, 1.0]]
print(' EXP(A) = \n', expm(A))





