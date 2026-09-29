"""
Financial model for upgrading BVG's e-bus depot chargers from unidirectional to
bidirectional (Bus-to-Grid, B2G), period 2025-2030.

It rebuilds the CAPEX and bus O&M figures from the proposal's assumptions, then runs
the charging-price and discharge-availability sensitivity analysis and writes the
results used by the web demo.

Usage:
    python analysis/b2g_financial_model.py
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "data" / "b2g_model.json"

# --- Fleet roll-out (BVG targets) ------------------------------------------------
FLEET_BY_YEAR = {2025: 227, 2026: 227, 2027: 550, 2028: 550, 2029: 550, 2030: 1250}
BUS_PRICE_EUR = 550_000               # Ebusco 2.2 / Solaris Urbino 18
OM_SHARE = 0.15                       # yearly O&M as a share of asset value

# --- Charging infrastructure -------------------------------------------------------
CHARGER_EUR_PER_KW = {"unidirectional": 350, "bidirectional": 455}   # +30 %
STATIONS_CAPEX_UNI_EUR = 136_500_000  # chargers, depot upgrades, software, civil works

# --- Operations (from the proposal's OPEX table) -----------------------------------
STATIONS_OM_EUR = 90_499_500
BASELINE_CHARGE_PRICE = 90            # EUR/MWh (SMARD, 2025)
BASELINE_CHARGING_COST_EUR = 114_586_056
# Night charging (00:00-05:00): 50 % of the fleet, 520 kWh average battery, 80 % charge.

# --- Discharging revenue, Scenario A (15 % of fleet, 50 % of battery, 150 EUR/MWh) -
REVENUE_A_BY_PERIOD = {"2025-2026": 2_326_568, "2027-2029": 14_092_650, "2030": 12_811_500}
DISCHARGE_PRICE = 150                 # EUR/MWh, conservative vs a 280 EUR/MWh peak

CHARGE_SCENARIOS = {"1": 10, "2": 20, "3": 30}          # EUR/MWh in the optimised window
DISCHARGE_SCENARIOS = {"A": 0.15, "B": 0.25, "C": 0.30}  # share of fleet discharging at peaks


def capex() -> dict:
    new_buses = FLEET_BY_YEAR[2030] - FLEET_BY_YEAR[2025]
    fleet = new_buses * BUS_PRICE_EUR
    ratio = CHARGER_EUR_PER_KW["bidirectional"] / CHARGER_EUR_PER_KW["unidirectional"]
    stations = {"unidirectional": STATIONS_CAPEX_UNI_EUR, "bidirectional": STATIONS_CAPEX_UNI_EUR * ratio}
    return {case: {"fleet": fleet, "stations": s, "total": fleet + s} for case, s in stations.items()}


def baseline_opex() -> dict:
    bus_years_value = sum(n * BUS_PRICE_EUR for n in FLEET_BY_YEAR.values())
    parts = {
        "bus_om": OM_SHARE * bus_years_value,
        "stations_om": STATIONS_OM_EUR,
        "charging": BASELINE_CHARGING_COST_EUR,
    }
    parts["total"] = sum(parts.values())
    return parts


def charging_savings(price_eur_mwh: float) -> float:
    """Charging cost scales with price: energy = baseline cost / baseline price."""
    energy_mwh = BASELINE_CHARGING_COST_EUR / BASELINE_CHARGE_PRICE
    return energy_mwh * (BASELINE_CHARGE_PRICE - price_eur_mwh)


def discharge_revenue(fleet_share: float) -> float:
    """Revenue scales with the share of buses discharging at peak hours."""
    return sum(REVENUE_A_BY_PERIOD.values()) * fleet_share / DISCHARGE_SCENARIOS["A"]


def scenario_matrix() -> dict:
    opex_total = baseline_opex()["total"]
    uni = {
        s: {"savings": charging_savings(p), "benefit": charging_savings(p) / opex_total}
        for s, p in CHARGE_SCENARIOS.items()
    }
    bi = {}
    for s, p in CHARGE_SCENARIOS.items():
        for d, share in DISCHARGE_SCENARIOS.items():
            total = charging_savings(p) + discharge_revenue(share)
            bi[s + d] = {"savings": charging_savings(p), "revenue": discharge_revenue(share), "benefit": total / opex_total}
    return {"unidirectional": uni, "bidirectional": bi}


def main() -> None:
    c, o, m = capex(), baseline_opex(), scenario_matrix()
    extra = c["bidirectional"]["total"] - c["unidirectional"]["total"]
    print(f"CAPEX 2025-2030: EUR {c['unidirectional']['total'] / 1e6:,.1f}M (uni) vs EUR {c['bidirectional']['total'] / 1e6:,.1f}M (bi), +EUR {extra / 1e6:,.1f}M")
    print(f"Baseline OPEX 2025-2030: EUR {o['total'] / 1e6:,.1f}M")
    print("Benefit in OPEX (savings + revenue) / baseline OPEX:")
    for s, v in m["unidirectional"].items():
        row = "  ".join(f"{s}{d}: {m['bidirectional'][s + d]['benefit']:.0%}" for d in DISCHARGE_SCENARIOS)
        print(f"  price {CHARGE_SCENARIOS[s]:>2} EUR /MWh  uni {v['benefit']:.0%}  |  bi {row}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "fleet_by_year": FLEET_BY_YEAR,
        "bus_price": BUS_PRICE_EUR,
        "capex": c,
        "opex": o,
        "baseline_charge_price": BASELINE_CHARGE_PRICE,
        "charging_energy_mwh": BASELINE_CHARGING_COST_EUR / BASELINE_CHARGE_PRICE,
        "revenue_a_by_period": REVENUE_A_BY_PERIOD,
        "revenue_a_total": sum(REVENUE_A_BY_PERIOD.values()),
        "charge_scenarios": CHARGE_SCENARIOS,
        "discharge_scenarios": DISCHARGE_SCENARIOS,
        "matrix": m,
    }, indent=1), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
