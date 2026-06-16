// DeliveryManager.h
#pragma once
#include "Common.h"
#include "InventoryManager.h"

class DeliveryManager {
private:
    std::vector<OutboundOrder> orders;

public:
    bool CreateOutboundOrder(const std::string& orderId, const std::string& barcode, int qty, InventoryManager& invManager);
    bool UpdateDeliveryStatus(const std::string& orderId, OrderStatus newStatus);
    void PrintDeliveryStatus() const;
    const std::vector<OutboundOrder>& GetOrders() const { return orders; }
};