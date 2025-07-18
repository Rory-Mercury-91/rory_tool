# utils/constants.py - STRUCTURE CORRIGÉE
# Constants and Configuration Module
# Created for RenExtract v2.5.0

"""
Module contenant toutes les constantes de l'application
"""

import os

# Version de l'application
VERSION = "2.5.0"

# ✅ CORRECTION : Dossier config renommé
FOLDERS = {
    "temp": "temporaires",
    "backup": "sauvegardes",
    "warnings": "avertissements",
    "configs": "dossier_configs"  # ✅ NOUVEAU : Renommé de "logs" à "dossier_configs"
}

# ✅ THÈMES COMPLÈTEMENT DIFFÉRENTS VISUELLEMENT
THEMES = {
    "dark": {
        # 🌙 MODE SOMBRE - Vraiment sombre
        "bg": "#252525",              # Gris plus foncé uniforme
        "fg": "#ffffff",              # Blanc pur
        "frame_bg": "#252525",        # Gris plus foncé pour les frames
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
        "bg": "#f0f0f0",              # Gris un peu plus foncé uniforme
        "fg": "#212121",              # Gris très foncé
        "frame_bg": "#f0f0f0",        # Gris un peu plus foncé pour frames
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
    "title": f"🎮 RenExtract v{VERSION}",
    "geometry": "1300x800",
    "min_size": (1300, 800)
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

# Ajout dans DEFAULT_CONFIG :
DEFAULT_CONFIG = {
    "last_directory": "",
    "auto_open_files": True,
    "dark_mode": True,
    "validation_enabled": True,
    "language": "fr",  # ✅ NOUVEAU : Langue par défaut
    "version": VERSION
}

# ✅ NOUVEAU : Configuration des notifications
NOTIFICATION_CONFIG = {
    "toast_duration": 3000,      # Durée des toasts en ms
    "reduce_popups": True,       # Réduire les popups automatiquement
    "smart_notifications": True  # Utiliser le système intelligent
}

# ✅ NOUVEAU : Messages critiques qui DOIVENT rester en popup
CRITICAL_POPUPS = [
    "fermer_application",        # Confirmation de fermeture
    "reinitialiser",            # Réinitialisation avec données
    "nettoyer_page",            # Nettoyage avec temps de session
    "validation_errors",        # Erreurs de validation importantes
    "file_corruption",          # Corruption de fichier
    "backup_restore"            # Restauration de sauvegarde
]

# ✅ NOUVEAU : Classification des messages
MESSAGE_PRIORITIES = {
    # Messages d'état (barre de statut uniquement)
    "STATUS_ONLY": [
        "extraction_progress",
        "reconstruction_progress", 
        "file_loading",
        "ready_state"
    ],
    
    # Notifications discrètes (toast)
    "TOAST": [
        "auto_open_toggle",
        "validation_toggle",
        "language_change",
        "theme_change",
        "operation_success",
        "minor_warnings"
    ],
    
    # Confirmations importantes (popup modal)
    "MODAL": [
        "quit_confirmation",
        "reset_with_data",
        "clean_with_data", 
        "critical_errors",
        "file_conflicts"
    ]
}

# ✅ NOUVEAU : Réduction intelligente des popups
POPUP_REDUCTION_RULES = {
    # Remplacer les popups d'information par des toasts
    "info_to_toast": [
        "extraction_complete",
        "reconstruction_complete",
        "auto_open_status",
        "validation_status",
        "glossary_operations"
    ],
    
    # Remplacer les avertissements mineurs par des toasts
    "warning_to_toast": [
        "drag_drop_unavailable",
        "file_format_warning",
        "minor_validation_issues"
    ],
    
    # Garder les popups critiques
    "keep_modal": [
        "quit_application",
        "data_loss_warning", 
        "file_corruption",
        "critical_validation_errors",
        "backup_operations"
    ]
}

# ✅ CORRECTION : Fichiers dans dossier_configs
FILE_NAMES = {
    "config": os.path.join(FOLDERS["configs"], "config.json"),
    "log": os.path.join(FOLDERS["configs"], "log.txt"),
    "tutorial_flag": os.path.join(FOLDERS["configs"], "tutorial_shown.flag")
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

def ensure_game_structure(game_name):
    """Crée la structure complète pour un jeu spécifique"""
    try:
        base_folders = [
            os.path.join(FOLDERS["temp"], game_name),
            os.path.join(FOLDERS["temp"], game_name, "fichiers_a_traduire"),
            os.path.join(FOLDERS["temp"], game_name, "fichiers_a_ne_pas_traduire"),
            os.path.join(FOLDERS["backup"], game_name),
            os.path.join(FOLDERS["warnings"], game_name)
        ]
        
        for folder in base_folders:
            os.makedirs(folder, exist_ok=True)
            
        return True
    except Exception:
        return False

def ensure_complete_structure():
    """Crée la structure complète organisée"""
    try:
        from utils.constants import FOLDERS
        
        # Structure de base
        base_structure = [
            FOLDERS["temp"],
            FOLDERS["backup"], 
            FOLDERS["warnings"],
            FOLDERS["configs"]  # ✅ CORRECTION : Utiliser configs au lieu de logs
        ]
        
        for folder in base_structure:
            os.makedirs(folder, exist_ok=True)
        
        print("✅ Structure de base créée:")
        print(f"📁 {FOLDERS['temp']}/")
        print(f"📁 {FOLDERS['backup']}/") 
        print(f"📁 {FOLDERS['warnings']}/")
        print(f"📁 {FOLDERS['configs']}/")  # ✅ CORRECTION
        
        return True
    except Exception as e:
        print(f"❌ Erreur création structure: {e}")
        return False