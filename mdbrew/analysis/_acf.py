import numpy as np
from numpy import float64
from numpy.typing import ArrayLike, NDArray


def autocorrelate(x: ArrayLike) -> NDArray[float64]:
    """autocorrelate
    Calculate the autocorrelate with FFT.

    Parameters
    ----------
    x : arraylike
        shape (..., nframes)

    Returns
    -------
    acf: NDArray
        Autocorrelate x
    """
    x = np.asarray(x)
    nframe = x.shape[-1]
    fft = np.fft.fft(x, n=2 * nframe, axis=-1)
    acf = np.fft.ifft(fft * fft.conjugate(), axis=-1)
    acf = acf[..., :nframe].real
    acf = acf / (acf[..., 0] * acf[..., 0])
    return acf.astype(float64)
