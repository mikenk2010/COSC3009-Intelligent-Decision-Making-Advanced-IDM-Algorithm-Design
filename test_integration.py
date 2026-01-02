"""
Integration tests for the complete debate system.
Tests end-to-end workflows and system integration.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
from agents import DebateAgent, JudgeAgent, get_client
from simulation import run_standard_debate, run_mediated_debate, compare_results


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflows."""
    
    def setUp(self):
        """Set up test environment."""
        if 'OPENAI_BASE_URL' in os.environ:
            del os.environ['OPENAI_BASE_URL']
    
    def test_complete_standard_debate_workflow(self):
        """Test complete standard debate workflow."""
        question = "Janet's ducks lay eggs. She gets 3 times as many eggs from her ducks as she gets from her chickens. If she gets 3 eggs from her chickens, how many eggs does she get from her ducks?"
        
        result = run_standard_debate(question, rounds=3, mock_mode=True)
        
        # Verify structure
        self.assertEqual(result["question"], question)
        self.assertEqual(result["method"], "standard")
        self.assertEqual(len(result["log"]), 4)  # Round 0 + 3 rounds
        
        # Verify agents have history
        self.assertGreater(len(result["agent_a_history"]), 0)
        self.assertGreater(len(result["agent_b_history"]), 0)
        
        # Verify final answers exist
        self.assertIsNotNone(result["final_agent_a"])
        self.assertIsNotNone(result["final_agent_b"])
    
    def test_complete_mediated_debate_workflow(self):
        """Test complete mediated debate workflow."""
        question = "A coffee shop sells coffee for $2.50 per cup and tea for $1.75 per cup. If a customer buys 4 cups of coffee and 3 cups of tea, how much does the customer pay in total?"
        
        result = run_mediated_debate(question, rounds=3, mock_mode=True)
        
        # Verify structure
        self.assertEqual(result["question"], question)
        self.assertEqual(result["method"], "mediated")
        self.assertEqual(len(result["log"]), 4)  # Round 0 + 3 rounds
        
        # Verify judge history
        self.assertGreater(len(result["judge_history"]), 0)
        
        # Verify initial round has no judge feedback
        self.assertIsNone(result["log"][0]["judge_feedback"])
        
        # Verify revision rounds have judge feedback
        for i in range(1, len(result["log"])):
            self.assertIsNotNone(result["log"][i]["judge_feedback"])
    
    def test_comparison_workflow(self):
        """Test comparing standard and mediated debates."""
        question = "What is 2+2?"
        
        standard_result = run_standard_debate(question, rounds=2, mock_mode=True)
        mediated_result = run_mediated_debate(question, rounds=2, mock_mode=True)
        
        comparison = compare_results(standard_result, mediated_result)
        
        # Verify comparison structure
        self.assertIn("standard", comparison)
        self.assertIn("mediated", comparison)
        self.assertIn("consensus", comparison["standard"])
        self.assertIn("consensus", comparison["mediated"])


class TestAgentInteraction(unittest.TestCase):
    """Test agent interactions and communication."""
    
    def test_agent_peer_critique_flow(self):
        """Test agent peer critique in standard debate."""
        agent_a = DebateAgent("Agent A", mock_mode=True)
        agent_b = DebateAgent("Agent B", mock_mode=True)
        
        question = "What is 2+2?"
        
        # Initial answers
        answer_a = agent_a.generate_initial_answer(question)
        answer_b = agent_b.generate_initial_answer(question)
        
        # Agent A critiques B
        critique_a = agent_a.critique_peer(question, answer_b, round_num=1)
        
        # Agent B critiques A
        critique_b = agent_b.critique_peer(question, answer_a, round_num=1)
        
        # Verify both agents have history
        self.assertEqual(len(agent_a.history), 2)
        self.assertEqual(len(agent_b.history), 2)
        
        # Verify critique entries
        self.assertEqual(agent_a.history[1]["type"], "critique")
        self.assertEqual(agent_b.history[1]["type"], "critique")
    
    def test_judge_mediation_flow(self):
        """Test judge mediation in mediated debate."""
        agent_a = DebateAgent("Agent A", mock_mode=True)
        agent_b = DebateAgent("Agent B", mock_mode=True)
        judge = JudgeAgent(mock_mode=True)
        
        question = "What is 2+2?"
        
        # Initial answers
        answer_a = agent_a.generate_initial_answer(question)
        answer_b = agent_b.generate_initial_answer(question)
        
        # Judge evaluates
        feedback = judge.evaluate_answers(question, answer_a, answer_b, round_num=1)
        
        # Agents revise
        revision_a = agent_a.revise_from_judge_feedback(question, feedback, round_num=1)
        revision_b = agent_b.revise_from_judge_feedback(question, feedback, round_num=1)
        
        # Verify judge has history
        self.assertEqual(len(judge.history), 1)
        self.assertEqual(judge.history[0]["type"], "evaluation")
        
        # Verify agents have revision history
        self.assertEqual(agent_a.history[1]["type"], "revision")
        self.assertEqual(agent_b.history[1]["type"], "revision")
        self.assertEqual(agent_a.history[1]["judge_feedback"], feedback)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_agent_with_no_client(self):
        """Test agent handles missing client gracefully."""
        agent = DebateAgent("Agent A", mock_mode=False)
        agent.client = None
        
        response = agent.call_llm([{"role": "user", "content": "Test"}])
        self.assertIn("ERROR", response)
    
    def test_judge_with_no_client(self):
        """Test judge handles missing client gracefully."""
        judge = JudgeAgent(mock_mode=False)
        judge.client = None
        
        response = judge.call_llm([{"role": "user", "content": "Test"}])
        self.assertIn("ERROR", response)
    
    @patch('agents.OpenAI')
    def test_api_error_handling(self, mock_openai_class):
        """Test handling of API errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        os.environ['OPENAI_BASE_URL'] = 'http://ollama:11434/v1'
        agent = DebateAgent("Agent A", mock_mode=False)
        agent.client = mock_client
        
        response = agent.call_llm([{"role": "user", "content": "Test"}])
        self.assertIn("ERROR", response)
        self.assertIn("API call failed", response)


class TestModelConfiguration(unittest.TestCase):
    """Test model configuration and client setup."""
    
    def test_ollama_configuration(self):
        """Test Ollama configuration."""
        os.environ['OPENAI_BASE_URL'] = 'http://ollama:11434/v1'
        os.environ['OPENAI_API_KEY'] = 'ollama'
        
        client = get_client()
        self.assertIsNotNone(client)
    
    def test_openai_configuration(self):
        """Test OpenAI configuration."""
        if 'OPENAI_BASE_URL' in os.environ:
            del os.environ['OPENAI_BASE_URL']
        os.environ['OPENAI_API_KEY'] = 'sk-test123'
        
        client = get_client()
        self.assertIsNotNone(client)
    
    def test_mock_mode_independence(self):
        """Test mock mode works independently of client configuration."""
        # Even with no client, mock mode should work
        if 'OPENAI_BASE_URL' in os.environ:
            del os.environ['OPENAI_BASE_URL']
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        agent = DebateAgent("Agent A", mock_mode=True)
        response = agent.generate_initial_answer("What is 2+2?")
        
        self.assertIsNotNone(response)
        self.assertIn("Mock", response)


class TestDataConsistency(unittest.TestCase):
    """Test data consistency across debate rounds."""
    
    def test_history_consistency(self):
        """Test agent history is consistent across rounds."""
        question = "What is 2+2?"
        result = run_standard_debate(question, rounds=3, mock_mode=True)
        
        # Verify each round has correct structure
        for i, entry in enumerate(result["log"]):
            self.assertEqual(entry["round"], i)
            self.assertIn("agent_a", entry)
            self.assertIn("agent_b", entry)
        
        # Verify agent histories match log entries
        self.assertEqual(len(result["agent_a_history"]), len(result["log"]))
        self.assertEqual(len(result["agent_b_history"]), len(result["log"]))
    
    def test_mediated_history_consistency(self):
        """Test mediated debate history consistency."""
        question = "What is 2+2?"
        result = run_mediated_debate(question, rounds=3, mock_mode=True)
        
        # Verify judge history matches revision rounds
        revision_rounds = [e for e in result["log"] if e["round"] > 0]
        self.assertEqual(len(result["judge_history"]), len(revision_rounds))
        
        # Verify each revision round has judge feedback
        for entry in revision_rounds:
            self.assertIsNotNone(entry["judge_feedback"])


if __name__ == '__main__':
    unittest.main()

