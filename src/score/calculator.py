from typing import Dict, List, Any, Optional
import json
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from models import ScoreWithDetails

class ScoreCalculatorInput(BaseModel):
    scores_json: str = Field(description="JSON string containing scores data to calculate averages from")

    
@tool("calculate_average_scores", args_schema=ScoreCalculatorInput, description=(
    "Calculate average scores from provided scores data. "
    "The scores data must be provided in JSON format. "
    "The JSON string should contain an array of scores with fields: score_first, score_second, score_final, and score_over_rall."
))
def calculate_average_scores(scores_json: str) -> str:
    """
    Calculate average scores from provided scores data.

    Args:
        scores_json: JSON string containing scores data

    Returns:
        A JSON string containing the calculated average scores
    """
    try:
        # Parse the scores data
        data = json.loads(scores_json)

        if "scores" not in data or not data["scores"]:
            return json.dumps({
                "averages": {},
                "message": "No scores data provided or scores array is empty"
            })

        scores = data["scores"]

        # Calculate averages
        overall_averages = {
            "score_first": 0.0,
            "score_second": 0.0,
            "score_final": 0.0,
            "score_over_rall": 0.0,
            "count": 0
        }

        semester_averages = {}

        for score in scores:
            # Skip scores with missing values
            if not all(score.get(key) is not None for key in ["score_first", "score_second", "score_final", "score_over_rall"]):
                continue

            semester = score.get("semester", "unknown")
            if semester not in semester_averages:
                semester_averages[semester] = {
                    "score_first": 0.0,
                    "score_second": 0.0,
                    "score_final": 0.0,
                    "score_over_rall": 0.0,
                    "count": 0
                }

            # Update overall averages
            overall_averages["score_first"] += score.get("score_first", 0)
            overall_averages["score_second"] += score.get("score_second", 0)
            overall_averages["score_final"] += score.get("score_final", 0)
            overall_averages["score_over_rall"] += score.get("score_over_rall", 0)
            overall_averages["count"] += 1

            # Update semester averages
            semester_averages[semester]["score_first"] += score.get("score_first", 0)
            semester_averages[semester]["score_second"] += score.get("score_second", 0)
            semester_averages[semester]["score_final"] += score.get("score_final", 0)
            semester_averages[semester]["score_over_rall"] += score.get("score_over_rall", 0)
            semester_averages[semester]["count"] += 1

        # Calculate final averages
        if overall_averages["count"] > 0:
            overall_averages["score_first"] /= overall_averages["count"]
            overall_averages["score_second"] /= overall_averages["count"]
            overall_averages["score_final"] /= overall_averages["count"]
            overall_averages["score_over_rall"] /= overall_averages["count"]

        for semester in semester_averages:
            if semester_averages[semester]["count"] > 0:
                semester_averages[semester]["score_first"] /= semester_averages[semester]["count"]
                semester_averages[semester]["score_second"] /= semester_averages[semester]["count"]
                semester_averages[semester]["score_final"] /= semester_averages[semester]["count"]
                semester_averages[semester]["score_over_rall"] /= semester_averages[semester]["count"]

        # Round to 2 decimal places
        for key in ["score_first", "score_second", "score_final", "score_over_rall"]:
            overall_averages[key] = round(overall_averages[key], 2)
            for semester in semester_averages:
                semester_averages[semester][key] = round(semester_averages[semester][key], 2)

        result = {
            "overall_average": {
                key: overall_averages[key] for key in ["score_first", "score_second", "score_final", "score_over_rall"]
            },
            "semester_averages": {
                semester: {
                    key: semester_averages[semester][key]
                    for key in ["score_first", "score_second", "score_final", "score_over_rall"]
                }
                for semester in semester_averages
            },
            "total_subjects": overall_averages["count"],
            "message": f"Calculated averages for {overall_averages['count']} subjects across {len(semester_averages)} semesters"
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"averages": {}, "message": f"Error calculating averages: {str(e)}"})
