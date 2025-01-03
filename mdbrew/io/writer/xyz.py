from numpy import column_stack, savetxt

from mdbrew.io.writer.base import BaseWriter


class XYZWriter(BaseWriter):
    fmt = "xyz"
    _required_attributes = ["atom", "coord"]

    def _write_mdstate(self, file, mdstate):
        data = column_stack([getattr(mdstate, attr) for attr in self._required_attributes]).astype(str)
        file.write(f"{data.shape[0]}\n\n")
        savetxt(file, data, fmt="%s", delimiter=" ")
