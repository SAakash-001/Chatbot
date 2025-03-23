import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils import (
        extract_doi_and_title,
        match_query_to_response,
        has_frustration_indicators
    )
except ImportError as e:
    print(f"Error importing from utils: {e}")
    raise

class TestDOIExtraction(unittest.TestCase):
    """Test the DOI and title extraction functions."""
    
    def test_direct_format(self):
        """Test extraction from direct format: 'DOI', 'Title'."""
        test_cases = [
            # Format: input_string, expected_doi, expected_title
            ("'10.1016/j.patcog.2023.101234', 'Computer Vision Advances'", 
             "10.1016/j.patcog.2023.101234", "Computer Vision Advances"),
            
            ("10.1016/j.patcog.2023.101234, Computer Vision Advances", 
             "10.1016/j.patcog.2023.101234", "Computer Vision Advances"),
             
            ("\"10.1109/tnn.2022.123456\", \"Neural Network Architecture\"", 
             "10.1109/tnn.2022.123456", "Neural Network Architecture"),
        ]
        
        for input_str, expected_doi, expected_title in test_cases:
            doi, title = extract_doi_and_title(input_str)
            self.assertEqual(doi, expected_doi)
            self.assertEqual(title, expected_title)
    
    def test_natural_language_format(self):
        """Test extraction from natural language text."""
        test_cases = [
            # Format: input_string, expected_doi, expected_title
            ("My article titled Computer Vision Advances with DOI 10.1016/j.patcog.2023.101234", 
             "10.1016/j.patcog.2023.101234", "Computer Vision Advances"),
            
            ("I'm looking for the paper 'Neural Network Architecture' with DOI 10.1109/tnn.2022.123456", 
             "10.1109/tnn.2022.123456", "Neural Network Architecture"),
             
            ("The publication about Machine Learning Applications with DOI 10.1002/int.22986", 
             "10.1002/int.22986", "Machine Learning Applications"),
        ]
        
        for input_str, expected_doi, expected_title in test_cases:
            doi, title = extract_doi_and_title(input_str)
            self.assertEqual(doi, expected_doi)
            self.assertEqual(title, expected_title)
    
    def test_no_doi(self):
        """Test behavior when no DOI is present."""
        test_cases = [
            "I need help with my invoice",
            "What payment methods do you accept?",
            "How do I change my email address?"
        ]
        
        for input_str in test_cases:
            doi, title = extract_doi_and_title(input_str)
            self.assertIsNone(doi)
            self.assertIsNone(title)

class TestQueryMatching(unittest.TestCase):
    """Test the query matching function."""
    
    def setUp(self):
        """Set up a sample response mapping for testing."""
        self.sample_responses = {
            "General Queries": {
                "Available payment options": ["Sample response"],
                "Recommended browsers": ["Sample response"],
                "Login issues": ["Sample response"]
            },
            "License & Access Issues": {
                "License Link Not Received": ["Sample response"],
                "Email Update Request": ["Sample response"],
                "Password Reset Issues": ["Sample response"]
            }
        }
    
    def test_payment_methods_queries(self):
        """Test matching for payment method questions."""
        queries = [
            "What payment methods do you accept?",
            "How can I pay?",
            "What are the payment options?",
            "Which payment methods are available?",
            "Ways to pay"
        ]
        
        for query in queries:
            category, sub_category = match_query_to_response(query, self.sample_responses)
            self.assertEqual(category, "General Queries")
            self.assertEqual(sub_category, "Available payment options")
    
    def test_browser_queries(self):
        """Test matching for browser compatibility questions."""
        queries = [
            "Which browsers are recommended?",
            "What browser should I use?",
            "Recommended browsers for SciPris"
        ]
        
        for query in queries:
            category, sub_category = match_query_to_response(query, self.sample_responses)
            self.assertEqual(category, "General Queries")
            self.assertEqual(sub_category, "Recommended browsers")
    
    def test_unmatched_queries(self):
        """Test behavior with queries that don't match any pattern."""
        queries = [
            "Random text",
            "Hello world",
            "42"
        ]
        
        for query in queries:
            category, sub_category = match_query_to_response(query, self.sample_responses)
            self.assertIsNone(category)
            self.assertIsNone(sub_category)

class TestFrustrationDetection(unittest.TestCase):
    """Test the frustration detection function."""
    
    def test_frustration_detection(self):
        """Test detection of user frustration."""
        messages = [
            "Why isn't this WORKING!!",
            "I already told you my DOI",
            "This is stupid???",
            "HELP ME NOW",
            "I've tried this again and again"
        ]
        
        for message in messages:
            self.assertTrue(has_frustration_indicators(message))
    
    def test_non_frustration(self):
        """Test non-detection of frustration in normal messages."""
        messages = [
            "How can I pay for my invoice?",
            "I'd like to know about payment methods",
            "Can you help me find my article?",
            "What browser should I use?"
        ]
        
        for message in messages:
            self.assertFalse(has_frustration_indicators(message))

if __name__ == "__main__":
    unittest.main() 