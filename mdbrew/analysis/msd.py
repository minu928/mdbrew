import numpy as np
from tqdm import trange


class MSD(object):
    def __init__(self, coords, *, fft: bool = True, dtype: str = float):
        self.dtype = dtype
        self.fft = bool(fft)
        self.coords = np.array(coords, dtype=self.dtype)
        self.nframes, self.natoms, self.ndims = self.coords.shape

    def run(self):
        if self.fft:
            self._msd = self._calc_msd_with_fft()
        else:
            self._msd = self._calc_msd_with_window()
        return self

    @property
    def msd(self):
        if not hasattr(self, "_msd"):
            self.run()
        return self._msd

    def _calc_msd_with_window(self):
        coords = self.coords
        nframs = self.nframes
        msd_list = np.zeros(nframs, dtype=float)
        for frame in trange(1, nframs, unit="frame"):
            displacement = coords[frame:] - coords[:-frame]
            square_displacement = np.sum(np.square(displacement), axis=-1)
            msd_list[frame] = np.mean(square_displacement)
        return msd_list

    def _calc_msd_with_fft(self):
        S_1 = self._calc_S1()
        S_2 = self._calc_S2()
        msd_list = np.subtract(S_1, 2.0 * S_2)
        return msd_list.mean(axis=1)

    def _calc_S1(self):
        coords = self.coords
        nframs = self.nframes
        natoms = self.natoms
        empty_matrix = np.zeros((nframs, natoms))
        D = np.square(coords).sum(axis=-1)
        D = np.append(D, empty_matrix, axis=0)
        Q = 2.0 * np.sum(D, axis=0)
        S_1 = empty_matrix
        for m in trange(nframs, unit="frame"):
            Q -= D[m - 1, :] + D[nframs - m, :]
            S_1[m, :] = Q / (nframs - m)
        return S_1

    def _calc_S2(self):
        coords = self.coords
        nframs = self.nframes
        X = np.fft.fft(coords, n=2 * nframs, axis=0)
        dot_X = X * X.conjugate()
        x = np.fft.ifft(dot_X, axis=0)
        x = x[:nframs].real
        x = x.sum(axis=-1)
        n = np.arange(nframs, 0, -1)
        return x / n[:, np.newaxis]
