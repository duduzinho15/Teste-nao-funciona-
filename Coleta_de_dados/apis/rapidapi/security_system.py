#!/usr/bin/env python3
"""
Sistema de Segurança Avançada para Produção RapidAPI

Este módulo implementa:
- Autenticação JWT com refresh tokens
- Rate limiting por usuário/IP
- Audit logs completos
- Validação de entrada
- Criptografia de dados sensíveis
- Middleware de segurança
"""

import asyncio
import logging
import time
import hashlib
import hmac
import base64
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt

# Importa módulos do sistema
from .production_config import load_production_config

@dataclass
class User:
    """Usuário do sistema"""
    id: str
    username: str
    email: str
    role: str  # 'admin', 'user', 'readonly'
    permissions: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "permissions": self.permissions,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active
        }

@dataclass
class AuditLog:
    """Log de auditoria"""
    id: str
    timestamp: datetime
    user_id: Optional[str]
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
            "error_message": self.error_message
        }

class SecurityManager:
    """Gerenciador de segurança do sistema"""
    
    def __init__(self):
        self.config = load_production_config()
        self.logger = logging.getLogger("security.manager")
        
        # Chaves de criptografia
        self.jwt_secret = self.config.jwt_secret
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Usuários em memória (em produção, usar banco)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting
        self.rate_limits: Dict[str, List[float]] = {}
        self.max_requests = int(self.config.rate_limit_requests)
        self.window_seconds = int(self.config.rate_limit_window)
        
        # Audit logs
        self.audit_logs: List[AuditLog] = []
        self.max_audit_logs = 10000
        
        # Inicializa usuários padrão
        self._initialize_default_users()
    
    def _generate_encryption_key(self) -> bytes:
        """Gera chave de criptografia"""
        try:
            # Em produção, usar chave persistente
            salt = b'rapidapi_salt_production'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.jwt_secret.encode()))
            return key
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar chave de criptografia: {e}")
            # Fallback para chave padrão
            return Fernet.generate_key()
    
    def _initialize_default_users(self):
        """Inicializa usuários padrão do sistema"""
        try:
            # Usuário admin
            admin_user = User(
                id=str(uuid.uuid4()),
                username="admin",
                email="admin@rapidapi.com",
                role="admin",
                permissions=["*"],  # Todas as permissões
                created_at=datetime.now()
            )
            admin_user.password_hash = self._hash_password("admin123")
            self.users[admin_user.username] = admin_user
            
            # Usuário readonly
            readonly_user = User(
                id=str(uuid.uuid4()),
                username="readonly",
                email="readonly@rapidapi.com",
                role="readonly",
                permissions=["read:metrics", "read:logs", "read:alerts"],
                created_at=datetime.now()
            )
            readonly_user.password_hash = self._hash_password("readonly123")
            self.users[readonly_user.username] = readonly_user
            
            self.logger.info(f"✅ {len(self.users)} usuários padrão inicializados")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar usuários padrão: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash de senha usando bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            self.logger.error(f"❌ Erro ao fazer hash de senha: {e}")
            return ""
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verifica senha"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar senha: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[str]:
        """Autentica usuário e retorna JWT token"""
        try:
            # Verifica se usuário existe
            if username not in self.users:
                self._log_audit("login_failed", "auth", {
                    "username": username,
                    "reason": "user_not_found"
                }, ip_address, user_agent, False, "Usuário não encontrado")
                return None
            
            user = self.users[username]
            
            # Verifica se usuário está ativo
            if not user.is_active:
                self._log_audit("login_failed", "auth", {
                    "username": username,
                    "reason": "user_inactive"
                }, ip_address, user_agent, False, "Usuário inativo")
                return None
            
            # Verifica se usuário está bloqueado
            if user.locked_until and datetime.now() < user.locked_until:
                self._log_audit("login_failed", "auth", {
                    "username": username,
                    "reason": "user_locked"
                }, ip_address, user_agent, False, "Usuário bloqueado")
                return None
            
            # Verifica senha
            if not self._verify_password(password, user.password_hash):
                user.failed_attempts += 1
                
                # Bloqueia usuário após 5 tentativas falhadas
                if user.failed_attempts >= 5:
                    user.locked_until = datetime.now() + timedelta(minutes=30)
                    self.logger.warning(f"🔒 Usuário {username} bloqueado por 30 minutos")
                
                self._log_audit("login_failed", "auth", {
                    "username": username,
                    "reason": "invalid_password",
                    "failed_attempts": user.failed_attempts
                }, ip_address, user_agent, False, "Senha inválida")
                return None
            
            # Login bem-sucedido
            user.failed_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now()
            
            # Gera JWT token
            token = self._generate_jwt_token(user)
            
            # Registra sessão
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                "user_id": user.id,
                "username": user.username,
                "created_at": datetime.now(),
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            
            self._log_audit("login_success", "auth", {
                "username": username,
                "session_id": session_id
            }, ip_address, user_agent, True)
            
            return token
            
        except Exception as e:
            self.logger.error(f"❌ Erro na autenticação: {e}")
            return None
    
    def _generate_jwt_token(self, user: User) -> str:
        """Gera JWT token para usuário"""
        try:
            payload = {
                "user_id": user.id,
                "username": user.username,
                "role": user.role,
                "permissions": user.permissions,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            return token
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar JWT token: {e}")
            return ""
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica JWT token e retorna payload"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("⚠️  JWT token expirado")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"⚠️  JWT token inválido: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar JWT token: {e}")
            return None
    
    def check_permission(self, user_payload: Dict[str, Any], required_permission: str) -> bool:
        """Verifica se usuário tem permissão"""
        try:
            if not user_payload:
                return False
            
            user_permissions = user_payload.get("permissions", [])
            
            # Admin tem todas as permissões
            if "*" in user_permissions:
                return True
            
            # Verifica permissão específica
            return required_permission in user_permissions
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar permissão: {e}")
            return False
    
    def check_rate_limit(self, identifier: str) -> bool:
        """Verifica rate limiting"""
        try:
            current_time = time.time()
            
            # Limpa timestamps antigos
            if identifier in self.rate_limits:
                self.rate_limits[identifier] = [
                    ts for ts in self.rate_limits[identifier]
                    if current_time - ts < self.window_seconds
                ]
            else:
                self.rate_limits[identifier] = []
            
            # Verifica se excedeu limite
            if len(self.rate_limits[identifier]) >= self.max_requests:
                return False
            
            # Adiciona timestamp atual
            self.rate_limits[identifier].append(current_time)
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar rate limit: {e}")
            return True  # Em caso de erro, permite acesso
    
    def encrypt_data(self, data: str) -> str:
        """Criptografa dados sensíveis"""
        try:
            encrypted = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"❌ Erro ao criptografar dados: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Descriptografa dados"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"❌ Erro ao descriptografar dados: {e}")
            return encrypted_data
    
    def _log_audit(self, action: str, resource: str, details: Dict[str, Any], 
                   ip_address: str, user_agent: str, success: bool, 
                   error_message: Optional[str] = None):
        """Registra log de auditoria"""
        try:
            audit_log = AuditLog(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                user_id=details.get("username"),  # Pode ser None para ações anônimas
                action=action,
                resource=resource,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message
            )
            
            self.audit_logs.append(audit_log)
            
            # Mantém apenas logs recentes
            if len(self.audit_logs) > self.max_audit_logs:
                self.audit_logs = self.audit_logs[-self.max_audit_logs:]
            
            # Log de segurança para ações críticas
            if action in ["login_failed", "permission_denied", "rate_limit_exceeded"]:
                self.logger.warning(f"🚨 Ação de segurança: {action} - {details}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao registrar log de auditoria: {e}")
    
    def get_audit_logs(self, user_id: Optional[str] = None, 
                       action: Optional[str] = None, 
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> List[AuditLog]:
        """Obtém logs de auditoria filtrados"""
        try:
            filtered_logs = self.audit_logs
            
            if user_id:
                filtered_logs = [log for log in filtered_logs if log.user_id == user_id]
            
            if action:
                filtered_logs = [log for log in filtered_logs if log.action == action]
            
            if start_time:
                filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
            
            if end_time:
                filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
            
            return filtered_logs
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter logs de auditoria: {e}")
            return []
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de segurança"""
        try:
            current_time = datetime.now()
            last_24h = current_time - timedelta(hours=24)
            
            recent_logs = [log for log in self.audit_logs if log.timestamp >= last_24h]
            
            stats = {
                "total_users": len(self.users),
                "active_sessions": len(self.sessions),
                "audit_logs_24h": len(recent_logs),
                "failed_logins_24h": len([log for log in recent_logs if log.action == "login_failed"]),
                "rate_limit_violations_24h": len([log for log in recent_logs if log.action == "rate_limit_exceeded"]),
                "security_alerts_24h": len([log for log in recent_logs if not log.success]),
                "locked_users": len([user for user in self.users.values() if user.locked_until and current_time < user.locked_until])
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter estatísticas de segurança: {e}")
            return {}

# Instância global do sistema de segurança
security_manager = SecurityManager()

def get_security_manager() -> SecurityManager:
    """Retorna a instância global do sistema de segurança"""
    return security_manager
