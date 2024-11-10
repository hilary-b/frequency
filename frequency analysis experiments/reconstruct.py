from itertools import product, combinations
import random
import logging
import datetime
import json
import io
import sys
import time
from multiprocessing.pool import Pool
from csv import DictReader
import pickle
from ortools.sat.python import cp_model
from helpers import *
import boto3

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
    
    model = cp_model.CpModel()
    records = recval_dict.keys()
    record_candidates = {}

    # IF t == 1, just use singleton candidates
    if t == 1:
        return


    # LOAD SINGLETON CANDIDATES 
    t1_matches = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/matches/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())
    
    # Add constraints for every t-tuple of records
    for rec_t_tuple in combinations(records,t):
        val_t_tuple = tuple(sorted([recval_dict[r] for r in rec_t_tuple]))
        bounding_pair = get_mbq(val_t_tuple)
        freq = dp_dict[bounding_pair]
        matches = val_tup_freq_dict[freq]
    

    # Create 10 variables with values between 1 and 1000
    num_vars = 10
    variables = [model.NewIntVar(1, 1000, f'var{i}') for i in range(num_vars)]

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