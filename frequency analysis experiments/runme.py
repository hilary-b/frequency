from precompute import *
from datetime import datetime
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument('-t')
parser.add_argument('--dim')
parser.add_argument('--dist', default="uniform")
args=parser.parse_args()

t=int(args.t)
dim=int(args.dim)
dist = args.dist
n = 10


# for dim in range(1,4):
#     for t in range(1,(2*dim)+1):
#         precompute(t,dim,dist,n)

start = datetime.now()

precompute(t=t,dim=dim,dist=dist, n=n)

end = datetime.now()

total_time = end-start 
print(f"total time to run with t={t}, dim={dim}: {total_time}")