import math
import cmath


def c_mod(z):
    """returns modulus of complex number"""

    return math.sqrt(z.real ** 2 + z.imag ** 2)


def complex_to_board(size, z):
    """gives the board coordinates of a complex number"""
    return size[0] - size[1]/2 + z.real, size[1]/2 - z.imag


def board_to_complex(size, pos):
    """gives the complex number of a board point"""

    return pos[0] - size[0]+size[1]/2 + (size[1]/2 - pos[1]) * 1j


def discrete_fourier_transform(sequence, fourier_coefficients, g_u_i,
                               animation, percent_split):
    """Computes Discrete Fourier coefficients
    for the points of the manual or loaded drawing

    uses the formula:
    xn = 1/N * sum[k=0->k=N-1](Xk*exp(2*i*pi*k*n/N))

    xn: n-th fourier coefficient
    N: number of points from the sequence
    Xk: k-th elements of the sequence

    """

    # reset fourier coefficients list
    fourier_coefficients.clear()

    # number of points
    N = len(sequence)

    # compute discrete fourier transform coefficients
    for n in range(N):
        # nth-fourier coefficient
        xn = 0
        exp_base = cmath.exp(-2j * cmath.pi * n / N)
        exp = 1

        # display percentage progress
        percent = int(percent_split * (n / N))
        animation.display_rendering_percentage(percent)

        for k, point in enumerate(sequence):

            # stop if requested
            if g_u_i.quit_request:
                return

            # add new term to the discrete fourier coefficient
            xn += (point / exp) / N

            # new exponential factor
            exp *= exp_base

        # add new fourier coefficient
        fourier_coefficients.append(xn)