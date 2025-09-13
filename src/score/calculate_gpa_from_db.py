import json
import re
from typing import Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field, validator
from score.student_tool import global_db
from .models import ScoreFilter


def convert_to_he4(score: float) -> float:
    """Quy đổi điểm hệ 10 sang hệ 4"""
    if 9.0 <= score <= 10.0:
        return 4.0
    elif 8.5 <= score < 9.0:
        return 3.8
    elif 8.0 <= score < 8.5:
        return 3.5
    elif 7.0 <= score < 8.0:
        return 3.0
    elif 6.5 <= score < 7.0:
        return 2.5
    elif 5.5 <= score < 6.5:
        return 2.0
    elif 4.0 <= score < 5.5:
        return 1.0
    else:
        return 0.0


class GPAInput(BaseModel):
    student_code: str = Field(description="The student code to calculate GPA for")
    semester: Optional[str] = Field(
        None, description="Filter scores by semester in format ki1-2024-2025, k2-2024-2025"
    )
    subject_id: Optional[int] = Field(
        None, description="Filter scores by subject ID"
    )
    subject_name: Optional[str] = Field(
        None, description="Filter scores by subject name (case-insensitive, partial match allowed)"
    )

    @validator("semester")
    def validate_semester_format(cls, value):
        if value is None:
            return value
        pattern = r"^(ki|k)[1-2]-\d{4}-\d{4}$"
        if not re.match(pattern, value):
            raise ValueError("Semester must be in format ki1-2024-2025, k2-2024-2025")
        return value


@tool(
    "calculate_gpa_from_db",
    args_schema=GPAInput,
    description=(
        "Calculate GPA (system 10 and system 4) directly from DB using student_code. "
        "Optionally filter by semester, subject_id, or subject_name."
    )
)
async def calculate_gpa_from_db(
    student_code: str,
    semester: Optional[str] = None,
    subject_id: Optional[int] = None,
    subject_name: Optional[str] = None
) -> str:
    """
    Calculate GPA directly from the database with multiple filters.
    """
    try:
        # Tạo filter cho DB
        filter = ScoreFilter(
            student_code=student_code,
            semester=semester,
            subject_id=subject_id
        )

        scores = await global_db.db.get_scores(filter)

        if not scores:
            return json.dumps({
                "averages": {},
                "scores": [],
                "message": f"No scores found for student {student_code}"
                + (f" in semester {semester}" if semester else "")
                + (f" with subject_id {subject_id}" if subject_id else "")
                + (f" with subject_name {subject_name}" if subject_name else "")
            }, ensure_ascii=False)

        # Nếu filter theo subject_name
        if subject_name:
            scores = [s for s in scores if subject_name.lower() in s.subject_name.lower()]

        if not scores:
            return json.dumps({
                "averages": {},
                "scores": [],
                "message": f"No scores found after filtering by subject_name='{subject_name}'"
            }, ensure_ascii=False)

        # Tính GPA hệ 10 & hệ 4
        total_weighted_score10 = sum(s.score_over_rall * s.subject_credits for s in scores)
        total_weighted_score4 = sum(convert_to_he4(s.score_over_rall) * s.subject_credits for s in scores)
        total_credits = sum(s.subject_credits for s in scores)

        if total_credits == 0:
            return json.dumps({
                "averages": {},
                "scores": [s.model_dump() for s in scores],
                "message": "Total credits is zero, cannot calculate GPA"
            }, ensure_ascii=False)

        average_score10 = round(total_weighted_score10 / total_credits, 2)
        average_score4 = round(total_weighted_score4 / total_credits, 2)

        # Gắn thêm field hệ 4 vào từng môn
        scores_out = []
        for s in scores:
            d = s.model_dump()
            d["score_he4"] = convert_to_he4(s.score_over_rall)
            scores_out.append(d)

        return json.dumps({
            "averages": {
                "average_score_10": average_score10,
                "average_score_4": average_score4,
                "total_credits": total_credits
            },
            "scores": scores_out,
            "filters": {
                "student_code": student_code,
                "semester": semester,
                "subject_id": subject_id,
                "subject_name": subject_name
            },
            "message": "GPA calculated successfully"
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "averages": {},
            "scores": [],
            "message": f"Error calculating GPA: {str(e)}"
        }, ensure_ascii=False)

    finally:
        await global_db.close()
