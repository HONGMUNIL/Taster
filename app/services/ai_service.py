import os

from google import genai

from app.schemas.ai import AIReviewSummary


def summarize_reviews_with_ai(review_bodies: list[str]) -> AIReviewSummary:
    """
    리뷰 본문 목록을 받아 Gemini API로 요약 결과를 반환합니다.
    """

    if not review_bodies:
        return AIReviewSummary(
            summary="아직 등록된 리뷰가 없어 요약할 수 없습니다.",
            positive_keywords=[],
            negative_keywords=[],
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return AIReviewSummary(
            summary="GEMINI_API_KEY가 설정되지 않아 AI 요약을 실행할 수 없습니다.",
            positive_keywords=[],
            negative_keywords=[],
        )

    client = genai.Client(api_key=api_key)

    reviews_text = "\n".join(
        f"{index + 1}. {body}"
        for index, body in enumerate(review_bodies)
    )

    prompt = f"""
너는 맛집 리뷰를 요약하는 도우미야.

아래 리뷰들을 바탕으로 다음 3가지를 만들어줘.

1. 전체 요약
2. 긍정 키워드 목록
3. 부정 키워드 목록

조건:
- 한국어로 작성해.
- 리뷰에 없는 내용은 상상하지 마.
- 요약은 1~2문장으로 짧게 작성해.
- 키워드는 짧은 단어 형태로 뽑아줘.

리뷰 목록:
{reviews_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": AIReviewSummary.model_json_schema(),
        },
    )

    return AIReviewSummary.model_validate_json(response.text)