"""
Multi-Agent Debate System - Simulation Logic
100% LOCAL ONLY - Uses local Ollama models with robust error handling.
"""

import logging
from typing import Dict
from datetime import datetime
from agents import DebateAgent, JudgeAgent

# Configure logging
logger = logging.getLogger(__name__)


def run_standard_debate(topic: str, rounds: int = 3, mock_mode: bool = False) -> Dict:
    """
    Run a standard peer-to-peer debate between two agents.
    Simulates the peer-to-peer sycophancy problem.
    
    Args:
        topic: The mathematical problem to solve
        rounds: Number of debate rounds
        mock_mode: If True, use mock responses (for testing without model)
        
    Returns:
        Dictionary containing debate history and results (never crashes)
    """
    logger.info("=" * 80)
    logger.info("STARTING STANDARD DEBATE")
    logger.info(f"Topic: {topic[:100]}...")
    logger.info(f"Rounds: {rounds}, Mock Mode: {mock_mode}")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        logger.info("Initializing agents...")
        agent_a = DebateAgent("Agent A", "Math Expert", mock_mode=mock_mode)
        agent_b = DebateAgent("Agent B", "Math Expert", mock_mode=mock_mode)
        logger.info("Agents initialized successfully")
        
        debate_log = []
        
        # Round 0: Initial answers
        logger.info("Round 0: Generating initial answers...")
        round_start = datetime.now()
        try:
            agent_a_answer = agent_a.generate_initial_answer(topic)
        except Exception as e:
            logger.error(f"Error generating Agent A initial answer: {e}", exc_info=True)
            agent_a_answer = "[SIMULATION] Agent A initial answer: After analysis, I believe the answer is 42."
        
        try:
            agent_b_answer = agent_b.generate_initial_answer(topic)
        except Exception as e:
            logger.error(f"Error generating Agent B initial answer: {e}", exc_info=True)
            agent_b_answer = "[SIMULATION] Agent B initial answer: I've calculated and my answer is 42."
        
        round_elapsed = (datetime.now() - round_start).total_seconds()
        logger.info(f"Round 0 completed in {round_elapsed:.2f}s")
        
        debate_log.append({
            "round": 0,
            "type": "initial",
            "agent_a": agent_a_answer,
            "agent_b": agent_b_answer
        })
        
        # Subsequent rounds: Agents critique each other (peer-to-peer sycophancy)
        for round_num in range(1, rounds + 1):
            logger.info(f"Round {round_num}: Starting peer critique...")
            round_start = datetime.now()
            
            # Agent A critiques Agent B's last answer
            try:
                logger.debug(f"Round {round_num}: Agent A critiquing Agent B...")
                agent_a_critique = agent_a.critique_peer(
                    topic, 
                    agent_b.get_final_answer(), 
                    round_num
                )
            except Exception as e:
                logger.error(f"Error in Agent A critique: {e}", exc_info=True)
                agent_a_critique = "[SIMULATION] Agent A critique: I see your point, and I agree with your approach."
            
            # Agent B critiques Agent A's last answer
            try:
                logger.debug(f"Round {round_num}: Agent B critiquing Agent A...")
                agent_b_critique = agent_b.critique_peer(
                    topic, 
                    agent_a.get_final_answer(), 
                    round_num
                )
            except Exception as e:
                logger.error(f"Error in Agent B critique: {e}", exc_info=True)
                agent_b_critique = "[SIMULATION] Agent B critique: You're right! I agree with your solution."
            
            round_elapsed = (datetime.now() - round_start).total_seconds()
            logger.info(f"Round {round_num} completed in {round_elapsed:.2f}s")
            
            debate_log.append({
                "round": round_num,
                "type": "critique",
                "agent_a": agent_a_critique,
                "agent_b": agent_b_critique
            })
        
        total_elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 80)
        logger.info(f"STANDARD DEBATE COMPLETED in {total_elapsed:.2f}s")
        logger.info("=" * 80)
        
        result = {
            "question": topic,
            "method": "standard",
            "rounds": rounds,
            "log": debate_log,
            "final_agent_a": agent_a.get_final_answer(),
            "final_agent_b": agent_b.get_final_answer(),
            "agent_a_history": agent_a.history,
            "agent_b_history": agent_b.history
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Critical error in run_standard_debate: {str(e)}", exc_info=True)
        # Return a safe fallback result instead of crashing
        return {
            "question": topic,
            "method": "standard",
            "rounds": rounds,
            "log": [{
                "round": 0,
                "type": "initial",
                "agent_a": "[SIMULATION] Standard debate encountered an error. Using fallback mode.",
                "agent_b": "[SIMULATION] Standard debate encountered an error. Using fallback mode."
            }],
            "final_agent_a": "[SIMULATION] Fallback response",
            "final_agent_b": "[SIMULATION] Fallback response",
            "agent_a_history": [],
            "agent_b_history": []
        }


def run_mediated_debate(topic: str, rounds: int = 3, mock_mode: bool = False) -> Dict:
    """
    Run a mediated debate with a judge arbitrator.
    Judge prevents sycophancy by providing critical feedback.
    
    Args:
        topic: The mathematical problem to solve
        rounds: Number of debate rounds
        mock_mode: If True, use mock responses (for testing without model)
        
    Returns:
        Dictionary containing debate history and results (never crashes)
    """
    logger.info("=" * 80)
    logger.info("STARTING MEDIATED DEBATE")
    logger.info(f"Topic: {topic[:100]}...")
    logger.info(f"Rounds: {rounds}, Mock Mode: {mock_mode}")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        logger.info("Initializing agents and judge...")
        agent_a = DebateAgent("Agent A", "Math Expert", mock_mode=mock_mode)
        agent_b = DebateAgent("Agent B", "Math Expert", mock_mode=mock_mode)
        judge = JudgeAgent(mock_mode=mock_mode)
        logger.info("Agents and judge initialized successfully")
        
        debate_log = []
        
        # Round 0: Agent A & B generate initial answers
        logger.info("Round 0: Generating initial answers...")
        round_start = datetime.now()
        try:
            agent_a_initial = agent_a.generate_initial_answer(topic)
        except Exception as e:
            logger.error(f"Error generating Agent A initial answer: {e}", exc_info=True)
            agent_a_initial = "[SIMULATION] Agent A initial answer: After careful analysis, I believe the answer is 42."
        
        try:
            agent_b_initial = agent_b.generate_initial_answer(topic)
        except Exception as e:
            logger.error(f"Error generating Agent B initial answer: {e}", exc_info=True)
            agent_b_initial = "[SIMULATION] Agent B initial answer: I've calculated and my answer is 42."
        
        round_elapsed = (datetime.now() - round_start).total_seconds()
        logger.info(f"Round 0 completed in {round_elapsed:.2f}s")
        
        debate_log.append({
            "round": 0,
            "type": "initial",
            "agent_a": agent_a_initial,
            "agent_b": agent_b_initial,
            "judge_feedback": None
        })
        
        # Subsequent rounds: Judge evaluates, agents revise
        for round_num in range(1, rounds + 1):
            logger.info(f"Round {round_num}: Starting judge-mediated revision...")
            round_start = datetime.now()
            
            # Step 1: Judge reads both answers and outputs critique
            try:
                logger.debug(f"Round {round_num}: Judge evaluating answers...")
                judge_feedback = judge.critique(
                    topic,
                    agent_a.get_final_answer(),
                    agent_b.get_final_answer(),
                    round_num
                )
            except Exception as e:
                logger.error(f"Error in judge critique: {e}", exc_info=True)
                judge_feedback = "[SIMULATION] Judge feedback: I've reviewed both solutions. There are some errors that need correction."
            
            logger.debug(f"Round {round_num}: Judge feedback received")
            
            # Step 2: Agents revise based on judge's critique
            try:
                logger.debug(f"Round {round_num}: Agents revising based on judge feedback...")
                agent_a_revision = agent_a.revise_from_judge_feedback(
                    topic,
                    judge_feedback,
                    round_num
                )
            except Exception as e:
                logger.error(f"Error in Agent A revision: {e}", exc_info=True)
                agent_a_revision = "[SIMULATION] Agent A revision: Thank you for the feedback. I've corrected my answer."
            
            try:
                agent_b_revision = agent_b.revise_from_judge_feedback(
                    topic,
                    judge_feedback,
                    round_num
                )
            except Exception as e:
                logger.error(f"Error in Agent B revision: {e}", exc_info=True)
                agent_b_revision = "[SIMULATION] Agent B revision: I've considered the feedback and revised my solution."
            
            round_elapsed = (datetime.now() - round_start).total_seconds()
            logger.info(f"Round {round_num} completed in {round_elapsed:.2f}s")
            
            debate_log.append({
                "round": round_num,
                "type": "revision",
                "agent_a": agent_a_revision,
                "agent_b": agent_b_revision,
                "judge_feedback": judge_feedback
            })
        
        total_elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 80)
        logger.info(f"MEDIATED DEBATE COMPLETED in {total_elapsed:.2f}s")
        logger.info("=" * 80)
        
        result = {
            "question": topic,
            "method": "mediated",
            "rounds": rounds,
            "log": debate_log,
            "final_agent_a": agent_a.get_final_answer(),
            "final_agent_b": agent_b.get_final_answer(),
            "judge_history": judge.history,
            "agent_a_history": agent_a.history,
            "agent_b_history": agent_b.history
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Critical error in run_mediated_debate: {str(e)}", exc_info=True)
        # Return a safe fallback result instead of crashing
        return {
            "question": topic,
            "method": "mediated",
            "rounds": rounds,
            "log": [{
                "round": 0,
                "type": "initial",
                "agent_a": "[SIMULATION] Mediated debate encountered an error. Using fallback mode.",
                "agent_b": "[SIMULATION] Mediated debate encountered an error. Using fallback mode.",
                "judge_feedback": None
            }],
            "final_agent_a": "[SIMULATION] Fallback response",
            "final_agent_b": "[SIMULATION] Fallback response",
            "judge_history": [],
            "agent_a_history": [],
            "agent_b_history": []
        }


def mock_debate(topic: str, rounds: int = 3) -> Dict:
    """
    Simplified mock function as backup if local model fails to load.
    Returns hardcoded strings for demonstration.
    """
    return {
        "question": topic,
        "method": "mock",
        "rounds": rounds,
        "log": [
            {
                "round": 0,
                "type": "initial",
                "agent_a": "[Mock] Agent A: After analyzing the problem, I believe the answer is 42.",
                "agent_b": "[Mock] Agent B: I've calculated and my answer is 42 as well."
            }
        ] * (rounds + 1),
        "final_agent_a": "[Mock] Agent A final answer: 42",
        "final_agent_b": "[Mock] Agent B final answer: 42"
    }
