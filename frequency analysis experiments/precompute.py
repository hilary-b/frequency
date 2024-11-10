import pickle
import math
import time
import argparse
from itertools import product, combinations
from helpers import *
import boto3


def precompute(t,dim,dist,n,dp,valtup,matches):

    # Flags for which precompute tasks to perform
    compute_dp_freq = dp
    compute_val_tup_freq = valtup
    compute_matches = matches

    print(compute_dp_freq)
    print(compute_val_tup_freq)
    print(compute_matches)
    input("...")

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
        pass
    elif dim == 3:
        record_value_dict = {0:(4,2,9),1:(6,5,9),2:(3,2,1),3:(3,3,9),4:(3,3,1),5:(2,2,1),7:(2,1,10),9:(2,3,1),10:(4,3,9),11:(6,1,9)}
    elif dim == 4:
        pass
    elif dim == 5:
        pass

    # COMPUTE THE FREQUENCY OF EVERY DOMINANT PAIR
    if compute_dp_freq == True:
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
    if compute_val_tup_freq == True:

        # Load dominant pair frequency dict
        dp_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/dp_frequencies/{dist}/{dim}_dimensions.pkl").get()['Body'].read())

        # for a given domain and t value, find the frequency of every t tuple of values
        # and store in dict keyed by frequency
        precompute_timer = time.time()
        total_t_tups = math.comb(1000,t)
        progress_counter = 0
        vals = []
        path = f"val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl"
        val_tup_freq_dict = {}
        # all values in domain
        for v in product(range(1, N + 1), repeat=dim):
            vals.append(v)
        # iterate over all t-tuples of values
        for val_tuple in combinations(vals,t):
            sorted_val_tup = tuple(sorted(val_tuple)) # sort values for consistency
            bounding_pair = get_mbq(sorted_val_tup)
            freq = dp_dict[bounding_pair]
            # freq = compute_pair_weight(bounding_pair,dist,N)
            if freq in val_tup_freq_dict.keys():
                val_tup_freq_dict[freq].append(sorted_val_tup)
            else:
                val_tup_freq_dict[freq] = [sorted_val_tup]
            progress_counter += 1
            if progress_counter %100000 == 0:
                print(f"progress on val tuples: {progress_counter/total_t_tups}")
        # dump to pkl
        object = s3.Object('freq-analysis',f'results/{path}' )
        object.put(Body=pickle.dumps(val_tup_freq_dict))

        print(f"computed value tuple frequencies in {dim} dimension for {dist} dist in {time.time()-precompute_timer}")


    # COMPUTE RECORD-VALUE MATCHES FOR T-CONSTRAINT
    if compute_matches == True:
        precompute_timer = time.time()
        path = f"t{t}_matches/{dim}_dimensions.pkl"
        records = record_value_dict.keys()
        matches_dict = {}

        # Load dominant pair frequency dict
        # dp_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/dp_frequencies/{dist}/{dim}_dimensions.pkl").get()['Body'].read())

        # Load value frequency dict
        val_tup_freq_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())

        for t_tuple in combinations(records,t):
            sorted_tuple = tuple(sorted(t_tuple)) # sort record tuples for consistency
            matches = find_matches_for_tuple(sorted_tuple,record_value_dict,val_tup_freq_dict,dist,N)
            matches_dict[sorted_tuple] = matches

        # dump to pkl file
        object = s3.Object('freq-analysis',f'results/{path}')
        object.put(Body=pickle.dumps(matches_dict))

        print(f"precomputed t{t} matches for {dim} dimensions in {time.time()-precompute_timer} seconds")

    print("finished precompute task")
