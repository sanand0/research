"""Local sensitivity geometry of the frozen PK inverse problems."""
import csv, json, math, statistics
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

from pk_transfer import make_protocol, simulate_expm, to_physical

OUT=Path("results/pk-sensitivity.json")


def jacobian_log_concentration(u, eps=1e-5):
    u=np.asarray(u,float)
    cols=[]
    for j in range(len(u)):
        up=u.copy(); dn=u.copy()
        up[j]+=eps; dn[j]-=eps
        lp=np.log(np.maximum(simulate_expm(to_physical(up)),1e-300))
        lm=np.log(np.maximum(simulate_expm(to_physical(dn)),1e-300))
        cols.append((lp-lm)/(2*eps))
    return np.column_stack(cols)


def problem_units(rows,alg,md):
    d={}
    for subject in range(1,9):
        vals=[math.log10(max(float(r[f"obj_{md}d"]),1e-16)) for r in rows
              if r["algorithm"]==alg and int(r["subject"])==subject]
        d[subject]=statistics.median(vals)
    return d


def main():
    protocol=make_protocol()
    rows=list(csv.DictReader(open("results/pk-runs.csv")))
    p2=problem_units(rows,"scipy-p2-halton",200)
    cma=problem_units(rows,"cma-s30",200)
    subjects=[]
    conds=[]; cma_adv=[]
    for s in protocol["subjects"]:
        u=np.asarray(s["unit_truth"],float)
        j=jacobian_log_concentration(u)
        singular=np.linalg.svd(j,compute_uv=False)
        cond_j=float(singular[0]/singular[-1])
        cond_h=float(cond_j**2)
        # Sloppiest local parameter combination in normalized optimizer coords.
        _,_,vh=np.linalg.svd(j,full_matrices=False)
        sloppy=vh[-1]
        sid=s["subject"]
        adv=p2[sid]-cma[sid]
        conds.append(math.log10(cond_h)); cma_adv.append(adv)
        subjects.append({
            "subject":sid,
            "jacobian_singular_values":[float(x) for x in singular],
            "gauss_newton_condition":cond_h,
            "log10_gauss_newton_condition":math.log10(cond_h),
            "sloppiest_unit_direction":[float(x) for x in sloppy],
            "cma_log10_advantage_at_200d":adv,
        })
    rho=float(spearmanr(conds,cma_adv).statistic)
    out={"subjects":subjects,"spearman_log_condition_vs_cma_200d_advantage":rho}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
