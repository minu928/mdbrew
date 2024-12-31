from pathlib import Path
from setuptools import setup, find_packages


version_dict = {}
with open(Path(__file__).parents[0] / "mdbrew/_version.py") as this_v:
    exec(this_v.read(), version_dict)
version = version_dict["version"]
del version_dict


setup(
    name="mdbrew",
    version=version,
    author="Minwoo Kim",
    author_email="minu928@snu.ac.kr",
    url="https://github.com/minu928/mdbrew",
    install_requies=["numpy>=1.23.5,<2.0.0"],
    description="Postprocessing tools for the Molecular Dynamics simulation",
    packages=find_packages(),
    keywords=["MD", "LAMMPS", "GROMACS"],
    python_requires=">=3.10",
    package_data={"": ["*"]},
    zip_safe=False,
)
