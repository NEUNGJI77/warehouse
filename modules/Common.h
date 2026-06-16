#pragma once
#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <iomanip>

enum class UserRole { Admin, Operator };
enum class OrderStatus { Pending, Shipped, Delivered };

struct Product {
    std::string barcode;
    std::string name;
    int quantity;
};

struct Location {
    std::string zone;
    int section;
    int shelf;
};

struct OutboundOrder {
    std::string orderId;
    std::string barcode;
    int quantity;
    OrderStatus status;
};

struct User {
    std::string id;
    std::string name;
    UserRole role;
};