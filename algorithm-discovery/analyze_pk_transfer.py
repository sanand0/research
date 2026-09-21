import csv, json, math, statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
from pk_transfer import DIMENSION, MILESTONES_D, make_protocol, simulate_ivp, to_physical

PRIMARY=Path("results/pk-runs.csv")
ABLATION=Path("results/pk-ablation.csv")
OUT=Path("results/pk-analysis.json")

def boot(vals):
    a=np.asarray(vals,float); rng=np.random.default_rng(20260920)
    reps=np.array([np.mean(rng.choice(a,len(a),replace=True)) for _ in range(10000)])
    return [float(x) for x in np.quantile(reps,[.025,.975])]

def units(rows,alg,field,transform=float):
    d=defaultdict(list)
    for r in rows:
        if r["algorithm"]==alg: d[int(r["subject"])].append(transform(r[field]))
    return {k:statistics.median(v) for k,v in d.items()}

def compare(rows,a,b,md):
    f=f"obj_{md}d"
    ua=units(rows,a,f,lambda x:math.log10(max(float(x),1e-16)))
    ub=units(rows,b,f,lambda x:math.log10(max(float(x),1e-16)))
    vals=[ub[s]-ua[s] for s in sorted(ua)]
    return {"subjects":len(vals),"mean_log10_advantage":statistics.mean(vals),
            "median_log10_advantage":statistics.median(vals),
            "wins":sum(v>0 for v in vals),
            "mean_95pct_subject_bootstrap":boot(vals),"per_subject":vals}

def independent(rows,protocol):
    truths={s["subject"]:s for s in protocol["subjects"]}
    maxabs=maxrel=0.0
    for r in rows:
        sub=truths[int(r["subject"])]
        obs=simulate_ivp(np.array(list(sub["physical_truth"].values()),float))
        theta=to_physical(np.asarray(json.loads(r["best_x_json"]),float))
        pred=simulate_ivp(theta)
        resid=np.log(np.maximum(pred,1e-300))-np.log(np.maximum(obs,1e-300))
        ivp=float(np.mean(resid**2)); fast=float(r["final_objective"])
        diff=abs(ivp-fast); maxabs=max(maxabs,diff); maxrel=max(maxrel,diff/max(abs(fast),1e-16))
    return {"fits_checked":len(rows),"max_abs_objective_difference":maxabs,
            "max_rel_objective_difference":maxrel}

def main():
    protocol=make_protocol()
    primary=list(csv.DictReader(PRIMARY.open()))
    ablation=list(csv.DictReader(ABLATION.open()))
    allrows=primary+ablation
    out={"primary_runs":len(primary),"ablation_runs":len(ablation),
         "budget_overshoots":sum(int(r["nfev"])>int(r["budget"]) for r in allrows),
         "independent_solve_ivp_verification":independent(allrows,protocol),
         "primary_comparisons":{},"ablation_comparisons":{},"target_efficiency":{}}

    for a,b in [("scipy-p2-halton","scipy-default-p15"),
                ("lshade-p2","scipy-default-p15"),
                ("cma-s30","scipy-default-p15"),
                ("scipy-p2-halton","cma-s30"),
                ("lshade-p2","cma-s30"),
                ("scipy-p2-halton","lshade-p2")]:
        out["primary_comparisons"][f"{a}_vs_{b}"]={str(md):compare(primary,a,b,md) for md in MILESTONES_D}

    for a,b,label in [
        ("scipy-p2-lhs","scipy-default-p15","population_effect_lhs_2D_vs_15D"),
        ("scipy-p2-halton","scipy-p15-halton","population_effect_halton_2D_vs_15D"),
        ("scipy-p2-halton","scipy-p2-lhs","initialization_effect_at_2D_halton_vs_lhs"),
        ("scipy-p15-halton","scipy-default-p15","initialization_effect_at_15D_halton_vs_lhs")]:
        out["ablation_comparisons"][label]={str(md):compare(allrows,a,b,md) for md in MILESTONES_D}

    for alg in ["scipy-default-p15","scipy-p2-halton","lshade-p2","cma-s30"]:
        rs=[r for r in primary if r["algorithm"]==alg]
        out["target_efficiency"][alg]={}
        for field in ["hit_obj_1e-4","hit_obj_1e-6","hit_param_005","hit_param_001"]:
            hits=[int(r[field])/DIMENSION for r in rs if r[field]]
            out["target_efficiency"][alg][field]={
                "successes":len(hits),"runs":len(rs),
                "median_nfev_per_d_given_success":statistics.median(hits) if hits else None}
        out["target_efficiency"][alg]["nfev"]={
            "min":min(int(r["nfev"]) for r in rs),
            "median":statistics.median(int(r["nfev"]) for r in rs),
            "max":max(int(r["nfev"]) for r in rs)}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
