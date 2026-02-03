# tests/test_places_flow.py

from fastapi.testclient import TestClient


def test_create_and_list_places_basic(client: TestClient):
    # 1) 지역 만들기  (사용자가 "지역 선택" 드롭다운에서 보게 될 데이터)
    resp_area = client.post(
        "/areas",
        json={"name": "부산"},
    )
    assert resp_area.status_code == 201
    area_data = resp_area.json()
    area_id = area_data["id"]
    assert area_data["name"] == "부산"

    # 2) 카테고리 만들기 (예: "라멘", "카페" 같은 카테고리)
    resp_cat = client.post(
        "/category",
        json={"name": "라멘", "description": "라멘 가게"},
    )
    assert resp_cat.status_code == 201
    cat_data = resp_cat.json()
    cat_id = cat_data["id"]
    assert cat_data["name"] == "라멘"

    # 3) 가게 만들기  (부산 라멘집 등록)
    resp_place = client.post(
        "/places",
        json={
            "name": "부산 라멘집",
            "area_id": area_id,
            "category_id": cat_id,
        },
    )
    assert resp_place.status_code == 201
    place_data = resp_place.json()

    # 가게 생성 응답에 화면에서 쓸 정보가 잘 들어있는지 확인
    assert place_data["name"] == "부산 라멘집"
    assert place_data["area_name"] == "부산"
    assert place_data["category_name"] == "라멘"
    # 아직 리뷰가 없으니까
    assert place_data["avg_rating"] is None
    assert place_data["review_count"] == 0

    # 4) 가게 리스트 조회 (/places 화면에 해당)
    resp_list = client.get("/places")
    assert resp_list.status_code == 200
    places = resp_list.json()

    # 리스트에 방금 만든 가게가 1개 들어 있어야 함
    assert len(places) == 1
    p = places[0]

    # 리스트 화면에서도 같은 정보가 보이는지 최종 확인
    assert p["name"] == "부산 라멘집"
    assert p["area_name"] == "부산"
    assert p["category_name"] == "라멘"
    assert p["avg_rating"] is None
    assert p["review_count"] == 0
