# utils/logging.py
# Logging System Module
# Created for RenExtract v2.5.0

"""
Module de gestion des logs
"""

import datetime
import os
import re
from .constants import FILE_NAMES
from utils.constants import FOLDERS

def initialize_log():
    """Initialise/réinitialise le fichier log au démarrage"""
    try:
        # Créer le dossier configs s'il n'existe pas
        log_dir = os.path.dirname(FILE_NAMES["log"])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Réinitialiser le fichier log
        with open(FILE_NAMES["log"], 'w', encoding='utf-8') as f:
            f.write(f"=== RenExtract - LOG DE SESSION ===\n")
            f.write(f"Démarrage: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
    except Exception as e:
        print(f"⚠️ Impossible d'initialiser le log: {e}")

def log_message(level, message, exception=None):
    """
    Écrit un message dans le fichier log.txt
    
    Args:
        level (str): INFO, WARNING, ERREUR
        message (str): Message à logger
        exception (Exception, optional): Exception associée
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        
        if exception:
            log_line += f" | Exception: {str(exception)}"
        
        log_line += "\n"
        
        with open(FILE_NAMES["log"], 'a', encoding='utf-8', newline='') as f:
            f.write(log_line)
            
    except:
        pass  # Échec silencieux pour éviter les boucles d'erreur

def log_performance(operation, file_name, duration, details=None):
    """
    Log les performances d'une opération
    
    Args:
        operation (str): Type d'opération (extraction, reconstruction)
        file_name (str): Nom du fichier traité
        duration (float): Durée en secondes
        details (dict, optional): Détails supplémentaires
    """
    try:
        message = f"[PERFORMANCE] {operation} - {file_name} - {duration:.2f}s"
        
        if details:
            details_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {details_str}"
        
        log_message("INFO", message)
        
    except Exception as e:
        log_message("WARNING", f"Impossible de logger la performance: {str(e)}")

def anonymize_path(path):
    """
    Anonymise les chemins personnels pour la confidentialité
    
    Args:
        path (str): Chemin à anonymiser
        
    Returns:
        str: Chemin anonymisé
    """
    if not path:
        return "chemin_non_specifie"
    
    import getpass
    username = getpass.getuser()
    anonymized = path.replace(username, "USER")
    # ✅ CORRECTION : Échapper correctement les backslashes
    anonymized = re.sub(r'[A-Z]:[\\].*?[\\]', r'X:\\...\\', anonymized)
    return anonymized

def extract_game_name(file_path):
    """✅ CORRECTION : Extrait le nom du jeu de manière fiable"""
    try:
        if not file_path:
            return "Projet_Inconnu"
        
        # Normaliser le chemin
        normalized_path = os.path.normpath(file_path)
        path_parts = normalized_path.split(os.sep)
        
        # ✅ MÉTHODE 1 : Chercher le pattern temporaires/[NOM_JEU]/
        for i, part in enumerate(path_parts):
            if part.lower() == 'temporaires' and i + 1 < len(path_parts):
                game_name = path_parts[i + 1]
                if game_name and game_name != 'fichiers_a_traduire':
            
                    return game_name
        
        # ✅ MÉTHODE 2 : Chercher un pattern de nom de jeu typique
        for part in reversed(path_parts):  # Commencer par la fin
            if (len(part) > 3 and 
                not part.lower() in ['game', 'tl', 'french', 'english', 'fichiers_a_traduire', 'fichiers_a_ne_pas_traduire'] and
                not part.lower().startswith('round') and
                (any(char in part for char in ['-', '.', '_']) or any(char.isdigit() for char in part))):
                

                return part
        
        # ✅ MÉTHODE 3 : Fallback - utiliser le nom du fichier nettoyé
        filename = os.path.basename(file_path)
        if filename.endswith('.rpy'):
            filename = filename[:-4]
        
        # Nettoyer et créer un nom acceptable
        cleaned_name = filename.replace('_', '-')
        
        return cleaned_name if cleaned_name else "Projet_Inconnu"
        
    except Exception as e:

        return "Projet_Inconnu"