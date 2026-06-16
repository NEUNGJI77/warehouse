#include "InventoryManager.h"
#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
#include <cstdio> // 파일 삭제(remove)를 위한 부품
#include <sstream>  // 문자열 쪼개기(Split) 부품 추가

InventoryManager::InventoryManager() {
    isRunning = true;
    SaveToWebFolder();
    // 🌟 메인 프로그램과 별개로 쪽지를 감시하는 백그라운드 스레드 출발!
    syncThread = std::thread(&InventoryManager::CheckWebCommands, this);
}

InventoryManager::~InventoryManager() {
    isRunning = false;
    if (syncThread.joinable()) {
        syncThread.join(); // 프로그램 종료 시 스레드도 안전하게 퇴근시킵니다.
    }
}

// 🌟 백그라운드에서 0.5초마다 파이썬의 쪽지를 감시하는 로직
void InventoryManager::CheckWebCommands() {
    std::string cmdPath = "C:\\Users\\dlehd\\source\\repos\\LogisticsWeb\\commands.txt";
    while (isRunning) {
        std::ifstream fin(cmdPath);
        if (fin.is_open()) {
            std::string line;
            std::vector<std::string> lines;
            while (std::getline(fin, line)) {
                if (!line.empty()) lines.push_back(line);
            }
            fin.close();

            if (!lines.empty()) {
                std::lock_guard<std::recursive_mutex> lock(mtx);
                bool updated = false;

                for (const std::string& l : lines) {
                    std::stringstream ss(l);
                    std::string type;
                    std::getline(ss, type, ','); // 첫 번째 단어(QTY 또는 NEW) 읽기

                    try {
                        if (type == "QTY") {
                            std::string barcode, changeStr;
                            std::getline(ss, barcode, ',');
                            std::getline(ss, changeStr, ',');

                            int change = std::stoi(changeStr);
                            if (products.find(barcode) != products.end()) {
                                products[barcode].quantity += change;
                                if (products[barcode].quantity < 0) products[barcode].quantity = 0;
                                updated = true;
                            }
                        }
                        else if (type == "NEW") {
                            std::string barcode, name, qtyStr, zone, secStr, shelfStr;
                            std::getline(ss, barcode, ',');
                            std::getline(ss, name, ',');
                            std::getline(ss, qtyStr, ',');
                            std::getline(ss, zone, ',');
                            std::getline(ss, secStr, ',');
                            std::getline(ss, shelfStr, ',');

                            int qty = std::stoi(qtyStr);
                            int sec = std::stoi(secStr);
                            int shelf = std::stoi(shelfStr);

                            // 이미 있는 바코드면 수량만 추가, 없으면 새로 등록!
                            if (products.find(barcode) != products.end()) {
                                products[barcode].quantity += qty;
                            }
                            else {
                                products[barcode] = { barcode, name, qty };
                                productLocations[barcode] = { zone, sec, shelf };
                            }
                            updated = true;
                        }
                    }
                    catch (...) {
                        // 웹에서 이상한 글자를 보내도 C++ 프로그램이 튕기지 않도록 방어
                        std::cout << "🚨 [경고] 웹사이트에서 잘못된 형식의 데이터가 수신되었습니다.\n";
                    }
                }

                if (updated) SaveToWebFolder();
                std::remove(cmdPath.c_str());
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
}

bool InventoryManager::RegisterInbound(const std::string& barcode, const std::string& name, int qty, const Location& loc) {
    std::lock_guard<std::recursive_mutex> lock(mtx); // 자물쇠 ON
    if (barcode.empty() || qty <= 0) return false;

    if (products.find(barcode) != products.end()) {
        products[barcode].quantity += qty;
    }
    else {
        products[barcode] = { barcode, name, qty };
        productLocations[barcode] = loc;
    }

    SaveToWebFolder();
    return true;
}

bool InventoryManager::DeductInventory(const std::string& barcode, int qty) {
    std::lock_guard<std::recursive_mutex> lock(mtx); // 자물쇠 ON
    auto it = products.find(barcode);
    if (it == products.end() || it->second.quantity < qty) return false;

    it->second.quantity -= qty;
    SaveToWebFolder();
    return true;
}

const Product* InventoryManager::GetProduct(const std::string& barcode) const {
    std::lock_guard<std::recursive_mutex> lock(mtx); // 자물쇠 ON
    auto it = products.find(barcode);
    if (it == products.end()) return nullptr;
    return &(it->second);
}

void InventoryManager::PrintInventoryReport() const {
    std::lock_guard<std::recursive_mutex> lock(mtx); // 자물쇠 ON
    std::cout << "\n==================================================\n";
    std::cout << "          [도메인 2] 실시간 재고 현황 보고서          \n";
    std::cout << "==================================================\n";
    std::cout << std::left << std::setw(15) << "바코드/QR"
        << std::setw(15) << "상품명"
        << std::setw(10) << "재고량" << "보관위치(Zone-Sec-Shelf)\n";
    std::cout << "--------------------------------------------------\n";
    for (const auto& pair : products) {
        const auto& prod = pair.second;
        auto locIt = productLocations.find(prod.barcode);
        std::cout << std::left << std::setw(15) << prod.barcode
            << std::setw(15) << prod.name
            << std::setw(10) << prod.quantity;
        if (locIt != productLocations.end()) {
            std::cout << locIt->second.zone << "-" << locIt->second.section << "-" << locIt->second.shelf;
        }
        std::cout << "\n";
    }
    std::cout << "==================================================\n";
}

void InventoryManager::SaveToWebFolder() const {
    std::lock_guard<std::recursive_mutex> lock(mtx); // 자물쇠 ON
    std::string filePath = "C:\\Users\\dlehd\\source\\repos\\LogisticsWeb\\data.json";
    std::ofstream fout(filePath);
    if (!fout.is_open()) {
        std::cout << "\n🚨 [오류] 웹사이트로 데이터를 보낼 수 없습니다.\n";
        return;
    }

    fout << "{\n";
    int count = 0;
    int total = products.size();
    for (const auto& pair : products) {
        const auto& prod = pair.second;
        auto locIt = productLocations.find(prod.barcode);
        std::string loc = "미지정";
        if (locIt != productLocations.end()) {
            loc = locIt->second.zone + "-" + std::to_string(locIt->second.section) + "-" + std::to_string(locIt->second.shelf);
        }

        fout << "  \"" << prod.barcode << "\": {";
        fout << "\"name\": \"" << prod.name << "\", ";
        fout << "\"quantity\": " << prod.quantity << ", ";
        fout << "\"location\": \"" << loc << "\"}";

        count++;
        if (count < total) fout << ",\n";
        else fout << "\n";
    }
    fout << "}\n";
    fout.close();
}