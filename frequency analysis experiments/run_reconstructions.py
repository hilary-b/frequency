from reconstruct import *

# PARAMETERS
t = 2 # set t-constraint for reconstruction and/or finding matches
n = 10 # set number of records
dimensions = 1
distribution = 'uniform' # set query distribution
N = 0
iterate = False # set to true to find every reconstruction
exp_id = None # give a unique id to experiment

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
    pass
elif dimensions == 3:
    record_value_dict = {0:(4,2,9),1:(6,5,9),2:(3,2,1),3:(3,3,9),4:(3,3,1),5:(2,2,1),7:(2,1,10),9:(2,3,1),10:(4,3,9),11:(6,1,9)}
elif dimensions == 4:
    pass
elif dimensions == 5:
    pass

# LOAD dominant pair frequency dict


# FIND RECONSTRUCTION USING T-CONSTRAINT RESULTS
if iterate == False:
    solution = reconstruct(t,N,n,dimensions,distribution,record_value_dict,iterate=False,experiment_id=exp_id)
    print("found a reconstruction:")
    print(solution)
elif iterate == True:
    solutions = reconstruct(t,N,n,dimensions,distribution,record_value_dict,iterate=False,experiment_id=exp_id)
    print(f"found {len(solutions)} reconstructions")