from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from shared.schemas import LoginRequest, TokenResponse
from shared.models import User
from admin.core.security import hash_password, verify_password, create_access_token
from admin.api.deps import get_db
 
router = APIRouter()
 
@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login de usuario"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        email=user.email
    )
 
@router.post("/verify")
def verify_token(token: str, db: Session = Depends(get_db)):
    """Verifica si un token es válido"""
    try:
        from admin.core.security import decode_token
        payload = decode_token(token)
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        return {"valid": True, "user_id": user_id, "email": user.email}
    except HTTPException:
        raise