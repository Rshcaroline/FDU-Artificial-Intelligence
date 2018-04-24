#!/usr/bin/env python
"""
Grader for template assignment
Optionally run as grader.py [basic|all] to run a subset of tests
"""

import random

import graderUtil
import util
import collections
import copy
grader = graderUtil.Grader()
submission = grader.load('submission')


############################################################
# Problem 1a: N-Queens

def test1a_1():
    nQueensSolver = submission.BacktrackingSearch()
    nQueensSolver.solve(submission.create_nqueens_csp(8))
    grader.requireIsEqual(1.0, nQueensSolver.optimalWeight)
    grader.requireIsEqual(92, nQueensSolver.numOptimalAssignments)
    grader.requireIsEqual(2057, nQueensSolver.numOperations)

grader.addBasicPart('1a-1-basic', test1a_1, 5, maxSeconds=1, description="Basic test for create_nqueens_csp for n=8")

############################################################
# Problem 1b: Most constrained variable


def test1b_1():
    mcvSolver = submission.BacktrackingSearch()
    mcvSolver.solve(submission.create_nqueens_csp(8), mcv = True)
    grader.requireIsEqual(1.0, mcvSolver.optimalWeight)
    grader.requireIsEqual(92, mcvSolver.numOptimalAssignments)
    grader.requireIsEqual(1361, mcvSolver.numOperations)

grader.addBasicPart('1b-1-basic', test1b_1, 5, maxSeconds=1, description="Basic test for MCV with n-queens CSP")

############################################################
# Problem 1c: Arc consistency

def test1c_1():
    acSolver = submission.BacktrackingSearch()
    acSolver.solve(submission.create_nqueens_csp(8), ac3 = True)
    grader.requireIsEqual(1.0, acSolver.optimalWeight)
    grader.requireIsEqual(92, acSolver.numOptimalAssignments)
    grader.requireIsEqual(21, acSolver.firstAssignmentNumOperations)
    grader.requireIsEqual(769, acSolver.numOperations)

grader.addBasicPart('1c-1-basic', test1c_1, 10, maxSeconds=1, description="Basic test for AC-3 with n-queens CSP")

grader.grade()