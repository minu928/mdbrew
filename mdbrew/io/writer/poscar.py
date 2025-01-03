from numpy import unique, where, savetxt

from mdbrew.io.writer.base import BaseWriter


def update_defaults(kwargs: dict[str, any]):
    defaults = {}
    defaults["scale"] = float(kwargs.get("scale", 1.0))
    defaults["dynamics"] = kwargs.get("dynamics", "Cartesian")
    return defaults


class POSCARWriter(BaseWriter):
    fmt = "poscar"

    def __init__(self, filepath, **kwargs):
        super().__init__(filepath, **kwargs)
        self.__defaults = update_defaults(kwargs=kwargs)

    @property
    def _required_attributes(self):
        return ("atom", "box", "coord")

    def _write_mdstate(self, file, mdstate):
        # line: head
        scale = self.__defaults["scale"]
        file.write(f"POSCAR written by MDBrew\n{scale}\n")

        # line: box
        box = mdstate.box * scale
        for bi in box.astype(str):
            file.write(f"{' '.join(bi)}\n")

        # line: elements, counts
        atoms = mdstate.atom
        coords = mdstate.coord

        elements, counts = unique(atoms, return_counts=True)
        file.write(" ".join(elements) + "\n")
        file.write(" ".join(counts.astype(str)) + "\n")

        # line: dynamics
        file.write(self.__defaults["dynamics"] + "\n")

        # line: position
        for element in elements:
            idx = where(atoms == element)[0]
            savetxt(file, coords[idx], fmt="%f %f %f")
