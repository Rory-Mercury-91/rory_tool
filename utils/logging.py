# utils/logging.py
# Logging System Module
# Created for Traducteur Ren'Py Pro v1.1.0

"""
Module de gestion des logs et de l'historique des performances
"""

import datetime
import json
import os
import re
import urllib.request
import urllib.parse
from .constants import FILE_NAMES, LOG_ENDPOINT, LOG_EMAIL

# Variable globale pour tracker les erreurs
errors_occurred = False

def log_message(level, message, exception=None):
    """
    Écrit un message dans le fichier log.txt
    
    Args:
        level (str): INFO, WARNING, ERREUR
        message (str): Message à logger
        exception (Exception, optional): Exception associée
    """
    global errors_occurred
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        
        if exception:
            log_line += f" | Exception: {str(exception)}"
            if level == "ERREUR":
                errors_occurred = True
        
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
        
        log_line += "\n"
        
        # Lire le fichier existant pour voir si le projet existe déjà
        temps_content = ""
        if os.path.exists(FILE_NAMES["temps"]):
            with open(FILE_NAMES["temps"], 'r', encoding='utf-8') as f:
                temps_content = f.read()
        
        # Chercher si le projet existe déjà
        project_pattern = rf"^{re.escape(game_name)} - "
        project_found = False
        
        if temps_content and re.search(project_pattern, temps_content, re.MULTILINE):
            # Projet existant - calculer l'écart de temps
            project_found = True
            
            # Trouver la dernière date du projet
            project_lines = []
            in_project = False
            
            for line in temps_content.split('\n'):
                if re.match(project_pattern, line):
                    in_project = True
                    project_lines.append(line)
                elif line.startswith('---') and in_project:
                    project_lines.append(line)
                elif in_project and line.strip() and not line.startswith('['):
                    in_project = False
                    break
                elif in_project and line.startswith('['):
                    project_lines.append(line)
            
            # Extraire la dernière date
            last_date = None
            for line in reversed(project_lines):
                if line.startswith('['):
                    try:
                        date_match = re.search(r'\[(\d{4}-\d{2}-\d{2})', line)
                        if date_match:
                            last_date = datetime.datetime.strptime(date_match.group(1), '%Y-%m-%d')
                            break
                    except:
                        pass
            
            # Calculer l'écart
            current_date = datetime.datetime.now()
            if last_date:
                delta = current_date - last_date
                if delta.days > 0:
                    if delta.days >= 30:
                        months = delta.days // 30
                        time_diff = f"{months} mois plus tard" if months > 1 else "1 mois plus tard"
                    else:
                        time_diff = f"{delta.days} jours plus tard" if delta.days > 1 else "le lendemain"
                else:
                    time_diff = "même jour"
            else:
                time_diff = "nouvelle session"
            
            # Ajouter à la section existante
            session_header = f"\n--- Session du: {current_date.strftime('%Y-%m-%d')} ({time_diff}) ---\n"
            
            # Trouver où insérer dans le projet existant
            lines = temps_content.split('\n')
            new_content = []
            project_end_found = False
            
            for i, line in enumerate(lines):
                new_content.append(line)
                
                # Si on est dans le bon projet et qu'on trouve la fin
                if re.match(project_pattern, line):
                    # Chercher la fin de cette section de projet
                    j = i + 1
                    while j < len(lines):
                        if lines[j].strip() == "" and j + 1 < len(lines) and not lines[j + 1].startswith('[') and not lines[j + 1].startswith('---'):
                            # Fin de section trouvée
                            new_content.append(session_header)
                            new_content.append(log_line.rstrip())
                            project_end_found = True
                            break
                        elif j == len(lines) - 1:
                            # Fin de fichier
                            new_content.append(session_header)
                            new_content.append(log_line.rstrip())
                            project_end_found = True
                            break
                        j += 1
                    
                    if project_end_found:
                        # Ajouter le reste du fichier
                        new_content.extend(lines[j:])
                        break
            
            temps_content = '\n'.join(new_content)
        
        else:
            # Nouveau projet
            current_date = datetime.datetime.now()
            project_header = f"\n{game_name} - Première session: {current_date.strftime('%Y-%m-%d')}\n"
            
            if temps_content and not temps_content.endswith('\n'):
                temps_content += '\n'
            
            temps_content += project_header + log_line
        
        # Écrire le fichier mis à jour
        with open(FILE_NAMES["temps"], 'w', encoding='utf-8', newline='') as f:
            f.write(temps_content)
            
        log_message("INFO", f"Temps enregistrés pour {game_name}: {total_time:.2f}s total")
        return True
        
    except Exception as e:
        log_message("ERREUR", f"Impossible d'enregistrer les temps de performance", e)
        return False

def envoyer_logs_erreurs():
    """
    Propose d'envoyer les logs d'erreurs si des erreurs se sont produites
    """
    global errors_occurred
    
    if not errors_occurred or not os.path.exists(FILE_NAMES["log"]):
        return
    
    try:
        # Demander à l'utilisateur s'il veut envoyer les logs
        import tkinter.messagebox as messagebox
        
        result = messagebox.askyesno(
            "📤 Envoi de logs d'erreurs",
            "Des erreurs ont été détectées pendant l'utilisation.\n\n"
            "Voulez-vous envoyer anonymement les logs d'erreurs\n"
            "pour aider à améliorer l'application ?\n\n"
            "⚠️ Aucune information personnelle ne sera transmise."
        )
        
        if not result:
            return
        
        # Lire le fichier de log
        with open(FILE_NAMES["log"], 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Préparer les données pour l'envoi
        data = {
            'email': LOG_EMAIL,
            'subject': f'Logs d\'erreurs Traducteur Ren\'Py - {datetime.datetime.now().strftime("%Y-%m-%d")}',
            'message': f'Logs automatiques:\n\n{log_content}'
        }
        
        # Encoder les données
        data_encoded = urllib.parse.urlencode(data).encode('utf-8')
        
        # Créer la requête
        req = urllib.request.Request(LOG_ENDPOINT, data=data_encoded, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        # Envoyer avec timeout
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                messagebox.showinfo("✅ Succès", "Logs envoyés avec succès.\nMerci pour votre contribution !")
            else:
                messagebox.showwarning("⚠️ Attention", "Impossible d'envoyer les logs.")
                
    except Exception as e:
        log_message("WARNING", "Impossible d'envoyer les logs d'erreurs", e)
        # Ne pas afficher d'erreur à l'utilisateur pour éviter la frustration