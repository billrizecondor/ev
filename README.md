# Vehicle-to-Grid Integration of Berlin's Electric Bus Fleet

A technical and financial proposal that asks whether a BVG electric bus depot in Berlin should upgrade its planned chargers to **bidirectional (Bus-to-Grid, B2G)** charging.

🌐 **Live demo:** https://billrizecondor.github.io/ev/ · 📄 [Full proposal (PDF)](<Final Technical Proposal for Vehicle-to-Grid Integration of Berlin´s Electric Bus Fleet (1).pdf>)

**Team:** Billriz Condor, Carlos Andrés Villamar Martínez, Kien Long van Ho. Supervised by Bence Bróní Bereczk.

## Key results (2025–2030)

| | Unidirectional | Bidirectional (B2G) |
|---|---:|---:|
| CAPEX (1,023 new e-buses + charging stations) | €699.2M | €740.1M |
| Discharging revenue | – | €29.2–58.5M |
| Benefit in OPEX* | 16–21% | 22–33% |

\*Charging savings plus discharging revenue, as a share of baseline OPEX (€481.8M).

- Revenue from energy arbitrage alone does **not** cover bidirectional chargers. That's expected for a public operator that isn't run for profit.
- Bidirectional chargers cost **30% more per kW**, only about **€41M (+6%)** on top of an electrification programme that is already mandated.
- B2G adds system value: peak shaving, deferred grid upgrades, and up to about **101 t CO₂ a day** avoided by replacing fossil peaker plants.

## Live demo

The [interactive demo](https://billrizecondor.github.io/ev/) includes:
- a 24-hour depot timeline showing when buses charge, discharge and are on the road
- fleet roll-out, CAPEX and OPEX charts
- a scenario explorer with sliders for charging price and the share of the fleet discharging
- the full sensitivity matrix from the report
- the financial model code, loaded directly from this repo

## Code

`analysis/b2g_financial_model.py` rebuilds the CAPEX and bus O&M figures from the proposal's assumptions (fleet roll-out, €550k per bus, €350 vs. €455 per kW chargers, 15% O&M). It then runs the charging-price × discharge-availability scenarios and writes `docs/data/b2g_model.json`.

```bash
python analysis/b2g_financial_model.py
```

## Scope of the analysis

- Bus capacities (Ebusco 2.2, Solaris Urbino 18) and depot schedules
- Berlin electricity demand profiles, summer and winter
- Technical, environmental and economic impact assessment
- CAPEX/OPEX, revenue model and sensitivity analysis
- Business model canvas, risk analysis, and a roadmap from pilot to full grid integration
