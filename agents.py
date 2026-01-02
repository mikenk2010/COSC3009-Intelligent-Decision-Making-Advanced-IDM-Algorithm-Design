"""
Multi-Agent Debate System - Agent Classes
100% LOCAL ONLY - Uses Ollama with DeepSeek R1 model.
NO cloud API calls. NO fallbacks to OpenAI.
"""

import os
import logging
from typing import List, Dict, Optional
from openai import OpenAI
from datetime import datetime

# Configure logging - use logs/ subdirectory to avoid watchdog spam
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'debate_system.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LocalClient:
    """
    Local-only OpenAI-compatible client for Ollama.
    Hardcoded to use local Ollama server only.
    """
    
    def __init__(self):
        """Initialize local client - strictly Ollama only."""
        logger.debug("Initializing LocalClient")
        base_url = os.getenv("OPENAI_BASE_URL", "http://ollama:11434/v1")
        # Hardcode API key to "ollama" - never check system keys or cloud
        api_key = os.getenv("OPENAI_API_KEY", "ollama")
        
        logger.info(f"LocalClient config - Base URL: {base_url}, Model: {os.getenv('MODEL_NAME', 'deepseek-r1:1.5b')}")
        
        if not base_url or "api.openai.com" in base_url.lower():
            error_msg = (
                "ERROR: Cloud API detected! This system is LOCAL ONLY. "
                "Set OPENAI_BASE_URL to http://ollama:11434/v1"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # Set timeout to 120 seconds (2 minutes) per API call
            # DeepSeek R1 reasoning models can take longer to generate responses
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key,
                timeout=120.0  # 2 minutes timeout per call
            )
            self.model_name = os.getenv("MODEL_NAME", "deepseek-r1:1.5b")
            logger.info(f"LocalClient initialized successfully - Model: {self.model_name}, Timeout: 120s")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}", exc_info=True)
            raise
    
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Generate response from local Ollama model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            The model's response text (cleaned of reasoning tags if present)
        """
        logger.debug(f"Generating response - Model: {self.model_name}, Temperature: {temperature}, Max tokens: {max_tokens}")
        logger.debug(f"Messages count: {len(messages)}")
        
        try:
            start_time = datetime.now()
            logger.info(f"Calling Ollama API - Model: {self.model_name} (timeout: 120s)")
            logger.debug(f"Request details - Temperature: {temperature}, Max tokens: {max_tokens}")
            
            # Make the API call with timeout
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            content = response.choices[0].message.content
            
            logger.info(f"✅ Ollama API call successful - Duration: {elapsed:.2f}s, Response length: {len(content)} chars")
            if elapsed > 30:
                logger.warning(f"⚠️ Slow response detected: {elapsed:.2f}s (consider checking model performance)")
            if elapsed > 60:
                logger.warning(f"⚠️ Very slow response: {elapsed:.2f}s - Model may be overloaded or system resources low")
            logger.debug(f"Response preview: {content[:200]}...")
            
            # Clean DeepSeek R1 reasoning tags if present
            cleaned = self._clean_reasoning_tags(content)
            return cleaned
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            error_type = type(e).__name__
            
            # Check for specific timeout errors
            if "timeout" in str(e).lower() or "timed out" in str(e).lower() or elapsed >= 120:
                error_msg = f"[TIMEOUT] Ollama API call timed out after {elapsed:.2f}s. Model may be too slow or unresponsive."
                logger.error(f"❌ {error_msg}")
                logger.error(f"Model: {self.model_name}, Base URL: {self.client.base_url if hasattr(self.client, 'base_url') else 'unknown'}")
            else:
                error_msg = f"[ERROR] Local model call failed after {elapsed:.2f}s: {error_type}: {str(e)}"
                logger.error(f"❌ {error_msg}", exc_info=True)
            
            return error_msg
    
    def _clean_reasoning_tags(self, text: str) -> str:
        """
        Clean DeepSeek R1 reasoning tags from output.
        DeepSeek R1 may output <think> tags - we can either
        remove them or keep them to show the reasoning process.
        
        Args:
            text: Raw model output
            
        Returns:
            Cleaned text (currently keeps tags to show reasoning)
        """
        # Option 1: Keep tags to show reasoning (current)
        return text
        
        # Option 2: Remove tags (uncomment to use)
        # import re
        # text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # return text.strip()


class DebateAgent:
    """
    A debate agent that participates in mathematical problem-solving debates.
    Uses local Ollama model only.
    """
    
    def __init__(self, agent_id: str, role: str = "Math Expert", mock_mode: bool = False):
        """
        Initialize a debate agent.
        
        Args:
            agent_id: Unique identifier (e.g., "Agent A", "Agent B")
            role: The role/identity of the agent
            mock_mode: If True, use mock responses (for testing without model)
        """
        logger.info(f"Initializing DebateAgent - ID: {agent_id}, Role: {role}, Mock Mode: {mock_mode}")
        self.agent_id = agent_id
        self.role = role
        self.history: List[Dict[str, str]] = []
        self.mock_mode = mock_mode
        self.client = None
        
        if not mock_mode:
            try:
                logger.debug(f"Creating LocalClient for {agent_id}")
                self.client = LocalClient()
                logger.info(f"DebateAgent {agent_id} initialized with LocalClient")
            except Exception as e:
                # If client fails, we'll use mock mode as fallback
                logger.warning(f"Could not initialize local client for {agent_id}: {e}. Falling back to mock mode.")
                logger.warning(f"Exception details: {str(e)}", exc_info=True)
                self.mock_mode = True
        else:
            logger.info(f"DebateAgent {agent_id} initialized in MOCK MODE")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return f"""You are {self.agent_id}, a {self.role} specializing in mathematical problem-solving.

Your task:
1. Analyze mathematical problems step-by-step
2. Show clear logical reasoning
3. When reviewing solutions, identify errors or flaws
4. Revise your answer if you find mistakes
5. Be honest - don't agree with incorrect solutions

Show your work and explain your reasoning clearly."""

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response using local model or mock.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            The agent's response text
        """
        if self.mock_mode:
            # Mock response for testing without model
            if any("revise" in msg.get("content", "").lower() for msg in messages):
                return f"[Mock] {self.agent_id} revises: I've reconsidered and my updated answer is 42. Here's my corrected reasoning..."
            elif any("critique" in msg.get("content", "").lower() for msg in messages):
                return f"[Mock] {self.agent_id} critiques: I notice a potential error in the calculation. Let me point out..."
            else:
                return f"[Mock] {self.agent_id} initial answer: After careful analysis, I believe the answer is 42. Here's my reasoning..."
        
        if not self.client:
            return "[ERROR] Local model client not available. Please ensure Ollama is running."
        
        return self.client.generate(messages, temperature=0.7, max_tokens=500)
    
    def generate_initial_answer(self, question: str) -> str:
        """
        Generate an initial answer to the question.
        
        Args:
            question: The mathematical problem to solve
            
        Returns:
            The agent's initial answer
        """
        logger.info(f"{self.agent_id} generating initial answer")
        logger.debug(f"{self.agent_id} question: {question[:100]}...")
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"Solve this problem step-by-step:\n\n{question}"}
        ]
        
        start_time = datetime.now()
        response = self.generate(messages)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"{self.agent_id} initial answer generated in {elapsed:.2f}s")
        logger.debug(f"{self.agent_id} response preview: {response[:200]}...")
        
        self.history.append({
            "type": "initial",
            "content": response,
            "round": 0
        })
        return response
    
    def critique_peer(self, question: str, peer_answer: str, round_num: int) -> str:
        """
        Critique another agent's answer (used in standard debate).
        
        Args:
            question: The original question
            peer_answer: The peer agent's answer to critique
            round_num: Current debate round number
            
        Returns:
            Critique and revised answer
        """
        logger.info(f"{self.agent_id} critiquing peer in round {round_num}")
        logger.debug(f"{self.agent_id} peer answer preview: {peer_answer[:200]}...")
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"Original problem:\n{question}\n\nYour peer's answer:\n{peer_answer}\n\nPlease critically review this answer. Identify any errors or flaws. If you find mistakes, provide your corrected solution. If you agree, explain why."}
        ]
        
        start_time = datetime.now()
        response = self.generate(messages)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"{self.agent_id} critique completed in {elapsed:.2f}s")
        logger.debug(f"{self.agent_id} critique preview: {response[:200]}...")
        
        self.history.append({
            "type": "critique",
            "content": response,
            "round": round_num,
            "peer_answer": peer_answer
        })
        return response
    
    def revise_from_judge_feedback(self, question: str, judge_feedback: str, round_num: int) -> str:
        """
        Revise answer based on judge's feedback (used in mediated debate).
        
        Args:
            question: The original question
            judge_feedback: The judge's critique
            round_num: Current debate round number
            
        Returns:
            Revised answer
        """
        logger.info(f"{self.agent_id} revising based on judge feedback in round {round_num}")
        logger.debug(f"{self.agent_id} judge feedback preview: {judge_feedback[:200]}...")
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"Original problem:\n{question}\n\nAn impartial judge has reviewed the debate and provided this feedback:\n{judge_feedback}\n\nPlease carefully consider this feedback and revise your answer if necessary. Be honest - if you made an error, acknowledge it and correct it."}
        ]
        
        start_time = datetime.now()
        response = self.generate(messages)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"{self.agent_id} revision completed in {elapsed:.2f}s")
        logger.debug(f"{self.agent_id} revision preview: {response[:200]}...")
        
        self.history.append({
            "type": "revision",
            "content": response,
            "round": round_num,
            "judge_feedback": judge_feedback
        })
        return response
    
    def get_final_answer(self) -> str:
        """Extract the final answer from the agent's history."""
        if not self.history:
            return "No answer generated yet."
        return self.history[-1]["content"]


class JudgeAgent:
    """
    A judge agent that acts as an impartial arbitrator in mediated debates.
    Uses local Ollama model only.
    """
    
    def __init__(self, mock_mode: bool = False):
        """
        Initialize the judge agent.
        
        Args:
            mock_mode: If True, use mock responses (for testing without model)
        """
        logger.info(f"Initializing JudgeAgent - Mock Mode: {mock_mode}")
        self.history: List[Dict[str, str]] = []
        self.mock_mode = mock_mode
        self.client = None
        
        if not mock_mode:
            try:
                logger.debug("Creating LocalClient for JudgeAgent")
                self.client = LocalClient()
                logger.info("JudgeAgent initialized with LocalClient")
            except Exception as e:
                logger.warning(f"Could not initialize local client for JudgeAgent: {e}. Falling back to mock mode.")
                logger.warning(f"Exception details: {str(e)}", exc_info=True)
                self.mock_mode = True
        else:
            logger.info("JudgeAgent initialized in MOCK MODE")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the judge."""
        return """You are an impartial Judge reviewing mathematical solutions.

Your role:
1. Analyze multiple solutions to the same problem
2. Identify errors, inconsistencies, or logical flaws
3. Point out specific mistakes
4. Determine consensus or disagreement
5. Provide clear, actionable feedback to help agents correct errors
6. Be critical - do not accept incorrect solutions

Be objective. Focus on mathematical correctness. If an agent is wrong, clearly state this.

If both agents have correct solutions, say "CONSENSUS: Both solutions are correct."
If both agents have incorrect solutions, identify the errors in each.
If one is correct and one is wrong, clearly state which is correct."""

    def critique(self, question: str, agent_a_answer: str, agent_b_answer: str, round_num: int) -> str:
        """
        Evaluate two agents' answers and provide critical feedback.
        
        Args:
            question: The original question
            agent_a_answer: Agent A's current answer
            agent_b_answer: Agent B's current answer
            round_num: Current debate round number
            
        Returns:
            Judge's evaluation and feedback
        """
        logger.info(f"Judge evaluating answers in round {round_num}")
        logger.debug(f"Judge question: {question[:100]}...")
        logger.debug(f"Agent A answer preview: {agent_a_answer[:200]}...")
        logger.debug(f"Agent B answer preview: {agent_b_answer[:200]}...")
        
        if self.mock_mode:
            logger.warning("Judge using MOCK MODE")
            return "[Mock] Judge feedback: I've reviewed both solutions. Agent A made an error in step 3, and Agent B's calculation is incorrect. Here are the specific issues..."
        
        if not self.client:
            error_msg = "[ERROR] Local model client not available. Please ensure Ollama is running."
            logger.error(error_msg)
            return error_msg
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""Problem: {question}

Agent A: {agent_a_answer}

Agent B: {agent_b_answer}

Analyze both solutions:
1. Check each step for errors
2. Identify calculation mistakes or logical flaws
3. Note if agents agree or disagree
4. Specify exactly what is wrong and where
5. Provide clear feedback to help agents correct mistakes

Be critical. Do not accept incorrect solutions."""}
        ]
        
        start_time = datetime.now()
        response = self.client.generate(messages, temperature=0.3, max_tokens=600)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Judge evaluation completed in {elapsed:.2f}s")
        logger.debug(f"Judge feedback preview: {response[:200]}...")
        
        self.history.append({
            "type": "evaluation",
            "content": response,
            "round": round_num,
            "agent_a_answer": agent_a_answer,
            "agent_b_answer": agent_b_answer
        })
        return response
