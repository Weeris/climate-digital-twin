"""
HK Risk Report Generator

Generates risk assessment reports for HK property portfolios.
Supports PDF, CSV, and HTML output formats.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import csv
import json


@dataclass
class HKDistrictSummary:
    """District-level risk summary."""
    district: str
    total_exposure: float
    property_count: int
    avg_damage_ratio: float
    avg_insurance_coverage: float
    total_premium: float
    expected_loss: float
    risk_score: float


@dataclass
class PortfolioAnalysis:
    """Portfolio-level analysis results."""
    total_exposure: float
    total_insurance_coverage: float
    coverage_gap: float
    total_premium: float
    expected_annual_loss: float
    district_summaries: List[HKDistrictSummary]
    concentration_analysis: Dict
    recommendations: List[str]


class HKReportGenerator:
    """Generates risk assessment reports for HK portfolios."""
    
    def __init__(self):
        """Initialize report generator."""
        self.report_date = datetime.now().strftime("%Y-%m-%d")
    
    def generate_district_summary(
        self,
        portfolio: List[Dict],
        district: str
    ) -> HKDistrictSummary:
        """Generate risk summary for a district."""
        district_props = [p for p in portfolio if p.get("district", "").lower() == district.lower()]
        
        if not district_props:
            return None
        
        total_value = sum(p.get("property_value", 0) for p in district_props)
        avg_damage = sum(p.get("damage_ratio", 0) for p in district_props) / len(district_props)
        avg_coverage = sum(p.get("insurance_coverage", 0) for p in district_props) / len(district_props)
        total_premium = sum(p.get("annual_premium", 0) for p in district_props)
        expected_loss = sum(p.get("expected_loss", 0) for p in district_props)
        
        # Calculate risk score (0-100)
        risk_score = min(100, avg_damage * 100 + (1 - avg_coverage / total_value if total_value > 0 else 0) * 50)
        
        return HKDistrictSummary(
            district=district,
            total_exposure=total_value,
            property_count=len(district_props),
            avg_damage_ratio=avg_damage,
            avg_insurance_coverage=avg_coverage,
            total_premium=total_premium,
            expected_loss=expected_loss,
            risk_score=risk_score
        )
    
    def analyze_portfolio(self, portfolio: List[Dict]) -> PortfolioAnalysis:
        """Analyze entire portfolio and generate summary."""
        districts = set(p.get("district", "unknown").lower() for p in portfolio)
        
        district_summaries = []
        for district in districts:
            summary = self.generate_district_summary(portfolio, district)
            if summary:
                district_summaries.append(summary)
        
        total_exposure = sum(p.get("property_value", 0) for p in portfolio)
        total_coverage = sum(p.get("insurance_coverage", 0) for p in portfolio)
        coverage_gap = max(0, total_exposure - total_coverage)
        total_premium = sum(p.get("annual_premium", 0) for p in portfolio)
        expected_loss = sum(p.get("expected_loss", 0) for p in portfolio)
        
        # Concentration analysis
        weights = [s.total_exposure / total_exposure for s in district_summaries if total_exposure > 0]
        hhi = sum(w ** 2 for w in weights) if weights else 0
        
        concentration = {
            "hhi": hhi,
            "max_district": max(district_summaries, key=lambda s: s.total_exposure).district if district_summaries else None,
            "max_weight": max(weights) if weights else 0,
            "concentration_level": "high" if hhi > 0.25 else "medium" if hhi > 0.15 else "low"
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(district_summaries, concentration)
        
        return PortfolioAnalysis(
            total_exposure=total_exposure,
            total_insurance_coverage=total_coverage,
            coverage_gap=coverage_gap,
            total_premium=total_premium,
            expected_annual_loss=expected_loss,
            district_summaries=district_summaries,
            concentration_analysis=concentration,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        summaries: List[HKDistrictSummary],
        concentration: Dict
    ) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        # Check for coverage gaps
        for summary in summaries:
            if summary.avg_insurance_coverage < summary.total_exposure * 0.8:
                recommendations.append(
                    f"Increase insurance coverage for {summary.district}: "
                    f"current coverage {summary.avg_insurance_coverage/summary.total_exposure*100:.0f}% of exposure"
                )
        
        # High-risk districts
        high_risk = [s for s in summaries if s.risk_score > 50]
        for district in high_risk:
            recommendations.append(
                f"Implement mitigation measures for {district}: "
                f"risk score {district.risk_score:.0f}"
            )
        
        # Concentration risk
        if concentration["concentration_level"] == "high":
            recommendations.append(
                f"Reduce concentration in {concentration['max_district']}: "
                f"current weight {concentration['max_weight']*100:.0f}%"
            )
        
        # Typhoon-prone areas
        typhoon_districts = [s for s in summaries if "island" in s.district or "southern" in s.district]
        for district in typhoon_districts:
            recommendations.append(
                f"Review typhoon coverage for {district} due to elevated exposure"
            )
        
        return recommendations
    
    def generate_csv_report(self, portfolio: List[Dict], output_path: str) -> None:
        """Export portfolio analysis to CSV."""
        analysis = self.analyze_portfolio(portfolio)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(["HK Climate Risk Report"])
            writer.writerow(["Report Date", self.report_date])
            writer.writerow([])
            
            # Summary
            writer.writerow(["Portfolio Summary"])
            writer.writerow(["Total Exposure (HKD)", analysis.total_exposure])
            writer.writerow(["Total Insurance Coverage (HKD)", analysis.total_insurance_coverage])
            writer.writerow(["Coverage Gap (HKD)", analysis.coverage_gap])
            writer.writerow(["Total Annual Premium (HKD)", analysis.total_premium])
            writer.writerow(["Expected Annual Loss (HKD)", analysis.expected_annual_loss])
            writer.writerow([])
            
            # District details
            writer.writerow(["District Analysis"])
            writer.writerow([
                "District", "Properties", "Exposure (HKD)", "Damage Ratio",
                "Coverage (HKD)", "Premium (HKD)", "Expected Loss (HKD)", "Risk Score"
            ])
            
            for summary in analysis.district_summaries:
                writer.writerow([
                    summary.district,
                    summary.property_count,
                    summary.total_exposure,
                    f"{summary.avg_damage_ratio:.2%}",
                    summary.avg_insurance_coverage,
                    summary.total_premium,
                    summary.expected_loss,
                    f"{summary.risk_score:.1f}"
                ])
            
            writer.writerow([])
            
            # Recommendations
            writer.writerow(["Recommendations"])
            for i, rec in enumerate(analysis.recommendations, 1):
                writer.writerow([f"{i}. {rec}"])
    
    def generate_html_report(self, portfolio: List[Dict], output_path: str) -> None:
        """Export portfolio analysis to HTML."""
        analysis = self.analyze_portfolio(portfolio)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>HK Climate Risk Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; }}
        .summary {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>HK Climate Risk Report</h1>
    <p>Report Date: {self.report_date}</p>
    
    <div class="summary">
        <h2>Portfolio Summary</h2>
        <p><strong>Total Exposure:</strong> ${analysis.total_exposure:,.0f} HKD</p>
        <p><strong>Insurance Coverage:</strong> ${analysis.total_insurance_coverage:,.0f} HKD</p>
        <p><strong>Coverage Gap:</strong> ${analysis.coverage_gap:,.0f} HKD</p>
        <p><strong>Annual Premium:</strong> ${analysis.total_premium:,.0f} HKD</p>
        <p><strong>Expected Annual Loss:</strong> ${analysis.expected_annual_loss:,.0f} HKD</p>
    </div>
    
    <h2>District Analysis</h2>
    <table>
        <tr>
            <th>District</th>
            <th>Properties</th>
            <th>Exposure (HKD)</th>
            <th>Damage Ratio</th>
            <th>Risk Score</th>
        </tr>
"""
        
        for summary in analysis.district_summaries:
            html += f"""        <tr>
            <td>{summary.district}</td>
            <td>{summary.property_count}</td>
            <td>${summary.total_exposure:,.0f}</td>
            <td>{summary.avg_damage_ratio:.1%}</td>
            <td>{summary.risk_score:.0f}</td>
        </tr>
"""
        
        html += """    </table>
    
    <h2>Recommendations</h2>
    <ul>
"""
        
        for rec in analysis.recommendations:
            html += f"        <li>{rec}</li>\n"
        
        html += """    </ul>
</body>
</html>
"""
        
        with open(output_path, 'w') as f:
            f.write(html)