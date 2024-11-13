from precompute import *
from datetime import datetime
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument('-t')
parser.add_argument('--dim')
parser.add_argument('--dist', default="uniform")
parser.add_argument('--dp',type=int,default=0)
parser.add_argument('--valtup',type=int,default=0)
parser.add_argument('--matches',type=int,default=0)
parser.add_argument('--small',type=int,default=1)
args=parser.parse_args()

t=int(args.t)
dim=int(args.dim)
dist = args.dist
n = 10
dp = args.dp
valtup = args.valtup
matches = args.matches
small = args.small

start = datetime.now()

precompute(t=t,dim=dim,dist=dist, n=n,dp=dp,valtup=valtup,matches=matches,small=small)

end = datetime.now()

total_time = end-start 
print(f"total time to run with t={t}, dim={dim}: {total_time}")