# 물류창고 자동화 시스템

Python Flask 웹 대시보드와 C++ 백엔드가 파일 기반 IPC로 연동되는 물류창고 관리 시스템입니다.

## 구조

```
warehouse/
├── backend/        # C++ 창고 관리 백엔드
│   ├── main.cpp
│   ├── warehouse.cpp
│   └── warehouse.h
├── modules/        # C++ 공통 모듈
│   ├── Common.h
│   ├── DeliveryManager.cpp / .h
│   ├── InventoryManager.cpp / .h
│   ├── SystemMonitor.cpp / .h
│   └── UserManager.cpp / .h
├── web/            # Python Flask 웹 대시보드
│   ├── LogisticsWeb.py
│   ├── LogisticsWeb.spec
│   └── requirements.txt
├── data.json           # 재고 데이터 (C++ ↔ Flask 공유)
├── users.json.example  # 사용자 계정 형식 예시
├── .env.example        # 환경변수 설정 예시
└── 서버실행.bat
```

## 아키텍처

```
[브라우저] ──HTTP──▶ [Flask 웹서버]
                          │
                    파일 기반 IPC
                    ┌─────┴─────┐
               data.json    commands.txt
                    └─────┬─────┘
                     [C++ 백엔드]
```

- `data.json` — C++ 백엔드가 재고를 기록, Flask가 읽어서 화면에 표시
- `commands.txt` — Flask가 명령을 추가, C++ 백엔드가 읽어서 처리

## 실행 방법

### 웹 서버 (Flask)

```bash
cd web
pip install -r requirements.txt

# .env 파일 생성 (루트 기준)
cp .env.example .env

# 사용자 계정 파일 생성 (루트 기준, users.json.example 참고)
cp users.json.example ../users.json
# users.json의 password 필드에 SHA256 해시값 입력

# 서버 실행
python LogisticsWeb.py
# → http://127.0.0.1:5000
```

또는 루트 폴더에서 `서버실행.bat` 더블클릭.

### C++ 백엔드 (Visual Studio)

`backend/` 폴더를 Visual Studio 2022로 열어 빌드합니다.  
빌드 전 `main.cpp`의 `DATA_PATH`, `CMD_PATH` 경로를 실제 환경에 맞게 수정하세요.

### EXE 패키징 (PyInstaller)

```bash
cd web
pyinstaller LogisticsWeb.spec
# 결과물: web/dist/LogisticsWeb.exe
```

## 주요 기능

| 기능 | 설명 |
|------|------|
| 재고 조회 | 실시간 재고 현황 (5초 폴링) |
| 입고 처리 | 신규 상품 등록 및 수량 증감 |
| 주문 관리 | 출고 주문 생성·처리·취소 |
| 저재고 알림 | 임계값 이하 상품 경고 |
| 사용자 권한 | Admin / Operator 역할 분리 |

## commands.txt 프로토콜

```
QTY,<바코드>,<수량변화>                              # 수량 증감
NEW,<바코드>,<상품명>,<수량>,<존>,<섹션>,<선반>     # 신규 입고
```

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/inventory` | 전체 재고 반환 |
| POST | `/api/update` | commands.txt에 명령 추가 |

## 환경변수 (.env)

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `PORT` | `5000` | 서버 포트 |
| `HOST` | `0.0.0.0` | 바인딩 주소 |
| `FLASK_DEBUG` | `0` | 디버그 모드 |
| `SECRET_KEY` | — | 세션 암호화 키 (운영 시 반드시 변경) |
| `DATA_PATH` | 스크립트 기준 | data.json 경로 |
| `CMD_PATH` | 스크립트 기준 | commands.txt 경로 |

## 기술 스택

- **백엔드**: C++20 (MSVC)
- **웹 서버**: Python 3, Flask
- **패키징**: PyInstaller
- **IPC**: 파일 기반 (JSON, TXT)
