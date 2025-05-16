"""
Score package for KMA Agent.

This package provides tools for accessing and processing student score data.
"""

from .score_tool import create_score_tool, get_student_scores
from .student_tool import create_student_info_tool, get_student_info
from .calculator import create_score_calculator, calculate_average_scores
from .database import Database
from .models import Student, Subject, Score, ScoreWithDetails, ScoreFilter, ScoreResponse

__version__ = "0.1.0"
__all__ = [
    "create_score_tool", 
    "get_student_scores",
    "create_student_info_tool", 
    "get_student_info",
    "create_score_calculator", 
    "calculate_average_scores",
    "Database",
    "Student", 
    "Subject", 
    "Score", 
    "ScoreWithDetails", 
    "ScoreFilter", 
    "ScoreResponse"
]
