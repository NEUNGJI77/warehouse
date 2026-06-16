#include "DeliveryManager.h"

bool DeliveryManager::CreateOutboundOrder(const std::string& orderId, const std::string& barcode, int qty, InventoryManager& invManager) {
    if (!invManager.DeductInventory(barcode, qty)) {
        std::cout << "❌ [출고 실패] 재고가 부족하거나 등록되지 않은 바코드입니다.\n";
        return false;
    }
    orders.push_back({ orderId, barcode, qty, OrderStatus::Pending });

    std::cout << "✅ [출고 완료] 주문 ID '" << orderId << "' (상품 바코드: " << barcode << ", 수량: " << qty << ") 출고 처리가 완료되었습니다.\n";
    
    return true;
}

bool DeliveryManager::UpdateDeliveryStatus(const std::string& orderId, OrderStatus newStatus) {
    for (auto& order : orders) {
        if (order.orderId == orderId) {
            order.status = newStatus;
            return true;
        }
    }
    return false;
}

void DeliveryManager::PrintDeliveryStatus() const {
    std::cout << "\n==================================================\n";
    std::cout << "          [도메인 4] 출고 및 배송 추적 현황          \n";
    std::cout << "==================================================\n";
    std::cout << std::left << std::setw(15) << "주문 ID"
        << std::setw(15) << "상품 바코드"
        << std::setw(8) << "수량" << "배송 상태\n";
    std::cout << "--------------------------------------------------\n";
    for (const auto& order : orders) {
        std::string statusStr;
        switch (order.status) {
        case OrderStatus::Pending:   statusStr = "출고대기(Pending)"; break;
        case OrderStatus::Shipped:   statusStr = "배송중(Shipped)"; break;
        case OrderStatus::Delivered: statusStr = "배송완료(Delivered)"; break;
        }
        std::cout << std::left << std::setw(15) << order.orderId
            << std::setw(15) << order.barcode
            << std::setw(8) << order.quantity
            << statusStr << "\n";
    }
    std::cout << "==================================================\n";
}