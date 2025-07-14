# utils/constants.py - THÈMES CORRIGÉS
# Constants and Configuration Module
# Created for Traducteur Ren'Py Pro v1.9.0

"""
Module contenant toutes les constantes de l'application
"""

import os

# Version de l'application
VERSION = "1.8.0"

# Dossiers d'organisation
FOLDERS = {
    "temp": "temporaires",
    "backup": "sauvegardes",
    "warnings": "avertissements",
    "logs": "logs"
}

# ✅ THÈMES COMPLÈTEMENT DIFFÉRENTS VISUELLEMENT
THEMES = {
    "dark": {
        # 🌙 MODE SOMBRE - Vraiment sombre
        "bg": "#1e1e1e",              # Gris très foncé (VS Code style)
        "fg": "#ffffff",              # Blanc pur
        "frame_bg": "#2d2d2d",        # Gris foncé pour les frames
        "button_bg": "#3c3c3c",       # Gris moyen pour boutons
        "entry_bg": "#252526",        # Gris très foncé pour zone de texte
        "entry_fg": "#cccccc",        # Gris clair pour texte
        "select_bg": "#0078d4",       # Bleu Microsoft
        "select_fg": "#ffffff",       # Blanc sur sélection
        "accent": "#4CAF50",          # Vert accent
        "warning": "#ffb74d",         # Orange warning
        "danger": "#f44336",          # Rouge danger
        "button_fg": "#ffffff"        # ✅ BLANC pour boutons en mode sombre
    },
    "light": {
        # ☀️ MODE CLAIR - Vraiment clair
        "bg": "#ffffff",              # Blanc pur
        "fg": "#212121",              # Gris très foncé
        "frame_bg": "#f5f5f5",        # Gris très clair pour frames
        "button_bg": "#e0e0e0",       # Gris clair pour boutons
        "entry_bg": "#ffffff",        # Blanc pur pour zone de texte
        "entry_fg": "#212121",        # Noir pour texte
        "select_bg": "#1976d2",       # Bleu Material Design
        "select_fg": "#ffffff",       # Blanc sur sélection
        "accent": "#2e7d32",          # Vert foncé
        "warning": "#f57c00",         # Orange foncé
        "danger": "#c62828",          # Rouge foncé
        "button_fg": "#000000"        # ✅ NOIR pour boutons en mode clair
    }
}

# Configuration des fenêtres
WINDOW_CONFIG = {
    "title": f"🎮 Traducteur Ren'Py Pro v{VERSION}",
    "geometry": "1100x700",
    "min_size": (900, 600)
}

# Codes spéciaux Ren'Py à protéger
SPECIAL_CODES = [
    r'%%',           # Pourcentage littéral
    r'\\%',          # Pourcentage échappé
    r'\\n',          # Retour à la ligne
    r'\\t',          # Tabulation
    r'\\r',          # Retour chariot
    r'\\\\',         # Backslash échappé
    r'\\[a-zA-Z]',   # Autres séquences d'échappement
    r'%[a-zA-Z_][a-zA-Z0-9_]*',  # Variables Ren'Py style %variable
    r'%\([^)]+\)',   # Variables Ren'Py style %(variable)
    r'--',           # Tirets doubles
    r'—',            # Tiret cadratin
    r'–',            # Tiret demi-cadratin
    r'\.\.\.+',      # Points de suspension
]

# Ordres de protection pour les textes vides
PROTECTION_ORDER = [
    (r'\"', 'Guillemets échappés'),  # EN PREMIER !
    ('""', 'Chaînes vides'),
    ('" "', 'Un espace'),
    ('"  "', 'Deux espaces'),
    ('"   "', 'Trois espaces')
]

# Types de fichiers supportés
SUPPORTED_FILES = {
    "renpy": [("Ren'Py script", "*.rpy")],
    "text": [("Texte", "*.txt")],
    "all": [("Tous fichiers", "*.*")]
}

# Messages d'interface
MESSAGES = {
    "extraction_success": "✅ Extraction terminée en {time:.2f}s !",
    "reconstruction_success": "✅ Fichier traduit créé en {time:.2f}s",
    "no_file_loaded": "⚠️ Erreur: Chargez d'abord un fichier .rpy",
    "files_missing": "⚠️ Erreur: Fichiers manquants",
    "extraction_in_progress": "⚙️ Extraction en cours...",
    "reconstruction_in_progress": "🔧 Reconstruction en cours..."
}

# Configuration par défaut
DEFAULT_CONFIG = {
    "last_directory": "",
    "auto_open_files": True,
    "dark_mode": True,
    "validation_enabled": True,
    "version": VERSION
}

# Noms de fichiers avec chemins organisés
FILE_NAMES = {
    "config": "config.json",
    "log": os.path.join(FOLDERS["logs"], "log.txt"),
    "tutorial_flag": "tutorial_shown.flag"
}

# Fonction utilitaire pour créer les dossiers
def ensure_folders_exist():
    """Crée tous les dossiers nécessaires s'ils n'existent pas"""
    for folder_name, folder_path in FOLDERS.items():
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
        except Exception:
            pass  # Échec silencieux