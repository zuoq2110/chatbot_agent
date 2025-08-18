from fastapi import Depends, HTTPException, status
from backend.auth.jwt import get_current_user
from backend.models.user import UserResponse

def require_auth(current_user = Depends(get_current_user)):
    """
    Middleware để yêu cầu xác thực cho các endpoint được bảo vệ
    
    Args:
        current_user: Người dùng hiện tại từ token (có thể là UserResponse hoặc dict)
        
    Returns:
        Thông tin người dùng nếu đã xác thực
        
    Raises:
        HTTPException: Nếu người dùng không được xác thực
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập để sử dụng tính năng này",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user
