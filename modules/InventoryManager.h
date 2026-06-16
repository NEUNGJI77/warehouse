#pragma once
#include "Common.h"
#include <mutex>   // 🌟 겹침 방지 자물쇠
#include <thread>  // 🌟 백그라운드 스레드
#include <atomic>  // 🌟 안전한 종료 스위치

class InventoryManager {
private:
    std::map<std::string, Product> products;
    std::map<std::string, Location> productLocations;

    mutable std::recursive_mutex mtx; // 자물쇠 (동시에 데이터 만지는 것 방지)
    std::atomic<bool> isRunning;      // 프로그램 종료 스위치
    std::thread syncThread;           // 쪽지를 확인할 그림자 분신

    void SaveToWebFolder() const;
    void CheckWebCommands();          // 분신이 무한히 반복할 쪽지 감시 로직

public:
    InventoryManager();
    ~InventoryManager(); // 🌟 프로그램이 꺼질 때 스레드를 청소할 파괴자 추가

    bool RegisterInbound(const std::string& barcode, const std::string& name, int qty, const Location& loc);
    bool DeductInventory(const std::string& barcode, int qty);
    const Product* GetProduct(const std::string& barcode) const;

    // 데이터를 반환할 때도 자물쇠를 꼭 채워야 에러가 안 납니다.
    std::map<std::string, Product> GetAllProducts() const {
        std::lock_guard<std::recursive_mutex> lock(mtx);
        return products;
    }

    void PrintInventoryReport() const;
};