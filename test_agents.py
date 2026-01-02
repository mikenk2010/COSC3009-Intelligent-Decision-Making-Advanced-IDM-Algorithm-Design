"""
Comprehensive test suite for agents.py
Tests DebateAgent and JudgeAgent classes with various scenarios.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
from agents import DebateAgent, JudgeAgent, get_client, get_model_name


class TestClientFunctions(unittest.TestCase):
    """Test get_client() and get_model_name() functions."""
    
    def setUp(self):
        """Clear environment variables before each test."""
        if 'OPENAI_BASE_URL' in os.environ:
            del os.environ['OPENAI_BASE_URL']
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
    
    def test_get_model_name_with_ollama(self):
        """Test get_model_name returns Ollama model when base_url is set."""
        os.environ['OPENAI_BASE_URL'] = 'http://ollama:11434/v1'
        model = get_model_name()
        self.assertEqual(model, "deepseek-r1:1.5b")
    
    def test_get_model_name_without_ollama(self):
        """Test get_model_name returns OpenAI model when base_url is not set."""
        if 'OPENAI_BASE_URL' in os.environ:
            del os.environ['OPENAI_BASE_URL']
        model = get_model_name()
        self.assertEqual(model, "gpt-4")
    
    @patch('agents.OpenAI')
    def test_get_client_with_ollama(self, mock_openai):
        """Test get_client creates Ollama client when base_url is set."""
        os.environ['OPENAI_BASE_URL'] = 'http://ollama:11434/v1'
        os.environ['OPENAI_API_KEY'] = 'ollama'
        
        client = get_client()
        mock_openai.assert_called_once_with(
            base_url='http://ollama:11434/v1',
            api_key='ollama'
        )
    
    @patch('agents.OpenAI')
    def test_get_client_with_openai(self, mock_openai):
        """Test get_client creates OpenAI client when base_url is not set."""
        if 'OPENAI_BASE_URL' in os.environ:
            del os.environ['OPENAI_BASE_URL']
        os.environ['OPENAI_API_KEY'] = 'sk-test123'
        
        client = get_client()
        mock_openai.assert_called_once_with(api_key='sk-test123')
    
    def test_get_client_no_api_key(self):
        """Test get_client returns None when no valid API key."""
        if 'OPENAI_BASE_URL' in os.environ:
            del os.environ['OPENAI_BASE_URL']
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        client = get_client()
        self.assertIsNone(client)


class TestDebateAgent(unittest.TestCase):
    """Test DebateAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if 'OPENAI_BASE_URL' in os.environ:
            del os.environ['OPENAI_BASE_URL']
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = DebateAgent("Agent A", "Math Expert", mock_mode=True)
        self.assertEqual(agent.agent_id, "Agent A")
        self.assertEqual(agent.role, "Math Expert")
        self.assertTrue(agent.mock_mode)
        self.assertEqual(len(agent.history), 0)
    
    def test_get_system_prompt(self):
        """Test system prompt generation."""
        agent = DebateAgent("Agent A", "Math Expert", mock_mode=True)
        prompt = agent.get_system_prompt()
        self.assertIn("Agent A", prompt)
        self.assertIn("Math Expert", prompt)
        self.assertIn("mathematical", prompt.lower())
    
    def test_call_llm_mock_mode_initial(self):
        """Test call_llm in mock mode for initial answer."""
        agent = DebateAgent("Agent A", mock_mode=True)
        messages = [{"role": "user", "content": "Solve: 2+2"}]
        response = agent.call_llm(messages)
        self.assertIn("Mock", response)
        self.assertIn("Agent A", response)
    
    def test_call_llm_mock_mode_critique(self):
        """Test call_llm in mock mode for critique."""
        agent = DebateAgent("Agent A", mock_mode=True)
        messages = [{"role": "user", "content": "Critique this answer"}]
        response = agent.call_llm(messages)
        self.assertIn("critiques", response.lower())
    
    def test_call_llm_mock_mode_revise(self):
        """Test call_llm in mock mode for revision."""
        agent = DebateAgent("Agent A", mock_mode=True)
        messages = [{"role": "user", "content": "Revise your answer"}]
        response = agent.call_llm(messages)
        self.assertIn("revises", response.lower())
    
    def test_call_llm_no_client(self):
        """Test call_llm returns error when no client available."""
        agent = DebateAgent("Agent A", mock_mode=False)
        agent.client = None
        messages = [{"role": "user", "content": "Test"}]
        response = agent.call_llm(messages)
        self.assertIn("ERROR", response)
    
    @patch('agents.OpenAI')
    def test_call_llm_with_client(self, mock_openai_class):
        """Test call_llm makes API call when client is available."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        os.environ['OPENAI_BASE_URL'] = 'http://ollama:11434/v1'
        agent = DebateAgent("Agent A", mock_mode=False)
        agent.client = mock_client
        
        messages = [{"role": "user", "content": "Test"}]
        response = agent.call_llm(messages)
        
        self.assertEqual(response, "Test response")
        mock_client.chat.completions.create.assert_called_once()
    
    def test_generate_initial_answer(self):
        """Test generate_initial_answer creates history entry."""
        agent = DebateAgent("Agent A", mock_mode=True)
        question = "What is 2+2?"
        response = agent.generate_initial_answer(question)
        
        self.assertIsNotNone(response)
        self.assertEqual(len(agent.history), 1)
        self.assertEqual(agent.history[0]["type"], "initial")
        self.assertEqual(agent.history[0]["round"], 0)
    
    def test_critique_peer(self):
        """Test critique_peer creates history entry."""
        agent = DebateAgent("Agent A", mock_mode=True)
        question = "What is 2+2?"
        peer_answer = "The answer is 5"
        
        response = agent.critique_peer(question, peer_answer, round_num=1)
        
        self.assertIsNotNone(response)
        self.assertEqual(len(agent.history), 1)
        self.assertEqual(agent.history[0]["type"], "critique")
        self.assertEqual(agent.history[0]["round"], 1)
        self.assertEqual(agent.history[0]["peer_answer"], peer_answer)
    
    def test_revise_from_judge_feedback(self):
        """Test revise_from_judge_feedback creates history entry."""
        agent = DebateAgent("Agent A", mock_mode=True)
        question = "What is 2+2?"
        judge_feedback = "Your answer is incorrect"
        
        response = agent.revise_from_judge_feedback(question, judge_feedback, round_num=1)
        
        self.assertIsNotNone(response)
        self.assertEqual(len(agent.history), 1)
        self.assertEqual(agent.history[0]["type"], "revision")
        self.assertEqual(agent.history[0]["round"], 1)
        self.assertEqual(agent.history[0]["judge_feedback"], judge_feedback)
    
    def test_get_final_answer_with_history(self):
        """Test get_final_answer returns last history entry."""
        agent = DebateAgent("Agent A", mock_mode=True)
        agent.history = [
            {"content": "First answer"},
            {"content": "Second answer"},
            {"content": "Final answer"}
        ]
        
        result = agent.get_final_answer()
        self.assertEqual(result, "Final answer")
    
    def test_get_final_answer_no_history(self):
        """Test get_final_answer returns default when no history."""
        agent = DebateAgent("Agent A", mock_mode=True)
        result = agent.get_final_answer()
        self.assertEqual(result, "No answer generated yet.")


class TestJudgeAgent(unittest.TestCase):
    """Test JudgeAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if 'OPENAI_BASE_URL' in os.environ:
            del os.environ['OPENAI_BASE_URL']
    
    def test_judge_initialization(self):
        """Test judge initializes correctly."""
        judge = JudgeAgent(mock_mode=True)
        self.assertTrue(judge.mock_mode)
        self.assertEqual(len(judge.history), 0)
    
    def test_get_system_prompt(self):
        """Test judge system prompt."""
        judge = JudgeAgent(mock_mode=True)
        prompt = judge.get_system_prompt()
        self.assertIn("Judge", prompt)
        self.assertIn("impartial", prompt.lower())
        self.assertIn("critical", prompt.lower())
    
    def test_call_llm_mock_mode(self):
        """Test judge call_llm in mock mode."""
        judge = JudgeAgent(mock_mode=True)
        messages = [{"role": "user", "content": "Evaluate these answers"}]
        response = judge.call_llm(messages)
        self.assertIn("Mock", response)
        self.assertIn("Judge", response)
    
    def test_call_llm_no_client(self):
        """Test judge call_llm returns error when no client."""
        judge = JudgeAgent(mock_mode=False)
        judge.client = None
        messages = [{"role": "user", "content": "Test"}]
        response = judge.call_llm(messages)
        self.assertIn("ERROR", response)
    
    def test_evaluate_answers(self):
        """Test evaluate_answers creates history entry."""
        judge = JudgeAgent(mock_mode=True)
        question = "What is 2+2?"
        agent_a_answer = "The answer is 4"
        agent_b_answer = "The answer is 5"
        
        response = judge.evaluate_answers(question, agent_a_answer, agent_b_answer, round_num=1)
        
        self.assertIsNotNone(response)
        self.assertEqual(len(judge.history), 1)
        self.assertEqual(judge.history[0]["type"], "evaluation")
        self.assertEqual(judge.history[0]["round"], 1)
    
    def test_check_consensus_numerical_match(self):
        """Test check_consensus detects numerical agreement."""
        judge = JudgeAgent(mock_mode=True)
        answer_a = "The answer is 42"
        answer_b = "I believe it's 42"
        
        result = judge.check_consensus(answer_a, answer_b)
        self.assertTrue(result)
    
    def test_check_consensus_numerical_mismatch(self):
        """Test check_consensus detects numerical disagreement."""
        judge = JudgeAgent(mock_mode=True)
        answer_a = "The answer is 42"
        answer_b = "I believe it's 43"
        
        result = judge.check_consensus(answer_a, answer_b)
        self.assertFalse(result)
    
    def test_check_consensus_keyword_agreement(self):
        """Test check_consensus detects keyword-based agreement."""
        judge = JudgeAgent(mock_mode=True)
        # Both answers need to contain the same keyword for consensus
        answer_a = "I agree with the solution"
        answer_b = "I also agree with this approach"
        
        result = judge.check_consensus(answer_a, answer_b)
        self.assertTrue(result)
    
    def test_check_consensus_no_agreement(self):
        """Test check_consensus detects no agreement."""
        judge = JudgeAgent(mock_mode=True)
        answer_a = "The answer is unclear"
        answer_b = "I disagree with this approach"
        
        result = judge.check_consensus(answer_a, answer_b)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

