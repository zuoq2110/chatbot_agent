# KMA Score Agent

This module provides tools for accessing and processing student score data from a PostgreSQL database.

## Components

1. **Models**: Pydantic models for representing student, subject, and score data.
2. **Database Connection**: Asynchronous PostgreSQL connection handling via asyncpg.
3. **Score Tool**: Tool for retrieving student scores with filtering options.
4. **Student Info Tool**: Tool for retrieving student information.
5. **Score Calculator**: Tool for calculating average scores.

## Database Schema

The module expects the following PostgreSQL database schema:

```sql
CREATE TABLE "public"."scores" (
    "score_text" varchar(100),
    "score_first" float4,
    "score_second" float4,
    "score_final" float4,
    "score_over_rall" float4,
    "semester" varchar(255),
    "student_code" varchar(20),
    "subject_id" int4
);

CREATE TABLE "public"."students" (
    "student_code" varchar(20) NOT NULL DEFAULT ''::character varying,
    "student_name" varchar(100) NOT NULL,
    "student_class" varchar(20) DEFAULT ''::character varying,
    PRIMARY KEY ("student_code")
);

CREATE TABLE "public"."subjects" (
    "subject_id" int4 NOT NULL DEFAULT nextval('subjects_subject_id_seq'::regclass),
    "subject_name" varchar(100) NOT NULL,
    "subject_credits" int8,
    PRIMARY KEY ("subject_id")
);

ALTER TABLE "public"."scores" ADD FOREIGN KEY ("student_code") REFERENCES "public"."students"("student_code");
ALTER TABLE "public"."scores" ADD FOREIGN KEY ("subject_id") REFERENCES "public"."subjects"("subject_id");
```

## Configuration

Database connection details should be stored in a `.env` file with the following variable:

```
POSTGRES_URI=postgresql://username:password@localhost:5432/kma_db
```

## Usage

### Score Tool

```python
from src.score.score_tool import create_score_tool

# Create tool
score_tool = create_score_tool()

# Get scores for a student
result = await score_tool.get_student_scores(student_code="CT123", semester="2023_1")
```

### Student Info Tool

```python
from src.score.student_tool import create_student_info_tool

# Create tool
student_tool = create_student_info_tool()

# Get student information
result = await student_tool.get_student_info(student_code="CT123")
```

### Score Calculator

```python
from src.score.calculator_tool import create_score_calculator

# Create tool
calculator = create_score_calculator()

# Calculate averages
scores_json = '{"scores": [...]}'  # JSON string with scores data
result = calculator.calculate_average_scores(scores_json=scores_json)
```
