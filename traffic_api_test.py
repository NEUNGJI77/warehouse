import requests
import sys

SERVICE_KEY = "c7c3034a9a3109d485bf504dcdcd8d4fd77ca1d483983455ada07682f0bc43c5"

# 테스트할 엔드포인트 목록
endpoints = [
    "https://apis.data.go.kr/6260000/ItsServiceNew/getItsLinkList",
    "https://apis.data.go.kr/6260000/ItsLinkService/getItsLinkList",
    "https://apis.data.go.kr/6260000/ItsSotonService/getItsSotonInfo",
]

for url in endpoints:
    params = {
        "serviceKey": SERVICE_KEY,
        "numOfRows": 5,
        "pageNo": 1,
        "type": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"URL: {url}")
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {response.text[:300]}")
        print("-" * 60)
    except Exception as e:
        print(f"오류: {e}")
