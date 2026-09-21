# Literature and implementation references

Checked 2026-09-10. Primary/official sources are preferred; secondary sources are only for discovery or cross-checking.

- SciPy `differential_evolution` current stable documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html
- van Stein & Bäck, **LLaMEA: A Large Language Model Evolutionary Algorithm for Automatically Generating Metaheuristics** (2024): https://arxiv.org/abs/2405.20132
- COCO / BBOB overview and function definitions: https://coco-platform.org/testsuites/bbob/overview.html and https://numbbo.github.io/coco/
- Zhang & Sanderson, **JADE: Adaptive Differential Evolution With Optional External Archive** (IEEE TEC, 2009), DOI 10.1109/TEVC.2009.2014613.
- Tanabe & Fukunaga, **Success-history based parameter adaptation for Differential Evolution** (CEC 2013), DOI 10.1109/CEC.2013.6557555.
- Tanabe & Fukunaga, **Improving the search performance of SHADE using linear population size reduction** / L-SHADE (CEC 2014), DOI 10.1109/CEC.2014.6900380.
- Vermetten, Caraffini, Kononova & Bäck, **Modular Differential Evolution** (GECCO 2023), DOI 10.1145/3583131.3590417; implementation: https://github.com/Dvermetten/ModDE
- Hansen, **The CMA Evolution Strategy: A Tutorial**: https://arxiv.org/abs/1604.00772 ; current pycma docs: https://cma-es.github.io/apidocs-pycma/
- Auger, Brockhoff & Hansen, **Mirrored Sampling and Sequential Selection for Evolution Strategies** (PPSN 2010): https://www.cmap.polytechnique.fr/~dimo.brockhoff/publicationListFiles/baha2010a.pdf
- Wang, Emmerich & Bäck, **Mirrored Orthogonal Sampling for Covariance Matrix Adaptation Evolution Strategies** (Evolutionary Computation, 2019), DOI 10.1162/evco_a_00251.
- Choi et al., **Asynchronous differential evolution with adaptive correlation matrix**: prior art for accumulating covariance/correlation information from successful DE steps.

## Novelty notes after Candidate 1

Mirrored/antithetic sampling is an established derandomization principle in evolution strategies and has been extended to orthogonal sampling. A targeted search did not surface the exact rule used by PairDE—balancing DE difference-vector donor counts while assigning opposite signs to paired targets—but that is not enough for a novelty claim. Because the underlying principle is known and PairDE failed development, classify it as a useful-combination/transfer candidate rather than a new mechanism.

Covariance/eigen-space crossover and successful-step correlation learning also predate this project. Candidate 2 should receive a targeted prior-art search before code is written.

## Candidate 2 novelty screen (2026-09-10)

- Jastrebski & Arnold, **Improving evolution strategies through active covariance matrix adaptation** (CEC 2006): negative covariance updates use unpromising offspring; summarized in current CMA-ES references at https://cma-es.github.io/ and in https://direct.mit.edu/evco/article/28/3/405/94999/Diagonal-Acceleration-for-Covariance-Matrix .
- Takahama & Sakai, **An Adaptive Differential Evolution Algorithm Utilizing Failure Information and Success Information** (CEC 2021), DOI 10.1109/CEC45853.2021.9504715. Failure information in DE is therefore not itself novel.
- Glasmachers & Krause, **The Hessian Estimation Evolution Strategy** (PPSN 2020), https://arxiv.org/abs/2003.13256; and **Convergence Analysis of the Hessian Estimation Evolution Strategy** (Evolutionary Computation 2022), DOI 10.1162/evco_a_00295. Direct curvature estimation from function values is prior art and can converge independently of quadratic conditioning.
- Wang et al., **Utilizing cumulative population distribution information in differential evolution** (Applied Soft Computing 2016), DOI 10.1016/j.asoc.2016.07.012. Covariance/eigen-coordinate DE is established.
- Zhang & Yuen, **A directional mutation operator for differential evolution algorithms** (Applied Soft Computing 2015), DOI 10.1016/j.asoc.2015.02.005. Fitness-improving directions guiding future mutation are established.
- Chen et al., **Dimension-feature-guided adaptive differential evolution algorithm** (Expert Systems with Applications 2026), DOI 10.1016/j.eswa.2025.130783, and **Differential evolution with dimensionally adaptive inheritance** (Engineering Applications of AI 2026), DOI 10.1016/j.engappai.2025.112587. Per-dimension adaptive crossover/inheritance is a currently active and crowded direction.

Candidate 2 (`RejDE`) should therefore be classified as a **useful-combination/transfer attempt**, not a new covariance-learning mechanism: it applies an active-CMA-like negative-information principle to DE trial-parent displacements after explicitly whitening out DE's existing proposal covariance, with no extra objective evaluations. The targeted search did not surface this exact construction, but its conceptual ingredients are established.

## Batch 3 additions — crossover/population/selection

- Li, Feng & Hu, **Covariance and crossover matrix guided differential evolution for global numerical optimization** (SpringerPlus, 2016): https://doi.org/10.1186/s40064-016-2838-5
- Wang et al., **Differential evolution based on covariance matrix learning and bimodal distribution parameter setting (CoBiDE)** (Applied Soft Computing, 2014): https://doi.org/10.1016/j.asoc.2014.01.038
- Choi, **An efficient eigenvector-based crossover for differential evolution: Simplifying with rank-one updates** (AIMS Mathematics, 2025): https://doi.org/10.3934/math.2025162
- Viktorin et al., **Distance based parameter adaptation for Success-History based Differential Evolution** (Swarm and Evolutionary Computation, 2019): https://doi.org/10.1016/j.swevo.2018.10.013
- **A dimensional difference-based population size adjustment framework for differential evolution** (Information Sciences, 2024): https://www.sciencedirect.com/science/article/pii/S0020025524000239
- **Differential evolution with adaptive mechanism of population size according to current population diversity** (Swarm and Evolutionary Computation, 2019): https://doi.org/10.1016/j.swevo.2019.03.014
- Piotrowski, **Review of Differential Evolution population size** (Swarm and Evolutionary Computation, 2017): https://doi.org/10.1016/j.swevo.2016.05.003
- Milani & Santucci, **Asynchronous differential evolution** (CEC 2010): https://hdl.handle.net/20.500.12071/11233
- **Is selection all you need in differential evolution?** (Applied Soft Computing, 2026): https://www.sciencedirect.com/science/article/pii/S1568494625014516

Novelty implication: preserving rotation through covariance/eigen-coordinate crossover, adapting CR/F, changing population size, and changing/restarting selection are all established research directions. Batch 4's proposed within-generation early-abort/resample mechanism must be screened specifically against asynchronous and per-evaluation DE before coding.

## Batch 4 — sequential scheduling / expensive evaluations

- SciPy differential_evolution documentation, current 1.18: dithering samples one mutation constant per generation; callable custom strategies and immediate updating are public behavior. https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html
- Zhabitskaya & Zhabitsky, Asynchronous Differential Evolution (MMCP 2011), DOI 10.1007/978-3-642-28212-6_41. Removes the population-generation loop and updates the population one evaluated trial at a time.
- Ye, Li, Wang & Suganthan, A comprehensive survey of adaptive strategies in differential evolutionary algorithms, DOI 10.1016/j.swevo.2025.102081. Useful novelty map for F/CR, mutation, population-size, search-space, learning, and composite adaptations.
- Ren & Meng, A survey on expensive optimization problems using differential evolution (Applied Soft Computing 170, 2025, 112727), DOI 10.1016/j.asoc.2025.112727. Frames limited function evaluations as the core EOP constraint and surveys framework, surrogate-assisted, and parallel/distributed DE approaches.
- Neri & Tirronen, Scale factor local search in differential evolution (Memetic Computing 1, 2009, 153–171), DOI 10.1007/s12293-009-0008-9. Direct prior art for line-searching the DE scale factor to generate higher-quality offspring.

## Batch 5 — hybrids, micro-populations, and population sizing

- Kämpf & Robinson / later hybrid-framework review: DE and CMA-ES have been applied sequentially for prefixed generations; summarized in the MOS hybrid literature.
- Zhang, Sun, Bäck, Zhang & Xu, **Controlling Sequential Hybrid Evolutionary Algorithm by Q-Learning**, IEEE Computational Intelligence Magazine 18(1), 2023, DOI 10.1109/MCI.2022.3222057. Explicitly treats switch timing in sequential hybrids as a learnable control problem.
- Qian et al., **A sequential algorithm portfolio approach for black box optimization**, Swarm and Evolutionary Computation 44 (2019), 559–570, DOI 10.1016/j.swevo.2018.07.001.
- Brown, Jin, Leach & Hodgson, **μJADE: adaptive differential evolution with a small population**. Relevant prior art for micro-populations plus an external archive; the archive is motivated as enlarging possible trial outcomes as if the population were larger.
- Piotrowski, **Review of Differential Evolution population size**, Swarm and Evolutionary Computation 32 (2017), 1–24, DOI 10.1016/j.swevo.2016.05.003.
- Kitamura & Fukunaga, **Is selection all you need in differential evolution?**, Applied Soft Computing 186C (2026), 114138. Recent evidence that retaining otherwise discarded candidates can replace several explicit population/archive mechanisms.
- SciPy differential_evolution documentation: array-valued init overrides popsize, enabling exact custom population sizes through the public API.

## Batch 6 — pharmacokinetic inverse-problem transfer

- Tutorial example of a two-compartment pharmacokinetic model with first-order absorption. The state equations use dosing, central, and peripheral amounts with ka, CL, Vc, Q, Vp and central concentration Ac/Vc. https://pmc.ncbi.nlm.nih.gov/articles/PMC10787214/
- PKPy: Python framework implementing one- and two-compartment pharmacokinetic models with and without first-order absorption. https://pmc.ncbi.nlm.nih.gov/articles/PMC12574595/
- SciPy solve_ivp documentation, used as the independent numerical ODE evaluator. https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
