"""
Multi-Agent Debate System - Agent Classes
100% LOCAL ONLY - Uses Ollama with Qwen 2.5 model.
Robust fallback to simulation mode on timeout/errors.
"""

import os
import logging
from typing import List, Dict, Optional
from openai import OpenAI
from datetime import datetime
import random

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
    Implements robust timeout handling with automatic fallback to simulation.
    """
    
    def __init__(self):
        """Initialize local client - strictly Ollama only."""
        logger.debug("Initializing LocalClient")
        base_url = os.getenv("OPENAI_BASE_URL", "http://ollama:11434/v1")
        api_key = os.getenv("OPENAI_API_KEY", "ollama")
        
        logger.info(f"LocalClient config - Base URL: {base_url}, Model: {os.getenv('MODEL_NAME', 'qwen2.5:1.5b')}")
        
        if not base_url or "api.openai.com" in base_url.lower():
            error_msg = (
                "ERROR: Cloud API detected! This system is LOCAL ONLY. "
                "Set OPENAI_BASE_URL to http://ollama:11434/v1"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            timeout_seconds = float(os.getenv("OLLAMA_TIMEOUT", "120.0"))
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key,
                timeout=timeout_seconds
            )
            self.model_name = os.getenv("MODEL_NAME", "qwen2.5:1.5b")
            self.timeout = timeout_seconds
            logger.info(f"LocalClient initialized - Model: {self.model_name}, Timeout: {timeout_seconds}s")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}", exc_info=True)
            raise
    
    def _generate_simulation_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a simulated response when API fails.
        Creates contextually appropriate mock responses.
        """
        # Extract context from messages
        user_content = ""
        system_content = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_content = msg.get("content", "")
            elif msg.get("role") == "system":
                system_content = msg.get("content", "")
        
        # Determine response type based on context
        if "judge" in system_content.lower() or "judge" in user_content.lower():
            # Judge response
            return "[SIMULATION] Judge Feedback: I've reviewed both solutions. Agent A's calculation contains an error in step 2. Agent B's approach is correct. Please revise your answer, Agent A."
        elif "critique" in user_content.lower() or "review" in user_content.lower():
            # Critique response
            return "[SIMULATION] After reviewing the peer's answer, I notice a potential issue. However, I maintain my original answer with some refinements."
        elif "revise" in user_content.lower() or "feedback" in user_content.lower():
            # Revision response
            return "[SIMULATION] Thank you for the feedback. I've reconsidered and here's my revised answer with corrections."
        else:
            # Initial answer
            return "[SIMULATION] After careful analysis, I believe the answer is 42. Here's my step-by-step reasoning: First, I identify the key variables..."
    
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 400) -> str:
        """
        Generate response from local Ollama model with timeout guard and fallback.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            The model's response text OR simulation response on timeout/error
        """
        logger.debug(f"Generating response - Model: {self.model_name}, Temperature: {temperature}, Max tokens: {max_tokens}")
        
        try:
            start_time = datetime.now()
            logger.info(f"Calling Ollama API - Model: {self.model_name} (timeout: {self.timeout}s)")
            
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
            if elapsed > 60:
                logger.warning(f"⚠️ Slow response: {elapsed:.2f}s")
            
            return content
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            error_type = type(e).__name__
            
            # Check for timeout or connection errors
            is_timeout = (
                "timeout" in str(e).lower() or 
                "timed out" in str(e).lower() or 
                elapsed >= self.timeout or
                "ConnectionError" in error_type or
                "Connection" in error_type
            )
            
            if is_timeout:
                logger.warning(f"⏱️ Timeout/Connection error after {elapsed:.2f}s - Using simulation fallback")
                logger.warning(f"Error type: {error_type}, Message: {str(e)[:200]}")
                # Return simulation response instead of crashing
                return self._generate_simulation_response(messages)
            else:
                logger.warning(f"⚠️ API error ({error_type}) - Using simulation fallback: {str(e)[:200]}")
                # Return simulation response for any error to prevent crashes
                return self._generate_simulation_response(messages)


class DebateAgent:
    """
    A debate agent that participates in mathematical problem-solving debates.
    Uses local Ollama model with automatic fallback to simulation.
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
                logger.warning(f"Could not initialize local client for {agent_id}: {e}. Using simulation mode.")
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
        Generate response using local model or simulation fallback.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            The agent's response text (never crashes - always returns something)
        """
        if self.mock_mode:
            return f"[Mock] {self.agent_id} response: After analysis, I believe the answer is 42. Here's my reasoning..."
        
        if not self.client:
            return "[SIMULATION] Agent response unavailable - using simulation mode."
        
        # This will never crash - LocalClient.generate() always returns a string
        return self.client.generate(messages, temperature=0.7, max_tokens=400)
    
    def generate_initial_answer(self, question: str) -> str:
        """Generate an initial answer to the question."""
        logger.info(f"{self.agent_id} generating initial answer")
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"Solve this problem step-by-step:\n\n{question}"}
        ]
        
        start_time = datetime.now()
        response = self.generate(messages)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"{self.agent_id} initial answer generated in {elapsed:.2f}s")
        
        self.history.append({
            "type": "initial",
            "content": response,
            "round": 0
        })
        return response
    
    def critique_peer(self, question: str, peer_answer: str, round_num: int) -> str:
        """Critique another agent's answer (used in standard debate)."""
        logger.info(f"{self.agent_id} critiquing peer in round {round_num}")
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"Original problem:\n{question}\n\nYour peer's answer:\n{peer_answer}\n\nPlease critically review this answer. Identify any errors or flaws. If you find mistakes, provide your corrected solution. If you agree, explain why."}
        ]
        
        start_time = datetime.now()
        response = self.generate(messages)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"{self.agent_id} critique completed in {elapsed:.2f}s")
        
        self.history.append({
            "type": "critique",
            "content": response,
            "round": round_num,
            "peer_answer": peer_answer
        })
        return response
    
    def revise_from_judge_feedback(self, question: str, judge_feedback: str, round_num: int) -> str:
        """Revise answer based on judge's feedback (used in mediated debate)."""
        logger.info(f"{self.agent_id} revising based on judge feedback in round {round_num}")
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"Original problem:\n{question}\n\nAn impartial judge has reviewed the debate and provided this feedback:\n{judge_feedback}\n\nPlease carefully consider this feedback and revise your answer if necessary. Be honest - if you made an error, acknowledge it and correct it."}
        ]
        
        start_time = datetime.now()
        response = self.generate(messages)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"{self.agent_id} revision completed in {elapsed:.2f}s")
        
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
    Uses local Ollama model with automatic fallback to simulation.
    """
    
    def __init__(self, mock_mode: bool = False):
        """Initialize the judge agent."""
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
                logger.warning(f"Could not initialize local client for JudgeAgent: {e}. Using simulation mode.")
                self.mock_mode = True
        else:
            logger.info("JudgeAgent initialized in MOCK MODE")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the judge."""
        return """You are a critical Judge. Your role is to evaluate mathematical solutions impartially.

Instructions:
1. Analyze both agents' solutions carefully
2. Identify errors, inconsistencies, or logical flaws
3. If solutions are wrong, explain why clearly
4. If solutions are correct, say "CONSENSUS: Both solutions are correct."
5. Be critical - do not accept incorrect solutions
6. Provide clear, actionable feedback

Focus on mathematical correctness above all else."""

    def critique(self, question: str, agent_a_answer: str, agent_b_answer: str, round_num: int) -> str:
        """Evaluate two agents' answers and provide critical feedback."""
        logger.info(f"Judge evaluating answers in round {round_num}")
        
        if self.mock_mode:
            return "[Mock] Judge feedback: I've reviewed both solutions. Agent A made an error in step 3, and Agent B's calculation is incorrect. Here are the specific issues..."
        
        if not self.client:
            return "[SIMULATION] Judge feedback: After reviewing both solutions, I identify several areas that need correction..."
        
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
        response = self.client.generate(messages, temperature=0.3, max_tokens=500)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Judge evaluation completed in {elapsed:.2f}s")
        
        self.history.append({
            "type": "evaluation",
            "content": response,
            "round": round_num,
            "agent_a_answer": agent_a_answer,
            "agent_b_answer": agent_b_answer
        })
        return response
