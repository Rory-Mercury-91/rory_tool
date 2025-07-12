# utils/constants.py
# Constants and Configuration Module
# Created for Traducteur Ren'Py Pro v1.1.0

"""
Module contenant toutes les constantes de l'application
"""

# Version de l'application
VERSION = "1.1.0"

# Configuration pour l'envoi de logs
LOG_ENDPOINT = "https://formspree.io/f/mrbknkvn"
LOG_EMAIL = "Traduction-Rory-Mercury91@proton.me"

# Couleurs pour les thèmes
# utils/constants.py - Section THEMES corrigée

THEMES = {
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#ffffff",
        "frame_bg": "#3c3c3c", 
        "button_bg": "#3c3c3c",
        "entry_bg": "#404040",
        "entry_fg": "#ffffff",
        "select_bg": "#0078d4",
        "select_fg": "#ffffff",
        "accent": "#4CAF50",
        "warning": "#ffc107", 
        "danger": "#dc3545",
        "button_fg": "#000000"
    },
    "light": {
        # Mode "confortable" - Ni trop clair, ni trop foncé
        "bg": "#f6f6f4",           # Gris chaud très clair
        "fg": "#333333",           # Gris foncé standard
        "frame_bg": "#eeebe7",     # Beige gris clair
        "button_bg": "#eeebe7",    # Harmonisé avec frame
        "entry_bg": "#ffffff",     # Blanc pur pour le texte (lisibilité)
        "entry_fg": "#2c2c2c",     # Gris très foncé pour contraste
        "select_bg": "#4a90e2",    # Bleu plus doux
        "select_fg": "#ffffff",    # Blanc sur bleu
        "accent": "#43a047",       # Vert équilibré
        "warning": "#fb8c00",      # Orange équilibré
        "danger": "#d32f2f",       # Rouge standard
        "button_fg": "#000000"     # Noir pour lisibilité
    }
}

# Configuration des fenêtres
WINDOW_CONFIG = {
    "title": f"🎮 Traducteur Ren'Py Pro v{VERSION}",
    "geometry": "1100x700",  # MODIFIÉ : Élargi de 1000x700 à 1100x700
    "min_size": (900, 600)   # MODIFIÉ : Minimum augmenté aussi
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
    "validation_enabled": True,  # NOUVEAU : Validation activée par défaut
    "version": VERSION
}

# Noms de fichiers
FILE_NAMES = {
    "config": "config.json",
    "log": "log.txt",
    "temps": "temps.txt",
    "tutorial_flag": "tutorial_shown.flag"
}