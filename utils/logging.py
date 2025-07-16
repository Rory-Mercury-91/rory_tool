# utils/logging.py
# Logging System Module
# Created for Traducteur Ren'Py Pro v2.2.0

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
            f.write(f"=== TRADUCTEUR REN'PY PRO - LOG DE SESSION ===\n")
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
    """
    ✅ CORRECTION : Extrait le nom du jeu principal depuis le chemin
    
    Exemple:
    C:\\Users\\Rory Mercury 91\\Documents\\GuiltyPleasure-0.49-pc\\game\\tl\\fr_zenpy_DeepL_andric31
    -> GuiltyPleasure-0.49-pc
    """
    try:
        if not file_path:
            return "Projet_Inconnu"
        
        # Normaliser le chemin
        normalized_path = os.path.normpath(file_path)
        path_parts = normalized_path.split(os.sep)
        
        # Debug : afficher le chemin pour comprendre
        log_message("DEBUG", f"Chemin analysé: {file_path}")
        log_message("DEBUG", f"Parties du chemin: {path_parts}")
        
        # Chercher le dossier principal du jeu
        # On veut trouver le dossier qui contient "game" ou "tl"
        for i, part in enumerate(path_parts):
            part_lower = part.lower()
            
            # Si on trouve "game" ou "tl", le dossier parent est le jeu
            if part_lower in ['game', 'tl']:
                if i > 0:
                    game_folder = path_parts[i - 1]
                    log_message("DEBUG", f"Nom du jeu détecté: {game_folder}")
                    return game_folder
        
        # Si pas trouvé par la méthode game/tl, chercher des patterns typiques
        for i, part in enumerate(path_parts):
            part_lower = part.lower()
            
            # Ignorer les dossiers système et utilisateur
            if part_lower in ['documents', 'desktop', 'downloads', 'users', 'program files', 'windows']:
                continue
            
            # Chercher des patterns de nom de jeu
            if (len(part) > 3 and 
                not part.isdigit() and 
                not part_lower.startswith('user') and
                not part_lower in ['game', 'tl', 'french', 'english', 'scripts', 'script']):
                
                # Vérifier si c'est probablement un nom de jeu
                if (any(char.isalpha() for char in part) and 
                    ('.' in part or '-' in part or len(part) > 5)):
                    
                    log_message("DEBUG", f"Nom du jeu détecté par pattern: {part}")
                    return part
        
        # Fallback : utiliser le nom du fichier
        filename = os.path.basename(file_path)
        if filename.endswith('.rpy'):
            filename = filename[:-4]  # Enlever .rpy
        
        log_message("DEBUG", f"Fallback nom du jeu: {filename}")
        return filename if filename else "Projet_Inconnu"
        
    except Exception as e:
        log_message("WARNING", f"Impossible d'extraire le nom du jeu de {anonymize_path(file_path)}", e)
        return "Projet_Inconnu"