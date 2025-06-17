import httpx
import json
import os
from typing import Dict, Any
from ..models.homework import Homework
from ..models.submission import SubmissionFile


class AIService:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")

    async def grade_submission(
            self,
            homework: Homework,
            files: list[SubmissionFile]
    ) -> Dict[str, Any]:
        """Grade submission using DeepSeek AI"""

        # Prepare file contents
        file_contents = ""
        for file in files:
            file_contents += f"=== {file.file_name} ===\n{file.content}\n\n"

        # Create grading prompt
        prompt = f"""
You are an expert programming instructor. Grade this {homework.file_extension} code submission.

HOMEWORK: {homework.title}
DESCRIPTION: {homework.description}
POINTS: {homework.points}
GRADING CRITERIA: {homework.ai_grading_prompt}

SUBMITTED FILES:
{file_contents}

Please grade this submission on 3 criteria (0-100 each):
1. Task Completeness - How well does the code fulfill the requirements?
2. Code Quality - Code structure, readability, best practices
3. Correctness - Does the code work correctly and handle edge cases?

Return your response as JSON in this exact format:
{{
    "task_completeness": <score 0-100>,
    "code_quality": <score 0-100>, 
    "correctness": <score 0-100>,
    "total": <average of the three scores>,
    "overall_feedback": "<brief 2-3 sentence summary>",
    "task_completeness_feedback": "<specific feedback on task completion>",
    "code_quality_feedback": "<specific feedback on code quality>",
    "correctness_feedback": "<specific feedback on correctness>"
}}

Be constructive and specific in your feedback. Focus on what the student did well and areas for improvement.
"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )

                if response.status_code != 200:
                    raise Exception(f"AI API error: {response.status_code} - {response.text}")

                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]

                # Parse JSON response
                try:
                    grades = json.loads(ai_response)

                    # Validate required fields
                    required_fields = [
                        "task_completeness", "code_quality", "correctness", "total",
                        "overall_feedback", "task_completeness_feedback",
                        "code_quality_feedback", "correctness_feedback"
                    ]

                    for field in required_fields:
                        if field not in grades:
                            raise ValueError(f"Missing field: {field}")

                    # Ensure scores are integers between 0-100
                    for score_field in ["task_completeness", "code_quality", "correctness", "total"]:
                        grades[score_field] = max(0, min(100, int(grades[score_field])))

                    return grades

                except (json.JSONDecodeError, ValueError) as e:
                    # Fallback if AI response is not valid JSON
                    return {
                        "task_completeness": 70,
                        "code_quality": 70,
                        "correctness": 70,
                        "total": 70,
                        "overall_feedback": "Automatic grading encountered an issue. Please review manually.",
                        "task_completeness_feedback": "Unable to assess automatically.",
                        "code_quality_feedback": "Unable to assess automatically.",
                        "correctness_feedback": "Unable to assess automatically."
                    }

        except Exception as e:
            # Fallback scoring in case of API failure
            return {
                "task_completeness": 50,
                "code_quality": 50,
                "correctness": 50,
                "total": 50,
                "overall_feedback": f"AI grading service unavailable. Error: {str(e)}",
                "task_completeness_feedback": "Manual review required.",
                "code_quality_feedback": "Manual review required.",
                "correctness_feedback": "Manual review required."
            }