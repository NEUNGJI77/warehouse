#pragma once
#include "Common.h"

class UserManager {
private:
    std::map<std::string, User> users;

public:
    UserManager();
    bool AddUser(const std::string& id, const std::string& name, UserRole role);
    bool Authenticate(const std::string& id, UserRole requiredRole) const;
    const User* GetUser(const std::string& id) const;
};