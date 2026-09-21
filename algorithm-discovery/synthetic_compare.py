"""Matched RejDE-on/off comparison on fresh quadratics; Hessian is evaluator-only."""
from __future__ import annotations
import csv, math, time
from pathlib import Path
import numpy as np
from bench import BudgetExhausted, run_rejde
from geometry_probe import quadratic

class BudgetedQuadratic:
    def __init__(self, d, condition, rotated, problem_seed, budget):
        self.h, self.center = quadratic(d, condition, rotated, problem_seed)
        self.dimension=d; self.budget=budget; self.nfev=0
        self.lb=np.full(d,-5.0); self.ub=np.full(d,5.0)
        self.best_y=math.inf; self.objective_ns=0
    def __call__(self,x):
        if self.nfev>=self.budget: raise BudgetExhausted
        x=np.asarray(x,float); e=x-self.center
        t=time.perf_counter_ns(); y=float(e@self.h@e); self.objective_ns += time.perf_counter_ns()-t
        self.nfev+=1; self.best_y=min(self.best_y,y); return y

def main():
    out=Path('results/synthetic-rejde.csv'); rows=[]
    cfg={"popsize":5,"init":"halton","mutation":(0.5,1.0),"recombination":0.7}
    for d in (5,10):
      for condition in (1.0,100.0,10000.0):
       for rotated in (False,True):
        for instance in range(1,6):
         pseed=70000+1000*d+100*int(np.log10(condition+1))+10*int(rotated)+instance
         for seed in (1,2):
          for active in (False,True):
           obj=BudgetedQuadratic(d,condition,rotated,pseed,200*d)
           run_rejde(obj,seed,{**cfg,"active":active})
           rows.append(dict(d=d,condition=condition,rotated=int(rotated),instance=instance,seed=seed,active=int(active),nfev=obj.nfev,error=obj.best_y))
    with out.open('w',newline='') as f:
      w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
    print('wrote',len(rows),'rows',out)
if __name__=='__main__': main()
