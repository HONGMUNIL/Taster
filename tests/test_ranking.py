from fastapi.testclient import TestClient


def test_health_ok(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_rankings_basic_structure(client: TestClient):
    # 1) 지역 생성
    resp_area = client.post(
        "/areas",
        json={"name": "오사카"},
    )
    assert resp_area.status_code == 201
    area_data = resp_area.json()
    area_id = area_data["id"]

    # 2) 카테고리 생성
    resp_cat = client.post(
        "/category",
        json={"name": "라멘", "description": "라멘 가게"},
    )
    assert resp_cat.status_code == 201
    cat_data = resp_cat.json()
    category_id = cat_data["id"]

    # 3) 가게 두 개 생성
    resp_place1 = client.post(
        "/places",
        json={"name": "오사카 라멘집 1호", "area_id": area_id, "category_id": category_id},
    )
    assert resp_place1.status_code == 201
    place1 = resp_place1.json()

    resp_place2 = client.post(
        "/places",
        json={"name": "오사카 라멘집 2호", "area_id": area_id, "category_id": category_id},
    )
    assert resp_place2.status_code == 201
    place2 = resp_place2.json()

    # 4) 랭킹 API 호출
    resp_rank = client.get("/rankings")
    assert resp_rank.status_code == 200

    items = resp_rank.json()

    # 가게 두 개가 랭킹 결과에 있어야 함
    assert len(items) == 2

    # 응답 구조 확인
    first = items[0]
    required_keys = {"place_id", "place_name", "bayes_score", "avg_rating", "review_count"}

    # 랭킹 각 아이템이 필요한 키를 다 가지고 있는지
    assert required_keys.issubset(first.keys())

    # 우리가 만든 가게 id들이 랭킹 결과에 포함되어 있는지
    place_ids = {item["place_id"] for item in items}
    assert place1["id"] in place_ids
    assert place2["id"] in place_ids
