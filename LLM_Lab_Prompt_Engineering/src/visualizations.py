"""
Visualizations Module
Creates charts and plots for prompt evaluation analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any


def setup_style():
    """Set up consistent plotting style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")


def plot_accuracy_comparison(evaluations: Dict[str, Dict], save_path: str = None):
    """
    Create bar chart comparing accuracy scores across variants.
    
    Args:
        evaluations: Dict mapping variant_id to evaluation results
        save_path: Optional path to save the figure
    """
    setup_style()
    
    variants = list(evaluations.keys())
    scores = [evaluations[v]['summary']['accuracy_score'] for v in variants]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(variants, scores, color=sns.color_palette("husl", len(variants)))
    
    ax.set_xlabel('Prompt Variant', fontsize=12)
    ax.set_ylabel('Accuracy Score (0-2)', fontsize=12)
    ax.set_title('Accuracy Score Comparison Across Prompt Variants', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 2.5)
    
    # Add value labels on bars
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(score), ha='center', va='bottom', fontsize=11)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_completeness_comparison(evaluations: Dict[str, Dict], save_path: str = None):
    """Create bar chart for completeness percentages."""
    setup_style()
    
    variants = list(evaluations.keys())
    percentages = [evaluations[v]['summary']['completeness_pct'] for v in variants]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(variants, percentages, color=sns.color_palette("coolwarm", len(variants)))
    
    ax.set_xlabel('Prompt Variant', fontsize=12)
    ax.set_ylabel('Completeness (%)', fontsize=12)
    ax.set_title('Checklist Completeness Across Prompt Variants', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)
    
    # Add value labels
    for bar, pct in zip(bars, percentages):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{pct}%', ha='center', va='bottom', fontsize=11)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_token_efficiency(evaluations: Dict[str, Dict], save_path: str = None):
    """Create scatter plot of accuracy vs token count (efficiency trade-off)."""
    setup_style()
    
    variants = list(evaluations.keys())
    token_counts = [evaluations[v]['summary']['token_count'] for v in variants]
    accuracy_scores = [evaluations[v]['summary']['accuracy_score'] for v in variants]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(token_counts, accuracy_scores, 
                         c=range(len(variants)), cmap='viridis',
                         s=200, alpha=0.7, edgecolors='black')
    
    # Label each point
    for i, variant in enumerate(variants):
        ax.annotate(variant, (token_counts[i], accuracy_scores[i]),
                   xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax.set_xlabel('Token Count', fontsize=12)
    ax.set_ylabel('Accuracy Score (0-2)', fontsize=12)
    ax.set_title('Token Efficiency: Accuracy vs. Response Length', fontsize=14, fontweight='bold')
    ax.set_ylim(-0.1, 2.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_radar_chart(evaluations: Dict[str, Dict], save_path: str = None):
    """
    Create radar chart comparing all metrics across variants.
    Metrics: Accuracy, Completeness, Efficiency (inverse of tokens), Safety (inverse of issues)
    """
    setup_style()
    
    variants = list(evaluations.keys())
    
    # Prepare normalized metrics (0-1 scale)
    metrics = ['Accuracy', 'Completeness', 'Efficiency', 'Safety']
    
    data = []
    for v in variants:
        summary = evaluations[v]['summary']
        accuracy_norm = summary['accuracy_score'] / 2  # 0-2 -> 0-1
        completeness_norm = summary['completeness_pct'] / 100  # 0-100 -> 0-1
        
        # Efficiency: lower tokens = higher efficiency (normalized inverse)
        max_tokens = max(evaluations[vv]['summary']['token_count'] for vv in variants)
        efficiency_norm = 1 - (summary['token_count'] / max_tokens) if max_tokens > 0 else 0.5
        
        # Safety: fewer issues = higher safety
        max_issues = max(evaluations[vv]['summary']['issue_count'] for vv in variants)
        safety_norm = 1 - (summary['issue_count'] / (max_issues + 1))
        
        data.append([accuracy_norm, completeness_norm, efficiency_norm, safety_norm])
    
    # Create radar chart
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    colors = sns.color_palette("husl", len(variants))
    
    for i, (variant, values) in enumerate(zip(variants, data)):
        values += values[:1]  # Complete the circle
        ax.plot(angles, values, 'o-', linewidth=2, label=variant, color=colors[i])
        ax.fill(angles, values, alpha=0.1, color=colors[i])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_title('Multi-Metric Comparison Across Prompt Variants', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_issues_heatmap(evaluations: Dict[str, Dict], save_path: str = None):
    """Create heatmap showing issue types across variants."""
    setup_style()
    
    # Collect all issue types
    all_issue_types = set()
    for v, eval_result in evaluations.items():
        for issue in eval_result.get('failure_behaviors', {}).get('issues', []):
            all_issue_types.add(issue['type'])
    
    if not all_issue_types:
        print("No issues detected across variants.")
        return None
    
    all_issue_types = sorted(list(all_issue_types))
    variants = list(evaluations.keys())
    
    # Create matrix
    matrix = []
    for v in variants:
        row = []
        issues = evaluations[v].get('failure_behaviors', {}).get('issues', [])
        issue_types_in_v = [i['type'] for i in issues]
        for issue_type in all_issue_types:
            row.append(1 if issue_type in issue_types_in_v else 0)
        matrix.append(row)
    
    df = pd.DataFrame(matrix, index=variants, columns=all_issue_types)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(df, annot=True, cmap='RdYlGn_r', cbar_kws={'label': 'Issue Present'},
                ax=ax, fmt='d', linewidths=0.5)
    
    ax.set_title('Failure Behaviors Across Prompt Variants', fontsize=14, fontweight='bold')
    ax.set_xlabel('Issue Type', fontsize=12)
    ax.set_ylabel('Prompt Variant', fontsize=12)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def generate_all_visualizations(evaluations: Dict[str, Dict], output_dir: str = "results"):
    """Generate all visualization plots and save to output directory."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    figs = {}
    
    figs['accuracy'] = plot_accuracy_comparison(evaluations, f"{output_dir}/accuracy_comparison.png")
    figs['completeness'] = plot_completeness_comparison(evaluations, f"{output_dir}/completeness_comparison.png")
    figs['efficiency'] = plot_token_efficiency(evaluations, f"{output_dir}/token_efficiency.png")
    figs['radar'] = plot_radar_chart(evaluations, f"{output_dir}/radar_comparison.png")
    figs['issues'] = plot_issues_heatmap(evaluations, f"{output_dir}/issues_heatmap.png")
    
    print(f"All visualizations saved to {output_dir}/")
    return figs


if __name__ == "__main__":
    # Demo with sample data
    sample_evaluations = {
        'P1_direct': {'summary': {'accuracy_score': 1, 'completeness_pct': 50, 'token_count': 150, 'issue_count': 2},
                      'failure_behaviors': {'issues': [{'type': 'Overconfidence'}, {'type': 'Missing Uncertainty Language'}]}},
        'P2_constrained': {'summary': {'accuracy_score': 2, 'completeness_pct': 80, 'token_count': 200, 'issue_count': 1},
                           'failure_behaviors': {'issues': [{'type': 'Missing Uncertainty Language'}]}},
        'P3_role_based': {'summary': {'accuracy_score': 2, 'completeness_pct': 90, 'token_count': 300, 'issue_count': 1},
                          'failure_behaviors': {'issues': [{'type': 'Over-elaboration'}]}},
    }
    
    generate_all_visualizations(sample_evaluations, "results")
