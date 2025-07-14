# utils/logging.py
# Logging System Module
# Created for Traducteur Ren'Py Pro v1.5.0

"""
Module de gestion des logs
"""

import datetime
import os
import re
from .constants import FILE_NAMES

def initialize_log():
    """Initialise/réinitialise le fichier log au démarrage"""
    try:
        # Créer le dossier logs s'il n'existe pas
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
    anonymized = re.sub(r'[A-Z]:\\.*?\\', r'X:\\...\\', anonymized)
    return anonymized

def extract_game_name(file_path):
    """
    Extrait le nom du jeu depuis le chemin de fichier
    
    Args:
        file_path (str): Chemin du fichier
        
    Returns:
        str: Nom du jeu formaté
    """
    try:
        # Normaliser le chemin
        normalized_path = file_path.replace('\\', '/')
        path_parts = normalized_path.split('/')
        
        # Chercher un dossier qui ressemble à un nom de jeu
        for part in reversed(path_parts):
            # Ignorer les dossiers techniques
            if part.lower() in ['game', 'tl', 'french', 'english', 'scripts', 'script']:
                continue
            if part.lower().startswith('script') or part.lower().endswith('.rpy'):
                continue
            
            # Si le dossier contient un nom de jeu potentiel
            if len(part) > 3 and not part.isdigit():
                # Nettoyer le nom (versions, caractères spéciaux)
                clean_name = re.sub(r'-v?\d+\.?\d*.*', '', part)
                clean_name = re.sub(r'[-_]', ' ', clean_name)
                
                # Capitaliser correctement
                words = clean_name.split()
                formatted_words = []
                for word in words:
                    if word.lower() in ['vn', 'rpg', 'sim']:
                        formatted_words.append(word.upper())
                    else:
                        formatted_words.append(word.capitalize())
                
                return ' '.join(formatted_words)
        
        # Fallback: utiliser le nom du fichier
        filename = os.path.basename(file_path).replace('.rpy', '')
        return filename.replace('_', ' ').title()
        
    except Exception as e:
        log_message("WARNING", f"Impossible d'extraire le nom du jeu de {anonymize_path(file_path)}", e)
        return "Projet Inconnu"

# SUPPRIMÉ: log_temps_performance() - Plus nécessaire