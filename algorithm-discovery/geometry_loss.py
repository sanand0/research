"""Diagnose where best/1 DE loses useful quadratic geometry under small budgets.

The Hessian is evaluator-only. Metrics compare inverse step covariance against true
curvature before crossover, after crossover, and after greedy selection.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.stats import qmc, spearmanr

from geometry_probe import quadratic


def rho_inverse_cov(steps: np.ndarray, h: np.ndarray, seed: int) -> float:
    steps = np.asarray(steps, float)
    if steps.size == 0:
        return float("nan")
    steps = np.atleast_2d(steps)
    steps = steps[np.linalg.norm(steps, axis=1) > 1e-14]
    d = h.shape[0]
    if len(steps) < d:
        return float("nan")
    u = steps / np.linalg.norm(steps, axis=1, keepdims=True)
    cov = d * (u.T @ u) / len(u) + 1e-6 * np.eye(d)
    metric = np.linalg.inv(cov)
    rng = np.random.default_rng(seed)
    z = rng.normal(size=(500, d)); z /= np.linalg.norm(z, axis=1, keepdims=True)
    true = np.einsum("ij,jk,ik->i", z, h, z)
    pred = np.einsum("ij,jk,ik->i", z, metric, z)
    return float(spearmanr(true, pred).statistic)


def directional_scale(steps: np.ndarray, h: np.ndarray) -> tuple[float, float]:
    """Median absolute projection on softest and stiffest Hessian eigenvectors."""
    if len(steps) == 0:
        return float("nan"), float("nan")
    _, vecs = np.linalg.eigh(h)
    proj = np.abs(np.asarray(steps) @ vecs)
    return float(np.median(proj[:, 0])), float(np.median(proj[:, -1]))


def run_case(d: int, condition: float, rotated: bool, seed: int, cr: float, f_lo: float, f_hi: float, budget_d: int) -> list[dict]:
    rng = np.random.default_rng(seed)
    h, center = quadratic(d, condition, rotated, 120_000 + seed)
    lb = np.full(d, -5.0); ub = np.full(d, 5.0); span = ub - lb
    n = 5 * d
    pop = qmc.scale(qmc.Halton(d, scramble=True, seed=seed).random(n), lb, ub)
    def f(x):
        e=x-center; return float(e@h@e)
    vals=np.array([f(x) for x in pop]); nfev=n; generation=0; out=[]
    while nfev < budget_d*d:
        generation += 1
        best=pop[np.argmin(vals)].copy(); scale=float(rng.uniform(f_lo,f_hi)) if f_hi>f_lo else f_lo
        donor_steps=[]; trial_steps=[]; trials=[]
        for i in range(n):
            eligible=np.delete(np.arange(n),i); a,b=rng.choice(eligible,2,replace=False)
            donor=best+scale*(pop[a]-pop[b]); donor_step=donor-pop[i]
            mask=rng.random(d)<cr; mask[rng.integers(d)]=True
            trial=np.where(mask,donor,pop[i]); bad=(trial<lb)|(trial>ub); trial[bad]=rng.uniform(lb[bad],ub[bad])
            donor_steps.append(donor_step/span); trial_steps.append((trial-pop[i])/span); trials.append(trial)
        accepted=[]; improvements=[]; remaining=min(n,budget_d*d-nfev)
        parent_vals=vals.copy()
        for i,trial in enumerate(trials[:remaining]):
            y=f(trial); nfev+=1
            if y <= vals[i]:
                accepted.append((trial-pop[i])/span); improvements.append(vals[i]-y); pop[i]=trial; vals[i]=y
        donor_arr=np.asarray(donor_steps[:remaining]); trial_arr=np.asarray(trial_steps[:remaining]); acc_arr=np.asarray(accepted)
        sd,td=directional_scale(donor_arr,h); st,tt=directional_scale(trial_arr,h); sa,ta=directional_scale(acc_arr,h)
        out.append({
            "dimension":d,"condition":condition,"rotated":int(rotated),"seed":seed,"cr":cr,"f_lo":f_lo,"f_hi":f_hi,
            "generation":generation,"nfev":nfev,"accept_rate":len(accepted)/remaining,
            "rho_inv_donor":rho_inverse_cov(donor_arr,h,seed+generation*11),
            "rho_inv_trial":rho_inverse_cov(trial_arr,h,seed+generation*13),
            "rho_inv_accepted":rho_inverse_cov(acc_arr,h,seed+generation*17),
            "soft_donor":sd,"stiff_donor":td,"soft_trial":st,"stiff_trial":tt,"soft_accepted":sa,"stiff_accepted":ta,
            "best":float(vals.min()),
        })
    return out


def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,default=Path('results/geometry-loss.csv')); p.add_argument('--seeds',type=int,default=10); p.add_argument('--budget-d',type=int,default=100)
    args=p.parse_args(); rows=[]
    for d in (5,10):
      for condition in (1.0,100.0,10000.0):
       for rotated in (False,True):
        for cr in (0.3,0.7,1.0):
         for f_lo,f_hi in ((0.5,1.0),):
          for seed in range(1,args.seeds+1): rows += run_case(d,condition,rotated,seed,cr,f_lo,f_hi,args.budget_d)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',newline='') as f:
      w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
    print('wrote',len(rows),'rows to',args.output)
if __name__=='__main__': main()
