# Technical Paper: Linking Climate Monte Carlo Simulations to Credit Risk Models

## Extending the Extended Vasicek Framework for Physical Climate Risk Assessment

---

## Abstract

This paper provides a technical methodology for integrating Monte Carlo simulation outputs into credit risk models, extending the framework outlined in BIS Working Paper No. 1274. We present a comprehensive approach for translating physical climate hazard projections into Probability of Default (PD) and Loss Given Default (LGD) adjustments using the Extended Vasicek Model.

**Keywords:** Climate Risk, Credit Risk, Monte Carlo Simulation, Extended Vasicek Model, Physical Risk, Financial Risk Modeling

---

## 1. Introduction

### 1.1 Background

The impact of physical climate risks on financial institutions has become increasingly significant. Central banks and financial supervisors face the challenge of quantifying how climate events—floods, wildfires, cyclones, and droughts—affect credit portfolios.

BIS Working Paper No. 1274 introduced an extended version of the Vasicek model to incorporate physical climate risk as a stochastic factor in credit risk modeling. This paper extends that work by:

1. Providing a technical bridge between Monte Carlo simulation outputs and credit risk parameters
2. Demonstrating how climate hazard scenarios translate into PD/LGD adjustments
3. Implementing portfolio-level risk aggregation methodologies

### 1.2 Problem Statement

The challenge lies in connecting two distinct modeling domains:

| Domain | Focus | Output |
|--------|-------|--------|
| **Climate Science** | Physical hazard intensity, frequency, spatial extent | Hazard maps, damage functions |
| **Credit Risk** | PD, LGD, EAD, capital adequacy | Probability of default, expected losses |

Our framework provides the mathematical and computational bridge between these domains.

---

## 2. Theoretical Framework

### 2.1 The Extended Vasicek Model

The original Vasicek model describes the dynamics of the default intensity:

$$dPD_t = \kappa(\theta - PD_t)dt + \sigma_{PD} \sqrt{PD_t} dW_t$$

**Where:**
- $\kappa$ = speed of mean reversion
- $\theta$ = long-run mean PD
- $\sigma_{PD}$ = volatility of PD
- $dW_t$ = Wiener process (Brownian motion)

#### Climate Extension (BIS 1274)

The BIS 1274 extension introduces a climate shock factor:

$$PD_t^{climate} = PD_t \times (1 + \beta_{climate} \times Z_{climate})$$

**Where:**
- $\beta_{climate}$ = climate sensitivity coefficient (0 to 1)
- $Z_{climate}$ = standardized climate shock
- The factor $(1 + \beta \times Z)$ represents the multiplicative impact on PD

### 2.2 Monte Carlo Integration

Monte Carlo simulations provide the distribution of climate shocks:

$$Z_{climate} \sim N(0, 1)$$

For each simulation path $s$:

$$PD_{T,s}^{climate} = PD_0 \times (1 + \beta_{climate} \times ClimateFactor_s \times Z_{s})$$

**Where:**
- $ClimateFactor_s$ = scenario-specific climate intensity (0 to 1)
- $Z_s$ = random shock for simulation $s$

---

## 3. Methodology

### 3.1 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLIMATE DIGITAL TWIN PIPELINE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐        │
│  │  CLIMATE DATA   │────▶│   MONTE CARLO   │────▶│   CREDIT RISK  │        │
│  │  INGESTION     │     │   SIMULATION    │     │   CALCULATION  │        │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘        │
│         │                        │                        │                   │
│         ▼                        ▼                        ▼                   │
│  • Hazard intensity        • 10,000+ paths          • PD adjustment        │
│  • Spatial exposure       • Climate shocks          • LGD adjustment        │
│  • Vulnerability curves   • Distribution stats      • EL/UL calculation    │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         OUTPUTS                                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ Stressed PD │  │  Adjusted   │  │   Capital   │  │  Portfolio  │  │   │
│  │  │  Metrics    │  │    EL/UL    │  │  Impact     │  │    VaR      │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Hazard to Financial Translation

#### Step 1: Physical Damage Calculation

For a given hazard intensity $H$ (e.g., flood depth in meters):

$$DamageRatio = f(H, AssetType, ConstructionType)$$

**Flood Damage Function:**
```
if depth ≤ 0.3m:  damage = 0.05 + 0.10 × (depth / 0.3)
elif depth ≤ 1.0m: damage = 0.15 + 0.25 × ((depth - 0.3) / 0.7)
elif depth ≤ 2.0m: damage = 0.40 + 0.30 × ((depth - 1.0) / 1.0)
else: damage = min(1.0, 0.70 + 0.15 × ((depth - 2.0) / 3.0))
```

#### Step 2: Climate Factor Derivation

The physical damage ratio translates to a climate factor:

$$ClimateFactor = DamageRatio \times RegionalMultiplier$$

Where RegionalMultiplier accounts for:
- Local flood protection standards
- Building codes compliance
- Historical recovery rates

#### Step 3: PD Adjustment

$$PD_{adjusted} = PD_{base} \times (1 + \beta_{climate} \times ClimateFactor)$$

**Typical β values:**
| Asset Type | β (Climate Sensitivity) |
|------------|------------------------|
| Residential | 0.3 - 0.5 |
| Commercial | 0.4 - 0.6 |
| Industrial | 0.5 - 0.8 |

#### Step 4: LGD Adjustment

$$LGD_{adjusted} = min(1.0, LGD_{base} \times (1 + 0.5 \times ClimateFactor))$$

The 0.5 factor reflects that collateral damage typically doesn't fully destroy recovery value.

### 3.3 Monte Carlo Simulation Architecture

```python
class MonteCarloEngine:
    """
    Monte Carlo engine for climate credit risk simulation.
    
    Connects physical hazard scenarios to credit risk distributions.
    """
    
    def run_simulation(
        self,
        portfolio: List[PortfolioAsset],
        climate_factor: float,
        n_simulations: int = 10000
    ) -> Dict:
        """
        Run Monte Carlo simulation.
        
        Returns:
            - PD distribution
            - Portfolio value distribution
            - Risk metrics (VaR, ES)
        """
        
        # Initialize portfolio value paths
        portfolio_values = np.zeros((n_simulations, time_steps + 1))
        portfolio_values[:, 0] = initial_value
        
        # Generate correlated climate shocks
        climate_shocks = np.random.standard_normal((n_simulations, time_steps))
        
        # Apply climate factor to each simulation path
        for t in range(1, time_steps + 1):
            for s in range(n_simulations):
                # Climate impact on portfolio
                climate_impact = (
                    climate_factor * 
                    climate_shocks[s, t] *
                    np.sqrt(t / time_steps)  # Risk accumulates
                )
                
                # Apply to portfolio value
                portfolio_values[s, t] = (
                    portfolio_values[s, t-1] * 
                    (1 - climate_impact)
                )
        
        return {
            "paths": portfolio_values,
            "distribution": portfolio_values[:, -1],
            "returns": (portfolio_values[:, -1] - initial_value) / initial_value
        }
```

---

## 4. Implementation Details

### 4.1 Expected Loss (EL) Calculation

$$EL = EAD \times PD \times LGD$$

**Climate-adjusted EL:**

$$EL_{climate} = EAD \times PD_{stressed} \times LGD_{stressed}$$

Where:
- $PD_{stressed} = PD_{base} \times (1 + \beta \times ClimateFactor \times Z_{99\%})$
- $Z_{99\%}$ = 99th percentile of standard normal (≈ 2.33)

### 4.2 Unexpected Loss (UL) Calculation

Using Basel IRB approximation:

$$UL = EAD \times \sqrt{PD \times LGD^2 \times (1 - PD)} \times \sqrt{Correlation}$$

**Climate-stressed UL:**

$$UL_{climate} = EAD \times \sqrt{PD_{stressed} \times LGD_{stressed}^2 \times (1 - PD_{stressed})} \times \sqrt{Correlation}$$

### 4.3 Capital Adequacy Impact

$$Capital_{additional} = (UL_{climate} - UL_{base}) \times CapitalRatio$$

**Climate Buffer (recommended):**

$$Capital_{buffer} = 15\% \times Capital_{climate}$$

---

## 5. Scenario Framework Integration

### 5.1 NGFS Scenario Mapping

| Scenario Category | Climate Factor | Physical Risk Level |
|-------------------|-----------------|---------------------|
| Orderly (NZ 2050) | 0.15 - 0.20 | Medium-Low |
| Disorderly (Divergent) | 0.30 - 0.35 | Medium-High |
| Hot House (NDCs) | 0.50 - 0.60 | High - Very High |

### 5.2 Multi-Scenario Comparison

```python
def compare_scenarios(
    portfolio: List[PortfolioAsset],
    scenarios: Dict[str, float]  # scenario_name -> climate_factor
) -> pd.DataFrame:
    """
    Compare risk metrics across climate scenarios.
    """
    results = {}
    
    for name, factor in scenarios.items():
        simulation = MonteCarloEngine().run_simulation(
            portfolio=portfolio,
            climate_factor=factor
        )
        
        # Calculate stressed PD
        stressed_pd = calculate_stressed_pd(
            base_pd=portfolio[0].base_pd,
            climate_factor=factor,
            confidence=0.99
        )
        
        results[name] = {
            "climate_factor": factor,
            "mean_return": np.mean(simulation["returns"]),
            "var_5": np.percentile(simulation["returns"], 5),
            "expected_shortfall": np.mean(simulation["returns"][simulation["returns"] < np.percentile(simulation["returns"], 5)]),
            "stressed_pd": stressed_pd,
            "probability_of_loss": np.mean(simulation["returns"] < 0)
        }
    
    return pd.DataFrame(results).T
```

---

## 6. Practical Application: Thailand Real Estate Case

### 6.1 Portfolio Structure

| Region | Asset Type | Exposure (THB) | Base PD | Base LGD |
|--------|------------|----------------|---------|----------|
| Bangkok Central | Residential | 50,000,000 | 2.0% | 40% |
| Bangkok Periphery | Residential | 30,000,000 | 1.5% | 40% |
| Chonburi | Commercial | 80,000,000 | 3.0% | 45% |
| Ayutthaya | Industrial | 120,000,000 | 4.0% | 50% |
| Rayong | Commercial | 60,000,000 | 2.5% | 40% |

### 6.2 Hazard Scenarios

**Flood Depth Projections (100-year event):**

| Region | Current (m) | Orderly (m) | Disorderly (m) | Hot House (m) |
|--------|-------------|-------------|----------------|---------------|
| Bangkok Central | 1.2 | 1.4 | 1.8 | 2.4 |
| Ayutthaya | 2.5 | 3.0 | 3.8 | 4.5 |

### 6.3 Results Summary

**Sample Output (Hot House Scenario):**

| Metric | Base | Climate-Stressed | Impact |
|--------|------|-------------------|--------|
| Expected Loss | 2,400,000 | 4,800,000 | +100% |
| Unexpected Loss | 8,500,000 | 15,200,000 | +79% |
| Capital Required | 680,000 | 1,216,000 | +79% |
| Climate Buffer | - | 182,400 | - |

---

## 7. Limitations and Future Work

### 7.1 Current Limitations

1. **Simplified Damage Functions**: Using depth-damage curves may not capture all vulnerability factors
2. **Correlation Assumptions**: Climate and systematic risk correlation is assumed constant
3. **Single Hazard Focus**: Primary implementation focuses on flood; other hazards need validation
4. **Recovery Assumptions**: LGD adjustments use simplified multipliers

### 7.2 Future Enhancements

1. **Multi-Hazard Modeling**: Combine flood, wildfire, cyclone, and drought scenarios
2. **Spatial Correlation**: Implement geographic correlation for portfolio aggregation
3. **Real-Time Updates**: Connect to live climate data feeds
4. **Machine Learning Integration**: Use ML for improved damage function calibration
5. **Regulatory Reporting**: Add Basel-compliant reporting formats

---

## 8. Conclusion

This paper presents a comprehensive framework for integrating Monte Carlo climate simulations into credit risk models using the Extended Vasicek approach. The methodology allows financial institutions to:

1. **Quantify physical climate risk** in credit portfolios
2. **Stress test** portfolios under various climate scenarios
3. **Calculate capital impacts** for regulatory compliance
4. **Compare scenarios** for risk management decisions

The framework provides a practical bridge between climate science and financial risk management, enabling more informed decision-making in the face of climate uncertainty.

---

## References

1. BIS Working Paper No. 1274: "Incorporating physical climate risks into banks' credit risk models"
2. Basel Committee on Banking Supervision: "Basel III: The Liquidity Coverage Ratio and Net Stable Funding Ratio"
3. NGFS: "NGFS Climate Scenarios Database Technical Documentation"
4. IPCC Sixth Assessment Report: "Climate Change 2021 - The Physical Science Basis"

---

## Appendix A: Mathematical Notation Summary

| Symbol | Definition |
|--------|------------|
| $PD$ | Probability of Default |
| $LGD$ | Loss Given Default |
| $EAD$ | Exposure at Default |
| $EL$ | Expected Loss |
| $UL$ | Unexpected Loss |
| $\beta_{climate}$ | Climate sensitivity coefficient |
| $Z$ | Standard normal shock |
| $\kappa$ | Speed of mean reversion |
| $\theta$ | Long-run mean |
| $\sigma$ | Volatility |
| $ClimateFactor$ | Physical damage ratio |

---

## Appendix B: Implementation Code

### B.1 Core Credit Risk Calculator

```python
class ClimateVasicek:
    """
    Extended Vasicek Model for Climate-Adjusted Credit Risk.
    """
    
    def run_full_analysis(
        self,
        exposure: float,
        time_horizon: int,
        physical_damage_ratio: float,
        n_simulations: int = 10000
    ) -> Dict:
        """
        Complete climate credit risk analysis.
        """
        # Climate adjustment
        adjustment = self.calculate_climate_adjustment(physical_damage_ratio)
        
        # Monte Carlo for stressed PD
        pd_result = self.calculate_adjusted_pd_monte_carlo(
            time_horizon=time_horizon,
            climate_factor=adjustment["climate_factor"],
            n_simulations=n_simulations
        )
        
        # Expected Loss
        base_el = exposure * self.base_pd * self.base_lgd
        stressed_el = exposure * pd_result["stressed_pd"] * adjustment["adjusted_lgd"]
        
        # Unexpected Loss
        base_ul = self.calculate_unexpected_loss(exposure, self.base_pd, self.base_lgd)
        stressed_ul = self.calculate_unexpected_loss(
            exposure, pd_result["stressed_pd"], adjustment["adjusted_lgd"]
        )
        
        # Capital
        base_capital = self.calculate_capital_requirement(base_ul)
        stressed_capital = self.calculate_capital_requirement(stressed_ul)
        
        return {
            "expected_loss": {"base": base_el, "stressed": stressed_el},
            "unexpected_loss": {"base": base_ul, "stressed": stressed_ul},
            "capital": {
                "base": base_capital["base_capital"],
                "stressed": stressed_capital["adjusted_capital"],
                "climate_buffer": stressed_capital["adjusted_capital"] * 0.15
            },
            "pd_analysis": {
                "base_pd": self.base_pd,
                "stressed_pd": pd_result["stressed_pd"]
            }
        }
```

---

*Document Version: 1.0*  
*Date: February 2026*  
*Climate Digital Twin Framework*
