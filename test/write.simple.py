from mdbrew.io import read, write


head = "../src/trj/test"
fmts = ["extxyz", "xyz", "lammpstrj", "poscar", "pdb", "gro", "lmps"]
for fmt in fmts:
    try:
        write("tmp.extxyz", read(f"{head}.{fmt}"))
    except:
        print(f"{fmt:12s} is Failure.")
    else:
        print(f"{fmt:12s} is Success.")
