# core/file_manager.py
# File Management Module
# Created for Traducteur Ren'Py Pro v2.3.0

"""
Module de gestion des fichiers et opérations système
"""

import os
import sys
import subprocess
import glob
from utils.logging import log_message, anonymize_path
from utils.config import config_manager

class FileManager:
    """Gestionnaire de fichiers pour le Traducteur Ren'Py Pro"""
    
    def __init__(self):
        self.opened_files = set()
        self.selected_folder_path = ""
        self.is_folder_mode = False
    
    def open_single_file(self, initial_dir=None):
        """
        Ouvre un fichier .rpy unique
        
        Args:
            initial_dir (str, optional): Dossier initial
            
        Returns:
            str: Chemin du fichier sélectionné ou None
        """
        try:
            from tkinter import filedialog
            
            # Utiliser le dernier dossier si disponible
            if not initial_dir:
                initial_dir = config_manager.get_last_directory()
                if not initial_dir or not os.path.exists(initial_dir):
                    initial_dir = None
            
            filepath = filedialog.askopenfilename(
                title="📂 Sélectionnez votre fichier .rpy",
                filetypes=[("Ren'Py script", "*.rpy"), ("Tous fichiers", "*.*")],
                initialdir=initial_dir
            )
            
            if filepath:
                # Sauvegarder le dossier pour la prochaine fois
                config_manager.set_last_directory(filepath)
                self.is_folder_mode = False
                
                log_message("INFO", f"Fichier unique ouvert: {anonymize_path(filepath)}")
                return filepath
            
            return None
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors de l'ouverture du fichier unique", e)
            raise
    
    def open_folder(self, initial_dir=None):
        """
        Ouvre un dossier contenant des fichiers .rpy
        
        Args:
            initial_dir (str, optional): Dossier initial
            
        Returns:
            dict: Informations sur le dossier et les fichiers
        """
        try:
            from tkinter import filedialog, messagebox
            
            # Utiliser le dernier dossier si disponible
            if not initial_dir:
                initial_dir = config_manager.get_last_directory()
                if not initial_dir or not os.path.exists(initial_dir):
                    initial_dir = None
            
            folder_path = filedialog.askdirectory(
                title="📁 Sélectionnez un dossier contenant les fichiers .rpy",
                initialdir=initial_dir
            )
            
            if not folder_path:
                return None
            
            # Sauvegarder le dossier
            config_manager.set_last_directory(folder_path + "/dummy.rpy")
            
            self.selected_folder_path = folder_path
            self.is_folder_mode = True
            self.opened_files.clear()
            
            # Chercher les fichiers .rpy
            rpy_files = glob.glob(os.path.join(folder_path, "*.rpy"))
            
            if not rpy_files:
                log_message("WARNING", f"Aucun fichier .rpy trouvé dans {anonymize_path(folder_path)}")
                messagebox.showwarning("⚠️ Attention", "Aucun fichier .rpy trouvé dans ce dossier.")
                return None
            
            result = {
                'folder_path': folder_path,
                'files': rpy_files,
                'total_files': len(rpy_files),
                'current_file': None
            }
            
            # Ouvrir le premier fichier
            if rpy_files:
                first_file = rpy_files[0]
                self.opened_files.add(first_file)
                result['current_file'] = first_file
            
            log_message("INFO", f"Mode dossier activé: {len(rpy_files)} fichiers trouvés dans {anonymize_path(folder_path)}")
            return result
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors de l'ouverture du dossier", e)
            raise
    
    def get_next_file(self):
        """
        Récupère le prochain fichier dans le mode dossier
        
        Returns:
            str: Chemin du prochain fichier ou None si terminé
        """
        if not self.is_folder_mode or not self.selected_folder_path:
            return None
        
        # Chercher le prochain fichier .rpy non ouvert
        rpy_files = glob.glob(os.path.join(self.selected_folder_path, "*.rpy"))
        available_files = [f for f in rpy_files if f not in self.opened_files]
        
        if available_files:
            next_file = available_files[0]
            self.opened_files.add(next_file)
            
            remaining = len(available_files) - 1
            log_message("INFO", f"Fichier suivant ouvert: {anonymize_path(next_file)} ({remaining} restants)")
            
            return {
                'file': next_file,
                'remaining': remaining
            }
        
        return None
    
    def get_folder_status(self):
        """
        Récupère le statut du mode dossier
        
        Returns:
            dict: Informations sur l'état du dossier
        """
        if not self.is_folder_mode:
            return None
        
        total_files = len(glob.glob(os.path.join(self.selected_folder_path, "*.rpy")))
        processed_files = len(self.opened_files)
        remaining_files = total_files - processed_files
        
        return {
            'total': total_files,
            'processed': processed_files,
            'remaining': remaining_files,
            'folder_path': self.selected_folder_path
        }
    
    def reset(self):
        """Remet à zéro le gestionnaire de fichiers"""
        self.opened_files.clear()
        self.selected_folder_path = ""
        self.is_folder_mode = False
        log_message("INFO", "Gestionnaire de fichiers réinitialisé")
    
    def load_file_content(self, filepath):
        """
        Charge le contenu d'un fichier
        
        Args:
            filepath (str): Chemin du fichier
            
        Returns:
            list: Lignes du fichier
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.readlines()
            
            log_message("INFO", f"Fichier chargé: {len(content)} lignes - {anonymize_path(filepath)}")
            return content
            
        except Exception as e:
            log_message("ERREUR", f"Impossible de charger le fichier {anonymize_path(filepath)}", e)
            raise

class FileOpener:
    """Gestionnaire d'ouverture automatique des fichiers"""
    
    @staticmethod
    def open_files(file_list, auto_open_enabled=True):
        """
        Ouvre une liste de fichiers selon les préférences
        
        Args:
            file_list (list): Liste des fichiers à ouvrir
            auto_open_enabled (bool): Si l'ouverture automatique est activée
        """
        if not auto_open_enabled:
            log_message("INFO", "Auto-ouverture désactivée - Fichiers non ouverts automatiquement")
            return
        
        if not file_list:
            return
        
        try:
            for filepath in file_list:
                if filepath and os.path.exists(filepath):
                    FileOpener._open_single_file(filepath)
                    
            log_message("INFO", f"Fichiers ouverts automatiquement: {len(file_list)}")
            
        except Exception as e:
            log_message("WARNING", "Impossible d'ouvrir automatiquement les fichiers", e)
    
    @staticmethod
    def _open_single_file(filepath):
        """
        Ouvre un fichier unique avec l'application par défaut
        
        Args:
            filepath (str): Chemin du fichier à ouvrir
        """
        try:
            if os.name == 'nt':  # Windows
                os.startfile(filepath)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', filepath])
            else:  # Linux et autres Unix
                subprocess.call(['xdg-open', filepath])
                
        except Exception as e:
            log_message("WARNING", f"Impossible d'ouvrir {filepath}", e)

class ProjectManager:
    """Gestionnaire de projets pour le multi-projets"""
    
    def __init__(self):
        self.active_projects = {}
    
    def register_project(self, filepath, project_data):
        """
        Enregistre un projet actif
        
        Args:
            filepath (str): Chemin du fichier principal
            project_data (dict): Données du projet
        """
        project_key = os.path.dirname(filepath)
        self.active_projects[project_key] = {
            'main_file': filepath,
            'data': project_data,
            'timestamp': os.path.getmtime(filepath)
        }
        
        log_message("INFO", f"Projet enregistré: {anonymize_path(project_key)}")
    
    def get_project_info(self, filepath):
        """
        Récupère les informations d'un projet
        
        Args:
            filepath (str): Chemin d'un fichier du projet
            
        Returns:
            dict: Informations du projet ou None
        """
        project_key = os.path.dirname(filepath)
        return self.active_projects.get(project_key)
    
    def cleanup_old_projects(self, max_age_hours=24):
        """
        Nettoie les anciens projets de la mémoire
        
        Args:
            max_age_hours (int): Âge maximum en heures
        """
        import time
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        to_remove = []
        for project_key, project_info in self.active_projects.items():
            if project_info['timestamp'] < cutoff_time:
                to_remove.append(project_key)
        
        for project_key in to_remove:
            del self.active_projects[project_key]
        
        if to_remove:
            log_message("INFO", f"Nettoyage: {len(to_remove)} anciens projets supprimés")

class TempFileManager:
    """Gestionnaire des fichiers temporaires"""
    
    @staticmethod
    def list_temp_files(pattern="*_mapping.txt"):
        """
        Liste les fichiers temporaires correspondant au pattern
        
        Args:
            pattern (str): Pattern de recherche
            
        Returns:
            list: Liste des fichiers temporaires trouvés
        """
        try:
            temp_files = glob.glob(pattern)
            temp_files.extend(glob.glob("*_positions.json"))
            temp_files.extend(glob.glob("*_asterix_mapping.txt"))
            temp_files.extend(glob.glob("*_empty_mapping.txt"))
            
            return list(set(temp_files))  # Supprimer les doublons
            
        except Exception as e:
            log_message("WARNING", "Erreur lors de la liste des fichiers temporaires", e)
            return []
    
    @staticmethod
    def cleanup_temp_files(file_base=None):
        """
        Nettoie les fichiers temporaires
        
        Args:
            file_base (str, optional): Base spécifique à nettoyer
        """
        try:
            if file_base:
                # Nettoyer pour un projet spécifique
                patterns = [
                    f"{file_base}_mapping.txt",
                    f"{file_base}_positions.json", 
                    f"{file_base}_asterix_mapping.txt",
                    f"{file_base}_empty_mapping.txt"
                ]
            else:
                # Nettoyer tous les fichiers temporaires
                patterns = [
                    "*_mapping.txt",
                    "*_positions.json",
                    "*_asterix_mapping.txt", 
                    "*_empty_mapping.txt"
                ]
            
            cleaned_files = []
            for pattern in patterns:
                files = glob.glob(pattern)
                for file in files:
                    try:
                        os.remove(file)
                        cleaned_files.append(file)
                    except:
                        pass
            
            if cleaned_files:
                log_message("INFO", f"Fichiers temporaires nettoyés: {len(cleaned_files)}")
            
            return cleaned_files
            
        except Exception as e:
            log_message("WARNING", "Erreur lors du nettoyage des fichiers temporaires", e)
            return []

# Utilitaires
def ensure_directory_exists(directory):
    """
    S'assure qu'un dossier existe, le crée sinon
    
    Args:
        directory (str): Chemin du dossier
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            log_message("INFO", f"Dossier créé: {anonymize_path(directory)}")
    except Exception as e:
        log_message("WARNING", f"Impossible de créer le dossier {anonymize_path(directory)}", e)

def get_file_info(filepath):
    """
    Récupère les informations détaillées d'un fichier
    
    Args:
        filepath (str): Chemin du fichier
        
    Returns:
        dict: Informations du fichier
    """
    try:
        stats = os.stat(filepath)
        return {
            'size': stats.st_size,
            'size_mb': round(stats.st_size / (1024 * 1024), 2),
            'modified': stats.st_mtime,
            'created': stats.st_ctime,
            'exists': True,
            'readable': os.access(filepath, os.R_OK),
            'writable': os.access(filepath, os.W_OK)
        }
    except Exception as e:
        return {
            'exists': False,
            'error': str(e)
        }

# Instance globale du gestionnaire de fichiers
file_manager = FileManager()
project_manager = ProjectManager()