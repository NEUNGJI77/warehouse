#include "warehouse.h"

Warehouse::Warehouse() : orderCounter(1000) {}

// ===== 상품 관리 =====
void Warehouse::addProduct(const string& id, const string& name, int qty, double price, const string& location) {
    if (inventory.find(id) != inventory.end()) {
        cout << "[오류] 상품 ID '" << id << "'는 이미 존재합니다.\n";
        return;
    }
    inventory[id] = Product(id, name, qty, price, location);
    cout << "[성공] 상품 추가: " << name << " (수량: " << qty << ")\n";
}

void Warehouse::removeProduct(const string& id) {
    if (inventory.erase(id)) {
        cout << "[성공] 상품 삭제: " << id << "\n";
    } else {
        cout << "[오류] 상품 ID '" << id << "'를 찾을 수 없습니다.\n";
    }
}

void Warehouse::updateProductQuantity(const string& id, int newQuantity) {
    auto it = inventory.find(id);
    if (it != inventory.end()) {
        it->second.quantity = newQuantity;
        cout << "[성공] 상품 수량 업데이트: " << id << " -> " << newQuantity << "\n";
    } else {
        cout << "[오류] 상품 ID '" << id << "'를 찾을 수 없습니다.\n";
    }
}

void Warehouse::displayAllProducts() const {
    if (inventory.empty()) {
        cout << "\n[알림] 등록된 상품이 없습니다.\n";
        return;
    }
    
    cout << "\n========== 전체 재고 현황 ==========\n";
    cout << left << setw(15) << "상품ID" << setw(20) << "상품명" 
         << setw(10) << "수량" << setw(12) << "가격" << setw(12) << "위치" << "\n";
    cout << string(69, '-') << "\n";
    
    for (const auto& pair : inventory) {
        const Product& p = pair.second;
        cout << left << setw(15) << p.productID 
             << setw(20) << p.productName 
             << setw(10) << p.quantity 
             << setw(12) << fixed << setprecision(2) << p.price
             << setw(12) << p.location << "\n";
    }
    cout << string(69, '=') << "\n\n";
}

Product* Warehouse::getProduct(const string& id) {
    auto it = inventory.find(id);
    if (it != inventory.end()) {
        return &it->second;
    }
    return nullptr;
}

// ===== 주문 관리 =====
void Warehouse::createOrder(const string& productID, int quantity) {
    Product* product = getProduct(productID);
    
    if (!product) {
        cout << "[오류] 상품 ID '" << productID << "'를 찾을 수 없습니다.\n";
        return;
    }
    
    if (product->quantity < quantity) {
        cout << "[오류] 재고 부족! 현재 재고: " << product->quantity << ", 요청 수량: " << quantity << "\n";
        return;
    }
    
    string orderID = "ORD" + to_string(orderCounter++);
    Order newOrder(orderID, productID, quantity);
    orders.push_back(newOrder);
    
    cout << "[성공] 주문 생성: " << orderID << " (상품: " << product->productName 
         << ", 수량: " << quantity << ")\n";
}

void Warehouse::processOrder(const string& orderID) {
    for (auto& order : orders) {
        if (order.orderID == orderID && order.status == "pending") {
            Product* product = getProduct(order.productID);
            if (product) {
                product->quantity -= order.quantity;
                order.status = "processing";
                cout << "[성공] 주문 처리 중: " << orderID << "\n";
            }
            return;
        }
    }
    cout << "[오류] 주문 ID '" << orderID << "'를 찾을 수 없거나 이미 처리됨.\n";
}

void Warehouse::cancelOrder(const string& orderID) {
    for (auto& order : orders) {
        if (order.orderID == orderID && order.status == "pending") {
            order.status = "cancelled";
            cout << "[성공] 주문 취소: " << orderID << "\n";
            return;
        }
    }
    cout << "[오류] 주문 ID '" << orderID << "'를 찾을 수 없거나 이미 처리됨.\n";
}

void Warehouse::displayAllOrders() const {
    if (orders.empty()) {
        cout << "\n[알림] 등록된 주문이 없습니다.\n";
        return;
    }
    
    cout << "\n========== 전체 주문 현황 ==========\n";
    cout << left << setw(12) << "주문ID" << setw(12) << "상품ID" 
         << setw(8) << "수량" << setw(15) << "상태" << setw(12) << "주문일" << "\n";
    cout << string(59, '-') << "\n";
    
    for (const auto& order : orders) {
        cout << left << setw(12) << order.orderID 
             << setw(12) << order.productID 
             << setw(8) << order.quantity 
             << setw(15) << order.status 
             << setw(12) << order.orderDate << "\n";
    }
    cout << string(59, '=') << "\n\n";
}

void Warehouse::displayOrdersByStatus(const string& status) const {
    cout << "\n========== 상태별 주문 현황: [" << status << "] ==========\n";
    
    bool found = false;
    for (const auto& order : orders) {
        if (order.status == status) {
            cout << "주문ID: " << order.orderID << ", 상품ID: " << order.productID 
                 << ", 수량: " << order.quantity << ", 주문일: " << order.orderDate << "\n";
            found = true;
        }
    }
    
    if (!found) {
        cout << "[알림] 해당 상태의 주문이 없습니다.\n";
    }
    cout << "\n";
}

// ===== 재고 조회 =====
int Warehouse::getProductQuantity(const string& productID) const {
    auto it = inventory.find(productID);
    if (it != inventory.end()) {
        return it->second.quantity;
    }
    return -1;
}

void Warehouse::checkLowStock(int threshold) const {
    cout << "\n========== 저재고 알림 (기준: " << threshold << "개 이하) ==========\n";
    
    bool found = false;
    for (const auto& pair : inventory) {
        const Product& p = pair.second;
        if (p.quantity <= threshold) {
            cout << "[경고] " << p.productID << " - " << p.productName 
                 << " (현재 재고: " << p.quantity << "개)\n";
            found = true;
        }
    }
    
    if (!found) {
        cout << "[알림] 저재고 상품이 없습니다.\n";
    }
    cout << "\n";
}

// ===== 통계 =====
void Warehouse::displayInventoryStatus() const {
    cout << "\n========== 재고 통계 ==========\n";
    cout << "총 상품 종류: " << inventory.size() << "개\n";
    cout << "총 주문 건수: " << orders.size() << "개\n";
    cout << "총 재고 가치: " << fixed << setprecision(2) << getTotalInventoryValue() << "원\n\n";
}

double Warehouse::getTotalInventoryValue() const {
    double total = 0;
    for (const auto& pair : inventory) {
        const Product& p = pair.second;
        total += p.quantity * p.price;
    }
    return total;
}

// ===== 웹 연동 (파일 IPC) =====
void Warehouse::exportToJson(const string& filepath) const {
    ofstream file(filepath);
    if (!file.is_open()) return;

    file << "{\n";
    bool first = true;
    for (const auto& pair : inventory) {
        const Product& p = pair.second;
        if (!first) file << ",\n";
        file << "  \"" << p.productID << "\": {\n";
        file << "    \"name\": \"" << p.productName << "\",\n";
        file << "    \"quantity\": " << p.quantity << ",\n";
        file << "    \"location\": \"" << p.location << "\"\n";
        file << "  }";
        first = false;
    }
    file << "\n}\n";
}

void Warehouse::processCommandFile(const string& cmdPath) {
    ifstream file(cmdPath);
    if (!file.is_open()) return;

    vector<string> lines;
    string line;
    while (getline(file, line)) {
        if (!line.empty()) lines.push_back(line);
    }
    file.close();

    if (lines.empty()) return;

    // 처리 후 파일 비우기
    ofstream clear(cmdPath, ios::trunc);
    clear.close();

    cout << "\n[웹] " << lines.size() << "개 명령 수신\n";

    for (const auto& cmd : lines) {
        istringstream ss(cmd);
        string type;
        getline(ss, type, ',');

        if (type == "QTY") {
            string barcode, changeStr;
            getline(ss, barcode, ',');
            getline(ss, changeStr, ',');
            try {
                int change = stoi(changeStr);
                auto it = inventory.find(barcode);
                if (it != inventory.end()) {
                    it->second.quantity = max(0, it->second.quantity + change);
                    cout << "  [QTY] " << barcode << " "
                         << (change > 0 ? "+" : "") << change
                         << " -> " << it->second.quantity << "개\n";
                } else {
                    cout << "  [QTY] 오류: " << barcode << " 상품 없음\n";
                }
            } catch (...) {}
        }
        else if (type == "NEW") {
            string barcode, name, qtyStr, zone, sec, shelf;
            getline(ss, barcode, ',');
            getline(ss, name, ',');
            getline(ss, qtyStr, ',');
            getline(ss, zone, ',');
            getline(ss, sec, ',');
            getline(ss, shelf, ',');
            try {
                string location = zone + "-" + sec + "-" + shelf;
                int qty = stoi(qtyStr);
                if (inventory.find(barcode) == inventory.end()) {
                    inventory[barcode] = Product(barcode, name, qty, 0.0, location);
                    cout << "  [NEW] 입고: " << name << " " << qty << "개 (" << location << ")\n";
                } else {
                    inventory[barcode].quantity += qty;
                    cout << "  [NEW] 추가입고: " << barcode << " +" << qty << "개\n";
                }
            } catch (...) {}
        }
    }
}
