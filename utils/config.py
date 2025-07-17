# utils/config.py
# Configuration Management Module
# Created for Traducteur Ren'Py Pro v2.4.4

"""
Module de gestion de la configuration et des préférences utilisateur
"""

import json
import os
from .constants import DEFAULT_CONFIG, FILE_NAMES, VERSION, FOLDERS, ensure_folders_exist
from .logging import log_message

class ConfigManager:
    """Gestionnaire de configuration de l'application"""
    
    def __init__(self):
        # ✅ CORRECTION : S'assurer que le dossier configs existe
        ensure_folders_exist()
        
        self.config_file = FILE_NAMES["config"]
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    log_message("INFO", f"Configuration chargée: {self.anonymize_path(self.config.get('last_directory', ''))}")
            else:
                # Créer un fichier de config par défaut
                self.save_config()
                log_message("INFO", "Configuration par défaut créée")
        except Exception as e:
            log_message("WARNING", "Impossible de charger la configuration", e)
            self.config = DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Sauvegarde la configuration dans le fichier JSON"""
        try:
            # ✅ CORRECTION : S'assurer que le dossier existe avant de sauvegarder
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            # Mettre à jour la version
            self.config["version"] = VERSION
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            log_message("INFO", f"Configuration v{VERSION} sauvegardée dans {FOLDERS['configs']}")
        except Exception as e:
            log_message("WARNING", "Impossible de sauvegarder la configuration", e)
    
    def get(self, key, default=None):
        """Récupère une valeur de configuration"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Définit une valeur de configuration et sauvegarde"""
        self.config[key] = value
        self.save_config()
    
    def get_last_directory(self):
        """Récupère le dernier dossier utilisé"""
        return self.config.get("last_directory", "")
    
    def set_last_directory(self, filepath):
        """Définit le dernier dossier utilisé depuis un chemin de fichier"""
        if filepath:
            directory = os.path.dirname(filepath)
            self.set("last_directory", directory)
            log_message("INFO", f"Dossier mémorisé: {self.anonymize_path(directory)}")
    
    def is_auto_open_enabled(self):
        """Vérifie si l'ouverture automatique est activée"""
        return self.config.get("auto_open_files", True)
    
    def toggle_auto_open(self):
        """Bascule l'option d'ouverture automatique"""
        current = self.is_auto_open_enabled()
        self.set("auto_open_files", not current)
        return not current

    def is_validation_enabled(self):
        """Vérifie si la validation est activée"""
        return self.config.get("validation_enabled", True)

    def toggle_validation(self):
        """Bascule l'option de validation"""
        current = self.is_validation_enabled()
        self.set("validation_enabled", not current)
        return not current

    def is_dark_mode_enabled(self):
        """Vérifie si le mode sombre est activé"""
        return self.config.get("dark_mode", True)
    
    def toggle_dark_mode(self):
        """Bascule le mode sombre"""
        current = self.is_dark_mode_enabled()
        self.set("dark_mode", not current)
        return not current
    
    @staticmethod
    def anonymize_path(path):
        """Anonymise les chemins personnels pour la confidentialité"""
        if not path:
            return "chemin_non_specifie"
        
        import getpass
        import re
        username = getpass.getuser()
        anonymized = path.replace(username, "USER")
        anonymized = re.sub(r'[A-Z]:\\.*?\\', r'X:\\...\\', anonymized)
        return anonymized

# Instance globale du gestionnaire de configuration
config_manager = ConfigManager()