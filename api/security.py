"""
SISTEMA DE SEGURANÇA DA API FASTAPI
===================================

Sistema de autenticação baseado em API Key para controle de acesso.
Implementa middleware de segurança e validação de tokens.

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader, APIKey
from typing import Optional
import logging
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import get_api_settings

# Configuração de logging
logger = logging.getLogger(__name__)

# Configuração de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração de autenticação
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
security = HTTPBearer(auto_error=False)

# Cache de API keys válidas (em produção, usar Redis ou banco)
VALID_API_KEYS = set()

def init_api_keys():
    """Inicializa as API keys válidas."""
    try:
        settings = get_api_settings()
        # Usar valor padrão se não conseguir obter as configurações
        api_key = getattr(settings, 'api_key', 'apostapro-api-key-change-in-production')
        VALID_API_KEYS.add(api_key)
        logger.info("Sistema de API Keys inicializado")
    except Exception as e:
        # Usar valor padrão em caso de erro
        VALID_API_KEYS.add('apostapro-api-key-change-in-production')
        logger.warning(f"Erro ao inicializar API Keys, usando valor padrão: {e}")

# ============================================================================
# FUNÇÕES DE VALIDAÇÃO
# ============================================================================

def verify_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """
    Verifica se a API key é válida.
    
    Args:
        api_key_header: API key do header da requisição
        
    Returns:
        str: API key válida
        
    Raises:
        HTTPException: Se a API key for inválida
    """
    if not api_key_header:
        logger.warning("Tentativa de acesso sem API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key é obrigatória. Inclua o header 'X-API-Key'",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key_header not in VALID_API_KEYS:
        logger.warning(f"Tentativa de acesso com API key inválida: {api_key_header[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    logger.debug("API key validada com sucesso")
    return api_key_header

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um token JWT de acesso.
    
    Args:
        data: Dados para incluir no token
        expires_delta: Tempo de expiração
        
    Returns:
        str: Token JWT codificado
    """
    settings = get_api_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verifica e decodifica um token JWT.
    
    Args:
        credentials: Credenciais do header Authorization
        
    Returns:
        dict: Payload do token decodificado
        
    Raises:
        HTTPException: Se o token for inválido
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorização é obrigatório",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    settings = get_api_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Erro na validação do token JWT: {e}")
        raise credentials_exception

# ============================================================================
# DEPENDÊNCIAS DE SEGURANÇA
# ============================================================================

def get_current_api_key(api_key: str = Depends(verify_api_key)) -> str:
    """
    Dependência para obter a API key atual validada.
    
    Args:
        api_key: API key validada
        
    Returns:
        str: API key atual
    """
    return api_key

def get_optional_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Dependência para obter a API key opcional (não obrigatória).
    
    Args:
        api_key: API key do header (opcional)
        
    Returns:
        Optional[str]: API key se fornecida, None caso contrário
    """
    if api_key and api_key in VALID_API_KEYS:
        return api_key
    return None

# ============================================================================
# MIDDLEWARE DE RATE LIMITING
# ============================================================================

class RateLimitMiddleware:
    """Middleware para controle de rate limiting."""
    
    def __init__(self):
        self.requests = {}  # Em produção, usar Redis
        self.settings = get_api_settings()
    
    def is_rate_limited(self, client_ip: str, api_key: Optional[str] = None) -> bool:
        """
        Verifica se o cliente excedeu o rate limit.
        
        Args:
            client_ip: IP do cliente
            api_key: API key (se fornecida)
            
        Returns:
            bool: True se excedeu o limite
        """
        now = datetime.now()
        key = f"{client_ip}:{api_key}" if api_key else client_ip
        
        # Limpar requisições antigas
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if (now - req_time).seconds < self.settings.api_rate_limit_period
            ]
        else:
            self.requests[key] = []
        
        # Verificar limite
        if len(self.requests[key]) >= self.settings.api_rate_limit:
            logger.warning(f"Rate limit excedido para {key}")
            return True
        
        # Adicionar requisição atual
        self.requests[key].append(now)
        return False
    
    def get_rate_limit_info(self, client_ip: str, api_key: Optional[str] = None) -> dict:
        """
        Obtém informações sobre o rate limit atual.
        
        Args:
            client_ip: IP do cliente
            api_key: API key (se fornecida)
            
        Returns:
            dict: Informações do rate limit
        """
        key = f"{client_ip}:{api_key}" if api_key else client_ip
        current_requests = len(self.requests.get(key, []))
        
        return {
            "limit": self.settings.api_rate_limit,
            "remaining": max(0, self.settings.api_rate_limit - current_requests),
            "reset_in": self.settings.api_rate_limit_period,
            "current": current_requests
        }

# Instância global do rate limiter
rate_limiter = RateLimitMiddleware()

# ============================================================================
# FUNÇÕES DE UTILIDADE
# ============================================================================

def hash_password(password: str) -> str:
    """
    Gera hash de uma senha.
    
    Args:
        password: Senha em texto plano
        
    Returns:
        str: Hash da senha
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash.
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha
        
    Returns:
        bool: True se a senha estiver correta
    """
    return pwd_context.verify(plain_password, hashed_password)

def add_api_key(api_key: str) -> bool:
    """
    Adiciona uma nova API key válida.
    
    Args:
        api_key: Nova API key
        
    Returns:
        bool: True se adicionada com sucesso
    """
    if api_key and len(api_key) >= 10:
        VALID_API_KEYS.add(api_key)
        logger.info(f"Nova API key adicionada: {api_key[:10]}...")
        return True
    return False

def remove_api_key(api_key: str) -> bool:
    """
    Remove uma API key válida.
    
    Args:
        api_key: API key para remover
        
    Returns:
        bool: True se removida com sucesso
    """
    if api_key in VALID_API_KEYS:
        VALID_API_KEYS.remove(api_key)
        logger.info(f"API key removida: {api_key[:10]}...")
        return True
    return False

def get_api_keys_count() -> int:
    """
    Retorna o número de API keys válidas.
    
    Returns:
        int: Número de API keys
    """
    return len(VALID_API_KEYS)

# Inicializar API keys na importação
init_api_keys()
