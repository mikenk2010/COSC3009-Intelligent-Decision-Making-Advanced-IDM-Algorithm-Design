"""
Script to update Assignment_Report.md with actual experimental results.
Run this after collect_experimental_data.py completes.
"""

import json
import re

def update_report_with_results(results_file="experimental_results.json", report_file="Assignment_Report.md"):
    """Update the report with actual experimental results."""
    
    # Read results
    try:
        with open(results_file, "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {results_file} not found. Run collect_experimental_data.py first.")
        return False
    
    standard = results.get("standard", {})
    mediated = results.get("mediated", {})
    
    if not standard or not mediated:
        print("ERROR: Results file is incomplete or contains mock data.")
        print("Please run collect_experimental_data.py with real model (not --mock)")
        return False
    
    # Read report
    try:
        with open(report_file, "r") as f:
            report_content = f.read()
    except FileNotFoundError:
        print(f"ERROR: {report_file} not found.")
        return False
    
    # Calculate improvements
    accuracy_improvement = mediated.get("accuracy", 0) - standard.get("accuracy", 0)
    sycophancy_reduction = standard.get("sycophancy_rate", 0) - mediated.get("sycophancy_rate", 0)
    sycophancy_reduction_pct = (sycophancy_reduction / standard.get("sycophancy_rate", 1)) * 100 if standard.get("sycophancy_rate", 0) > 0 else 0
    consensus_quality_improvement = mediated.get("consensus_quality", 0) - standard.get("consensus_quality", 0)
    
    # Update the table
    old_table = r"\| \*\*Accuracy\*\* \| 78\.2% \| 88\.7% \| \+10\.5% \|"
    new_table = f"| **Accuracy** | {standard.get('accuracy', 0):.1f}% | {mediated.get('accuracy', 0):.1f}% | {accuracy_improvement:+.1f}% |"
    report_content = re.sub(old_table, new_table, report_content)
    
    old_table = r"\| \*\*Sycophancy Rate\*\* \| 34\.6% \| 12\.1% \| -65\.0% \|"
    new_table = f"| **Sycophancy Rate** | {standard.get('sycophancy_rate', 0):.1f}% | {mediated.get('sycophancy_rate', 0):.1f}% | {sycophancy_reduction:+.1f}% |"
    report_content = re.sub(old_table, new_table, report_content)
    
    old_table = r"\| \*\*False Consensus\*\* \| 28\.3% \| 8\.9% \| -68\.6% \|"
    new_table = f"| **False Consensus** | {standard.get('false_consensus_rate', 0):.1f}% | {mediated.get('false_consensus_rate', 0):.1f}% | {mediated.get('false_consensus_rate', 0) - standard.get('false_consensus_rate', 0):+.1f}% |"
    report_content = re.sub(old_table, new_table, report_content)
    
    old_table = r"\| \*\*True Consensus\*\* \| 49\.9% \| 79\.8% \| \+59\.9% \|"
    new_table = f"| **True Consensus** | {standard.get('true_consensus_rate', 0):.1f}% | {mediated.get('true_consensus_rate', 0):.1f}% | {mediated.get('true_consensus_rate', 0) - standard.get('true_consensus_rate', 0):+.1f}% |"
    report_content = re.sub(old_table, new_table, report_content)
    
    old_table = r"\| \*\*Consensus Quality\*\* \| 63\.8% \| 89\.9% \| \+40\.9% \|"
    new_table = f"| **Consensus Quality** | {standard.get('consensus_quality', 0):.1f}% | {mediated.get('consensus_quality', 0):.1f}% | {consensus_quality_improvement:+.1f}% |"
    report_content = re.sub(old_table, new_table, report_content)
    
    # Update key findings
    old_finding = r"1\. \*\*Accuracy Improvement\*\*: Mediated debate achieves 13\.4% relative improvement \(78\.2% → 88\.7%\)"
    if standard.get("accuracy", 0) > 0:
        relative_improvement = (accuracy_improvement / standard.get("accuracy", 1)) * 100
        new_finding = f"1. **Accuracy Improvement**: Mediated debate achieves {relative_improvement:.1f}% relative improvement ({standard.get('accuracy', 0):.1f}% → {mediated.get('accuracy', 0):.1f}%)"
    else:
        new_finding = f"1. **Accuracy Improvement**: Mediated debate shows {accuracy_improvement:+.1f} percentage point change ({standard.get('accuracy', 0):.1f}% → {mediated.get('accuracy', 0):.1f}%)"
    report_content = re.sub(old_finding, new_finding, report_content)
    
    old_finding = r"2\. \*\*Sycophancy Reduction\*\*: 65% reduction in sycophantic incidents \(34\.6% → 12\.1%\)"
    new_finding = f"2. **Sycophancy Reduction**: {sycophancy_reduction_pct:.1f}% reduction in sycophantic incidents ({standard.get('sycophancy_rate', 0):.1f}% → {mediated.get('sycophancy_rate', 0):.1f}%)"
    report_content = re.sub(old_finding, new_finding, report_content)
    
    old_finding = r"3\. \*\*Consensus Quality\*\*: 40\.9% improvement in consensus correctness \(63\.8% → 89\.9%\)"
    new_finding = f"3. **Consensus Quality**: {consensus_quality_improvement:+.1f} percentage point improvement ({standard.get('consensus_quality', 0):.1f}% → {mediated.get('consensus_quality', 0):.1f}%)"
    report_content = re.sub(old_finding, new_finding, report_content)
    
    # Update conclusion
    old_conclusion = r"1\. \*\*13\.4% relative accuracy improvement\*\* \(78\.2% → 88\.7%\)"
    if standard.get("accuracy", 0) > 0:
        relative_improvement = (accuracy_improvement / standard.get("accuracy", 1)) * 100
        new_conclusion = f"1. **{relative_improvement:.1f}% relative accuracy improvement** ({standard.get('accuracy', 0):.1f}% → {mediated.get('accuracy', 0):.1f}%)"
    else:
        new_conclusion = f"1. **{accuracy_improvement:+.1f} percentage point accuracy change** ({standard.get('accuracy', 0):.1f}% → {mediated.get('accuracy', 0):.1f}%)"
    report_content = re.sub(old_conclusion, new_conclusion, report_content)
    
    old_conclusion = r"2\. \*\*65% reduction in sycophancy incidents\*\* \(34\.6% → 12\.1%\)"
    new_conclusion = f"2. **{sycophancy_reduction_pct:.1f}% reduction in sycophancy incidents** ({standard.get('sycophancy_rate', 0):.1f}% → {mediated.get('sycophancy_rate', 0):.1f}%)"
    report_content = re.sub(old_conclusion, new_conclusion, report_content)
    
    old_conclusion = r"3\. \*\*40\.9% improvement in consensus quality\*\* \(63\.8% → 89\.9%\)"
    new_conclusion = f"3. **{consensus_quality_improvement:+.1f} percentage point improvement in consensus quality** ({standard.get('consensus_quality', 0):.1f}% → {mediated.get('consensus_quality', 0):.1f}%)"
    report_content = re.sub(old_conclusion, new_conclusion, report_content)
    
    # Add note about experimental setup
    if "### 4.1 Experimental Setup" in report_content:
        setup_note = """
**Note:** These results are based on actual experimental runs of the system. The data was collected by running both Standard and Mediated debates on the test problems and analyzing the outcomes. Due to the small sample size (3 problems), these results should be interpreted as preliminary findings. Larger-scale evaluation would provide more statistically robust conclusions.
"""
        # Insert after experimental setup
        report_content = report_content.replace(
            "**Temperature:** Agents at 0.7, Judge at 0.3",
            f"**Temperature:** Agents at 0.7, Judge at 0.3{setup_note}"
        )
    
    # Write updated report
    with open(report_file, "w") as f:
        f.write(report_content)
    
    print(f"✅ Updated {report_file} with experimental results")
    print(f"\nResults Summary:")
    print(f"  Standard Debate Accuracy: {standard.get('accuracy', 0):.1f}%")
    print(f"  Mediated Debate Accuracy: {mediated.get('accuracy', 0):.1f}%")
    print(f"  Accuracy Improvement: {accuracy_improvement:+.1f}%")
    print(f"  Sycophancy Reduction: {sycophancy_reduction_pct:.1f}%")
    
    return True

if __name__ == "__main__":
    update_report_with_results()

