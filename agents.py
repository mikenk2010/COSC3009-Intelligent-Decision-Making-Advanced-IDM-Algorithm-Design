"""
Hybrid Multi-Agent Debate System - Agents Module
Supports both OpenAI Cloud and Local Ollama inference with automatic fallback.

Priority:
1. OpenAI Cloud (gpt-4o-mini) if valid API key exists
2. Local Ollama (qwen2.5:1.5b) as fallback
"""

import os
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from openai import OpenAI, AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ensure_readable_formatting(text: str) -> str:
    """
    Post-process text to ensure proper line breaks and readability.
    Ensures paragraphs are separated by double line breaks for proper Markdown rendering.
    """
    if not text:
        return text
    
    # Replace single newlines with double newlines if they appear to be paragraph breaks
    # This helps when LLM outputs dense text without proper spacing
    lines = text.split('\n')
    processed_lines = []
    
    for i, line in enumerate(lines):
        processed_lines.append(line)
        # If current line is not empty and next line is not empty and not a list item,
        # add an extra newline for paragraph spacing
        if (i < len(lines) - 1 and 
            line.strip() and 
            lines[i + 1].strip() and 
            not lines[i + 1].strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '#'))):
            # Check if current line doesn't end with punctuation that suggests continuation
            if not line.rstrip().endswith((':', ';', ',')):
                processed_lines.append('')
    
    return '\n'.join(processed_lines)


def sanitize_latex(text: str) -> str:
    """
    Remove LaTeX formatting from text to prevent rendering issues.
    
    Converts:
    - $...$ and $$...$$ to plain text
    - \frac{a}{b} to a/b
    - \text{...} to plain text
    - \cdot to *
    - \sum to sum
    - \rightarrow to ->
    - \textbf{...} to **...**
    - Subscripts like R_{t+1} to R(t+1) or R_next
    - Other LaTeX commands to plain text equivalents
    """
    if not text:
        return text
    
    import re
    
    # Remove dollar signs (math delimiters)
    text = text.replace('$$', '').replace('$', '')
    
    # Convert common LaTeX fractions: \frac{a}{b} -> a/b
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', text)
    
    # Convert \text{...} to plain text
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    
    # Convert \textbf{...} to **...**
    text = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', text)
    
    # Convert \cdot to *
    text = text.replace('\\cdot', '*')
    
    # Convert \sum to sum
    text = text.replace('\\sum', 'sum')
    
    # Convert \rightarrow to ->
    text = text.replace('\\rightarrow', '->')
    
    # Convert subscripts: R_{t+1} -> R(t+1), G_{standard} -> G(standard)
    text = re.sub(r'([A-Za-z]+)_\{([^}]+)\}', r'\1(\2)', text)
    
    # Convert simple subscripts: R_t -> R(t)
    text = re.sub(r'([A-Za-z]+)_([a-z0-9]+)', r'\1(\2)', text)
    
    # Remove other LaTeX commands (backslash followed by letters)
    text = re.sub(r'\\([a-zA-Z]+)', r'\1', text)
    
    # Clean up extra spaces
    text = ' '.join(text.split())
    
    return text


class SmartClient:
    """
    Hybrid inference client that automatically chooses between OpenAI and Ollama.
    
    Priority:
    1. OpenAI Cloud (if valid API key exists and works)
    2. Local Ollama (automatic fallback)
    
    Features:
    - Automatic fallback on quota/auth errors
    - Runtime switching between providers
    - Detailed logging of provider usage
    """
    
    def __init__(self):
        """Initialize the SmartClient with automatic provider detection."""
        logger.debug("Initializing SmartClient...")
        
        # Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
        self.local_model = os.getenv("LOCAL_MODEL", "qwen2.5:1.5b")
        self.timeout = float(os.getenv("API_TIMEOUT", "300.0"))
        self.force_local = os.getenv("FORCE_LOCAL", "false").lower() == "true"
        
        # State
        self.client: Optional[OpenAI] = None
        self.model: str = ""
        self.provider: str = ""  # "openai" or "local"
        self.fallback_triggered: bool = False
        
        # Initialize the appropriate client
        self._initialize_client()
    
    def _is_valid_openai_key(self, key: str) -> bool:
        """Check if the API key looks valid (basic format check)."""
        if not key:
            return False
        # OpenAI keys start with 'sk-' and are typically 51+ characters
        # Also accept 'sk-proj-' format for project keys
        return key.startswith("sk-") and len(key) >= 20
    
    def _initialize_client(self):
        """Initialize the appropriate client based on configuration."""
        
        # Check if we should use OpenAI
        use_openai = (
            not self.force_local and 
            self._is_valid_openai_key(self.openai_api_key)
        )
        
        if use_openai:
            logger.info("🌐 Attempting to use OpenAI Cloud...")
            try:
                self.client = OpenAI(
                    api_key=self.openai_api_key,
                    timeout=self.timeout
                )
                self.model = self.openai_model
                self.provider = "openai"
                logger.info(f"✅ OpenAI client initialized - Model: {self.model}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize OpenAI client: {e}")
                self._switch_to_local()
        else:
            if self.force_local:
                logger.info("🔧 FORCE_LOCAL is enabled - Using local Ollama")
            else:
                logger.info("🔑 No valid OpenAI API key found - Using local Ollama")
            self._switch_to_local()
    
    def _switch_to_local(self):
        """Switch to local Ollama inference."""
        logger.info("🏠 Switching to Local Ollama...")
        try:
            self.client = OpenAI(
                base_url=self.ollama_base_url,
                api_key="ollama",  # Ollama doesn't need a real key
                timeout=self.timeout
            )
            self.model = self.local_model
            self.provider = "local"
            self.fallback_triggered = True
            logger.info(f"✅ Local Ollama client initialized - Model: {self.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Local client: {e}")
            raise RuntimeError(f"Cannot initialize any inference provider: {e}")
    
    def generate(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7, 
        max_tokens: int = 400
    ) -> Tuple[str, str]:
        """
        Generate a response using the current provider.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Tuple of (content, provider) where provider is "OpenAI" or "Local Qwen"
        """
        logger.debug(f"Generating response - Provider: {self.provider}, Model: {self.model}")
        
        try:
            start_time = datetime.now()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            content = response.choices[0].message.content
            
            # Ensure readable formatting (line breaks, but preserve LaTeX)
            content = ensure_readable_formatting(content)
            
            provider_name = "OpenAI" if self.provider == "openai" else "Local Qwen"
            logger.info(f"✅ Response generated - Provider: {provider_name}, Time: {elapsed:.2f}s")
            
            return content, provider_name
            
        except (AuthenticationError, RateLimitError) as e:
            # OpenAI quota/auth error - switch to local
            logger.warning(f"⚠️ OpenAI failed ({type(e).__name__}): {str(e)[:100]}")
            logger.warning("🔄 Switching to Local Fallback...")
            
            if self.provider == "openai":
                self._switch_to_local()
                # Retry with local
                return self.generate(messages, temperature, max_tokens)
            else:
                # Already on local, return error
                return f"[ERROR] API call failed: {str(e)[:100]}", "Error"
                
        except APITimeoutError as e:
            logger.warning(f"⏱️ API Timeout: {str(e)[:100]}")
            
            if self.provider == "openai":
                # Try local as fallback
                logger.warning("🔄 Timeout on OpenAI - Switching to Local Fallback...")
                self._switch_to_local()
                return self.generate(messages, temperature, max_tokens)
            else:
                # Local also timed out - return simulation
                return self._generate_simulation_response(messages), "Simulation"
                
        except APIConnectionError as e:
            logger.warning(f"🔌 Connection Error: {str(e)[:100]}")
            
            if self.provider == "openai":
                # Try local as fallback
                logger.warning("🔄 Connection error on OpenAI - Switching to Local Fallback...")
                self._switch_to_local()
                return self.generate(messages, temperature, max_tokens)
            else:
                # Local connection failed - return simulation
                return self._generate_simulation_response(messages), "Simulation"
                
        except Exception as e:
            logger.error(f"❌ Unexpected error: {type(e).__name__}: {str(e)[:100]}")
            
            if self.provider == "openai":
                # Try local as fallback
                logger.warning("🔄 Unexpected error on OpenAI - Switching to Local Fallback...")
                self._switch_to_local()
                return self.generate(messages, temperature, max_tokens)
            else:
                # Return simulation as last resort
                return self._generate_simulation_response(messages), "Simulation"
    
    def _generate_simulation_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a simulated response when all providers fail."""
        # Extract context
        user_content = ""
        system_content = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_content = msg.get("content", "")
            elif msg.get("role") == "system":
                system_content = msg.get("content", "")
        
        # Generate contextual response with proper Markdown formatting
        if "judge" in system_content.lower():
            response = """[SIMULATION] Judge Feedback:

### Evaluation of Agent A
- **Strengths:** Approach shows good reasoning
- **Status:** Review completed

### Evaluation of Agent B
- **Issues Found:** Should verify the calculation in step 2

### Recommendation
Please both agents revise your answers considering these points."""
        elif "critique" in user_content.lower():
            response = """[SIMULATION] Review Complete:

### Analysis
- After reviewing the solution, I agree with the general approach
- The calculation appears correct

### Conclusion
My final answer remains the same."""
        else:
            # Math problem response
            response = """[SIMULATION] Solution:

### Step 1: Identify Key Values
- First, I identify the key values from the problem

### Step 2: Apply Operation
- Then apply the relevant operation

### Step 3: Calculate
- Perform the calculation

### Final Answer
The answer is **42**."""
        
        # Ensure readable formatting (preserve LaTeX in simulation responses)
        return ensure_readable_formatting(response)
    
    def get_status(self) -> Dict:
        """Get current client status for UI display."""
        return {
            "provider": self.provider,
            "model": self.model,
            "provider_name": "OpenAI Cloud" if self.provider == "openai" else "Local Ollama",
            "fallback_triggered": self.fallback_triggered,
            "openai_key_configured": self._is_valid_openai_key(self.openai_api_key),
            "force_local": self.force_local
        }


# Legacy LocalClient for backward compatibility
class LocalClient(SmartClient):
    """
    Backward-compatible alias for SmartClient.
    Use SmartClient directly for new code.
    """
    pass


class DebateAgent:
    """
    A debate agent that can generate answers and critique other agents.
    Uses SmartClient for hybrid inference.
    """
    
    def __init__(self, agent_id: str, role: str, mock_mode: bool = False):
        """
        Initialize a debate agent.
        
        Args:
            agent_id: Unique identifier (e.g., "Agent A")
            role: Role description (e.g., "Math Expert")
            mock_mode: If True, use mock responses instead of API
        """
        logger.info(f"Initializing DebateAgent - ID: {agent_id}, Role: {role}, Mock Mode: {mock_mode}")
        
        self.agent_id = agent_id
        self.role = role
        self.mock_mode = mock_mode
        self.history: List[str] = []
        self.current_answer: str = ""
        self.last_provider: str = ""
        
        if not mock_mode:
            logger.debug(f"Creating SmartClient for {agent_id}")
            self.client = SmartClient()
        else:
            self.client = None
        
        logger.info(f"DebateAgent {agent_id} initialized")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return f"""You are {self.agent_id}, a {self.role} specializing in mathematical problem-solving.

Your task:
1. Analyze mathematical problems step-by-step
2. Show clear logical reasoning
3. When reviewing solutions, identify errors or flaws
4. Revise your answer if you find mistakes
5. Be honest - don't agree with incorrect solutions

**CRITICAL FORMATTING REQUIREMENTS:**
You must structure your response using clear **Markdown formatting** for maximum readability:

1. **Use Headers** (e.g., `### Step 1: Analysis`, `### Step 2: Calculation`) to separate major sections
2. **Use Bullet Points** (`- `) for lists, steps, or key points
3. **Use Bold** (`**text**`) for final answers, key numbers, and important conclusions
4. **Add Double Line Breaks** (`\n\n`) between paragraphs for readability
5. **Break up dense text** into smaller, digestible sections with clear headers

**MATH FORMATTING RULES (STRICT):**
1. **Inline Math:** MUST be wrapped in single dollar signs.
   - BAD: The probability is 1/2.
   - BAD: The probability is \( \frac{1}{2} \).
   - GOOD: The probability is $\frac{1}{2}$.
2. **Display Math (Block Equations):** MUST be wrapped in double dollar signs.
   - BAD: \[ x = 5 \]
   - GOOD: $$x = 5$$
3. **Common Symbols:**
   - Use `\times` for multiplication (not `*` or `x`).
   - Use `\frac{{num}}{{denom}}` for fractions.
   - Use `\approx` for approximate values.
   - Use `\text{{...}}` for words inside equations (e.g., $$\text{{Total}} = 50$$).
4. **No Naked Math:** Never write a bare equation without dollar signs.

**Example of Good Formatting:**
```
### Step 1: Identify Key Information
- Sarah read **15 pages** on Monday
- Sarah read **23 pages** on Tuesday
- Sarah read **18 pages** on Wednesday
- Total pages in book: **200**

### Step 2: Calculate Total Pages Read
$$Total = 15 + 23 + 18 = 56 \text{{ pages}}$$

### Step 3: Calculate Remaining Pages
$$Remaining = 200 - 56 = 144 \text{{ pages}}$$

### Conclusion
Sarah has **144 pages** left to read.
```

Show your work and explain your reasoning clearly with proper Markdown and LaTeX formatting."""
    
    def generate_initial_answer(self, question: str) -> str:
        """Generate an initial answer to a question."""
        logger.info(f"{self.agent_id} generating initial answer")
        
        if self.mock_mode:
            self.current_answer = f"""[MOCK] {self.agent_id}'s answer:

### Step 1: Analysis
- Let me solve this step by step
- Identify key values from the problem

### Step 2: Calculation
- Apply the relevant operation

### Conclusion
The answer is **42**."""
            self.history.append(self.current_answer)
            self.last_provider = "Mock"
            return self.current_answer
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"Solve this problem step-by-step:\n\n{question}"}
        ]
        
        start_time = datetime.now()
        # Use higher max_tokens for detailed solutions
        response, provider = self.client.generate(messages, max_tokens=800)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        self.current_answer = response
        self.history.append(response)
        self.last_provider = provider
        
        logger.info(f"{self.agent_id} initial answer generated in {elapsed:.2f}s via {provider}")
        return response
    
    def critique_peer(self, question: str, peer_answer: str, round_num: int) -> str:
        """Critique a peer's answer and potentially revise own answer."""
        logger.info(f"{self.agent_id} critiquing peer in round {round_num}")
        
        if self.mock_mode:
            self.current_answer = f"""[MOCK] {self.agent_id}'s critique:

### Review of Peer's Answer
- I reviewed the peer's answer carefully
- I agree with their approach

### Revised Answer
My revised answer: **42**."""
            self.history.append(self.current_answer)
            self.last_provider = "Mock"
            return self.current_answer
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""Question: {question}

Your previous answer:
{self.current_answer}

Peer's answer to review:
{peer_answer}

Round {round_num}: Review the peer's answer. If you find errors, explain them. If their answer is better, acknowledge it. Then provide your revised answer (or confirm your original if you believe it's correct)."""}
        ]
        
        start_time = datetime.now()
        # Use higher max_tokens for detailed critiques and revisions
        response, provider = self.client.generate(messages, max_tokens=1000)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        self.current_answer = response
        self.history.append(response)
        self.last_provider = provider
        
        logger.info(f"{self.agent_id} critique completed in {elapsed:.2f}s via {provider}")
        return response
    
    def revise_from_judge_feedback(self, question: str, judge_feedback: str, round_num: int) -> str:
        """Revise answer based on judge feedback."""
        logger.info(f"{self.agent_id} revising based on judge feedback in round {round_num}")
        
        if self.mock_mode:
            self.current_answer = f"""[MOCK] {self.agent_id}'s revision:

### Consideration of Judge's Feedback
- Based on the judge's feedback, I've revised my answer
- I've corrected the identified errors

### Conclusion
The correct answer is **42**."""
            self.history.append(self.current_answer)
            self.last_provider = "Mock"
            return self.current_answer
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""Question: {question}

Your previous answer:
{self.current_answer}

Judge's feedback:
{judge_feedback}

Round {round_num}: Consider the judge's feedback carefully. If the judge identified errors in your solution, correct them. Provide your revised answer."""}
        ]
        
        start_time = datetime.now()
        # Use higher max_tokens for detailed revisions based on judge feedback
        response, provider = self.client.generate(messages, max_tokens=1000)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        self.current_answer = response
        self.history.append(response)
        self.last_provider = provider
        
        logger.info(f"{self.agent_id} revision completed in {elapsed:.2f}s via {provider}")
        return response
    
    def get_final_answer(self) -> str:
        """Get the agent's current/final answer."""
        return self.current_answer


class JudgeAgent:
    """
    An impartial judge that evaluates debate agent responses.
    Uses SmartClient for hybrid inference with lower temperature for consistency.
    """
    
    def __init__(self, mock_mode: bool = False):
        """Initialize the judge agent."""
        logger.info(f"Initializing JudgeAgent - Mock Mode: {mock_mode}")
        
        self.mock_mode = mock_mode
        self.history: List[str] = []
        self.last_provider: str = ""
        
        if not mock_mode:
            logger.debug("Creating SmartClient for Judge")
            self.client = SmartClient()
        else:
            self.client = None
        
        logger.info("JudgeAgent initialized")
    
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

**CRITICAL FORMATTING REQUIREMENTS:**
You must structure your response using clear **Markdown formatting** for maximum readability:

1. **Use Headers** (e.g., `### Evaluation of Agent A`, `### Evaluation of Agent B`, `### Overall Assessment`) to separate sections
2. **Use Bullet Points** (`- `) for lists of errors, strengths, or recommendations
3. **Use Bold** (`**text**`) for key findings, errors identified, and final verdicts
4. **Add Double Line Breaks** (`\n\n`) between paragraphs for readability
5. **Break up dense text** into smaller, digestible sections with clear headers

**MATH FORMATTING RULES (STRICT):**
1. **Inline Math:** MUST be wrapped in single dollar signs.
   - BAD: The calculation shows 15 + 23 = 38.
   - BAD: The calculation shows \( 15 + 23 = 38 \).
   - GOOD: The calculation shows $15 + 23 = 38$.
2. **Display Math (Block Equations):** MUST be wrapped in double dollar signs.
   - BAD: \[ Total = 15 + 23 + 18 \]
   - GOOD: $$Total = 15 + 23 + 18$$
3. **Common Symbols:**
   - Use `\times` for multiplication (not `*` or `x`).
   - Use `\frac{{num}}{{denom}}` for fractions.
   - Use `\approx` for approximate values.
   - Use `\text{{...}}` for words inside equations (e.g., $$\text{{Error}} = 40 - 38 = 2$$).
4. **No Naked Math:** Never write a bare equation without dollar signs.

**Example of Good Formatting:**
```
### Evaluation of Agent A
- **Strengths:** Clear step-by-step approach
- **Errors Found:** Calculation error in step 2 (should be 15 + 23 = 38, not 40)
- **Recommendation:** Recalculate the total pages read

### Evaluation of Agent B
- **Strengths:** Correct final calculation
- **Errors Found:** Missing explanation of intermediate steps
- **Recommendation:** Add more detail to show work

### Overall Assessment
Both agents need to revise their solutions. Agent A has a calculation error. Agent B needs to show more work.
```

Focus on mathematical correctness above all else, and present your evaluation in clear, structured Markdown format."""

    def critique(self, question: str, agent_a_answer: str, agent_b_answer: str, round_num: int) -> str:
        """Evaluate both agents' answers and provide feedback."""
        logger.info(f"Judge evaluating answers in round {round_num}")
        
        if self.mock_mode:
            feedback = f"""[MOCK] Judge's evaluation for round {round_num}:

### Evaluation of Agent A
- **Strengths:** Shows reasonable approach
- **Status:** Calculation is correct

### Evaluation of Agent B
- **Strengths:** Shows reasonable approach
- **Issues Found:** Should verify step 2

### Overall Assessment
Both agents should revise accordingly."""
            self.history.append(feedback)
            self.last_provider = "Mock"
            return feedback
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""Question: {question}

Agent A's answer:
{agent_a_answer}

Agent B's answer:
{agent_b_answer}

Round {round_num}: Evaluate both solutions. Identify any errors or inconsistencies. Provide specific feedback for each agent."""}
        ]
        
        start_time = datetime.now()
        # Use lower temperature for judge (more consistent/deterministic)
        # Use higher max_tokens for detailed judge feedback
        response, provider = self.client.generate(messages, temperature=0.3, max_tokens=800)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        self.history.append(response)
        self.last_provider = provider
        
        logger.info(f"Judge evaluation completed in {elapsed:.2f}s via {provider}")
        return response


def get_inference_status() -> Dict:
    """
    Get the current inference status for UI display.
    Creates a temporary SmartClient to check configuration.
    """
    try:
        client = SmartClient()
        return client.get_status()
    except Exception as e:
        logger.error(f"Error getting inference status: {e}")
        return {
            "provider": "error",
            "model": "unknown",
            "provider_name": "Error",
            "fallback_triggered": False,
            "openai_key_configured": False,
            "force_local": False,
            "error": str(e)
        }


def test_connection() -> Tuple[bool, str, str]:
    """
    Test the inference connection.
    
    Returns:
        Tuple of (success, message, provider)
    """
    try:
        client = SmartClient()
        response, provider = client.generate(
            [{"role": "user", "content": "Say 'Hello' in one word."}],
            max_tokens=5,
            temperature=0.1
        )
        
        if response.startswith("[ERROR]") or response.startswith("[SIMULATION]"):
            return False, response, provider
        
        return True, f"Connection successful: {response[:50]}", provider
        
    except Exception as e:
        return False, f"Connection failed: {str(e)[:100]}", "Error"
