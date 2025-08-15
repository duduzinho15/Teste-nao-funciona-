#!/usr/bin/env python3
"""
Configuração simples para o sistema ML
"""
import os
from pathlib import Path

def get_ml_config():
    """Retorna configuração básica do sistema ML"""
    class Config:
        def __init__(self):
            self.data_dir = Path(__file__).parent / "data"
            self.cache_dir = Path(__file__).parent / "cache"
            self.monitoring_dir = Path(__file__).parent / "monitoring"
            self.models_dir = Path(__file__).parent / "saved_models"
            
            # Criar diretórios se não existirem
            self.data_dir.mkdir(exist_ok=True)
            self.cache_dir.mkdir(exist_ok=True)
            self.monitoring_dir.mkdir(exist_ok=True)
            self.models_dir.mkdir(exist_ok=True)
    
    return Config()

# Configuração global
ml_config = get_ml_config()
