from mdbrew.analysis.rdf.base import BaseRDF
from mdbrew.analysis.rdf.numpy import NumpyRDF


RDF = BaseRDF


def build(a, b, box=None, *, nbins: int = 100, ranges: tuple[float, float] = (0, 6)) -> RDF:
    args = dict(a=a, b=b, box=box)
    if all(hasattr(arg, "__array__") for arg in args.values()):
        return NumpyRDF(**args, nbins=nbins, ranges=ranges)
    raise ValueError("Unsupported input types")
