"""
Prompts Module
Manages prompt variants and their construction.
"""

from typing import Dict, Any, List
import yaml


def load_prompts(config_path: str = "config/experiment_config.yaml") -> Dict[str, Any]:
    """Load prompt configurations from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('prompts', {})


def load_query_context(config_path: str = "config/experiment_config.yaml") -> Dict[str, str]:
    """Load the base query and context from config."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('query', {})


class PromptBuilder:
    """Builds prompts from templates and query context."""
    
    def __init__(self, config_path: str = "config/experiment_config.yaml"):
        self.config_path = config_path
        self.prompts = load_prompts(config_path)
        self.query_context = load_query_context(config_path)
    
    def get_variant_names(self) -> List[str]:
        """Return list of all prompt variant names."""
        return list(self.prompts.keys())
    
    def get_variant_info(self, variant_id: str) -> Dict[str, str]:
        """Get name and description for a variant."""
        variant = self.prompts.get(variant_id, {})
        return {
            "id": variant_id,
            "name": variant.get('name', variant_id),
            "description": variant.get('description', '')
        }
    
    def build_prompt(self, variant_id: str) -> str:
        """
        Build a complete prompt from a variant template.
        
        Args:
            variant_id: The prompt variant identifier (e.g., 'P1_direct')
            
        Returns:
            The fully constructed prompt string
        """
        if variant_id not in self.prompts:
            raise ValueError(f"Unknown variant: {variant_id}")
        
        template = self.prompts[variant_id]['template']
        query = self.query_context.get('base', '')
        context = self.query_context.get('context', '')
        
        # Replace placeholders
        prompt = template.replace('{query}', query)
        prompt = prompt.replace('{context}', context)
        
        return prompt.strip()
    
    def build_all_prompts(self) -> Dict[str, Dict[str, str]]:
        """
        Build all prompt variants.
        
        Returns:
            Dict mapping variant_id to {'prompt': str, 'name': str, 'description': str}
        """
        all_prompts = {}
        for variant_id in self.get_variant_names():
            info = self.get_variant_info(variant_id)
            all_prompts[variant_id] = {
                **info,
                'prompt': self.build_prompt(variant_id)
            }
        return all_prompts
    
    def get_prompts_table(self) -> List[Dict[str, str]]:
        """Get prompts as a list suitable for creating a DataFrame."""
        all_prompts = self.build_all_prompts()
        table = []
        for variant_id, data in all_prompts.items():
            table.append({
                'Variant ID': variant_id,
                'Name': data['name'],
                'Description': data['description'],
                'Prompt Preview': data['prompt'][:150] + '...' if len(data['prompt']) > 150 else data['prompt']
            })
        return table


# Convenience function
def preview_prompts(config_path: str = "config/experiment_config.yaml"):
    """Print all prompt variants for quick review."""
    builder = PromptBuilder(config_path)
    all_prompts = builder.build_all_prompts()
    
    for variant_id, data in all_prompts.items():
        print(f"\n{'='*60}")
        print(f"Variant: {data['name']} ({variant_id})")
        print(f"Description: {data['description']}")
        print(f"{'='*60}")
        print(data['prompt'])
        print()


if __name__ == "__main__":
    preview_prompts()
