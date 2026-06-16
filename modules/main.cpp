// main.cpp
#include "UserManager.h"
#include "InventoryManager.h"
#include "DeliveryManager.h"
#include "SystemMonitor.h"

int main() {
    // 윈도우 콘솔 한글 인코딩 깨짐 방지
    std::system("chcp 65001 > nul");

    UserManager userMgr;
    InventoryManager invMgr;
    DeliveryManager delMgr;
    SystemMonitor sysMonitor;

    std::string currentUserId;
    std::cout << "==================================================\n";
    std::cout << "       물류창고자동화관리시스템 제어 콘솔\n";
    std::cout << "==================================================\n";
    std::cout << "사원 번호(ID)를 입력하세요 (예: 22110025 또는 op01): ";
    std::cin >> currentUserId;

    const User* currentUser = userMgr.GetUser(currentUserId);
    if (!currentUser) {
        std::cout << "❌ 등록되지 않은 사용자입니다. 프로그램을 종료합니다.\n";
        return 0;
    }

    std::cout << "\n🔓 [" << currentUser->name << "] 님 환영합니다. (권한: "
        << (currentUser->role == UserRole::Admin ? "관리자" : "운영자") << ")\n";

    while (true) {
        std::cout << "\n--- [메인 메뉴] ---\n";
        std::cout << "1. 상품 입고 등록 (QR/바코드 스캔 시뮬레이션)\n";
        std::cout << "2. 출고 주문 생성 (재고 차감 연동)\n";
        std::cout << "3. 배송 상태 업데이트\n";
        std::cout << "4. 실시간 재고 보고서 출력\n";
        std::cout << "5. 통합 대시보드 및 시스템 자원 점검\n";
        std::cout << "6. 시스템 종료\n";
        std::cout << "선택할 명령 번호: ";

        int choice;
        std::cin >> choice;
        if (std::cin.fail()) {
            std::cin.clear();
            std::cin.ignore(1000, '\n');
            std::cout << "⚠️ 숫자로 입력해 주세요.\n";
            continue;
        }

        if (choice == 6) {
            std::cout << "정상적으로 시스템을 종료합니다.\n";
            break;
        }

        switch (choice) {
        case 1: { // 입고
            if (!userMgr.Authenticate(currentUserId, UserRole::Operator)) {
                std::cout << "🔒 권한이 부족합니다. (Operator 이상 권한 필요)\n";
                break;
            }
            std::string barcode, name, zone;
            int qty, section, shelf;
            std::cout << "바코드(QR) 문자열 입력: "; std::cin >> barcode;
            std::cout << "상품명 입력: "; std::cin >> name;
            std::cout << "입고 수량: "; std::cin >> qty;
            std::cout << "보관 구역(Zone - 예: A): "; std::cin >> zone;
            std::cout << "섹션 번호(숫자): "; std::cin >> section;
            std::cout << "선반 층수(숫자): "; std::cin >> shelf;

            if (invMgr.RegisterInbound(barcode, name, qty, { zone, section, shelf })) {
                std::cout << "✅ 입고 및 창고 보관 위치 할당이 완료되었습니다.\n";
            }
            else {
                std::cout << "❌ 입고 실패 (수량 등을 확인하세요).\n";
            }
            break;
        }
        case 2: { // 출고
            if (!userMgr.Authenticate(currentUserId, UserRole::Operator)) {
                std::cout << "🔒 권한이 부족합니다.\n";
                break;
            }
            std::string orderId, barcode;
            int qty;
            std::cout << "새 주문 ID 입력: "; std::cin >> orderId;
            std::cout << "출고할 상품 바코드 입력: "; std::cin >> barcode;
            std::cout << "출고 수량: "; std::cin >> qty;

            delMgr.CreateOutboundOrder(orderId, barcode, qty, invMgr);
            break;
        }
        case 3: { // 배송 상태 변경
            if (!userMgr.Authenticate(currentUserId, UserRole::Operator)) {
                std::cout << "🔒 권한이 부족합니다.\n";
                break;
            }
            std::string orderId;
            int statusChoice;
            std::cout << "상태를 변경할 주문 ID 입력: "; std::cin >> orderId;
            std::cout << "변경할 상태 선택 (1: 배송중 / 2: 배송완료): "; std::cin >> statusChoice;

            OrderStatus nextStatus = (statusChoice == 2) ? OrderStatus::Delivered : OrderStatus::Shipped;
            if (delMgr.UpdateDeliveryStatus(orderId, nextStatus)) {
                std::cout << "✅ 배송 상태가 업데이트되었습니다.\n";
            }
            else {
                std::cout << "❌ 주문 ID를 찾을 수 없습니다.\n";
            }
            break;
        }
        case 4:
            invMgr.PrintInventoryReport();
            delMgr.PrintDeliveryStatus();
            break;
        case 5:
            sysMonitor.DisplayDashboard(invMgr, delMgr);
            // 시뮬레이션을 위해 임계치에 근접한 리소스 값 입력 예시
            sysMonitor.CheckSystemResources(78.5, 89.2); // Memory 85% 초과 상황 유도
            break;
        default:
            std::cout << "⚠️ 올바른 번호를 선택해 주세요.\n";
            break;
        }
    }
    return 0;
}