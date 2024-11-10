from precompute import *
from datetime import datetime
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument('-t')
parser.add_argument('--dim')
parser.add_argument('--dist', default="uniform")
parser.add_argument('--dp')
parser.add_argument('--valtup')
parser.add_argument('--matches')
args=parser.parse_args()

t=int(args.t)
dim=int(args.dim)
dist = args.dist
n = 10
dp = bool(args.dp)
valtup = bool(args.valtup)
matches = bool(args.matches)

start = datetime.now()

precompute(t=t,dim=dim,dist=dist, n=n,dp=dp,valtup=valtup,matches=matches)

end = datetime.now()

total_time = end-start 
print(f"total time to run with t={t}, dim={dim}: {total_time}")