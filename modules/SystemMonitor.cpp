#include "SystemMonitor.h"

void SystemMonitor::CheckSystemResources(double cpu, double mem) const {
    std::cout << "\n[시스템 리소스 상태] CPU: " << cpu << "% | MEMORY: " << mem << "%\n";
    if (cpu > 90.0) {
        std::cout << "🚨 [경고] CPU 임계치(90%) 초과! 관리자에게 SMS/이메일 긴급 알림 발송.\n";
    }
    if (mem > 85.0) {
        std::cout << "🚨 [경고] 메모리 임계치(85%) 초과! 관리자에게 SMS/이메일 긴급 알림 발송.\n";
    }
}

void SystemMonitor::DisplayDashboard(const InventoryManager& inv, const DeliveryManager& del) const {
    std::cout << "\n==================================================\n";
    std::cout << "       [도메인 5] 물류 자동화 통합 대시보드       \n";
    std::cout << "==================================================\n";

    int totalItems = 0;
    for (const auto& p : inv.GetAllProducts()) {
        totalItems += p.second.quantity;
    }

    int pCount = 0, sCount = 0, dCount = 0;
    for (const auto& o : del.GetOrders()) {
        if (o.status == OrderStatus::Pending) pCount++;
        else if (o.status == OrderStatus::Shipped) sCount++;
        else if (o.status == OrderStatus::Delivered) dCount++;
    }

    std::cout << " 📦 [총 재고지표] 등록 물품: " << inv.GetAllProducts().size() << "종 | 총 수량: " << totalItems << "개\n";
    std::cout << " 🚚 [출고지표] 대기: " << pCount << "건 | 배송중: " << sCount << "건 | 완료: " << dCount << "건\n";
    std::cout << "==================================================\n";
}