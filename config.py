"""
config.py - Módulo de configuración de categorías personalizadas

Permite al usuario definir sus propias categorías y extensiones.
"""

import os
import json
from typing import Dict, Optional

# Ruta del archivo de configuración de categorías
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'categorias.json')

# Categorías por defecto
CATEGORIAS_DEFAULT = {
    'documentos': ['.pdf', '.docx', '.doc', '.txt', '.pptx', '.xlsx', '.csv'],
    'imagenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
    'multimedia': ['.mp4', '.mp3', '.avi', '.mov', '.wav', '.mkv'],
    'otros': []
}


def cargar_categorias() -> Dict:
    """
    Carga las categorías desde el archivo de configuración.
    Si no existe, retorna las categorías por defecto.

    Returns:
        Diccionario con categorías y sus extensiones
    """
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                categorias = json.load(f)
            if 'otros' not in categorias:
                categorias['otros'] = []
            return categorias
        except Exception:
            return dict(CATEGORIAS_DEFAULT)

    return dict(CATEGORIAS_DEFAULT)


def guardar_categorias(categorias_dict: Dict) -> bool:
    """
    Guarda las categorías en el archivo de configuración.

    Args:
        categorias_dict: Diccionario con categorías y listas de extensiones

    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        for cat, exts in categorias_dict.items():
            if not isinstance(cat, str) or not isinstance(exts, list):
                return False
            categorias_dict[cat] = [e.lower() if e.startswith('.') else f'.{e.lower()}' for e in exts]

        if 'otros' not in categorias_dict:
            categorias_dict['otros'] = []

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(categorias_dict, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def resetear_categorias() -> Dict:
    """
    Elimina el archivo de configuración y retorna las categorías por defecto.

    Returns:
        Diccionario con categorías por defecto
    """
    try:
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
    except Exception:
        pass
    return dict(CATEGORIAS_DEFAULT)
