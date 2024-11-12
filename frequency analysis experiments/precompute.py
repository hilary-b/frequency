import pickle
import math
import time
import multiprocessing
from itertools import product, combinations
from helpers import *
import boto3
from collections import defaultdict
from tqdm import tqdm
import psutil


def precompute(t,dim,dist,n,dp,valtup,matches):

    # Flags for which precompute tasks to perform
    compute_dp_freq = dp
    compute_val_tup_freq = valtup
    compute_matches = matches

    AWS_ACCESS_KEY_ID='AKIAYZTXUKO5VYMOKEQV'
    AWS_SECRET_ACCESS_KEY='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'

    s3 = boto3.resource('s3', 
                        use_ssl=False,
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                        )

    # USE FIXED DOMAIN FOR EACH DIMENSION
    # TODO: allow domain to vary
    if dim == 1:
        N = 1000
    elif dim == 2:
        N = 32
    elif dim == 3:
        N = 10
    elif dim == 4:
        N = 6
    elif dim == 5:
        N = 4

    # LOAD RECORDS/VALUES
    # TODO: load from file instead of hard-coding
    record_value_dict = {}
    if dim == 1:
        record_value_dict = {0:(782),1:(418),2:(801),5:(906),20:(78),25:(33),121:(968),309:(354),313:(165),334:(862)}
    elif dim == 2:
        record_value_dict = {0:(32,3),1:(19,20),2:(10,27),5:(4,23),20:(27,12),25:(3.13),121:(29,12),309:(30,9),313:(18,16),334:(5,24)}
    elif dim == 3:
        record_value_dict = {0:(4,2,9),1:(6,5,9),2:(3,2,1),3:(3,3,9),4:(3,3,1),5:(2,2,1),7:(2,1,10),9:(2,3,1),10:(4,3,9),11:(6,1,9)}
    elif dim == 4:
        pass
    elif dim == 5:
        pass

    # COMPUTE THE FREQUENCY OF EVERY DOMINANT PAIR
    if compute_dp_freq == 1:
        precompute_timer = time.time()
        path = f"dp_frequencies/{dist}/{dim}_dimensions.pkl"

        # intialize approximate progress counter
        total_pairs = (N**dim)**2
        total_dom_pairs = total_pairs/2**(dim-1)
        count = 0

        pair_frequency_dict = {}
        for v in product(range(1, N+1), repeat=dim): # iterate over all values in domain
            for dv in get_all_dominating_values(v,N): # iterate over all dominating values of v
                pair = (v,dv)
                frequency = compute_pair_weight(pair,dist,N)
                pair_frequency_dict[pair] = frequency
                count += 1
                if count % 1000 == 0:
                    print(f"approximately {count/total_dom_pairs} percent complete")

        # dump to pkl file

        object = s3.Object('freq-analysis',f'results/{path}')
        object.put(Body=pickle.dumps(pair_frequency_dict))

        print(f"computed dp frequencies in {dim} dimension for {dist} dist in {time.time()-precompute_timer}")


    # COMPUTE THE FREQUENCY OF EVERY T-TUPLE OF VALUES
    if compute_val_tup_freq == 1:

        # Load dominant pair frequency dict
        dp_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/dp_frequencies/{dist}/{dim}_dimensions.pkl").get()['Body'].read())

        # for a given domain and t value, find the frequency of every t tuple of values
        # and store in dict keyed by frequency
        precompute_timer = time.time()
        path = f"val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl"


        available_memory = psutil.virtual_memory().available  # in bytes
        chunk_size = min(available_memory // 10, 10000)  # 10% of available memory or 10,000 combinations

        results = chunk_and_process(dist, dim, N, t, dp_dict, chunk_size=chunk_size)
        print(f"computed value tuple frequencies in {dim} dimension for {dist} dist in {time.time()-precompute_timer}")

        # dump results to pkl
        with open('./3x3.pkl', 'wb') as f:
            pickle.dump(results, f)
        object = s3.Object('freq-analysis',f'results/{path}' )
        object.put(Body=pickle.dumps(results))

    # COMPUTE RECORD-VALUE MATCHES FOR T-CONSTRAINT
    if compute_matches == 1:
        precompute_timer = time.time()
        path = f"matches/{dist}/{dim}_dim/t{t}.pkl"
        records = record_value_dict.keys()
        matches_dict = {}

        # Load dominant pair frequency dict
        dp_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/dp_frequencies/{dist}/{dim}_dimensions.pkl").get()['Body'].read())

        # Load value frequency dict
        val_tup_freq_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())

        for t_tuple in combinations(records,t):
            sorted_tuple = tuple(sorted(t_tuple)) # sort record tuples for consistency
            matches = find_matches_for_tuple(sorted_tuple,record_value_dict,val_tup_freq_dict,dp_dict,dist,N)
            matches_dict[sorted_tuple] = matches

        # dump to pkl file
        object = s3.Object('freq-analysis',f'results/{path}')
        object.put(Body=pickle.dumps(matches_dict))

        print(f"precomputed t{t} matches for {dim} dimensions in {time.time()-precompute_timer} seconds")

    print("finished precompute task")
