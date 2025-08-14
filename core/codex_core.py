def get_full_vault():
    # Placeholder: return a static vault log or implement logic
    return {"vault": ["entry1", "entry2", "entry3"]}

def get_insight_threads():
    # Placeholder: return a static insight feed or implement logic
    return {"insights": ["insight1", "insight2", "insight3"]}
def get_suggestion():
    # Placeholder: return a static suggestion or implement logic
    return {"suggestion": "This is a sample suggestion from CodexCore."}

def store_memory(payload: dict):
    # Placeholder: store the payload in memory or database
    return {"status": "Memory stored", "payload": payload}
"""
Codex Core - ProPrime Series Core Logic Engine
Handles symbolic logic routing and auto-routing through run_llama() function.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import re
import json

# Add the core directory to the path for imports
sys.path.append(str(Path(__file__).parent))

from mistral_interface import run_mistral, run_mistral_with_context
from prompt_preprocessor import proprime_preprocessor, enhance_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SymbolicLogicRouter:
    """Routes symbolic logic queries through appropriate processing engines"""
    
    def __init__(self):
        self.symbolic_patterns = {
            'definition': r'(?i)define|what is|meaning of|explain',
            'logical': r'(?i)logic|reasoning|proof|theorem|syllogism',
            'symbolic': r'(?i)symbol|represent|cognition|semantic|metaphor',
            'philosophical': r'(?i)philosophy|ethics|morality|values|belief',
            'mathematical': r'(?i)math|equation|formula|calculate|compute',
            'analytical': r'(?i)analyze|breakdown|structure|pattern|relationship'
        }
        
        self.context_memory = []
        self.max_context_length = 10
    
    def classify_query(self, query: str) -> List[str]:
        """Classify the query into symbolic logic categories"""
        categories = []
        
        for category, pattern in self.symbolic_patterns.items():
            if re.search(pattern, query):
                categories.append(category)
        
        return categories if categories else ['general']
    
    def should_route_to_symbolic(self, query: str) -> bool:
        """Determine if query should be routed through symbolic processing"""
        categories = self.classify_query(query)
        
        # Route to symbolic processing if it matches any symbolic patterns
        symbolic_categories = ['definition', 'logical', 'symbolic', 'philosophical', 'analytical']
        return any(cat in symbolic_categories for cat in categories)
    
    def enhance_prompt_for_symbolic(self, query: str, categories: List[str]) -> str:
        """Enhance the prompt with symbolic processing instructions"""
        
        symbolic_instructions = {
            'definition': "Provide a clear, structured definition with symbolic components:",
            'logical': "Apply logical reasoning and symbolic logic principles:",
            'symbolic': "Consider symbolic representations and cognitive patterns:",
            'philosophical': "Analyze from philosophical and ethical perspectives:",
            'analytical': "Break down into structural components and relationships:"
        }
        
        # Build enhanced prompt
        enhanced = f"[SYMBOLIC PROCESSING MODE]\n\n"
        
        for category in categories:
            if category in symbolic_instructions:
                enhanced += f"{symbolic_instructions[category]}\n"
        
        enhanced += f"\nQuery: {query}\n\n"
        enhanced += "Respond with structured symbolic analysis including:\n"
        enhanced += "1. Core definition/concept\n"
        enhanced += "2. Symbolic representations\n"
        enhanced += "3. Logical relationships\n"
        enhanced += "4. Contextual applications\n"
        
        return enhanced
    
    def add_to_context(self, query: str, response: str):
        """Add query-response pair to context memory"""
        self.context_memory.append({
            'role': 'user',
            'content': query
        })
        self.context_memory.append({
            'role': 'assistant', 
            'content': response
        })
        
        # Trim context if it gets too long
        if len(self.context_memory) > self.max_context_length * 2:
            self.context_memory = self.context_memory[-self.max_context_length * 2:]

class CodexCore:
    """Main Codex Core engine for ProPrime Series"""
    
    def __init__(self):
        self.router = SymbolicLogicRouter()
        self.processing_stats = {
            'total_queries': 0,
            'symbolic_routed': 0,
            'general_routed': 0
        }
    
    def run_llama(self, prompt: str, use_context: bool = True, **kwargs) -> str:
        """
        Main entry point for running queries through the Codex Core.
        Auto-routes symbolic logic through enhanced processing.
        
        Args:
            prompt: The input query/prompt
            use_context: Whether to use conversation context
            **kwargs: Additional parameters for the model
            
        Returns:
            Processed response from the appropriate engine
        """
        try:
            self.processing_stats['total_queries'] += 1
            
            # Classify the query
            categories = self.router.classify_query(prompt)
            is_symbolic = self.router.should_route_to_symbolic(prompt)
            
            logger.info(f"Query classified as: {categories}")
            logger.info(f"Symbolic routing: {is_symbolic}")
            
            if is_symbolic:
                return self._process_symbolic_query(prompt, categories, use_context, **kwargs)
            else:
                return self._process_general_query(prompt, use_context, **kwargs)
                
        except Exception as e:
            logger.error(f"Error in run_llama: {e}")
            return f"[Codex Core Error] {e}"
    
    def _process_symbolic_query(self, prompt: str, categories: List[str], use_context: bool, **kwargs) -> str:
        """Process queries requiring symbolic logic routing"""
        self.processing_stats['symbolic_routed'] += 1
        
        # First, enhance with ProPrime pre-processor
        enhanced_prompt = enhance_prompt(prompt, include_glyphs=True, include_memories=True, include_frames=True)
        
        # Then apply symbolic logic enhancement
        symbolic_enhanced = self.router.enhance_prompt_for_symbolic(enhanced_prompt, categories)
        
        # Use context if available and requested
        if use_context and self.router.context_memory:
            response = run_mistral_with_context(symbolic_enhanced, self.router.context_memory, **kwargs)
        else:
            response = run_mistral(symbolic_enhanced, **kwargs)
        
        # Add to context memory (use original prompt for context)
        self.router.add_to_context(prompt, response)
        
        return response
    
    def _process_general_query(self, prompt: str, use_context: bool, **kwargs) -> str:
        """Process general queries with basic ProPrime enhancement"""
        self.processing_stats['general_routed'] += 1
        
        # Apply lighter ProPrime enhancement for general queries
        enhanced_prompt = enhance_prompt(prompt, include_glyphs=False, include_memories=True, include_frames=False)
        
        # Use context if available and requested
        if use_context and self.router.context_memory:
            response = run_mistral_with_context(enhanced_prompt, self.router.context_memory, **kwargs)
        else:
            response = run_mistral(enhanced_prompt, **kwargs)
        
        # Add to context memory (use original prompt for context)
        self.router.add_to_context(prompt, response)
        
        return response
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        base_stats = {
            **self.processing_stats,
            'context_length': len(self.router.context_memory),
            'symbolic_percentage': (self.processing_stats['symbolic_routed'] / 
                                  max(self.processing_stats['total_queries'], 1)) * 100
        }
        
        # Add pre-processor stats
        preprocessor_stats = proprime_preprocessor.get_processing_stats()
        base_stats.update({
            'preprocessor_' + k: v for k, v in preprocessor_stats.items()
        })
        
        return base_stats
    
    def add_legacy_memory(self, content: str, importance: float = 1.0, tags: Optional[List[str]] = None):
        """Add a legacy memory trace"""
        proprime_preprocessor.add_legacy_memory(content, importance, tags)
        logger.info(f"Added legacy memory: {content[:50]}...")
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze a query and return enhancement analysis"""
        # Get symbolic logic classification
        categories = self.router.classify_query(query)
        is_symbolic = self.router.should_route_to_symbolic(query)
        
        # Get pre-processor analysis
        preprocessor_analysis = proprime_preprocessor.analyze_query(query)
        
        return {
            'symbolic_categories': categories,
            'is_symbolic': is_symbolic,
            'preprocessor_analysis': preprocessor_analysis
        }
    
    def preview_enhancement(self, query: str, enhancement_level: str = "full") -> str:
        """Preview how a query would be enhanced without processing it"""
        if enhancement_level == "full":
            return enhance_prompt(query, include_glyphs=True, include_memories=True, include_frames=True)
        elif enhancement_level == "symbolic":
            categories = self.router.classify_query(query)
            enhanced = enhance_prompt(query, include_glyphs=True, include_memories=True, include_frames=True)
            return self.router.enhance_prompt_for_symbolic(enhanced, categories)
        elif enhancement_level == "basic":
            return enhance_prompt(query, include_glyphs=False, include_memories=True, include_frames=False)
        else:
            return query
    
    def clear_context(self):
        """Clear the conversation context"""
        self.router.context_memory.clear()
        logger.info("Context memory cleared")
    
    def export_context(self, filepath: str):
        """Export context memory to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.router.context_memory, f, indent=2)
            logger.info(f"Context exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export context: {e}")
    
    def import_context(self, filepath: str):
        """Import context memory from JSON file"""
        try:
            with open(filepath, 'r') as f:
                self.router.context_memory = json.load(f)
            logger.info(f"Context imported from {filepath}")
        except Exception as e:
            logger.error(f"Failed to import context: {e}")

# Global instance for easy access
codex_core = CodexCore()

def run_llama(prompt: str, **kwargs) -> str:
    """
    Convenience function to run queries through Codex Core
    
    Args:
        prompt: The input query/prompt
        **kwargs: Additional parameters
        
    Returns:
        Processed response
    """
    return codex_core.run_llama(prompt, **kwargs)

def symbolic_trigger(query: str, threshold: float = 0.5) -> bool:
    """
    Trigger function to determine if a query should be processed symbolically
    
    Args:
        query: The input query to analyze
        threshold: Confidence threshold for symbolic classification
        
    Returns:
        True if query should be processed symbolically, False otherwise
    """
    try:
        # Analyze the query
        analysis = codex_core.analyze_query(query)
        
        # Check if it's classified as symbolic
        is_symbolic = analysis.get('is_symbolic', False)
        
        # Get categories for additional analysis
        categories = analysis.get('symbolic_categories', [])
        
        # Calculate confidence score based on categories
        symbolic_categories = ['definition', 'logical', 'symbolic', 'philosophical', 'analytical']
        symbolic_matches = sum(1 for cat in categories if cat in symbolic_categories)
        confidence = symbolic_matches / len(symbolic_categories) if symbolic_categories else 0
        
        # Return True if either the router says it's symbolic or confidence is above threshold
        return is_symbolic or confidence >= threshold
        
    except Exception as e:
        logger.error(f"Error in symbolic_trigger: {e}")
        return False

# Example usage and testing
if __name__ == "__main__":
    # Test the symbolic logic routing
    test_cases = [
        "Define symbolic cognition",
        "What is the relationship between logic and reasoning?",
        "Explain the philosophical implications of AI consciousness",
        "How do you calculate the area of a circle?",
        "Tell me a joke",
        "Analyze the symbolic meaning of memory in AI systems"
    ]
    
    print("=" * 60)
    print("CODEX CORE - SYMBOLIC LOGIC ROUTER TEST")
    print("=" * 60)
    
    for i, test_prompt in enumerate(test_cases, 1):
        print(f"\n[TEST {i}] {test_prompt}")
        print("-" * 40)
        
        # Classify the query
        categories = codex_core.router.classify_query(test_prompt)
        is_symbolic = codex_core.router.should_route_to_symbolic(test_prompt)
        
        print(f"Categories: {categories}")
        print(f"Symbolic Routing: {is_symbolic}")
        
        # Run through codex core
        response = run_llama(test_prompt)
        print(f"Response: {response}")
        
        print("-" * 40)
    
    # Show processing stats
    print("\n" + "=" * 60)
    print("PROCESSING STATISTICS")
    print("=" * 60)
    stats = codex_core.get_processing_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
