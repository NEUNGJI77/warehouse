// SystemMonitor.h
#pragma once
#include "Common.h"
#include "InventoryManager.h"
#include "DeliveryManager.h"

class SystemMonitor {
public:
    void CheckSystemResources(double cpu, double mem) const;
    void DisplayDashboard(const InventoryManager& inv, const DeliveryManager& del) const;
};