from .echo_algorithm import *
from .ring_election import *
from .dolev import *
from .crash import *

def get_algorithm(name):
    if name == "echo":
        return EchoAlgorithm
    elif name == "ring":
        return RingElection
    elif name == "dolev":
        return DolevAlgorithm
    elif name == "dolev_byzantine":
        return DolevByzantine
    elif name == "crash":
        return Crash
    else:
        raise ValueError(f"Unknown algorithm: {name}")
