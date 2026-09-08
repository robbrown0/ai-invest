# Experiment Design

**Purpose:** Determine whether local AI and frontier research add investment value after costs, without hindsight contamination.

**Status:** DRAFT — protocol proposal, not evidence of returns or investment advice.

## Hypotheses and arms

The null position is that additional AI research does not improve risk-adjusted net performance beyond simpler controls. Test incremental local assistance, frontier assistance after its external costs, discovery outside the local candidate set, and persistence across differing regimes. HOLD/cash may be optimal. Negative results are useful scientific outcomes.

Each arm starts with the same chosen simulated $100–$300. Capital size is not a statistical sample size or a claim that real-world diversification is feasible. Small dollar costs can dominate this budget. Success never authorizes real money.

| Arm | Decision process | Treatment |
| --- | --- | --- |
| A — quantitative/basic | Preregistered eligibility, ranking, sizing and rebalancing; no LLM | Shared baseline data, deadlines, universe and risk policy |
| B — local AI | A plus bounded local extraction, bull/bear and synthesis | Log added information, tasks and resource use |
| C — frontier expert | B plus manual independent-then-comparison review | Log new sources/candidates, delay, costs and missed reviews |
| D — passive benchmark | Preregistered appropriate broad-market total-return ETF proxy and residual cash | Same initial capital, marks, minimum/fractional conventions, dividend and cost treatment |

The owner selects a legally available benchmark before seeing outcomes. This comparator is not a purchase recommendation. Hold base currency, start/cash flows, A/B/C long-only universe, risk policy, windows, accounting and simulated fill rules constant. D's broad index mandate may conflict with active individual/sector caps: disclose that difference and report raw plus exposure-matched comparisons rather than pretending identical mandates.

Maintain separate portfolios/economic ledgers per arm/run. Never infer independent arms' fills from one aggregate broker account. V0 can run all arms in a common deterministic simulator and use one isolated Alpaca PAPER account for execution-fidelity tests. Bind at most one active portfolio to a broker account in V0; extra paper accounts, if available, require distinct mappings. Strategy comparisons and broker fidelity results remain labeled separately.

Distinguish equal-information reasoning value from end-to-end workflow value. Paired frozen-packet/cutoff tests isolate reasoning. End-to-end frontier research may discover new data, but resulting decisions are eligible only after receipt/validation. Common scheduled deadlines use a preregistered late-frontier fallback (HOLD or the frozen B decision, selected before the experiment). Include failed/late research in end-to-end results; never choose the better hindsight fallback. P0 experiments are human-triggered; scheduled P1 experimentation follows automation/recovery gates.

## Preregistration and point-in-time information

Before the first decision freeze: hypothesis, primary endpoint, minimum economically useful effect, arms, model/prompt/strategy versions, universe, candidate rules/exploration quota, risk policy, horizons, rebalance times, entitlements, cost/fill assumptions, benchmark, evaluation dates, missingness/exclusions, stop rules and analysis plan. Register exploratory trials and failed searches, not only winners.

Preserve event, publication, provider availability when known, first observation and ingestion times, source corrections and provenance. Usable time is no earlier than all required availability/receipt times. Unknown historical availability makes the analysis exploratory. Store licensed snapshots or permitted excerpts plus content hashes. Never substitute current corrected filings, index constituents or future articles into a historical decision.

Use point-in-time universe membership, delisted securities and corporate actions when licensed data supports them. Missing survivorship-free history is a limitation; prioritize forward observations and do not silently purchase data. Current LLMs may know historical outcomes through training even with frozen prompts. Historical LLM backtests remain potentially contaminated unless knowledge availability is demonstrably compatible; locked forward predictions are primary evidence.

Separate chronological development/calibration, validation and untouched test windows. Purge/embargo overlapping label windows using the maximum horizon. Fit transforms/regime classifiers on training data only. Walk forward with immutable predictions; do not repeatedly tune on final holdouts. New model releases/hypotheses begin registered comparisons rather than rewrite prior experiments.

## Recommendation outcome registry

Before action record every serious candidate: discovery channel, selection probability where sampled, frozen thesis/action including HOLD/WATCH, confidence/forecast target, horizon, evidence/time, model/task versions, proposal link and decision time. Preserve rejected ideas with reasons: risk, cost, missing evidence, tradability, staleness, user choice or capacity.

At fixed registered horizons evaluate executed/non-executed ideas with identical marks/corporate-action conventions. Counterfactual entry uses the earliest executable time after information availability and common modeled costs, never pre-import prices. Delisted/missing outcomes stay visible with preregistered conservative handling rather than being dropped.

| Question | Method | Limitation |
| --- | --- | --- |
| Does confidence predict results? | Calibration and ranking by horizon/version | Sparse bins/correlated recommendations inflate certainty |
| How did rejected ideas do? | Counterfactual by reason versus executed pool | Selection bias precludes simple causal claims |
| Did risk controls help? | Offline paired constrained/unconstrained diagnostic ledger and stress losses | Different subsequent portfolios/opportunity costs; unconstrained path never executes |
| Which roles add value? | Preregistered task ablations with identical input cutoffs | Roles sharing a model are correlated |
| Which versions/regimes work? | Paired forward shadow comparisons, lagged regime labels | Multiple subgroups need multiplicity controls |
| Did frontier discover missed ideas? | Novel-candidate flag at first receipt, coverage and net outcomes | Search breadth/new information differs from reasoning skill |

Where feasible randomize additional research among matched eligible candidates, recording assignment before outcomes; use intention-to-treat including late/failed reviews. Never randomize away mandatory risk controls. Analyze both recommendations and portfolios: correct forecasts can reduce portfolio value through turnover/correlation.

## Economic ledger and metrics

Keep the economic ledger distinct from broker operational reconciliation. Track cash, positions, dividends, splits, fees and externally paid intelligence/data bills with evidence/times. Missing simulated economic events become labeled analytic adjustments, not fabricated broker fills/cash. Alpaca documents omissions including dividends, latency slippage and real liquidity effects. [Alpaca Paper Trading](https://docs.alpaca.markets/us/docs/paper-trading).

For the fixed-capital no-flow pilot, return is ending economic equity divided by initial equity minus one. Externally paid bills reduce analytic net equity even if paid outside the broker. Future flows require time-weighted strategy comparison plus separately reported money-weighted investor return; correctly time flows/expenses. Do not subtract costs twice.

| Metric | Convention |
| --- | --- |
| Total / benchmark return | Matched currency/endpoints and total-return treatment including cash/dividends |
| Excess return | Active minus matched benchmark return; disclose mandate/exposure differences |
| Net return | Ledger-based deduction of execution and allocated externally billed research/data/services |
| Maximum drawdown | Maximum peak-to-trough equity decline, gross and net separately |
| Volatility | Consistent periodic returns with sampling/annualization disclosed |
| Risk-adjusted return | Sharpe with aligned risk-free convention plus downside measure; sparse/zero-variance cases undefined |
| Turnover | Absolute traded principal over stated average equity/interval; consistent buy/sell-leg counting |
| Win rate / gain / loss | Fixed round-trip definition, partial-fill aggregation, realized/unrealized distinction, count/averages/largest loss |
| Sector concentration / correlation | Dated weights and estimator/window; unknown exposures and unstable samples labeled |
| Execution quality | Fills/nonfills/partials/rejects, arrival latency, spread and measured/modeled slippage |
| Model/data cost | Actual bills/subscription allocation separately from local resources, estimates and unknowns |

Do not annualize a few days into apparent evidence. Report paired effect sizes, uncertainty, sample/trial counts, missingness and multiplicity-adjusted comparisons. Use serial-dependence-aware methods such as a preregistered block bootstrap with sensitivity analysis; overlapping trades are not independent samples. Select one primary net endpoint and risk constraint first; secondary/subgroup claims remain exploratory unless registered separately.

## Duration, regimes and stops

A several-month pilot establishes measurement/control feasibility, not durable edge. Economic conclusions require prospective samples justified by effect-size/power analysis across different volatility, trend and liquidity regimes. Such regimes may take years; historic stress scenarios supplement but do not replace forward evidence. Neither a six- nor twelve-month timer proves profitability.

Safety stops are independent of statistical performance: control bypass, lost audit, tenant access failure, stale state, unresolved orders or severe poisoning halt affected workflows. Economic futility/benefit rules and any sequential testing must be preregistered to prevent repeated peeking. Preserve stopped arms and all costs. No experiment promotes an account to real-money modes.

## Evidence and human decisions

QA verifies synthetic dividend/split/partial-fill accounting, net cost deductions, matched cutoffs, rejection of out-of-time evidence, fixed-horizon rejected-idea results and fresh import data. Owner decisions: capital/benchmark; exact basic strategy/primary metric; effect-size/power plan; horizon/rebalance; late-frontier fallback; cost allocation; what evidence justifies more research. See [Cost Model](COST_MODEL.md) and [Model Governance](MODEL_GOVERNANCE.md).
