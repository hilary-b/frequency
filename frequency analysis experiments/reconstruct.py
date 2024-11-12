from itertools import product, combinations, permutations
import random
import logging
import datetime
import json
import io
import sys
import time
import math
from multiprocessing.pool import Pool
from csv import DictReader
import pickle
from ortools.sat.python import cp_model
from helpers import *
import boto3
from constraint import *

# python-constraint reconstruct
def reconstruct(t,N,n,dim,dist,recval_dict,iterate=False,experiment_id=None):

    AWS_ACCESS_KEY_ID='AKIAYZTXUKO5VYMOKEQV'
    AWS_SECRET_ACCESS_KEY='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'

    s3 = boto3.resource('s3', 
                        use_ssl=False,
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                        )
    
    # LOAD DOMINANT PAIR FREQUENCY DICT
    dp_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/dp_frequencies/{dist}/{dim}_dimensions.pkl").get()['Body'].read())

    # LOAD VALUE FREQUENCY DICT
    val_tup_freq_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())
    
    # LOAD T1 MATCHES
    t1_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/matches/{dist}/{dim}_dim/t1.pkl").get()['Body'].read())
    # print(t1_dict)
    # input("...")
    # initialize constraint problem using t1 matches as variable domains
    problem = Problem()
    records = list(recval_dict.keys())
    # save record indices
    rec_index = {}
    for i in range(len(records)):
        rec_index[records[i]]=i

    # create variables using t1 matches
    rec_strings = []
    for record in records:
        matches = t1_dict[(record,)]
        cleaned_matches = []
        for m in matches:
            cleaned_matches.append(m[0])
        # print(cleaned_matches)
        # input("...")
        problem.addVariable(str(record),cleaned_matches)
        rec_strings.append(str(record))
    problem.addConstraint(AllDifferentConstraint())
    
    # for t == 1, skip the rest and solve
    if t > 1:
        t_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/matches/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())
        # iterate over t-tuples of records
        for rec_tup in combinations(records,t):
            sorted_tuple = tuple(sorted(rec_tup))
            matches = t_dict[sorted_tuple]
            funcstring = "def func(*args): return ("

            # process each matching t-tuple
            num_matches = len(matches)
            stop = num_matches * math.factorial(t)
            clause_count = 0
            for match in matches:
                # process each permutation of a match
                for candidate in permutations(match,t):
                    # OR together each candidate
                    funcstring += "("
                    for i in range(t):
                        rec = sorted_tuple[i]
                        funcstring += f"args[{rec_index[rec]}] == {candidate[i]}"
                        if i != t-1:
                            funcstring += " and "
                        else:
                            funcstring += ")"
                    clause_count += 1
                    if clause_count != stop:
                        funcstring += " or "
            funcstring += ")"
            # print(funcstring)
            # input("...")
            exec(funcstring)    
            constraint_string = "problem.addConstraint(FunctionConstraint(func),rec_strings)"
            exec(constraint_string)

    # add the results as constraints
    # for t_minus_1_tup in combinations(rec_tup,t-1):
    #     # sort record_id tuple for consistency on lookups
    #     sorted_recs = tuple(sorted(list(t_minus_1_tup)))
        
    #     # get all t-1 matches
        # matches = t_minus_1_matches[sorted_recs]

    #     # add all the t-1 matches as OR'ed constraints
    #     # by dynamically creating a function
    #     funcstring = "def func(*args): return ("

    #     # OR together each match
    #     stop = len(matches)
    #     count = 0

    #     for m in matches:
    #         count += 1
    #         funcstring += "("
    #         for i in range(t-1):
    #             rec = t_minus_1_tup[i]
    #             # print(f"i = {i} rec: {rec} has position {rec_pos[rec]}")
    #             funcstring += f"args[{rec_pos[rec]}] == {m[i]}"
    #             if i != t-2:
    #                 funcstring += " and "
    #             else:
    #                 funcstring += ")"
    #         if count != stop:
    #             funcstring += " or "
    #     funcstring += ")"
    #     exec(funcstring)

    #     # add the t-1 constraint to the problem
    #     constraint_string = "problem.addConstraint(FunctionConstraint(func),rec_id_strings)"
    #     exec(constraint_string)
    #     count += 1
    #     if count % 100 == 0:
    #         print(count/total_t_tuples)

    # find a reconstruction!
    if iterate == False: # return a single reconstruction
        reconstruction = problem.getSolution()
        return reconstruction
    else: # return all possible reconstructions
        reconstructions = problem.getSolutions()
        return reconstructions





# OR-TOOLS IMPLEMENTATION
# def reconstruct(t,N,n,dim,dist,recval_dict,iterate=False,experiment_id=None):
    
#     AWS_ACCESS_KEY_ID='AKIAYZTXUKO5VYMOKEQV'
#     AWS_SECRET_ACCESS_KEY='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'

#     s3 = boto3.resource('s3', 
#                         use_ssl=False,
#                         aws_access_key_id=AWS_ACCESS_KEY_ID,
#                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#                         )
    
#     # LOAD DOMINANT PAIR FREQUENCY DICT
#     dp_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/dp_frequencies/{dist}/{dim}_dimensions.pkl").get()['Body'].read())

#     # LOAD VALUE FREQUENCY DICT
#     val_tup_freq_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())
    
#     records = list(recval_dict.keys())

#     # IF t == 1, just use singleton candidates
#     if t == 1:
#         t1_matches = val_tup_freq_dict
#         model = cp_model.CpModel()
#         # each record is a collection of integer variables, one for each dimension
#         vars = [[model.NewIntVar(1, N, f'rec_{records[i]}_{j}') for j in range(dim)] for i in range(n)]
        
#         # iterate over all records, adding matches as constraints
#         # for rec in records:
#         #     matches = t1_matches[(rec,)]
#         #     for match in matches:
                

#         # suppose these are possible assignments for recs 0 and 1
#         # retrieved from t2 matches dict
#         possible_assignments = [((1,2),(4,5)),((1,3),(4,6)),((4,3),(2,4))]

#         constraints = []

#         for assignment in possible_assignments:
#             valid_assignment = []
#             for j in range(dim):
#                 valid_assignment.append(vars[0][j] == assignment[0][j])  # x_i = (xi1, xi2, xi3)
#                 valid_assignment.append(vars[1][j] == assignment[1][j])  # x_{i+1} = (xj1, xj2, xj3)
#             bool_var = model.NewBoolVar(f"assignment_{i}_{i+1}")
#             model.AddBoolAnd(valid_assignment).OnlyEnforceIf(bool_var)  # Only enforce if this assignment is selected
#             bool_vars.append(bool_var)

#                     # Add a boolean variable that represents the validity of this assignment
#         bool_var = model.NewBoolVar(f"assignment_{i}_{i+1}")
#         model.AddBoolAnd(valid_assignment).OnlyEnforceIf(bool_var)  # Only enforce if this assignment is selected
#         bool_vars.append(bool_var)

#         # Add an "OR" constraint: only one valid assignment must be true
#         model.AddBoolOr(bool_vars)

#         # Solve the model
#         solver = cp_model.CpSolver()
#         status = solver.Solve(model)

#         # Check if a solution exists and print it
#         if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
#             print("Solution found:")
#             for i in range(n):
#                 print(f"x_{i} = ({solver.Value(x[i][0])}, {solver.Value(x[i][1])}, {solver.Value(x[i][2])})")
#         else:
#             print("No solution found.")
#         return


#     # LOAD SINGLETON CANDIDATES 
#     t1_matches = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/matches/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())
    
#     # Add constraints for every t-tuple of records
#     for rec_t_tuple in combinations(records,t):
#         val_t_tuple = tuple(sorted([recval_dict[r] for r in rec_t_tuple]))
#         bounding_pair = get_mbq(val_t_tuple)
#         freq = dp_dict[bounding_pair]
#         matches = val_tup_freq_dict[freq]
    

#     # Create 10 variables with values between 1 and 1000
#     num_vars = 10
#     variables = [model.NewIntVar(1, 1000, f'var{i}') for i in range(num_vars)]

    # # Create auxiliary Boolean variables for OR conditions
    # # For each OR condition, we will introduce a Boolean variable to represent whether the condition holds.
    # bool_var_1 = model.NewBoolVar('bool1')  # for the first part of OR
    # bool_var_2 = model.NewBoolVar('bool2')  # for the second part of OR

    # # Convert the integer constraints into Boolean variables
    # # First part: (var1 = 0 AND var2 = 3)
    # cond1_var1_eq_0 = model.NewBoolVar('cond1_var1_eq_0')  # var1 == 0
    # cond1_var2_eq_3 = model.NewBoolVar('cond1_var2_eq_3')  # var2 == 3
    # model.Add(variables[0] == 0).OnlyEnforceIf([cond1_var1_eq_0])
    # model.Add(variables[1] == 3).OnlyEnforceIf([cond1_var2_eq_3])
    # model.AddBoolAnd([cond1_var1_eq_0, cond1_var2_eq_3]).OnlyEnforceIf([bool_var_1])

    # # Second part: (var1 = 2 AND var2 = 5)
    # cond2_var1_eq_2 = model.NewBoolVar('cond2_var1_eq_2')  # var1 == 2
    # cond2_var2_eq_5 = model.NewBoolVar('cond2_var2_eq_5')  # var2 == 5
    # model.Add(variables[0] == 2).OnlyEnforceIf([cond2_var1_eq_2])
    # model.Add(variables[1] == 5).OnlyEnforceIf([cond2_var2_eq_5])
    # model.AddBoolAnd([cond2_var1_eq_2, cond2_var2_eq_5]).OnlyEnforceIf([bool_var_2])

    # # Ensure that at least one of the Boolean variables (bool_var_1 or bool_var_2) is true
    # model.AddBoolOr([bool_var_1, bool_var_2])

    # # Add the "unique assignment" constraint: All variables must take different values
    # model.AddAllDifferent(variables)

    # # Create a solver
    # solver = cp_model.CpSolver()

    # # Solve the model
    # status = solver.Solve(model)

    # # Check the result
    # if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    #     print('Solution found:')
    #     for i, var in enumerate(variables):
    #         print(f'var{i+1} = {solver.Value(var)}')
    # else:
    #     print('No solution found.')