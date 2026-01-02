"""
Comprehensive test suite for simulation.py
Tests debate simulation functions and result comparison.
"""

import unittest
from unittest.mock import patch, MagicMock
from simulation import (
    run_standard_debate,
    run_mediated_debate,
    extract_answer_from_response,
    compare_results
)


class TestStandardDebate(unittest.TestCase):
    """Test run_standard_debate function."""
    
    def test_standard_debate_basic(self):
        """Test basic standard debate execution."""
        question = "What is 2+2?"
        result = run_standard_debate(question, rounds=2, mock_mode=True)
        
        self.assertEqual(result["question"], question)
        self.assertEqual(result["method"], "standard")
        self.assertEqual(result["rounds"], 2)
        self.assertIn("log", result)
        self.assertIn("final_agent_a", result)
        self.assertIn("final_agent_b", result)
    
    def test_standard_debate_rounds(self):
        """Test standard debate creates correct number of rounds."""
        question = "What is 2+2?"
        result = run_standard_debate(question, rounds=3, mock_mode=True)
        
        # Should have round 0 (initial) + 3 rounds = 4 total entries
        self.assertEqual(len(result["log"]), 4)
        self.assertEqual(result["log"][0]["round"], 0)
        self.assertEqual(result["log"][0]["type"], "initial")
        self.assertEqual(result["log"][1]["round"], 1)
        self.assertEqual(result["log"][1]["type"], "critique")
    
    def test_standard_debate_initial_round(self):
        """Test initial round structure."""
        question = "What is 2+2?"
        result = run_standard_debate(question, rounds=1, mock_mode=True)
        
        initial = result["log"][0]
        self.assertIn("agent_a", initial)
        self.assertIn("agent_b", initial)
        self.assertIsNotNone(initial["agent_a"])
        self.assertIsNotNone(initial["agent_b"])
    
    def test_standard_debate_critique_rounds(self):
        """Test critique rounds structure."""
        question = "What is 2+2?"
        result = run_standard_debate(question, rounds=2, mock_mode=True)
        
        # Check first critique round
        critique = result["log"][1]
        self.assertEqual(critique["type"], "critique")
        self.assertIn("agent_a", critique)
        self.assertIn("agent_b", critique)
    
    def test_standard_debate_history(self):
        """Test agent history is preserved."""
        question = "What is 2+2?"
        result = run_standard_debate(question, rounds=1, mock_mode=True)
        
        self.assertIn("agent_a_history", result)
        self.assertIn("agent_b_history", result)
        self.assertGreater(len(result["agent_a_history"]), 0)
        self.assertGreater(len(result["agent_b_history"]), 0)


class TestMediatedDebate(unittest.TestCase):
    """Test run_mediated_debate function."""
    
    def test_mediated_debate_basic(self):
        """Test basic mediated debate execution."""
        question = "What is 2+2?"
        result = run_mediated_debate(question, rounds=2, mock_mode=True)
        
        self.assertEqual(result["question"], question)
        self.assertEqual(result["method"], "mediated")
        self.assertEqual(result["rounds"], 2)
        self.assertIn("log", result)
        self.assertIn("judge_history", result)
    
    def test_mediated_debate_rounds(self):
        """Test mediated debate creates correct number of rounds."""
        question = "What is 2+2?"
        result = run_mediated_debate(question, rounds=3, mock_mode=True)
        
        # Should have round 0 (initial) + 3 rounds = 4 total entries
        self.assertEqual(len(result["log"]), 4)
        self.assertEqual(result["log"][0]["round"], 0)
        self.assertEqual(result["log"][0]["type"], "initial")
    
    def test_mediated_debate_initial_round(self):
        """Test initial round has no judge feedback."""
        question = "What is 2+2?"
        result = run_mediated_debate(question, rounds=1, mock_mode=True)
        
        initial = result["log"][0]
        self.assertIsNone(initial["judge_feedback"])
        self.assertIn("agent_a", initial)
        self.assertIn("agent_b", initial)
    
    def test_mediated_debate_revision_rounds(self):
        """Test revision rounds have judge feedback."""
        question = "What is 2+2?"
        result = run_mediated_debate(question, rounds=2, mock_mode=True)
        
        # Check first revision round
        revision = result["log"][1]
        self.assertEqual(revision["type"], "revision")
        self.assertIsNotNone(revision["judge_feedback"])
        self.assertIn("agent_a", revision)
        self.assertIn("agent_b", revision)
    
    def test_mediated_debate_judge_history(self):
        """Test judge history is preserved."""
        question = "What is 2+2?"
        result = run_mediated_debate(question, rounds=2, mock_mode=True)
        
        self.assertIn("judge_history", result)
        self.assertGreater(len(result["judge_history"]), 0)


class TestExtractAnswer(unittest.TestCase):
    """Test extract_answer_from_response function."""
    
    def test_extract_answer_explicit(self):
        """Test extracting answer from explicit patterns."""
        response = "The answer is 42"
        result = extract_answer_from_response(response)
        self.assertEqual(result, "42")
    
    def test_extract_answer_with_colon(self):
        """Test extracting answer with colon."""
        response = "Answer: 42"
        result = extract_answer_from_response(response)
        self.assertEqual(result, "42")
    
    def test_extract_answer_final_number(self):
        """Test extracting last number as fallback."""
        response = "I calculated step 1: 10, step 2: 20, final: 42"
        result = extract_answer_from_response(response)
        self.assertEqual(result, "42")
    
    def test_extract_answer_decimal(self):
        """Test extracting decimal answer."""
        response = "The result is 42.5"
        result = extract_answer_from_response(response)
        self.assertEqual(result, "42.5")
    
    def test_extract_answer_no_number(self):
        """Test handling response with no number."""
        response = "I'm not sure about the answer"
        result = extract_answer_from_response(response)
        self.assertEqual(result, "Unable to extract")
    
    def test_extract_answer_multiple_numbers(self):
        """Test extracting answer when multiple numbers present."""
        response = "First I found 10, then 20, and the final answer is 30"
        result = extract_answer_from_response(response)
        # Should get the last number
        self.assertIn(result, ["30", "20"])  # Last number or pattern match
    
    def test_extract_answer_empty(self):
        """Test handling empty response."""
        response = ""
        result = extract_answer_from_response(response)
        self.assertEqual(result, "Unable to extract")


class TestCompareResults(unittest.TestCase):
    """Test compare_results function."""
    
    def test_compare_results_consensus_both(self):
        """Test comparison when both reach consensus."""
        standard_result = {
            "final_agent_a": "The answer is 42",
            "final_agent_b": "I agree, it's 42"
        }
        mediated_result = {
            "final_agent_a": "The answer is 42",
            "final_agent_b": "Yes, 42 is correct"
        }
        
        comparison = compare_results(standard_result, mediated_result)
        
        self.assertIn("standard", comparison)
        self.assertIn("mediated", comparison)
        # Both should extract "42" as answer
        self.assertIsNotNone(comparison["standard"]["agent_a_answer"])
        self.assertIsNotNone(comparison["mediated"]["agent_a_answer"])
    
    def test_compare_results_no_consensus(self):
        """Test comparison when neither reaches consensus."""
        standard_result = {
            "final_agent_a": "The answer is 42",
            "final_agent_b": "I think it's 43"
        }
        mediated_result = {
            "final_agent_a": "The answer is 42",
            "final_agent_b": "Actually, it's 44"
        }
        
        comparison = compare_results(standard_result, mediated_result)
        
        self.assertFalse(comparison["standard"]["consensus"])
        self.assertFalse(comparison["mediated"]["consensus"])
    
    def test_compare_results_different_consensus(self):
        """Test comparison when one reaches consensus and other doesn't."""
        standard_result = {
            "final_agent_a": "The answer is 42",
            "final_agent_b": "I think it's 43"
        }
        mediated_result = {
            "final_agent_a": "The answer is 42",
            "final_agent_b": "Yes, 42 is correct"
        }
        
        comparison = compare_results(standard_result, mediated_result)
        
        self.assertFalse(comparison["standard"]["consensus"])
        self.assertTrue(comparison["mediated"]["consensus"])
        self.assertIsNotNone(comparison["mediated"]["consensus_answer"])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_zero_rounds(self):
        """Test debate with zero rounds."""
        question = "What is 2+2?"
        result = run_standard_debate(question, rounds=0, mock_mode=True)
        
        # Should only have initial round
        self.assertEqual(len(result["log"]), 1)
        self.assertEqual(result["rounds"], 0)
    
    def test_empty_question(self):
        """Test debate with empty question."""
        question = ""
        result = run_standard_debate(question, rounds=1, mock_mode=True)
        
        # Should still execute without error
        self.assertIsNotNone(result)
        self.assertIn("log", result)
    
    def test_very_long_question(self):
        """Test debate with very long question."""
        question = "What is " + "2+2? " * 100
        result = run_standard_debate(question, rounds=1, mock_mode=True)
        
        # Should handle without error
        self.assertIsNotNone(result)
        self.assertEqual(result["question"], question)


if __name__ == '__main__':
    unittest.main()

