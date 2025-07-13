# utils/logging.py
# Logging System Module
# Created for Traducteur Ren'Py Pro v1.5.0

"""
Module de gestion des logs et de l'historique des performances
"""

import datetime
import json
import os
import re
from .constants import FILE_NAMES

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

def log_temps_performance(fichier_path, extraction_time, reconstruction_time, nb_textes, nb_asterix=0, nb_empty=0):
    """
    Enregistre les temps de performance dans temps.txt organisé par projet
    
    Args:
        fichier_path (str): Chemin du fichier traité
        extraction_time (float): Temps d'extraction
        reconstruction_time (float): Temps de reconstruction
        nb_textes (int): Nombre de textes traités
        nb_asterix (int): Nombre d'astérisques
        nb_empty (int): Nombre de textes vides
        
    Returns:
        bool: True si succès, False sinon
    """
    try:
        total_time = extraction_time + reconstruction_time
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(fichier_path)
        game_name = extract_game_name(fichier_path)
        
        # Préparer la ligne de log
        log_line = f"[{timestamp}] {filename} | Extraction: {extraction_time:.2f}s | Reconstruction: {reconstruction_time:.2f}s | Total: {total_time:.2f}s | Textes: {nb_textes}"
        
        if nb_asterix > 0:
            log_line += f" | Astérisques: {nb_asterix}"
        if nb_empty > 0:
            log_line += f" | Vides: {nb_empty}"
        
        # Lire le fichier existant
        content_lines = []
        if os.path.exists("temps.txt"):
            try:
                with open("temps.txt", 'r', encoding='utf-8') as f:
                    content_lines = f.readlines()
            except Exception as e:
                log_message("WARNING", f"Erreur lecture fichier temps existant: {e}")
                content_lines = []
        
        # Chercher si le projet existe déjà
        project_header = f"=== {game_name} ==="
        project_found = False
        project_line_index = -1
        
        for i, line in enumerate(content_lines):
            if line.strip() == project_header:
                project_found = True
                project_line_index = i
                break
        
        if project_found:
            # Ajouter à la fin de la section existante
            insert_index = len(content_lines)
            for i in range(project_line_index + 1, len(content_lines)):
                line = content_lines[i].strip()
                if line.startswith("===") or (line == "" and i + 1 < len(content_lines) and content_lines[i + 1].strip().startswith("===")):
                    insert_index = i
                    break
            
            # Insérer la nouvelle ligne
            content_lines.insert(insert_index, log_line + "\n")
        
        else:
            # Nouveau projet - ajouter à la fin
            if content_lines and not content_lines[-1].endswith('\n'):
                content_lines[-1] += '\n'
            
            if content_lines:  # Si le fichier n'est pas vide, ajouter une ligne vide avant
                content_lines.append('\n')
            
            content_lines.append(project_header + '\n')
            content_lines.append(log_line + '\n')
        
        # Écrire le fichier complet
        with open("temps.txt", 'w', encoding='utf-8') as f:
            f.writelines(content_lines)
        
        log_message("INFO", f"Temps enregistrés pour {game_name}: {total_time:.2f}s total")
        return True
        
    except Exception as e:
        log_message("ERREUR", f"Impossible d'enregistrer les temps de performance: {str(e)}", e)
        return False