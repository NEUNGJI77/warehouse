#include "warehouse.h"
#include <iostream>
#include <cstdlib>

using namespace std;

const string DATA_PATH = "C:\\Users\\dlehd\\source\\repos\\LogisticsWeb\\data.json";
const string CMD_PATH  = "C:\\Users\\dlehd\\source\\repos\\LogisticsWeb\\commands.txt";

void displayMenu() {
    cout << "\n";
    cout << "╔════════════════════════════════════════╗\n";
    cout << "║  물류창고자동화관리시스템 메인메뉴      ║\n";
    cout << "╚════════════════════════════════════════╝\n\n";
    cout << "[상품 관리]\n";
    cout << "  1. 상품 추가\n";
    cout << "  2. 상품 삭제\n";
    cout << "  3. 상품 수량 업데이트\n";
    cout << "  4. 전체 상품 조회\n\n";
    cout << "[주문 관리]\n";
    cout << "  5. 주문 생성\n";
    cout << "  6. 주문 처리\n";
    cout << "  7. 주문 취소\n";
    cout << "  8. 전체 주문 조회\n";
    cout << "  9. 상태별 주문 조회\n\n";
    cout << "[재고 관리]\n";
    cout << "  10. 저재고 확인\n";
    cout << "  11. 재고 통계\n\n";
    cout << "  0. 프로그램 종료\n";
    cout << "════════════════════════════════════════\n";
}

int main() {
    Warehouse warehouse;
    int choice;
    string id, name, location, status;
    int quantity, threshold;
    double price;
    
    system("chcp 65001 > nul");  // 윈도우 한글 인코딩
    
    cout << "[시스템 초기화] 샘플 데이터를 로드합니다...\n";
    warehouse.addProduct("P001", "노트북",  50,  1200000, "A-1-1");
    warehouse.addProduct("P002", "마우스",  200, 25000,   "A-1-2");
    warehouse.addProduct("P003", "키보드",  150, 80000,   "B-1-1");
    warehouse.addProduct("P004", "모니터",  30,  350000,  "B-1-2");
    warehouse.addProduct("P005", "프린터",  15,  450000,  "C-1-1");
    cout << "\n초기화 완료!\n";

    // 초기 재고를 웹 대시보드에 즉시 반영
    warehouse.exportToJson(DATA_PATH);
    
    while (true) {
        // 매 루프마다 웹에서 온 명령 자동 처리
        warehouse.processCommandFile(CMD_PATH);

        displayMenu();
        cout << "선택: ";
        cin >> choice;
        cin.ignore();  // 버퍼 제거
        
        switch (choice) {
            case 1: {
                cout << "\n[상품 추가]\n";
                cout << "상품 ID: ";
                getline(cin, id);
                cout << "상품명: ";
                getline(cin, name);
                cout << "수량: ";
                cin >> quantity;
                cout << "가격: ";
                cin >> price;
                cin.ignore();
                cout << "위치: ";
                getline(cin, location);
                warehouse.addProduct(id, name, quantity, price, location);
                warehouse.exportToJson(DATA_PATH);
                break;
            }

            case 2: {
                cout << "\n[상품 삭제]\n";
                cout << "상품 ID: ";
                getline(cin, id);
                warehouse.removeProduct(id);
                warehouse.exportToJson(DATA_PATH);
                break;
            }

            case 3: {
                cout << "\n[상품 수량 업데이트]\n";
                cout << "상품 ID: ";
                getline(cin, id);
                cout << "새로운 수량: ";
                cin >> quantity;
                cin.ignore();
                warehouse.updateProductQuantity(id, quantity);
                warehouse.exportToJson(DATA_PATH);
                break;
            }
            
            case 4: {
                warehouse.displayAllProducts();
                break;
            }
            
            case 5: {
                cout << "\n[주문 생성]\n";
                cout << "상품 ID: ";
                getline(cin, id);
                cout << "주문 수량: ";
                cin >> quantity;
                cin.ignore();
                warehouse.createOrder(id, quantity);
                warehouse.exportToJson(DATA_PATH);
                break;
            }

            case 6: {
                cout << "\n[주문 처리]\n";
                cout << "주문 ID: ";
                getline(cin, id);
                warehouse.processOrder(id);
                warehouse.exportToJson(DATA_PATH);
                break;
            }

            case 7: {
                cout << "\n[주문 취소]\n";
                cout << "주문 ID: ";
                getline(cin, id);
                warehouse.cancelOrder(id);
                warehouse.exportToJson(DATA_PATH);
                break;
            }
            
            case 8: {
                warehouse.displayAllOrders();
                break;
            }
            
            case 9: {
                cout << "\n[상태별 주문 조회]\n";
                cout << "상태 (pending/processing/completed/cancelled): ";
                getline(cin, status);
                warehouse.displayOrdersByStatus(status);
                break;
            }
            
            case 10: {
                cout << "\n[저재고 확인]\n";
                cout << "기준 수량 (이하): ";
                cin >> threshold;
                cin.ignore();
                warehouse.checkLowStock(threshold);
                break;
            }
            
            case 11: {
                warehouse.displayInventoryStatus();
                break;
            }
            
            case 0: {
                cout << "\n[종료] 프로그램을 종료합니다.\n";
                return 0;
            }
            
            default: {
                cout << "\n[오류] 잘못된 선택입니다. 다시 시도해주세요.\n";
            }
        }
    }
    
    return 0;
}