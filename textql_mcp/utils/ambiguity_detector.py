"""
Ambiguity detector implementations for the TextQL MCP Server.

This module provides various implementations of ambiguity detectors that
can be used with the TextQL MCP Server.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Callable, Set

logger = logging.getLogger("textql_mcp.ambiguity_detector")


class SimpleAmbiguityDetector:
    """Ambiguity detector that uses simple rules to detect ambiguous queries."""
    
    def __init__(self, ambiguous_keywords: Optional[List[str]] = None):
        """
        Initialize a SimpleAmbiguityDetector.
        
        Args:
            ambiguous_keywords: List of keywords that indicate ambiguity
        """
        self.ambiguous_keywords = set(ambiguous_keywords or [
            "what",
            "which",
            "how many",
            "how much",
            "any",
            "all",
            "can you",
            "could you",
            "would you",
            "should you",
        ])
        logger.info(f"Initialized SimpleAmbiguityDetector with {len(self.ambiguous_keywords)} keywords")
    
    def is_ambiguous(self, query: str) -> bool:
        """
        Check if a query is ambiguous.
        
        Args:
            query: The query to check
            
        Returns:
            True if the query is ambiguous, False otherwise
        """
        # Convert to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # Check for ambiguous keywords
        for keyword in self.ambiguous_keywords:
            if keyword in query_lower:
                logger.debug(f"Query contains ambiguous keyword: {keyword}")
                return True
        
        # Check for very short queries (potentially ambiguous)
        words = query_lower.split()
        if len(words) < 3:
            logger.debug(f"Query is too short: {len(words)} words")
            return True
        
        return False


class RegexAmbiguityDetector:
    """Ambiguity detector that uses regular expressions to detect ambiguous queries."""
    
    def __init__(self, ambiguous_patterns: Optional[List[str]] = None):
        """
        Initialize a RegexAmbiguityDetector.
        
        Args:
            ambiguous_patterns: List of regex patterns that indicate ambiguity
        """
        self.ambiguous_patterns = ambiguous_patterns or [
            r"^(what|which|how|who|when|where)",
            r"\b(any|all|some|few|many|much)\b",
            r"\b(can|could|would|should)\b.*\?",
            r"^[^.!?]{1,20}$",  # Very short queries
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.ambiguous_patterns]
        logger.info(f"Initialized RegexAmbiguityDetector with {len(self.ambiguous_patterns)} patterns")
    
    def is_ambiguous(self, query: str) -> bool:
        """
        Check if a query is ambiguous.
        
        Args:
            query: The query to check
            
        Returns:
            True if the query is ambiguous, False otherwise
        """
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(query):
                logger.debug(f"Query matches ambiguous pattern: {self.ambiguous_patterns[i]}")
                return True
        
        return False


class CallbackAmbiguityDetector:
    """Ambiguity detector that uses a callback function to detect ambiguous queries."""
    
    def __init__(self, callback: Callable[[str], bool]):
        """
        Initialize a CallbackAmbiguityDetector.
        
        Args:
            callback: Function that checks if a query is ambiguous
        """
        self.callback = callback
        logger.info("Initialized CallbackAmbiguityDetector")
    
    def is_ambiguous(self, query: str) -> bool:
        """
        Check if a query is ambiguous.
        
        Args:
            query: The query to check
            
        Returns:
            True if the query is ambiguous, False otherwise
        """
        try:
            result = self.callback(query)
            return result
        except Exception as e:
            logger.error(f"Error checking ambiguity: {e}")
            return True  # Assume ambiguous if error
