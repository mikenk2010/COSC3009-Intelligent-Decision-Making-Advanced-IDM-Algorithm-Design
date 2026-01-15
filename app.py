"""
Multi-Agent Debate System - Streamlit Web UI
Hybrid Inference: OpenAI Cloud (priority) with Local Ollama fallback.
Robust fallback mechanisms ensure the demo never crashes.
"""

import streamlit as st
import os
import logging
import requests
import json
from datetime import datetime
from pathlib import Path
from agents import DebateAgent, JudgeAgent, SmartClient, get_inference_status, test_connection
from simulation import run_standard_debate, run_mediated_debate, mock_debate

# Configure logging for Streamlit - use logs/ subdirectory to avoid watchdog spam
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'streamlit_app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("=" * 80)
logger.info("STREAMLIT APP STARTING")
logger.info(f"Start time: {datetime.now()}")
logger.info("=" * 80)

# History storage directory
HISTORY_DIR = Path("debate_history")
HISTORY_DIR.mkdir(exist_ok=True)
STANDARD_HISTORY_DIR = HISTORY_DIR / "standard"
MEDIATED_HISTORY_DIR = HISTORY_DIR / "mediated"
STANDARD_HISTORY_DIR.mkdir(exist_ok=True)
MEDIATED_HISTORY_DIR.mkdir(exist_ok=True)

def save_debate_history(result, debate_type="standard"):
    """
    Save debate result as HTML file and update history index.
    
    Args:
        result: Dictionary containing debate result
        debate_type: "standard" or "mediated"
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_dir = STANDARD_HISTORY_DIR if debate_type == "standard" else MEDIATED_HISTORY_DIR
    
    # Save as JSON for data
    json_file = history_dir / f"{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Generate HTML
    html_file = history_dir / f"{timestamp}.html"
    html_content = generate_html_report(result, debate_type, timestamp)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Update history index
    update_history_index(debate_type)
    
    logger.info(f"Saved {debate_type} debate history: {html_file}")
    return str(html_file), timestamp

def generate_html_report(result, debate_type, timestamp):
    """Generate HTML report from debate result."""
    debate_title = "Standard Debate (Peer-to-Peer)" if debate_type == "standard" else "Mediated Debate (With Judge)"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{debate_title} - {timestamp}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header .meta {{
            margin-top: 10px;
            opacity: 0.9;
            font-size: 14px;
        }}
        .question-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .question-box h2 {{
            margin-top: 0;
            color: #333;
        }}
        .message {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .message-header {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .agent-a {{ border-left: 4px solid #4CAF50; }}
        .agent-b {{ border-left: 4px solid #2196F3; }}
        .judge {{ border-left: 4px solid #FF9800; }}
        .final-answers {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 30px;
        }}
        .final-answer {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .final-answer h3 {{
            margin-top: 0;
            color: #333;
        }}
        pre {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            white-space: pre-wrap;
            font-family: inherit;
        }}
        .round-header {{
            background: #667eea;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            margin: 20px 0 10px 0;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{debate_title}</h1>
        <div class="meta">
            Timestamp: {timestamp.replace('_', ' ')} | 
            Rounds: {len(result.get('log', []))} | 
            Type: {debate_type.title()}
        </div>
    </div>
    
    <div class="question-box">
        <h2>📝 Question</h2>
        <p>{result.get('question', 'N/A')}</p>
    </div>
"""
    
    # Add debate log
    for entry in result.get('log', []):
        round_num = entry.get('round', 0)
        html += f'<div class="round-header">Round {round_num}</div>\n'
        
        if round_num == 0:
            html += f"""
            <div class="message agent-a">
                <div class="message-header">🤖 Agent A - Initial Answer</div>
                <pre>{entry.get('agent_a', 'N/A').replace('<', '&lt;').replace('>', '&gt;')}</pre>
            </div>
            <div class="message agent-b">
                <div class="message-header">🤖 Agent B - Initial Answer</div>
                <pre>{entry.get('agent_b', 'N/A').replace('<', '&lt;').replace('>', '&gt;')}</pre>
            </div>
"""
        else:
            if debate_type == "mediated" and entry.get('judge_feedback'):
                html += f"""
            <div class="message judge">
                <div class="message-header">⚖️ Judge's Evaluation</div>
                <pre>{entry.get('judge_feedback', 'N/A').replace('<', '&lt;').replace('>', '&gt;')}</pre>
            </div>
"""
            html += f"""
            <div class="message agent-a">
                <div class="message-header">🤖 Agent A - Revision</div>
                <pre>{entry.get('agent_a', 'N/A').replace('<', '&lt;').replace('>', '&gt;')}</pre>
            </div>
            <div class="message agent-b">
                <div class="message-header">🤖 Agent B - Revision</div>
                <pre>{entry.get('agent_b', 'N/A').replace('<', '&lt;').replace('>', '&gt;')}</pre>
            </div>
"""
    
    # Add final answers
    final_a = result.get('final_agent_a', 'N/A').replace('<', '&lt;').replace('>', '&gt;')
    final_b = result.get('final_agent_b', 'N/A').replace('<', '&lt;').replace('>', '&gt;')
    
    html += f"""
    <div class="final-answers">
        <div class="final-answer">
            <h3>🤖 Agent A - Final Answer</h3>
            <pre>{final_a}</pre>
        </div>
        <div class="final-answer">
            <h3>🤖 Agent B - Final Answer</h3>
            <pre>{final_b}</pre>
        </div>
    </div>
</body>
</html>
"""
    return html

def update_history_index(debate_type):
    """Update history index JSON file."""
    history_dir = STANDARD_HISTORY_DIR if debate_type == "standard" else MEDIATED_HISTORY_DIR
    index_file = history_dir / "index.json"
    
    # Get all history files
    history_files = sorted(history_dir.glob("*.json"), reverse=True)[:50]  # Keep last 50
    
    index_data = []
    for json_file in history_files:
        if json_file.name == "index.json":
            continue
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                timestamp = json_file.stem
                index_data.append({
                    "timestamp": timestamp,
                    "question": data.get('question', 'N/A')[:100],
                    "html_file": f"{timestamp}.html",
                    "json_file": f"{timestamp}.json"
                })
        except Exception as e:
            logger.warning(f"Error reading history file {json_file}: {e}")
    
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)

def get_history_list(debate_type="standard"):
    """Get list of history entries."""
    history_dir = STANDARD_HISTORY_DIR if debate_type == "standard" else MEDIATED_HISTORY_DIR
    index_file = history_dir / "index.json"
    
    if not index_file.exists():
        return []
    
    try:
        with open(index_file, 'r') as f:
            return json.load(f)
    except Exception:
        return []

# Page configuration
st.set_page_config(
    page_title="Local Multi-Agent Debate System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .status-online {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    .status-offline {
        background-color: #f44336;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    .status-openai {
        background-color: #10a37f;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    .status-local {
        background-color: #FF9800;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    .judge-message {
        background-color: #fff3e0;
        border-left: 5px solid #FF9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .provider-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-left: 8px;
    }
    .provider-openai {
        background-color: #10a37f;
        color: white;
    }
    .provider-local {
        background-color: #FF9800;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Preset math problems with descriptions
PRESET_PROBLEMS = {
    "Select a problem...": {
        "question": "",
        "description": "",
        "difficulty": "",
        "type": ""
    },
    "Problem 1: Janet's ducks": {
        "question": """Janet's ducks lay eggs. She gets 3 times as many eggs from her ducks as she gets from her chickens. If she gets 3 eggs from her chickens, how many eggs does she get from her ducks?""",
        "description": "A multiplication word problem involving ratios. Tests understanding of 'times as many' relationships.",
        "difficulty": "Easy",
        "type": "Multiplication & Ratios",
        "answer": "9 eggs"
    },
    "Problem 2: Coffee shop": {
        "question": """A coffee shop sells coffee for $2.50 per cup and tea for $1.75 per cup. If a customer buys 4 cups of coffee and 3 cups of tea, how much does the customer pay in total?""",
        "description": "A multi-step calculation involving unit prices and quantities. Requires multiplication and addition.",
        "difficulty": "Easy",
        "type": "Money & Calculations",
        "answer": "$15.25"
    },
    "Problem 3: Book pages": {
        "question": """Sarah reads 15 pages of a book on Monday, 23 pages on Tuesday, and 18 pages on Wednesday. If the book has 200 pages total, how many pages does Sarah have left to read?""",
        "description": "A subtraction problem with multiple additions. Tests sequential reasoning and subtraction skills.",
        "difficulty": "Easy",
        "type": "Addition & Subtraction",
        "answer": "144 pages"
    },
    "Problem 4: Complex calculation": {
        "question": """A store has 120 apples. They sell 3/4 of them in the morning. In the afternoon, they receive a shipment of 50 more apples. How many apples does the store have at the end of the day?""",
        "description": "A multi-step problem involving fractions and addition. Requires calculating a fraction of a number, then adding.",
        "difficulty": "Medium",
        "type": "Fractions & Multi-step",
        "answer": "80 apples"
    },
    "Problem 5: Age problem": {
        "question": """Tom is 3 times as old as his sister. In 5 years, Tom will be twice as old as his sister. How old is Tom now?""",
        "description": "An algebraic reasoning problem involving age relationships and future time. Requires setting up equations.",
        "difficulty": "Hard",
        "type": "Algebra & Logic",
        "answer": "15 years old"
    }
}


def check_ollama_status():
    """
    Check if Ollama server is reachable.
    
    Returns:
        Tuple of (is_online, status_message)
    """
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    ollama_host = ollama_host.rstrip('/')
    
    logger.debug(f"Checking Ollama status at: {ollama_host}")
    
    try:
        logger.debug(f"Making request to {ollama_host}/api/tags")
        start_time = datetime.now()
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.debug(f"Ollama API response received in {elapsed:.2f}s - Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                models = data.get("models", [])
                model_names = [model.get("name", "") for model in models]
                logger.debug(f"Found {len(model_names)} models: {model_names}")
                
                # Find the qwen2.5 model
                qwen_models = [name for name in model_names if "qwen2.5" in name or "qwen" in name.lower()]
                model_loaded = len(qwen_models) > 0
                
                if model_loaded:
                    # Get the first matching model name
                    model_name = qwen_models[0] if qwen_models else "qwen2.5:1.5b"
                    logger.info(f"Ollama is online and model is loaded: {model_name}")
                    return True, f"✅ Online | ✅ Model loaded: {model_name}"
                else:
                    logger.warning("Ollama is online but model is not loaded")
                    return True, "✅ Online | ⚠️ Model not loaded"
            except (ValueError, KeyError) as e:
                logger.error(f"Error parsing Ollama response: {str(e)}", exc_info=True)
                return True, "✅ Online | ⚠️ Could not check model"
        else:
            logger.error(f"Ollama returned status code: {response.status_code}")
            return False, f"❌ Error (Status: {response.status_code})"
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Cannot connect to Ollama: {str(e)}")
        return False, "❌ Offline - Cannot connect"
    except requests.exceptions.Timeout as e:
        logger.warning(f"Ollama request timeout: {str(e)}")
        return False, "⏳ Timeout - Still starting?"
    except Exception as e:
        logger.error(f"Unexpected error checking Ollama: {str(e)}", exc_info=True)
        return False, f"❌ Error: {str(e)[:50]}"


def calculate_progress(current: int, total: int, min_progress: float = 0.0, max_progress: float = 1.0) -> float:
    """
    Calculate progress value safely, ensuring it stays within [0.0, 1.0].
    
    Args:
        current: Current step number
        total: Total number of steps
        min_progress: Minimum progress value (default 0.0)
        max_progress: Maximum progress value (default 1.0)
    
    Returns:
        Progress value between min_progress and max_progress
    """
    if total == 0:
        return min_progress
    
    # Calculate progress as ratio
    progress = min(current / total, 1.0)  # Cap at 1.0
    
    # Scale to desired range
    scaled = min_progress + (progress * (max_progress - min_progress))
    
    # Ensure it's within bounds
    return max(min_progress, min(max_progress, scaled))


def fix_latex_rendering(text: str) -> str:
    """
    Helper to ensure common LLM LaTeX mistakes are fixed for Streamlit.
    Converts alternative LaTeX delimiters to standard $ and $$ format.
    """
    if not text:
        return text
    
    import re
    
    # 1. Convert \[ ... \] to $$...$$ (Display Math)
    # Handle multiline equations with re.DOTALL to match across newlines
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    
    # 2. Convert \( ... \) to $...$ (Inline Math)
    # Handle multiline inline math (though rare)
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    
    # 3. Fix "naked" fractions like \frac{1}{2} without $ signs
    # This regex looks for \frac that isn't preceded by a $ (not already in math mode)
    # We use negative lookbehind to ensure we're not inside $ delimiters
    # Pattern: \frac{...}{...} not preceded by $ and not followed by $
    def wrap_frac(match):
        return f'$\\frac{{{match.group(1)}}}{{{match.group(2)}}}$'
    text = re.sub(r'(?<!\$)(?<!\\)\\frac\{([^}]+)\}\{([^}]+)\}(?!\$)', wrap_frac, text)
    
    # 4. Ensure proper line breaks for Markdown
    lines = text.split('\n')
    processed_lines = []
    
    for i, line in enumerate(lines):
        processed_lines.append(line)
        # Add extra newline for paragraph spacing if needed
        if (i < len(lines) - 1 and 
            line.strip() and 
            lines[i + 1].strip() and 
            not lines[i + 1].strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '#'))):
            if not line.rstrip().endswith((':', ';', ',')):
                processed_lines.append('')
    
    return '\n'.join(processed_lines)


def format_text_with_latex(text: str) -> str:
    """
    Format text - returns text wrapped in HTML pre tag to prevent LaTeX rendering.
    All formatting/highlighting is disabled - text is displayed as normal plain text.
    Use this only for progress messages where you want plain text.
    """
    if not text:
        return text
    
    # Wrap in <pre> tag to display as plain text and prevent Streamlit from rendering LaTeX
    # Escape HTML special characters to prevent XSS
    import html
    escaped_text = html.escape(text)
    # Replace backslashes with HTML entity to prevent LaTeX rendering
    escaped_text = escaped_text.replace('\\', '&#92;')
    return f'<pre style="white-space: pre-wrap; font-family: inherit;">{escaped_text}</pre>'

def escape_latex_for_display(text: str) -> str:
    """
    Escape LaTeX commands for plain text display in progress messages.
    Escapes HTML and LaTeX characters to prevent rendering.
    """
    if not text:
        return text
    import html
    # Escape HTML special characters first
    text = html.escape(text)
    # Replace backslashes with HTML entity to prevent LaTeX rendering
    # This ensures \frac, \text, etc. display as literal text
    text = text.replace('\\', '&#92;')
    return text


def display_chat_messages(debate_log, show_judge=False):
    """Display debate log as chat messages."""
    for entry in debate_log:
        round_num = entry['round']
        
        if round_num == 0:
            # Initial round
            st.chat_message("user", avatar="📝").write(f"**Round {round_num}: Initial Answers**")
            
            with st.chat_message("assistant", avatar="🤖"):
                st.write("**Agent A:**")
                # Format for Markdown rendering with LaTeX sanitization
                formatted_text = fix_latex_rendering(entry['agent_a'])
                st.markdown(formatted_text)
            
            with st.chat_message("assistant", avatar="🤖"):
                st.write("**Agent B:**")
                formatted_text = fix_latex_rendering(entry['agent_b'])
                st.markdown(formatted_text)
        else:
            # Subsequent rounds
            if show_judge and entry.get('judge_feedback'):
                # Mediated debate - show judge feedback
                st.chat_message("user", avatar="⚖️").write(f"**Round {round_num}: Judge's Evaluation**")
                
                with st.chat_message("assistant", avatar="⚖️"):
                    st.markdown('<div class="judge-message">', unsafe_allow_html=True)
                    formatted_text = fix_latex_rendering(entry['judge_feedback'])
                    st.markdown(formatted_text)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.chat_message("user", avatar="💬").write(f"**Round {round_num}: Revisions**")
            
            with st.chat_message("assistant", avatar="🤖"):
                st.write("**Agent A:**")
                formatted_text = fix_latex_rendering(entry['agent_a'])
                st.markdown(formatted_text)
            
            with st.chat_message("assistant", avatar="🤖"):
                st.write("**Agent B:**")
                formatted_text = fix_latex_rendering(entry['agent_b'])
                st.markdown(formatted_text)


def main():
    """Main Streamlit application."""
    st.title("🤖 Hybrid Multi-Agent Debate System")
    st.markdown("**OpenAI Cloud ↔ Local Ollama | Automatic Fallback**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Inference Mode")
        
        # Get inference status
        inference_status = get_inference_status()
        provider = inference_status.get("provider", "unknown")
        model = inference_status.get("model", "unknown")
        provider_name = inference_status.get("provider_name", "Unknown")
        openai_configured = inference_status.get("openai_key_configured", False)
        force_local = inference_status.get("force_local", False)
        
        # Display mode badge
        if provider == "openai":
            st.markdown(f'<div class="status-openai">🟢 Mode: OpenAI Cloud<br/>Model: {model}</div>', unsafe_allow_html=True)
        elif provider == "local":
            st.markdown(f'<div class="status-local">🟠 Mode: Local Ollama<br/>Model: {model}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-offline">❌ Mode: Error<br/>{inference_status.get("error", "Unknown error")}</div>', unsafe_allow_html=True)
        
        # Configuration details
        with st.expander("📊 Configuration Details"):
            st.write(f"**Provider:** {provider_name}")
            st.write(f"**Model:** {model}")
            st.write(f"**OpenAI Key Configured:** {'✅ Yes' if openai_configured else '❌ No'}")
            st.write(f"**Force Local Mode:** {'✅ Yes' if force_local else '❌ No'}")
            
            if not openai_configured:
                st.info("💡 Add `OPENAI_API_KEY` to `.env` file to use OpenAI Cloud.")
        
        st.markdown("---")
        
        # Check Ollama status (for fallback)
        st.header("🏠 Local Ollama Status")
        is_online, status_msg = check_ollama_status()
        
        if is_online:
            st.markdown(f'<div class="status-online">{status_msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-offline">{status_msg}</div>', unsafe_allow_html=True)
            if provider == "local":
                st.error("⚠️ Local mode selected but Ollama is offline!")
        
        st.markdown("---")
        
        # Test connection button
        st.header("🧪 Test Connection")
        if st.button("Test Inference", use_container_width=True):
            with st.spinner("Testing connection..."):
                import time
                test_start = time.time()
                success, message, used_provider = test_connection()
                test_elapsed = time.time() - test_start
                
                if success:
                    # Performance feedback
                    if test_elapsed < 2:
                        perf_msg = "⚡ Excellent"
                    elif test_elapsed < 5:
                        perf_msg = "✅ Good"
                    elif test_elapsed < 10:
                        perf_msg = "⚠️ Acceptable"
                    else:
                        perf_msg = "🐌 Slow"
                    
                    st.success(f"✅ Test successful via **{used_provider}**!")
                    st.write(f"Response time: {test_elapsed:.2f}s ({perf_msg})")
                    st.code(message[:200])
                else:
                    st.error(f"❌ Test failed: {message}")
                    st.warning("**Troubleshooting:**")
                    if provider == "openai":
                        st.markdown("""
                        1. Check your `OPENAI_API_KEY` in `.env`
                        2. Verify API key has credits
                        3. System will auto-fallback to local Ollama
                        """)
                    else:
                        st.markdown("""
                        1. Check if Ollama is running: `docker compose ps`
                        2. Load model: `docker exec -it ollama-server ollama pull qwen2.5:1.5b`
                        3. Check logs: `docker compose logs ollama`
                        """)
        
        st.markdown("---")
        
        # Instructions based on mode
        st.header("📋 Setup Instructions")
        
        if provider == "openai":
            st.success("""
            **✅ OpenAI Mode Active**
            
            You're using OpenAI Cloud for fast inference.
            
            If you run out of quota, the system will automatically switch to local Ollama.
            """)
        else:
            st.info("""
            **🏠 Local Mode Active**
            
            **To use OpenAI (faster):**
            1. Get API key from [OpenAI](https://platform.openai.com/api-keys)
            2. Create `.env` file:
            ```
            OPENAI_API_KEY=sk-your-key
            ```
            3. Restart: `docker compose down && docker compose up -d`
            
            **To load local model:**
            ```bash
            docker exec -it ollama-server ollama pull qwen2.5:1.5b
            ```
            """)
        
        st.markdown("---")
        
        # Problem selection
        st.header("📝 Problem Selection")
        selected_problem = st.selectbox(
            "Choose a math problem:",
            options=list(PRESET_PROBLEMS.keys()),
            key="problem_selectbox"
        )
        
        # Initialize current_question
        current_question = ""
        
        # Display problem details and editable problem field
        # Check if a valid problem is selected (not the placeholder)
        if selected_problem and selected_problem != "Select a problem...":
            problem_info = PRESET_PROBLEMS.get(selected_problem)
            
            if problem_info and problem_info.get("question"):
                # Problem Details Section - ALWAYS SHOW THIS
                st.markdown("---")
                st.markdown("### 📋 Problem Details")
                
                col1, col2 = st.columns(2)
                with col1:
                    problem_type = problem_info.get('type', 'N/A')
                    st.markdown(f"**Type:** `{problem_type}`")
                with col2:
                    difficulty = problem_info.get('difficulty', 'N/A')
                    st.markdown(f"**Difficulty:** `{difficulty}`")
                
                description = problem_info.get('description', 'No description available')
                st.markdown(f"**Description:** {description}")
                
                if problem_info.get('answer'):
                    with st.expander("💡 Show Expected Answer"):
                        st.success(f"**Answer:** `{problem_info['answer']}`")
                
                st.markdown("---")
                
                # Editable problem field (pre-filled with selected problem)
                st.markdown("### ✏️ Edit Problem (Optional)")
                st.caption("You can modify the problem text below before running the debate")
                
                # Use session state to preserve edits
                session_key = f"editable_problem_{selected_problem}"
                if session_key not in st.session_state or st.session_state.get('last_selected_problem') != selected_problem:
                    st.session_state[session_key] = problem_info.get("question", "")
                    st.session_state.last_selected_problem = selected_problem
                
                editable_problem = st.text_area(
                    "Problem Text:",
                    value=st.session_state.get(session_key, problem_info.get("question", "")),
                    height=120,
                    help="Edit the problem text if needed, or leave as-is to use the original",
                    key=f"editable_problem_{selected_problem}",
                    label_visibility="collapsed"
                )
                
                # Note: The widget automatically stores its value in session state via the key
                # No need to manually update st.session_state[session_key] as it's already managed
                
                # Use edited version if modified, otherwise use original
                original_question = problem_info.get("question", "").strip()
                if editable_problem.strip() != original_question:
                    st.info("ℹ️ **Using your edited version** of the problem")
                    current_question = editable_problem.strip()
                else:
                    current_question = original_question
            else:
                st.warning(f"⚠️ Problem info not found for: {selected_problem}")
                current_question = ""
        else:
            # No problem selected - show custom problem input
            st.markdown("---")
            st.markdown("### ✏️ Custom Problem")
            custom_problem = st.text_area(
                "Enter your own mathematical problem:",
                height=120,
                help="Enter your own mathematical problem here",
                key="custom_problem"
            )
            current_question = custom_problem.strip() if custom_problem.strip() else ""
        
        # Number of rounds
        st.markdown("---")
        num_rounds = st.slider(
            "Number of Debate Rounds",
            min_value=1,
            max_value=5,
            value=3,
            help="Number of rounds for the debate"
        )
        
        # Mock mode (only if model fails)
        use_mock = st.checkbox(
            "Use Mock Mode (if model unavailable)",
            value=False,
            help="Use hardcoded responses if local model fails"
        )
        
        olympiad_mode = st.checkbox(
            "Use Olympiad Mode (for Math problems)",
            value=False,
            help="Agent experts for math"
        )

        st.markdown("---")
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Standard Debate", 
        "⚖️ Mediated Debate", 
        "📄 Paper Details & Solution",
        "📜 Standard History",
        "📜 Mediated History"
    ])
    
    # Initialize session state
    if 'standard_result' not in st.session_state:
        st.session_state.standard_result = None
    if 'mediated_result' not in st.session_state:
        st.session_state.mediated_result = None
    
    # Tab 1: Standard Debate
    with tab1:
        st.header("📊 Standard Debate (Peer-to-Peer)")
        st.markdown("*Agents directly critique each other's answers*")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            start_debate = st.button("🚀 Start Standard Debate", use_container_width=True)
        
        if start_debate:
            if not current_question:
                logger.warning("Standard debate attempted without question")
                st.error("Please select or enter a problem first!")
            else:
                logger.info("Starting standard debate from UI")
                logger.info(f"Question: {current_question[:100]}...")
                logger.info(f"Rounds: {num_rounds}, Mock Mode: {use_mock}")
                
                # Use st.status for visible progress
                with st.status("🔄 Running Standard Debate...", expanded=True) as status:
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    
                    try:
                        if use_mock:
                            logger.info("Using mock mode for standard debate")
                            progress_text.write("🔄 Running in Mock Mode...")
                            progress_bar.progress(0.5)
                            
                            st.session_state.standard_result = mock_debate(current_question, num_rounds)
                            
                            # Save to history
                            try:
                                html_file, timestamp = save_debate_history(
                                    st.session_state.standard_result, 
                                    "standard"
                                )
                                logger.info(f"Saved mock standard debate to history: {html_file}")
                            except Exception as e:
                                logger.error(f"Error saving history: {e}")
                            
                            progress_bar.progress(1.0)
                            progress_text.write("✅ Mock debate completed!")
                            status.update(label="✅ Mock Debate Completed!", state="complete", expanded=False)
                        else:
                            logger.info("Running real standard debate")
                            
                            # Initialize agents
                            progress_bar.progress(0.05)
                            progress_text.write("📝 Initializing agents...")
                            
                            from agents import DebateAgent

                            if olympiad_mode:
                                agent_a = DebateAgent("Agent A", "Math Expert", "olympiad" , mock_mode=False)
                                agent_b = DebateAgent("Agent B", "Math Expert", "olympiad" , mock_mode=False)
                                progress_text.write("✅ Olympiad mode is on!")
                            
                            else:
                                agent_a = DebateAgent("Agent A", "Math Expert", mock_mode=False)
                                agent_b = DebateAgent("Agent B", "Math Expert", mock_mode=False)
                            
                            progress_bar.progress(0.15)
                            progress_text.write("✅ Agents initialized")
                            
                            # Round 0: Initial answers
                            progress_bar.progress(0.20)
                            progress_text.write("📝 Generating initial answers...")
                            
                            import time
                            call_start = time.time()
                            agent_a_answer = agent_a.generate_initial_answer(current_question)
                            call_elapsed = time.time() - call_start
                            
                            if agent_a_answer.startswith("[ERROR]") or agent_a_answer.startswith("[TIMEOUT]"):
                                raise Exception(f"Agent A API call failed: {agent_a_answer}")
                            
                            progress_bar.progress(0.40)
                            agent_a_preview = agent_a_answer[:300] + "..." if len(agent_a_answer) > 300 else agent_a_answer
                            progress_text.markdown(f"""
✓ **Agent A Complete** ({call_elapsed:.1f}s)

**Agent A's Answer:**
{agent_a_preview}

**Next:** Generating Agent B's answer...
""")
                            
                            call_start = time.time()
                            agent_b_answer = agent_b.generate_initial_answer(current_question)
                            call_elapsed = time.time() - call_start
                            
                            if agent_b_answer.startswith("[ERROR]") or agent_b_answer.startswith("[TIMEOUT]"):
                                raise Exception(f"Agent B API call failed: {agent_b_answer}")
                            
                            progress_bar.progress(0.60)
                            agent_b_preview = agent_b_answer[:300] + "..." if len(agent_b_answer) > 300 else agent_b_answer
                            agent_b_preview_escaped = escape_latex_for_display(agent_b_preview)
                            progress_text.markdown(f"""
✓ **Agent B Complete** ({call_elapsed:.1f}s)

**Agent B's Answer:**
<pre style="white-space: pre-wrap; font-family: inherit;">{agent_b_preview_escaped}</pre>

**Round 0 Summary:** Both agents have provided initial answers. Starting critique rounds...
""", unsafe_allow_html=True)
                            
                            debate_log = [{
                                "round": 0,
                                "type": "initial",
                                "agent_a": agent_a_answer,
                                "agent_b": agent_b_answer
                            }]
                            
                            # Subsequent rounds
                            total_steps = 4 + num_rounds * 2
                            current_step = 4
                            
                            for round_num in range(1, num_rounds + 1):
                                progress_value = calculate_progress(current_step, total_steps, min_progress=0.2, max_progress=0.95)
                                progress_bar.progress(progress_value)
                                progress_text.markdown(f"""
📝 **Round {round_num} - Peer Critique Phase**

**What's happening:**
- Agent A is reviewing Agent B's solution
- Agent A is checking for errors, logical flaws, or calculation mistakes
- Agent A will provide critique and potentially revise its own answer

**Status:** Agent A analyzing Agent B's answer...
""")
                                current_step += 1
                                
                                agent_a_critique = agent_a.critique_peer(
                                    current_question,
                                    agent_b.get_final_answer(),
                                    round_num
                                )
                                
                                progress_value = calculate_progress(current_step, total_steps, min_progress=0.2, max_progress=0.95)
                                progress_bar.progress(progress_value)
                                agent_a_preview = agent_a_critique[:300] + "..." if len(agent_a_critique) > 300 else agent_a_critique
                                agent_a_preview_escaped = escape_latex_for_display(agent_a_preview)
                                progress_text.markdown(f"""
✓ **Round {round_num} - Agent A Critique Complete**

**Agent A's Critique & Revision:**
<pre style="white-space: pre-wrap; font-family: inherit;">{agent_a_preview_escaped}</pre>

**Next:** Agent B is now reviewing Agent A's solution...
""", unsafe_allow_html=True)
                                current_step += 1
                                
                                agent_b_critique = agent_b.critique_peer(
                                    current_question,
                                    agent_a.get_final_answer(),
                                    round_num
                                )
                                
                                progress_value = calculate_progress(current_step, total_steps, min_progress=0.2, max_progress=0.95)
                                progress_bar.progress(progress_value)
                                agent_b_preview = agent_b_critique[:300] + "..." if len(agent_b_critique) > 300 else agent_b_critique
                                agent_b_preview_escaped = escape_latex_for_display(agent_b_preview)
                                progress_text.markdown(f"""
✓ **Round {round_num} - Both Agents Complete**

**Agent B's Critique & Revision:**
<pre style="white-space: pre-wrap; font-family: inherit;">{agent_b_preview_escaped}</pre>

**Round {round_num} Summary:** Both agents have critiqued each other and revised their answers.
""", unsafe_allow_html=True)
                                current_step += 1
                                
                                debate_log.append({
                                    "round": round_num,
                                    "type": "critique",
                                    "agent_a": agent_a_critique,
                                    "agent_b": agent_b_critique
                                })
                            
                            # Finalize
                            progress_bar.progress(0.95)
                            progress_text.write("📝 Finalizing results...")
                            
                            st.session_state.standard_result = {
                                "question": current_question,
                                "method": "standard",
                                "rounds": num_rounds,
                                "log": debate_log,
                                "final_agent_a": agent_a.get_final_answer(),
                                "final_agent_b": agent_b.get_final_answer(),
                                "agent_a_history": agent_a.history,
                                "agent_b_history": agent_b.history
                            }
                            
                            # Save to history
                            try:
                                html_file, timestamp = save_debate_history(
                                    st.session_state.standard_result, 
                                    "standard"
                                )
                                logger.info(f"Saved standard debate to history: {html_file}")
                            except Exception as e:
                                logger.error(f"Error saving history: {e}")
                            
                            progress_bar.progress(1.0)
                            progress_text.write("✅ Standard Debate completed!")
                            status.update(label="✅ Standard Debate Completed!", state="complete", expanded=False)
                            logger.info("Standard debate completed successfully")
                            
                    except Exception as e:
                        logger.error(f"Error in standard debate: {str(e)}", exc_info=True)
                        progress_text.write(f"❌ Error: {str(e)}")
                        status.update(label="❌ Error occurred", state="error", expanded=True)
                        st.error(f"Error: {str(e)}")
                        st.info("Try enabling Mock Mode if the model is not loaded.")
        
        if st.session_state.standard_result:
            st.markdown(f"**Question:** {st.session_state.standard_result['question']}")
            st.markdown("---")
            display_chat_messages(st.session_state.standard_result['log'], show_judge=False)
            
            st.markdown("---")
            st.subheader("Final Answers")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Agent A:**")
                formatted_text = fix_latex_rendering(st.session_state.standard_result['final_agent_a'])
                st.markdown(formatted_text)
            with col2:
                st.write("**Agent B:**")
                formatted_text = fix_latex_rendering(st.session_state.standard_result['final_agent_b'])
                st.markdown(formatted_text)
        else:
            st.info("Click 'Start Standard Debate' to begin.")
    
    # Tab 2: Mediated Debate
    with tab2:
        st.header("⚖️ Mediated Debate (With Judge)")
        st.markdown("*Judge evaluates both agents and provides critical feedback*")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            start_mediated_debate = st.button("⚖️ Start Mediated Debate", use_container_width=True)
        
        if start_mediated_debate:
            if not current_question:
                logger.warning("Mediated debate attempted without question")
                st.error("Please select or enter a problem first!")
            else:
                logger.info("Starting mediated debate from UI")
                logger.info(f"Question: {current_question[:100]}...")
                logger.info(f"Rounds: {num_rounds}, Mock Mode: {use_mock}")
                
                # Initialize all progress state variables FIRST, before any other code
                try:
                    st.session_state.debate_in_progress = True
                    st.session_state.progress_message = "Initializing..."
                    st.session_state.progress_percent = 0
                    st.session_state.progress_detail = "Starting mediated debate..."
                except Exception as init_error:
                    logger.error(f"Error initializing session state: {init_error}")
                    # Fallback initialization
                    if 'progress_percent' not in st.session_state:
                        st.session_state['progress_percent'] = 0
                    if 'progress_message' not in st.session_state:
                        st.session_state['progress_message'] = "Initializing..."
                    if 'progress_detail' not in st.session_state:
                        st.session_state['progress_detail'] = "Starting..."
                    if 'debate_in_progress' not in st.session_state:
                        st.session_state['debate_in_progress'] = True
                
                # Use st.status for visible progress
                with st.status("🔄 Running Mediated Debate...", expanded=True) as status:
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    
                    try:
                        if use_mock:
                            logger.info("Using mock mode for mediated debate")
                            progress_text.write("🔄 Running in Mock Mode...")
                            st.session_state.progress_message = "🔄 Running in Mock Mode..."
                            progress_bar.progress(0.10)
                            st.session_state.progress_percent = 10
                            
                            import time
                            time.sleep(0.5)
                            progress_bar.progress(0.50)
                            st.session_state.progress_percent = 50
                            progress_text.write("Generating mock responses...")
                            st.session_state.progress_detail = "Generating mock responses..."
                            
                            st.session_state.mediated_result = mock_debate(current_question, num_rounds)
                            
                            # Save to history
                            try:
                                html_file, timestamp = save_debate_history(
                                    st.session_state.mediated_result, 
                                    "mediated"
                                )
                                logger.info(f"Saved mock mediated debate to history: {html_file}")
                            except Exception as e:
                                logger.error(f"Error saving history: {e}")
                            
                            progress_bar.progress(1.0)
                            st.session_state.progress_percent = 100
                            progress_text.write("✅ Mock debate completed!")
                            st.session_state.progress_detail = "✅ Mock debate completed!"
                            st.session_state.progress_message = "✅ Mock Debate Completed!"
                            status.update(label="✅ Mock Debate Completed!", state="complete", expanded=False)
                            time.sleep(0.5)
                            st.session_state.debate_in_progress = False
                        else:
                            logger.info("Running real mediated debate")
                            st.session_state.progress_message = "🔄 Running Mediated Debate..."
                            
                            # Show timing estimate
                            estimated_time = (3 + num_rounds * 3) * 15  # ~15s per LLM call (judge + 2 agents per round)
                            st.info(f"⏱️ **Estimated time:** ~{estimated_time//60}min {estimated_time%60}s ({(3 + num_rounds * 3)} LLM calls × ~15s each)")
                            
                            # Initialize agents and judge
                            progress_bar.progress(0.05)
                            st.session_state.progress_percent = 5
                            progress_text.write("📝 Initializing agents and judge...")
                            st.session_state.progress_detail = "Step 1/5: Initializing Agent A, Agent B, and Judge..."
                            from agents import DebateAgent, JudgeAgent
                            if olympiad_mode:
                                agent_a = DebateAgent("Agent A", "Math Expert", "olympiad" , mock_mode=False)
                                agent_b = DebateAgent("Agent B", "Math Expert", "olympiad" , mock_mode=False)
                                judge = JudgeAgent("olympiad", mock_mode=False)
                                progress_text.write("✅ Olympiad mode is on!")
                            
                            else:
                                agent_a = DebateAgent("Agent A", "Math Expert", mock_mode=False)
                                agent_b = DebateAgent("Agent B", "Math Expert", mock_mode=False)
                                judge = JudgeAgent(mock_mode=False)
                            
                            progress_bar.progress(0.15)
                            st.session_state.progress_percent = 15
                            progress_text.write("✅ Agents and Judge initialized")
                            st.session_state.progress_detail = "✅ Agents and Judge initialized"
                            
                            # Round 0: Initial answers
                            progress_bar.progress(0.20)
                            st.session_state.progress_percent = 20
                            progress_text.write("📝 Generating initial answers...")
                            st.session_state.progress_detail = "Generating initial answers..."
                            
                            import time
                            call_start = time.time()
                            agent_a_answer = agent_a.generate_initial_answer(current_question)
                            call_elapsed = time.time() - call_start
                            
                            if agent_a_answer.startswith("[ERROR]") or agent_a_answer.startswith("[TIMEOUT]"):
                                raise Exception(f"Agent A API call failed: {agent_a_answer}")
                            
                            progress_bar.progress(0.35)
                            st.session_state.progress_percent = 35
                            agent_a_preview = agent_a_answer[:300] + "..." if len(agent_a_answer) > 300 else agent_a_answer
                            agent_a_preview_escaped = escape_latex_for_display(agent_a_preview)
                            progress_text.markdown(f"""
✓ **Agent A Complete** ({call_elapsed:.1f}s)

**Agent A's Answer:**
<pre style="white-space: pre-wrap; font-family: inherit;">{agent_a_preview_escaped}</pre>

**Next:** Generating Agent B's answer...
""", unsafe_allow_html=True)
                            st.session_state.progress_detail = f"✓ Agent A done ({call_elapsed:.1f}s)"
                            
                            call_start = time.time()
                            agent_b_answer = agent_b.generate_initial_answer(current_question)
                            call_elapsed = time.time() - call_start
                            
                            if agent_b_answer.startswith("[ERROR]") or agent_b_answer.startswith("[TIMEOUT]"):
                                raise Exception(f"Agent B API call failed: {agent_b_answer}")
                            
                            progress_bar.progress(0.50)
                            st.session_state.progress_percent = 50
                            agent_b_preview = agent_b_answer[:300] + "..." if len(agent_b_answer) > 300 else agent_b_answer
                            agent_b_preview_escaped = escape_latex_for_display(agent_b_preview)
                            progress_text.markdown(f"""
✓ **Agent B Complete** ({call_elapsed:.1f}s)

**Agent B's Answer:**
<pre style="white-space: pre-wrap; font-family: inherit;">{agent_b_preview_escaped}</pre>

**Round 0 Summary:** Both agents have provided initial answers. Starting judge evaluation...
""", unsafe_allow_html=True)
                            st.session_state.progress_detail = f"✓ Agent B done ({call_elapsed:.1f}s)"
                            
                            debate_log = [{
                                "round": 0,
                                "type": "initial",
                                "agent_a": agent_a_answer,
                                "agent_b": agent_b_answer,
                                "judge_feedback": None
                            }]
                            
                            # Subsequent rounds with judge
                            total_steps = 5 + num_rounds * 3
                            current_step = 5
                            
                            for round_num in range(1, num_rounds + 1):
                                # Judge evaluation
                                progress_value = calculate_progress(current_step, total_steps, min_progress=0.2, max_progress=0.95)
                                progress_bar.progress(progress_value)
                                try:
                                    st.session_state.progress_percent = int(progress_value * 100)
                                except Exception:
                                    st.session_state.progress_percent = 0
                                progress_text.markdown(f"""
📝 **Round {round_num} - Judge Evaluation Phase**

**What's happening:**
- Judge is reading Agent A's current answer
- Judge is reading Agent B's current answer
- Judge is analyzing both solutions for errors, logical flaws, or inconsistencies
- Judge will provide critical feedback (not peer agreement)

**Status:** Judge analyzing both answers...
""")
                                st.session_state.progress_detail = f"Round {round_num}: Judge evaluating both answers..."
                                current_step += 1
                                
                                judge_feedback = judge.critique(
                                    current_question,
                                    agent_a.get_final_answer(),
                                    agent_b.get_final_answer(),
                                    round_num
                                )
                                
                                progress_value = calculate_progress(current_step, total_steps, min_progress=0.2, max_progress=0.95)
                                progress_bar.progress(progress_value)
                                try:
                                    st.session_state.progress_percent = int(progress_value * 100)
                                except Exception:
                                    st.session_state.progress_percent = 0
                                # Show judge feedback
                                judge_preview = judge_feedback[:400] + "..." if len(judge_feedback) > 400 else judge_feedback
                                judge_preview = judge_feedback[:300] + "..." if len(judge_feedback) > 300 else judge_feedback
                                judge_preview_escaped = escape_latex_for_display(judge_preview)
                                progress_text.markdown(f"""
✓ **Round {round_num} - Judge Evaluation Complete**

**Judge's Feedback:**
<pre style="white-space: pre-wrap; font-family: inherit;">{judge_preview_escaped}</pre>

**Next:** Agent A is now revising based on judge feedback...
""", unsafe_allow_html=True)
                                st.session_state.progress_detail = f"Round {round_num}: ✓ Judge feedback received"
                                current_step += 1
                                
                                # Agent A revision
                                progress_text.markdown(f"""
📝 **Round {round_num} - Agent A Revision**

**What's happening:**
- Agent A is reading the judge's feedback
- Agent A is analyzing the judge's critique
- Agent A is revising its answer based on judge feedback
- **Key:** Agent A does NOT see Agent B's answer directly (only judge feedback)

**Status:** Agent A revising...
""")
                                st.session_state.progress_detail = f"Round {round_num}: Agent A revising based on judge feedback..."
                                current_step += 1
                                
                                agent_a_revision = agent_a.revise_from_judge_feedback(
                                    current_question,
                                    judge_feedback,
                                    round_num
                                )
                                
                                progress_value = calculate_progress(current_step, total_steps, min_progress=0.2, max_progress=0.95)
                                progress_bar.progress(progress_value)
                                try:
                                    st.session_state.progress_percent = int(progress_value * 100)
                                except Exception:
                                    st.session_state.progress_percent = 0
                                # Show Agent A's revision
                                agent_a_preview = agent_a_revision[:400] + "..." if len(agent_a_revision) > 400 else agent_a_revision
                                agent_a_preview = agent_a_revision[:300] + "..." if len(agent_a_revision) > 300 else agent_a_revision
                                agent_a_preview_escaped = escape_latex_for_display(agent_a_preview)
                                progress_text.markdown(f"""
✓ **Round {round_num} - Agent A Revision Complete**

**Agent A's Revision:**
<pre style="white-space: pre-wrap; font-family: inherit;">{agent_a_preview_escaped}</pre>

**Next:** Agent B is now revising based on judge feedback...
""", unsafe_allow_html=True)
                                st.session_state.progress_detail = f"Round {round_num}: ✓ Agent A revision completed"
                                current_step += 1
                                
                                # Agent B revision
                                progress_text.markdown(f"""
📝 **Round {round_num} - Agent B Revision**

**What's happening:**
- Agent B is reading the judge's feedback
- Agent B is analyzing the judge's critique
- Agent B is revising its answer based on judge feedback
- **Key:** Agent B does NOT see Agent A's answer directly (only judge feedback)

**Status:** Agent B revising...
""")
                                st.session_state.progress_detail = f"Round {round_num}: Agent B revising based on judge feedback..."
                                current_step += 1
                                
                                agent_b_revision = agent_b.revise_from_judge_feedback(
                                    current_question,
                                    judge_feedback,
                                    round_num
                                )
                                
                                progress_value = calculate_progress(current_step, total_steps, min_progress=0.2, max_progress=0.95)
                                progress_bar.progress(progress_value)
                                try:
                                    st.session_state.progress_percent = int(progress_value * 100)
                                except Exception:
                                    st.session_state.progress_percent = 0
                                # Show Agent B's revision
                                agent_b_preview = agent_b_revision[:400] + "..." if len(agent_b_revision) > 400 else agent_b_revision
                                agent_b_preview = agent_b_revision[:300] + "..." if len(agent_b_revision) > 300 else agent_b_revision
                                agent_b_preview_escaped = escape_latex_for_display(agent_b_preview)
                                progress_text.markdown(f"""
✓ **Round {round_num} - Agent B Revision Complete**

**Agent B's Revision:**
<pre style="white-space: pre-wrap; font-family: inherit;">{agent_b_preview_escaped}</pre>

**Round {round_num} Summary:** Judge evaluated both answers. Both agents revised based on judge feedback.
""", unsafe_allow_html=True)
                                st.session_state.progress_detail = f"Round {round_num}: ✓ Agent B revision completed"
                                current_step += 1
                                
                                debate_log.append({
                                    "round": round_num,
                                    "type": "revision",
                                    "agent_a": agent_a_revision,
                                    "agent_b": agent_b_revision,
                                    "judge_feedback": judge_feedback
                                })
                            
                            # Finalize
                            progress_bar.progress(0.95)
                            st.session_state.progress_percent = 95
                            progress_text.write("📝 Finalizing results...")
                            st.session_state.progress_detail = "Finalizing results..."
                            
                            st.session_state.mediated_result = {
                                "question": current_question,
                                "method": "mediated",
                                "rounds": num_rounds,
                                "log": debate_log,
                                "final_agent_a": agent_a.get_final_answer(),
                                "final_agent_b": agent_b.get_final_answer(),
                                "judge_history": judge.history,
                                "agent_a_history": agent_a.history,
                                "agent_b_history": agent_b.history
                            }
                            
                            # Save to history
                            try:
                                html_file, timestamp = save_debate_history(
                                    st.session_state.mediated_result, 
                                    "mediated"
                                )
                                logger.info(f"Saved mediated debate to history: {html_file}")
                            except Exception as e:
                                logger.error(f"Error saving history: {e}")
                            
                            progress_bar.progress(1.0)
                            st.session_state.progress_percent = 100
                            progress_text.write("✅ Mediated Debate completed!")
                            st.session_state.progress_message = "✅ Mediated Debate Completed!"
                            st.session_state.progress_detail = "✅ All rounds completed successfully!"
                            status.update(label="✅ Mediated Debate Completed!", state="complete", expanded=False)
                            
                            logger.info("Mediated debate completed successfully")
                            import time
                            time.sleep(1)
                            st.session_state.debate_in_progress = False
                            st.rerun()
                    except Exception as e:
                        logger.error(f"Error in mediated debate: {str(e)}", exc_info=True)
                        progress_text.write(f"❌ Error: {str(e)}")
                        st.session_state.progress_message = "❌ Error occurred"
                        st.session_state.progress_detail = f"Error: {str(e)[:100]}"
                        status.update(label="❌ Error occurred", state="error", expanded=True)
                        st.session_state.debate_in_progress = False
                        st.error(f"Error: {str(e)}")
                        st.info("Try enabling Mock Mode if the model is not loaded.")
        
        if st.session_state.mediated_result:
            st.markdown(f"**Question:** {st.session_state.mediated_result['question']}")
            st.markdown("---")
            display_chat_messages(st.session_state.mediated_result['log'], show_judge=True)
            
            st.markdown("---")
            st.subheader("Final Answers")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Agent A:**")
                formatted_text = fix_latex_rendering(st.session_state.mediated_result['final_agent_a'])
                st.markdown(formatted_text)
            with col2:
                st.write("**Agent B:**")
                formatted_text = fix_latex_rendering(st.session_state.mediated_result['final_agent_b'])
                st.markdown(formatted_text)
        else:
            st.info("Click 'Start Mediated Debate' to begin.")
    
    # Tab 3: Paper Details & Solution
    with tab3:
        st.header("📄 Paper Details & Solution")
        
        # Paper Information
        st.subheader("📚 Research Paper")
        st.markdown("""
        **Title:** Breaking the Echo Chamber: Enhancing Multi-Agent Debate Consistency via Arbitrator Models
        
        **Baseline Paper:** Du et al. (2023) - "Improving Factuality and Reasoning in Language Models through Multiagent Debate"
        
        **Course:** COSC3009 - Advanced Intelligent Decision Making  
        **Institution:** RMIT University
        """)
        
        st.markdown("---")
        
        # Problem Statement
        st.subheader("🔍 The Problem: Sycophancy in Multi-Agent Systems")
        
        st.markdown("""
        **Sycophancy** (also called "Disagreement Collapse") is a critical flaw in peer-to-peer debate architectures:
        
        - Agents often **blindly agree** with each other's incorrect answers to maintain social harmony
        - This leads to **false consensus** on wrong solutions
        - The problem is documented in recent research (Hu et al., 2025 - "Peacemaker or Troublemaker")
        
        **Example of the Problem:**
        - Agent A: "I think 2+2=5" (incorrect, but confident)
        - Agent B: "You're right! I agree it's 5" (sycophancy - abandons correct answer of 4)
        - Result: System converges to **wrong answer** despite Agent B initially knowing the correct answer
        """)
        
        with st.expander("📊 Mathematical Definition"):
            st.markdown("""
            Sycophancy occurs when:
            
            Sycophancy(A_i, t) = 1 if:
            - Correct(A_i, t-1) = True (agent was correct in previous round)
            - Correct(A_i, t) = False (agent is now incorrect)
            - Agree(A_i, A_j, t) = True (agent agrees with peer)
            
            Otherwise, Sycophancy(A_i, t) = 0.
            
            Where an agent that was **initially correct** becomes **incorrect** after agreeing with a peer's wrong answer.
            """)
        
        st.markdown("---")
        
        # Solution
        st.subheader("💡 Our Solution: Mediated Debate with Judge")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Baseline (Standard Debate):**
            - **Topology:** Peer-to-Peer (Mesh Network)
            - **Flow:** Agent A ↔ Agent B
            - **Problem:** Agents directly critique each other
            - **Flaw:** Agent B often says "I agree with A" even if A is wrong
            """)
        
        with col2:
            st.markdown("""
            **Improved (Mediated Debate):**
            - **Topology:** Star Network (Centralized Judge)
            - **Flow:** Agent A + Agent B → Judge → Feedback
            - **Process:** Judge evaluates both answers independently
            - **Benefit:** Breaks the echo chamber, forces error correction
            """)
        
        st.markdown("---")
        
        # How It Works
        st.subheader("⚙️ How Mediated Debate Works")
        
        st.markdown("""
        **Step-by-Step Process:**
        
        1. **Initial Answers:** Agents A and B generate independent solutions
        2. **Judge Evaluation:** Judge (Agent C) reads both answers and provides critical feedback
        3. **Error Identification:** Judge points out specific errors or validates correctness
        4. **Agent Revision:** Agents receive judge's feedback (not peer's raw text) and revise
        5. **Iteration:** Process repeats for multiple rounds
        
        **Key Innovation:** Agents don't see each other's answers directly. They only see the judge's evaluation, which breaks the social pressure loop.
        """)
        
        with st.expander("🔬 Technical Details"):
            st.markdown("""
            **Update Rules:**
            
            **Standard Debate:**
            R(i, t+1) = LLM_i(q, R(i, t), Critique(R(j, t)))
            
            Each agent receives critiques from peers and updates their response.
            
            **Mediated Debate:**
            R(i, t+1) = LLM_i(q, R(i, t), Judge(R(1, t), ..., R(n, t)))
            
            Each agent receives the judge's evaluation of all responses, not direct peer critiques.
            
            The judge function operates with a different objective:
            Judge(...) = argmax_f [ LogicalCorrectness(f) - lambda * PrematureAgreement(f) ]
            
            Where lambda > 0 penalizes premature agreement, encouraging the judge to identify errors even when agents agree.
            
            This prioritizes **truth-seeking** over **consensus-seeking**.
            """)
        
        st.markdown("---")
        
        # Results
        st.subheader("📈 Expected Results")
        
        st.markdown("""
        Based on our hypothesis and implementation:
        
        | Metric | Standard Debate | Mediated Debate | Improvement |
        |--------|----------------|-----------------|-------------|
        | **Accuracy** | ~78% | ~88% | +10.5% |
        | **Sycophancy Rate** | ~35% | ~12% | -65% |
        | **Consensus Quality** | ~64% | ~90% | +40% |
        
        **Key Finding:** Mediated debate achieves higher accuracy by preventing correct agents from switching to incorrect solutions.
        """)
        
        st.markdown("---")
        
        # Implementation
        st.subheader("🛠️ Implementation Details")
        
        st.markdown("""
        **Technology Stack:**
        - **LLM:** DeepSeek-R1:1.5b (Reasoning model with Chain-of-Thought)
        - **Infrastructure:** Docker + Ollama (100% local, no cloud)
        - **Framework:** Streamlit for UI
        - **Why DeepSeek-R1?** Explicit reasoning makes it superior as a judge compared to standard chat models
        
        **Judge Prompt Engineering:**
        - **Permissive of conflict:** Allows disagreement when solutions differ
        - **Strict on logic:** Rejects incorrect solutions regardless of confidence
        - **Actionable feedback:** Provides specific error locations and corrections
        """)
        
        with st.expander("🔐 Why Local-First?"):
            st.markdown("""
            - **Reproducibility:** Exact same environment across machines
            - **Privacy:** No data leaves your machine
            - **Zero Cost:** No API charges per token
            - **Data Sovereignty:** Complete control over model behavior
            """)
        
        st.markdown("---")
        
        # References
        st.subheader("📚 References")
        
        st.markdown("""
        1. **Du, Y., et al. (2023).** "Improving Factuality and Reasoning in Language Models through Multiagent Debate." *arXiv preprint arXiv:2305.14325*.
        
        2. **Hu, X., et al. (2025).** "Peacemaker or Troublemaker: The Role of Agreement in Multi-Agent Debate Systems." *Proceedings of the International Conference on Machine Learning*.
        
        3. **Kahneman, D. (2011).** *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
        """)
        
        st.markdown("---")
        
        # Key Takeaways
        st.subheader("🎯 Key Takeaways")
        
        st.markdown("""
        - **Problem:** Peer-to-peer debates suffer from sycophancy (false consensus)
        - **Solution:** Centralized judge arbitrator breaks the echo chamber
        - **Result:** Higher accuracy, lower sycophancy, better consensus quality
        - **Impact:** Essential for enterprise MAS where truthfulness > politeness
        """)
    
    # Tab 4: Standard Debate History
    with tab4:
        st.header("📜 Standard Debate History")
        st.markdown("View past Standard Debate results")
        
        history_list = get_history_list("standard")
        
        if not history_list:
            st.info("No debate history yet. Run a Standard Debate to create history entries.")
        else:
            st.markdown(f"**Total debates:** {len(history_list)}")
            st.markdown("---")
            
            for idx, entry in enumerate(history_list[:20]):  # Show last 20
                with st.expander(f"📝 {entry['timestamp'].replace('_', ' ')} - {entry['question'][:80]}..."):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Question:** {entry['question']}")
                    with col2:
                        html_path = STANDARD_HISTORY_DIR / entry['html_file']
                        if html_path.exists():
                            with open(html_path, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                                st.download_button(
                                    "📥 Download HTML",
                                    html_content,
                                    file_name=entry['html_file'],
                                    mime="text/html",
                                    key=f"std_dl_{idx}"
                                )
                    
                    # Load and display full result
                    json_path = STANDARD_HISTORY_DIR / entry['json_file']
                    if json_path.exists():
                        with open(json_path, 'r') as f:
                            result = json.load(f)
                            st.markdown("---")
                            display_chat_messages(result.get('log', []), show_judge=False)
                            
                            st.markdown("---")
                            st.subheader("Final Answers")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Agent A:**")
                                formatted_text = fix_latex_rendering(result.get('final_agent_a', 'N/A'))
                                st.markdown(formatted_text)
                            with col2:
                                st.write("**Agent B:**")
                                formatted_text = fix_latex_rendering(result.get('final_agent_b', 'N/A'))
                                st.markdown(formatted_text)
    
    # Tab 5: Mediated Debate History
    with tab5:
        st.header("📜 Mediated Debate History")
        st.markdown("View past Mediated Debate results")
        
        history_list = get_history_list("mediated")
        
        if not history_list:
            st.info("No debate history yet. Run a Mediated Debate to create history entries.")
        else:
            st.markdown(f"**Total debates:** {len(history_list)}")
            st.markdown("---")
            
            for idx, entry in enumerate(history_list[:20]):  # Show last 20
                with st.expander(f"📝 {entry['timestamp'].replace('_', ' ')} - {entry['question'][:80]}..."):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Question:** {entry['question']}")
                    with col2:
                        html_path = MEDIATED_HISTORY_DIR / entry['html_file']
                        if html_path.exists():
                            with open(html_path, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                                st.download_button(
                                    "📥 Download HTML",
                                    html_content,
                                    file_name=entry['html_file'],
                                    mime="text/html",
                                    key=f"med_dl_{idx}"
                                )
                    
                    # Load and display full result
                    json_path = MEDIATED_HISTORY_DIR / entry['json_file']
                    if json_path.exists():
                        with open(json_path, 'r') as f:
                            result = json.load(f)
                            st.markdown("---")
                            display_chat_messages(result.get('log', []), show_judge=True)
                            
                            st.markdown("---")
                            st.subheader("Final Answers")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Agent A:**")
                                formatted_text = fix_latex_rendering(result.get('final_agent_a', 'N/A'))
                                st.markdown(formatted_text)
                            with col2:
                                st.write("**Agent B:**")
                                formatted_text = fix_latex_rendering(result.get('final_agent_b', 'N/A'))
                                st.markdown(formatted_text)
    
    # Footer with Progress Panel (always visible at bottom)
    st.markdown("---")
    
    # Progress Panel in Footer (always visible during execution)
    footer_progress_placeholder = st.empty()
    
    if 'debate_in_progress' in st.session_state and st.session_state.debate_in_progress:
        with footer_progress_placeholder.container():
            st.markdown("### 🔄 Live Debate Progress (Footer)")
            st.markdown("---")
            col1, col2 = st.columns([4, 1])
            with col1:
                if 'progress_message' in st.session_state:
                    st.info(f"**Status:** {st.session_state.progress_message}")
                if 'progress_percent' in st.session_state:
                    try:
                        progress_val = st.session_state.progress_percent
                        if isinstance(progress_val, (int, float)):
                            st.progress(progress_val / 100 if progress_val > 1 else progress_val)
                            st.caption(f"Progress: {progress_val}%")
                    except (KeyError, AttributeError, TypeError) as e:
                        logger.warning(f"Error displaying progress: {e}")
                        pass
                if 'progress_detail' in st.session_state:
                    st.markdown(f"**Current Step:** {st.session_state.progress_detail}")
            with col2:
                if st.button("❌ Cancel", key="cancel_debate", use_container_width=True):
                    st.session_state.debate_in_progress = False
                    st.session_state.progress_message = "Cancelled by user"
                    st.rerun()
            st.markdown("---")
    else:
        # Clear the footer progress when not in progress
        footer_progress_placeholder.empty()
    
    st.markdown("**Local Multi-Agent Debate System** | 100% Open Source | No Cloud Dependencies")


if __name__ == "__main__":
    main()
