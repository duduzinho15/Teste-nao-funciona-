"""
Dependências da API
==================

Este módulo contém as dependências compartilhadas entre os roteadores da API,
como conexões com o banco de dados e autenticação de usuários.

Autor: Sistema de API RESTful
Data: 2025-08-06
Versão: 1.0
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

# Importações locais
from .config import get_api_settings
from .schemas import TokenData, UserInDB
from Coleta_de_dados.database.config import SessionLocal
from Coleta_de_dados.database.models import User

# Configurações
settings = get_api_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def get_db() -> Generator[Session, None, None]:
    """
    Fornece uma sessão do banco de dados para cada requisição.
    
    Yields:
        Session: Sessão do banco de dados SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtém o usuário atual com base no token JWT.
    
    Args:
        token: Token JWT do cabeçalho de autorização
        db: Sessão do banco de dados
        
    Returns:
        User: Instância do usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica se o usuário atual está ativo.
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        User: Usuário ativo
        
    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user
