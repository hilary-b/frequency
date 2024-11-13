from itertools import combinations, permutations
import pickle
import boto3
from ortools.sat.python import *

def cpsat_reconstruct(t, N, n, dim, dist, recval_dict, iterate=False, experiment_id=None):
    AWS_ACCESS_KEY_ID = 'AKIAYZTXUKO5VYMOKEQV'
    AWS_SECRET_ACCESS_KEY = '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'

    # Initialize boto3 resource
    s3 = boto3.resource(
        's3',
        use_ssl=False,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # Load t=1 matches
    # dp_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/dp_frequencies/{dist}/{dim}_dimensions.pkl").get()['Body'].read())
    # val_tup_freq_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())
    t1_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/matches/{dist}/{dim}_dim/t1.pkl").get()['Body'].read())

    # Initialize CP-SAT solver model
    model = cp_model.CpModel()

    # Record index and variable creation
    records = list(recval_dict.keys())

    # Step 1: Create a mapping from tuples to unique integers
    tuple_to_index = {}
    index_to_tuple = {}
    current_index = 0
    
    for record in records:
        # print(f"rec {record}")
        matches = t1_dict[(record,)]
        # print(f"has matches {matches}")
        for match in matches:
            cleaned_match = match[0]
            if cleaned_match not in tuple_to_index:
                tuple_to_index[cleaned_match] = current_index
                index_to_tuple[current_index] = cleaned_match
                current_index += 1

    # print(f"tuple to index: {tuple_to_index}")
    # input("...")

    # Step 2: Use integer indices in the variable domains
    variables = {}
    for record in records:
        matches = [tuple_to_index[m[0]] for m in t1_dict[(record,)]]
        # print(f"record {record} has integer matches {matches}")
        variables[record] = model.NewIntVarFromDomain(cp_model.Domain.FromValues(matches), str(record))

    # Add AllDifferent constraint
    model.AddAllDifferent(variables.values())
    input("...")

    # Add t-wise constraints for t > 1
    if t > 1:
        t_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/matches/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())
        
        for rec_tup in combinations(records, t):
            sorted_tuple = tuple(sorted(rec_tup))
            # print(f"rec tuple is {sorted_tuple}")
            # input(",,,")
            matches = t_dict.get(sorted_tuple, [])
            # print(f"matches for rect tup {sorted_tuple} are {matches}")
            input("..")

            # Build the disjunctive constraint
            for match in matches:
                for i in range(t):
                    
                    # print(f"Constraining {variables[sorted_tuple[i]]} == {match[i]}")
                    # input("...")
                    model.AddVariable(variables[sorted_tuple[i]] == match[i])

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        solution = {record: index_to_tuple[solver.Value(variables[record])] for record in records}
        return solution if not iterate else [solution]  # Adjust for iteration logic if needed

    print("No solution found.")
    return None