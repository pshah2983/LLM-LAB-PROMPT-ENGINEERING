"""
Evaluator Module
Provides metrics and scoring functions for prompt evaluation.
"""

from typing import Dict, Any, List
import yaml


def load_evaluation_config(config_path: str = "config/experiment_config.yaml") -> Dict[str, Any]:
    """Load evaluation criteria from config."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('evaluation', {})


class ResponseEvaluator:
    """Evaluates LLM responses against defined criteria."""
    
    def __init__(self, config_path: str = "config/experiment_config.yaml"):
        self.config_path = config_path
        eval_config = load_evaluation_config(config_path)
        self.accuracy_criteria = eval_config.get('accuracy_criteria', [])
        self.completeness_checklist = eval_config.get('completeness_checklist', [])
    
    def evaluate_accuracy(self, response: str) -> Dict[str, Any]:
        """
        Evaluate accuracy based on presence of key concepts.
        
        Returns:
            Dict with 'score' (0-2), 'matched_criteria', 'missing_criteria'
        """
        response_lower = response.lower()
        matched = []
        missing = []
        
        for criterion in self.accuracy_criteria:
            # Simple keyword matching (can be enhanced with embeddings)
            keywords = criterion.lower().split()
            if any(kw in response_lower for kw in keywords):
                matched.append(criterion)
            else:
                missing.append(criterion)
        
        # Score: 0 (wrong), 1 (partial), 2 (fully correct)
        ratio = len(matched) / len(self.accuracy_criteria) if self.accuracy_criteria else 0
        if ratio >= 0.8:
            score = 2
        elif ratio >= 0.4:
            score = 1
        else:
            score = 0
        
        return {
            'score': score,
            'ratio': round(ratio, 2),
            'matched_criteria': matched,
            'missing_criteria': missing
        }
    
    def evaluate_completeness(self, response: str) -> Dict[str, Any]:
        """
        Evaluate completeness based on checklist coverage.
        
        Returns:
            Dict with 'percentage', 'covered_items', 'missing_items'
        """
        response_lower = response.lower()
        covered = []
        missing = []
        
        for item in self.completeness_checklist:
            keywords = item.lower().split()
            if any(kw in response_lower for kw in keywords):
                covered.append(item)
            else:
                missing.append(item)
        
        percentage = (len(covered) / len(self.completeness_checklist) * 100) if self.completeness_checklist else 0
        
        return {
            'percentage': round(percentage, 1),
            'covered_items': covered,
            'missing_items': missing
        }
    
    def evaluate_token_efficiency(self, response: str, token_count: int) -> Dict[str, Any]:
        """
        Evaluate token efficiency.
        
        Returns:
            Dict with 'token_count', 'words_per_token', 'efficiency_rating'
        """
        word_count = len(response.split())
        words_per_token = word_count / token_count if token_count > 0 else 0
        
        # Rating based on conciseness (lower token count for same info = better)
        if token_count < 200:
            rating = "Concise"
        elif token_count < 500:
            rating = "Moderate"
        else:
            rating = "Verbose"
        
        return {
            'token_count': token_count,
            'word_count': word_count,
            'words_per_token': round(words_per_token, 2),
            'efficiency_rating': rating
        }
    
    def detect_failure_behaviors(self, response: str) -> Dict[str, Any]:
        """
        Detect potential failure behaviors in the response.
        
        Returns:
            Dict with detected issues and confidence levels
        """
        response_lower = response.lower()
        issues = []
        
        # Overconfidence indicators
        overconfidence_phrases = [
            "definitely", "certainly", "absolutely", "without a doubt",
            "always", "never", "guaranteed"
        ]
        if any(phrase in response_lower for phrase in overconfidence_phrases):
            issues.append({
                'type': 'Overconfidence',
                'description': 'Response uses absolute language without hedging uncertainty',
                'severity': 'Medium'
            })
        
        # Potential hallucination indicators (mentions specific numbers without context)
        import re
        specific_stats = re.findall(r'\b\d{2,}\s*%\b|\b\$\d+(?:,\d+)*(?:\.\d+)?\s*(?:million|billion)?\b', response)
        if len(specific_stats) > 3:
            issues.append({
                'type': 'Potential Hallucination',
                'description': f'Response contains {len(specific_stats)} specific statistics that may need verification',
                'severity': 'High'
            })
        
        # Over-elaboration check
        word_count = len(response.split())
        if word_count > 600:
            issues.append({
                'type': 'Over-elaboration',
                'description': f'Response is {word_count} words, potentially too verbose',
                'severity': 'Low'
            })
        
        # Missing hedging language
        hedging_phrases = ["may", "might", "could", "typically", "often", "generally", "depending on"]
        if not any(phrase in response_lower for phrase in hedging_phrases):
            issues.append({
                'type': 'Missing Uncertainty Language',
                'description': 'Response lacks hedging language for uncertain claims',
                'severity': 'Medium'
            })
        
        return {
            'issues': issues,
            'issue_count': len(issues),
            'has_critical_issues': any(i['severity'] == 'High' for i in issues)
        }
    
    def full_evaluation(self, response: str, token_count: int, clarity_score: int = None) -> Dict[str, Any]:
        """
        Perform full evaluation of a response.
        
        Args:
            response: The LLM response text
            token_count: Number of tokens in the response
            clarity_score: Optional peer-rated clarity score (1-5)
            
        Returns:
            Complete evaluation dictionary
        """
        accuracy = self.evaluate_accuracy(response)
        completeness = self.evaluate_completeness(response)
        efficiency = self.evaluate_token_efficiency(response, token_count)
        failures = self.detect_failure_behaviors(response)
        
        return {
            'accuracy': accuracy,
            'completeness': completeness,
            'token_efficiency': efficiency,
            'failure_behaviors': failures,
            'clarity_score': clarity_score,
            'summary': {
                'accuracy_score': accuracy['score'],
                'completeness_pct': completeness['percentage'],
                'token_count': efficiency['token_count'],
                'issue_count': failures['issue_count']
            }
        }


def create_evaluation_summary(evaluations: Dict[str, Dict]) -> List[Dict]:
    """
    Create a summary table from multiple evaluations.
    
    Args:
        evaluations: Dict mapping variant_id to evaluation results
        
    Returns:
        List of dicts suitable for DataFrame creation
    """
    rows = []
    for variant_id, eval_result in evaluations.items():
        summary = eval_result.get('summary', {})
        rows.append({
            'Variant': variant_id,
            'Accuracy (0-2)': summary.get('accuracy_score', 'N/A'),
            'Completeness (%)': summary.get('completeness_pct', 'N/A'),
            'Token Count': summary.get('token_count', 'N/A'),
            'Issues Found': summary.get('issue_count', 'N/A'),
            'Clarity (1-5)': eval_result.get('clarity_score', 'TBD')
        })
    return rows


if __name__ == "__main__":
    # Quick test
    evaluator = ResponseEvaluator()
    sample_response = """
    To optimize inventory levels for seasonal demand, you should:
    1. Implement demand forecasting using historical data
    2. Calculate safety stock based on lead time variability
    3. Set reorder points accounting for the 6-week lead time
    4. Adjust inventory levels seasonally for the Q4 peak
    """
    
    result = evaluator.full_evaluation(sample_response, token_count=80)
    print("Evaluation Result:")
    print(f"Accuracy Score: {result['summary']['accuracy_score']}/2")
    print(f"Completeness: {result['summary']['completeness_pct']}%")
    print(f"Issues: {result['summary']['issue_count']}")
