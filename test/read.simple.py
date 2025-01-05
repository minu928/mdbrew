from mdbrew.io import read


head = "../src/trj/test"
fmts = ["extxyz", "xyz", "lammpstrj", "poscar", "pdb", "gro", "lmps"]
for fmt in fmts:
    try:
        read(f"{head}.{fmt}")
    except:
        print(f"{fmt:12s} is Failure.")
    else:
        print(f"{fmt:12s} is Success.")
