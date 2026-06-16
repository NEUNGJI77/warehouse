#include "UserManager.h"

UserManager::UserManager() {
    // 테스트용 기본 계정 등록
    AddUser("22110025", "이도윤", UserRole::Admin);
    AddUser("op01", "작업자A", UserRole::Operator);
}

bool UserManager::AddUser(const std::string& id, const std::string& name, UserRole role) {
    if (users.find(id) != users.end()) return false;
    users[id] = { id, name, role };
    return true;
}

bool UserManager::Authenticate(const std::string& id, UserRole requiredRole) const {
    auto it = users.find(id);
    if (it == users.end()) return false;
    if (it->second.role == UserRole::Admin) return true; // 관리자는 모든 권한 허용
    return it->second.role == requiredRole;
}

const User* UserManager::GetUser(const std::string& id) const {
    auto it = users.find(id);
    if (it == users.end()) return nullptr;
    return &(it->second);
}
