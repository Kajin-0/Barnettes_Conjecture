#!/usr/bin/env python3
"""Run sat_patch_library with an interruptible PySAT backend.

CaDiCaL's PySAT wrapper does not implement limited/interrupted solving.  The
underlying patch encoding is unchanged; this wrapper forces Glucose4 before
worker processes are forked so per-state time limits remain enforceable.
"""
from __future__ import annotations

import multiprocessing as mp

from pysat.solvers import Glucose4

import sat_patch_library as sat


def interruptible_solver():
    return Glucose4(), "glucose4"


if __name__ == "__main__":
    try:
        mp.set_start_method("fork")
    except RuntimeError:
        pass
    sat.new_solver = interruptible_solver
    sat.main()
