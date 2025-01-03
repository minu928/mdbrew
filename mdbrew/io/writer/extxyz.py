from numpy import column_stack, savetxt

from mdbrew.io.writer.base import BaseWriter
from mdbrew._core.mdstate import MDState


SUPPORTED_ATTRIBUTES = {"box": "Lattice", "stress": "stress", "virial": "virial", "energy": "energy"}
SUPPORTED_PROPERTIES = {"atom": "speciesS1", "coord": "posR3", "force": "forcesR3", "velocity": "velocitiesR3"}


class EXTXYZWriter(BaseWriter):
    fmt = "extxyz"

    @property
    def _required_attributes(self) -> tuple[str, ...]:
        return ("atom", "coord")

    def _write_mdstate(self, file, mdstate: MDState) -> None:
        attr_line = self.__make_attr_line(mdstate=mdstate)
        prop_line, prop_data = self.__make_prop_info(mdstate=mdstate)
        header = f'{attr_line} {prop_line} pbc="T T T"'

        file.write(f"{len(prop_data)}\n{header}\n")
        savetxt(file, column_stack(prop_data), fmt="%s", delimiter=" ")

    def __make_attr_line(self, mdstate: MDState) -> str:
        attributes = []
        for name, attr_name in SUPPORTED_ATTRIBUTES.items():
            if (value := getattr(mdstate, name)) is not None:
                flat_value = " ".join(value.flatten().astype(str))
                attributes.append(f'{attr_name}="{flat_value}"')
        return " ".join(attributes)

    def __make_prop_info(self, mdstate: MDState) -> tuple[str, list]:
        properties = []
        data = []
        for name, prop_name in SUPPORTED_PROPERTIES.items():
            if (value := getattr(mdstate, name)) is not None:
                properties.extend([prop_name[:-2], prop_name[-2], prop_name[-1]])
                data.append(value)
        prop_line = "Properties=" + ":".join(properties)
        return prop_line, data
