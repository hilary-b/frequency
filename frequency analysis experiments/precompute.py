import pickle
import math
import time
import argparse
from itertools import product, combinations
from helpers import *
import boto3
from tqdm import tqdm


def precompute(t,dim,dist,n,dp,valtup,matches,small):

    # Flags for which precompute tasks to perform
    compute_dp_freq = dp
    compute_val_tup_freq = valtup
    compute_matches = matches
    small = small

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
        record_value_dict = {0:(32,3),1:(19,20),2:(10,27),5:(4,23),20:(27,12),25:(3,13),121:(29,12),309:(30,9),313:(18,16),334:(5,24)}
    elif dim == 3:
        record_value_dict = {0:(4,2,9),1:(6,5,9),2:(3,2,1),3:(3,3,9),4:(3,3,1),5:(2,2,1),7:(2,1,10),9:(2,3,1),10:(4,3,9),11:(6,1,9)}
    elif dim == 4:
        record_value_dict = {0:(4,2,5,3),1:(6,5,2,1),2:(3,2,1,3),3:(3,4,3,6),4:(3,3,1,5),5:(2,2,1,6),7:(2,1,5,6),9:(2,3,1,1),10:(4,3,6,2),11:(6,1,6,3)}
    elif dim == 5:
        record_value_dict = {0:(4,2,1,3,2),1:(4,4,2,1,2),2:(3,2,1,3,1),3:(3,4,3,4,2),4:(3,3,1,1,4),5:(2,2,1,2,4),7:(2,1,1,2,2),9:(2,3,1,1,3),10:(4,3,1,2,1),11:(1,1,1,3,3)}

    if small == True:
        n = 5 # reduced record count
        if dim == 1:
            N = 100
            record_value_dict = {0:(78,),1:(41,),2:(80,),5:(90,),20:(31,)}
        elif dim == 2:
            N = 10
            record_value_dict = {0:(2,3),1:(9,10),2:(10,7),5:(4,3),20:(7,2)}
        elif dim == 3:
            N = 5
            record_value_dict = {0:(4,2,4),1:(1,5,4),2:(3,2,1),3:(3,3,4),4:(3,3,1),}

        # if we want to go to 4 dimensions, we can try a domain of 256
        # if dim == 1:
        #     N = 256
        # elif dim == 2:
        #     N = 16
        # elif dim == 3:
        #     N = 6
        # elif dim == 4:
        #     N = 4
    
    # COMPUTE THE FREQUENCY OF EVERY DOMINANT PAIR
    if compute_dp_freq == 1:
        precompute_timer = time.time()
        path = f"dp_frequencies/{dist}/{dim}_dimensions.pkl"

        pair_frequency_dict = {}
        for v in tqdm(product(range(1, N+1), repeat=dim)): # iterate over all values in domain
            for dv in get_all_dominating_values(v,N): # iterate over all dominating values of v
                pair = (v,dv)
                frequency = compute_pair_weight(pair,dist,N)
                pair_frequency_dict[pair] = frequency

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
        total_t_tups = math.comb(1000,t)
        progress_counter = 0
        vals = []
        path = f"val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl"
        val_tup_freq_dict = {}
        # all values in domain
        for v in product(range(1, N + 1), repeat=dim):
            vals.append(v)
        print(f"Total combinations: {total_t_tups}")
        # iterate over all t-tuples of values
        for val_tuple in tqdm(combinations(vals,t)):
            sorted_val_tup = tuple(sorted(val_tuple)) # sort values for consistency
            bounding_pair = get_mbq(sorted_val_tup,dim)
            freq = dp_dict[bounding_pair]

            if freq in val_tup_freq_dict.keys():
                val_tup_freq_dict[freq].append(sorted_val_tup)
            else:
                val_tup_freq_dict[freq] = [sorted_val_tup]
            # progress_counter += 1
            # if progress_counter %100000 == 0:
            #     print(f"progress on val tuples: {progress_counter/total_t_tups}")
        # dump to pkl
        object = s3.Object('freq-analysis',f'results/{path}' )
        object.put(Body=pickle.dumps(val_tup_freq_dict))

        print(f"computed value tuple frequencies in {dim} dimension for {dist} dist in {time.time()-precompute_timer}")


    # COMPUTE RECORD-VALUE MATCHES FOR T-CONSTRAINT

    # # method that uses t-1 results to refine matches
    # if compute_matches == 1:
    #     precompute_timer = time.time()
    #     path = f"matches/{dist}/{dim}_dim/t{t}.pkl"
    #     records = list(record_value_dict.keys())
    #     matches_dict = {}

    #     # Load dominant pair frequency dict
    #     dp_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/dp_frequencies/{dist}/{dim}_dimensions.pkl").get()['Body'].read())

    #     # Load value frequency dict
    #     val_tup_freq_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())
        
    #     # for t==1 just compute singleton candidates and store as t1 matches
    #     if t == 1:
        
    #         for t_tuple in combinations(records,t):
    #             sorted_tuple = tuple(sorted(t_tuple)) # sort record tuples for consistency
    #             matches = find_matches_for_tuple(sorted_tuple,record_value_dict,val_tup_freq_dict,dp_dict,dist,N)
    #             matches_dict[sorted_tuple] = matches

    #         # dump to pkl file
    #         object = s3.Object('freq-analysis',f'results/{path}')
    #         object.put(Body=pickle.dumps(matches_dict))

    #         print(f"precomputed t{t} matches for {dim} dimensions in {time.time()-precompute_timer} seconds")
        
    #     # for t > 1, use small solver instances to refine matches
    #     if t > 1:

    
    # old method without t-1 checks
    if compute_matches == 1:
        precompute_timer = time.time()
        path = f"matches/{dist}/{dim}_dim/t{t}.pkl"
        records = list(record_value_dict.keys())
        matches_dict = {}

        # Load dominant pair frequency dict
        dp_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/dp_frequencies/{dist}/{dim}_dimensions.pkl").get()['Body'].read())

        # Load value frequency dict
        val_tup_freq_dict = pickle.loads(s3.Bucket("freq-analysis").Object(f"results/val_tup_frequencies/{dist}/{dim}_dim/t{t}.pkl").get()['Body'].read())

        # # handle singleton tests slightly differently
        # if t == 1:
        #     for record in records:
        #         # print(((record,),))
        #         # input("...")
        #         matches = find_matches_for_tuple((record,),record_value_dict,val_tup_freq_dict,dp_dict,dist,dim,N,t)
        #         # print(f"matches {matches}")
        #         # print(f"matches dict {matches_dict}")
        #         # input("...")
        #         matches_dict[record] = matches
        # else:
        for rec_t_tuple in tqdm(combinations(records,t)):
            sorted_tuple = tuple(sorted(rec_t_tuple)) # sort record tuples for consistency
            # print(sorted_tuple)
            # input("...")
            matches = find_matches_for_tuple(sorted_tuple,record_value_dict,val_tup_freq_dict,dp_dict,dist,dim,N,t)
            matches_dict[sorted_tuple] = matches

        object = s3.Object('freq-analysis',f'results/{path}')
        object.put(Body=pickle.dumps(matches_dict))

        print(f"computed t{t} matches for {dim} dimensions in {time.time()-precompute_timer} seconds")

    print("finished precompute task")

    # print(f"value frequency dict:")
    # input("...")
    # print(val_tup_freq_dict)
    # input("...")
    # print("dp dict")
    # input("...")
    # print(dp_dict)
    # input("...")
    # print("matches dict")
    # input("///")
    # print(matches_dict)
