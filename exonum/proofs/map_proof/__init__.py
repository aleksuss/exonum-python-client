"""MapProof module.

This module contains classes to work with MapProofs obtained from the Exonum.

Most important ones are MapProofBuilder and CheckedMapProof"""
from .map_proof import MapProof, CheckedMapProof
from .map_proof_builder import MapProofBuilder
from .errors import MalformedMapProofError
