from reconstruct import *
from cpsatreconstruct import *

# PARAMETERS
t = 2 # set t-constraint for reconstruction and/or finding matches
n = 10 # set number of records
dimensions = 3
distribution = 'uniform' # set query distribution
N = 0
iterate = False # set to true to find every reconstruction
exp_id = None # give a unique id to experiment
special = True
cpsat = True

# USE FIXED DOMAIN FOR EACH DIMENSION
# TODO: allow domain to vary
if dimensions == 1:
    N = 1000
elif dimensions == 2:
    N = 32
elif dimensions == 3:
    N = 10
elif dimensions == 4:
    N = 6
elif dimensions == 5:
    N = 4

# LOAD RECORDS/VALUES
# TODO: load from file instead of hard-coding
record_value_dict = {}
if dimensions == 1:
    record_value_dict = {0:(782),1:(418),2:{801},5:(906),20:(78),25:(33),121:(968),309:(354),313:(165),334:(862)}
elif dimensions == 2:
    record_value_dict = {0:(32,3),1:(19,20),2:(10,27),5:(4,23),20:(27,12),25:(3,13),121:(29,12),313:(18,16),334:(5,24)}
# elif dimensions == 2:
#     record_value_dict = {0:(32,3),1:(19,20),2:(10,27),5:(4,23),20:(27,12),25:(3,13),121:(29,12),309:(30,9),313:(18,16),334:(5,24)}
# elif dimensions == 3:
#     record_value_dict = {0:(4,2,9),1:(6,5,9),2:(3,2,1),3:(3,3,9),4:(3,3,1),5:(2,2,1),7:(2,1,10),9:(2,3,1),10:(4,3,9),11:(6,1,9)}
elif dimensions == 3:
    record_value_dict = {0:(4,2,9),1:(6,5,9),2:(3,2,1),3:(3,3,9)}
elif dimensions == 4:
    record_value_dict = {0:(4,2,5,3),1:(6,5,2,1),2:(3,2,1,3),3:(3,4,3,6),4:(3,3,1,5),5:(2,2,1,6),7:(2,1,5,6),9:(2,3,1,1),10:(4,3,6,2),11:(6,1,6,3)}
elif dimensions == 5:
    record_value_dict = {0:(4,2,1,3,2),1:(4,4,2,1,2),2:(3,2,1,3,1),3:(3,4,3,4,2),4:(3,3,1,1,4),5:(2,2,1,2,4),7:(2,1,1,2,2),9:(2,3,1,1,3),10:(4,3,1,2,1),11:(1,1,1,3,3)}

    if special == True:
        N = 4
        n = 7
        # record_value_dict = {0:(1,2,3),1:(3,2,1),2:(2,2,2),3:(4,1,2),4:(3,2,2),5:(2,2,1),7:(1,1,1)}
        record_value_dict = {0:(1,2,3),1:(3,2,1),2:(2,2,2),3:(4,1,2),4:(3,2,2)}

if cpsat:
    start_time = time.time()
    if iterate == False:
        solution = cpsat_reconstruct(t,N,n,dimensions,distribution,record_value_dict,iterate=False,experiment_id=exp_id)
        print(f"found a reconstruction in {time.time()-start_time}:")
        print(solution)
    elif iterate == True:
        solutions = cpsat_reconstruct(t,N,n,dimensions,distribution,record_value_dict,iterate=True,experiment_id=exp_id)
        print(f"found {len(solutions)} reconstructions in {time.time()-start_time}")
        for s in solutions:
            print(s)
            input("...")
# FIND RECONSTRUCTION USING T-CONSTRAINT RESULTS
else:
    start_time = time.time()
    if iterate == False:
        solution = reconstruct(t,N,n,dimensions,distribution,record_value_dict,iterate=False,experiment_id=exp_id)
        print(f"found a reconstruction in {time.time()-start_time}:")
        print(solution)
    elif iterate == True:
        solutions = reconstruct(t,N,n,dimensions,distribution,record_value_dict,iterate=True,experiment_id=exp_id)
        print(f"found {len(solutions)} reconstructions in {time.time()-start_time}")
        for s in solutions:
            print(s)
            input("...")