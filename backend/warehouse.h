#ifndef WAREHOUSE_H
#define WAREHOUSE_H

#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <ctime>
#include <iomanip>

using namespace std;

struct Product {
    string productID;
    string productName;
    int quantity;
    double price;
    string location;
    
    Product() : quantity(0), price(0.0) {}
    Product(string id, string name, int qty, double p, string loc)
        : productID(id), productName(name), quantity(qty), price(p), location(loc) {}
};

struct Order {
    string orderID;
    string productID;
    int quantity;
    string status;  // "pending", "processing", "completed", "cancelled"
    string orderDate;
    
    Order(string oid, string pid, int qty) 
        : orderID(oid), productID(pid), quantity(qty), status("pending") {
        orderDate = getCurrentDate();
    }
    
    static string getCurrentDate() {
        time_t now = time(0);
        struct tm* timeinfo = localtime(&now);
        char buffer[11];
        strftime(buffer, sizeof(buffer), "%Y-%m-%d", timeinfo);
        return string(buffer);
    }
};

class Warehouse {
private:
    map<string, Product> inventory;  // 재고 저장소
    vector<Order> orders;            // 주문 저장소
    int orderCounter;
    
public:
    Warehouse();
    
    // 상품 관리
    void addProduct(const string& id, const string& name, int qty, double price, const string& location);
    void removeProduct(const string& id);
    void updateProductQuantity(const string& id, int newQuantity);
    void displayAllProducts() const;
    Product* getProduct(const string& id);
    
    // 주문 관리
    void createOrder(const string& productID, int quantity);
    void processOrder(const string& orderID);
    void cancelOrder(const string& orderID);
    void displayAllOrders() const;
    void displayOrdersByStatus(const string& status) const;
    
    // 재고 조회
    int getProductQuantity(const string& productID) const;
    void checkLowStock(int threshold) const;
    
    // 통계
    void displayInventoryStatus() const;
    double getTotalInventoryValue() const;

    // 웹 연동 (파일 IPC)
    void exportToJson(const string& filepath) const;
    void processCommandFile(const string& cmdPath);
};

#endif
