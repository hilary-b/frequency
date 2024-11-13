import math
import pickle
from itertools import product, combinations

# return the mbq of a t-tuple
def get_mbq(t_tup,dim):
    if type(t_tup[0]) != tuple:
        print("got a non tuple")
        input("!!!!")
    if len(t_tup[0]) != dim:
        print("dimension doesn't match tuple size")
        print("!!!!")
    
    t = len(t_tup)
    if t == 1:
        return((t_tup[0],t_tup[0]))
    
    minima = []
    maxima = []
    for d in range(dim):
        maxima.append(max([v[d] for v in t_tup]))
        minima.append(min([v[d] for v in t_tup]))
    return(tuple(minima),tuple(maxima))

# return True if u dominates v, else False
def dominates(u,v):
    dim = len(u)
    if all(u[i] >= v[i] for i in range(dim)):
        return True
    else:
        return False

# returns all values that dominate v in the domain
def get_all_dominating_values(v,N):
    dim = len(v)
    dominating_values = []
    for u in product(range(1, N + 1), repeat=dim):
        if dominates(u,v):
            dominating_values.append(u)
    return dominating_values

def find_matches_for_tuple(t_tuple,recval_dict,tup_val_dict,dp_dict,dist,dim,N):
    # t = len(t_tuple)
    # dimensions = len(t_tuple[0])
    # val_tuple = tuple([recval_dict[r] for r in t_tuple])
    val_tuple = []
    for r in t_tuple:
        val_tuple.append(recval_dict[r],)
    val_tuple = tuple(val_tuple)
    print(f"val_tuple: {val_tuple}")
    bounding_pair = get_mbq(val_tuple,dim)
    tuple_frequency = dp_dict[bounding_pair]
    print(f"bp: {bounding_pair}")
    if tuple_frequency == 2460:
        # print(tup_val_dict)
        input("...")
    matches = tup_val_dict[tuple_frequency]
    return matches

def make_random_points():
    import numpy as np

    # Generate 10 random x-coordinates between 0 and 1
    x = np.random.randrange(1,32)

    # Generate 10 random y-coordinates between 0 and 1
    y = np.random.randrange(1,32)

    # Combine x and y coordinates into a 2D array
    points = np.column_stack((x, y))

    print(points)

# returns Manhattan distance of points u and v
def l1_distance(u,v):
    sum = 0
    for i in range(len(u)):
        sum += abs(u[i]-v[i])
    return sum

# # count or enumerate the t-tuples that share a given dominant pair as mbq
# def count_tuples(t,dom_pair,enumerate=False):
#     # each point in the dominant pair represents
#     # the set of min/max values on each dimension
#     minima = dom_pair[0]
#     maxima = dom_pair[1]
#     dim = len(dom_pair[0])

# returns the weight of a dominant pair
def compute_pair_weight(pair,dist,N):
    lower = pair[0]
    upper = pair[1]
    dim = len(lower)
    max_query_size = dim*(N-1)
    pair_distance = l1_distance(lower,upper)
    pair_weight = 0
    pos_capacities = [(N - upper[i]) for i in range(dim)]
    neg_capacities = [(lower[i] - 1) for i in range(dim)]
    capacities =  pos_capacities + neg_capacities
    capacities = [c for c in capacities if c > 0]
    query_weighting = None

    # under uniform, simply count the queries covering the pair
    if dist == 'uniform':
        dominating_vals = 1
        for i in range(len(upper)):
            dominating_vals = dominating_vals * ((N+1)-upper[i])
        dominated_vals = 1
        for i in range(len(lower)):
            dominated_vals = dominated_vals * lower[i]
        return dominated_vals * dominating_vals

    # if dist == 'uniform':
    #     for q_size in range (pair_distance,max_query_size+1):
    #         balls = q_size-pair_distance
    #         num_queries = ball_bin_count(balls,capacities)
    #         pair_weight += (query_weighting(q_size) * num_queries)
    #     return pair_weight
    
    # elif dist == 'random':
    #     pair_weight = random_query_weights[pair]
    #     return pair_weight
    
    # elif dist == 'flattened':
    #     pass

def ball_bin_count(balls,bin_capacities):
    k = balls
    c = []
    for cap in bin_capacities:
        c.append(cap+1) 
    m = len(c)
    count = 0

    if m == 0 or k == 0:
        return 1

    for t in range(m+1): # t ranges from 0 to m
        t_sums = list(combinations(c,t))
        for j in range(1,(math.comb(m,t)+1)): # j ranges from 1 to m choose t
            if sum(t_sums[j-1]) <= k:
                count += (math.comb(m+k-sum(t_sums[j-1])-1,m-1) * ((-1)**t))
            else:
                pass
    return count

# given a dominant pair p, output all pairs for which p is a bounding pair
def get_non_dominant_pairs(pair):
    p0 = list(pair[0])
    p1 = list(pair[1])
    k = len(pair[0])
    result = [pair]

    if k == 1:
        return result
    elif pair[0] == pair[1]:
        return result
    permutations = [''.join(i) for i in product('01', repeat=k)]
    for p in permutations:
        # print(f"dominant pair: {pair}")
        # print(f"permutation: {p}")
        new_pair = [p0.copy(),p1.copy()]
        for i in range(len(p)):
            flag = int(p[int(i)])
            maximum = max(p0[i],p1[i])
            minimum = min(p0[i],p1[i])
            new_pair[flag][i] = maximum
            new_pair[abs(flag - 1)][i] = minimum
        # print(f"new pair: {new_pair}")
        new_pair = (tuple(new_pair[0]),tuple(new_pair[1]))
        result.append(new_pair)
    return result

# def count_flattened_matches(t,dim):
#     # load val:rec dictionary
#     with open(f'valrec_dicts/{dim}_valrec_dict.pkl', 'rb') as f:
#         valrec_dict = pickle.load(f)
    
#     all_values_records = valrec_dict.items()

#     # checks whether an assignment matches with a set of candidate assignments
# def check_assignment(assignment, candidates):
#     reverse = (assignment[1],assignment[0])
#     if assignment in list(candidates) or reverse in list(candidates):
#         return True
#     else:
#         return False
    
# def get_record_values(k):
#     features = ["'GAPICC'","'APICC'","'WI_X'","'HOSPID'"]
#     data_dict = {}
#     with open("data.csv") as f:
#         dict_reader = DictReader(f)
#         rows = list(dict_reader)
#     # iterate over rows
#     for i in range(len(rows)):
#         # check for empty value
#         skip = False
#         for j in range(k):
#             if rows[i][features[j]] == '.':
#                 skip = True
#         # process row 
#         if skip == False:
#             data_dict[i] = []
#             for j in range(k):
#                 value = rows[i][features[j]]
#                 if j == 3:
#                     value = int(value[-2])+1
#                 elif float(value) >= 1:
#                     value = 1
#                 else:
#                     value = int(round(float(value),1) * 10)
#                 data_dict[i].append(value)
#     return data_dict