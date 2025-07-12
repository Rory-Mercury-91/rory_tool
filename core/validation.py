# core/validation.py
# Validation and Security Module
# Created for Traducteur Ren'Py Pro v1.1.2

"""
Module de validation des fichiers et de sécurité
"""

import os
import re
import shutil
import datetime
from utils.logging import log_message

class FileValidator:
    """Classe pour la validation des fichiers Ren'Py"""
    
    # Patterns typiques des fichiers Ren'Py
    RENPY_PATTERNS = [
        r'label\s+\w+:',                    # Labels Ren'Py
        r'menu:',                           # Menus
        r'scene\s+\w+',                     # Changements de scène
        r'show\s+\w+',                      # Affichage de personnages
        r'hide\s+\w+',                      # Masquage de personnages
        r'\w+\s+".*"',                      # Dialogues (personnage + texte)
        r'translate\s+\w+\s+\w+:',          # Blocs de traduction
        r'old\s+".*"',                      # Anciennes traductions
        r'new\s+".*"',                      # Nouvelles traductions
        r'\$\s+.*',                         # Code Python intégré
        r'if\s+.*:',                        # Conditions
        r'jump\s+\w+',                      # Sauts
        r'call\s+\w+',                      # Appels
        r'return',                          # Retours
        r'with\s+\w+',                      # Transitions
        r'pause\s*\d*\.?\d*',               # Pauses
    ]
    
    @classmethod
    def is_renpy_file(cls, filepath):
        """
        Vérifie si un fichier est un vrai fichier Ren'Py
        
        Args:
            filepath (str): Chemin du fichier à valider
            
        Returns:
            dict: Résultat de la validation avec détails
        """
        result = {
            'is_valid': False,
            'confidence': 0,
            'patterns_found': [],
            'file_info': {},
            'warnings': [],
            'errors': []
        }
        
        try:
            # Vérifications de base
            if not os.path.exists(filepath):
                result['errors'].append("Fichier introuvable")
                return result
            
            if not filepath.lower().endswith('.rpy'):
                result['warnings'].append("Extension non .rpy")
            
            # Informations sur le fichier
            file_stats = os.stat(filepath)
            result['file_info'] = {
                'size': file_stats.st_size,
                'modified': datetime.datetime.fromtimestamp(file_stats.st_mtime),
                'encoding': 'unknown'
            }
            
            # Lecture et analyse du contenu
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                result['file_info']['encoding'] = 'utf-8'
            except UnicodeDecodeError:
                try:
                    with open(filepath, 'r', encoding='latin-1') as f:
                        content = f.read()
                    result['file_info']['encoding'] = 'latin-1'
                    result['warnings'].append("Encodage non-UTF8 détecté")
                except Exception as e:
                    result['errors'].append(f"Impossible de lire le fichier: {str(e)}")
                    return result
            
            if not content.strip():
                result['errors'].append("Fichier vide")
                return result
            
            # Analyse des patterns Ren'Py
            lines = content.split('\n')
            pattern_matches = 0
            dialogue_lines = 0
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Vérifier chaque pattern
                for pattern in cls.RENPY_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        if pattern not in result['patterns_found']:
                            result['patterns_found'].append(pattern)
                        pattern_matches += 1
                        break
                
                # Compter les lignes de dialogue potentielles
                if re.search(r'\w+\s+".*"', line) or re.search(r'".*"', line):
                    dialogue_lines += 1
            
            # Calcul de la confiance
            total_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            if total_lines > 0:
                confidence = min(100, (pattern_matches / total_lines) * 100)
                dialogue_ratio = (dialogue_lines / total_lines) * 100
                
                # Bonus pour les dialogues
                if dialogue_ratio > 10:
                    confidence += min(20, dialogue_ratio / 2)
                
                result['confidence'] = round(confidence, 1)
            
            # Déterminer la validité
            result['is_valid'] = (
                result['confidence'] > 15 and  # Au moins 15% de confiance
                len(result['patterns_found']) >= 2 and  # Au moins 2 patterns différents
                dialogue_lines > 0  # Au moins quelques dialogues
            )
            
            # Messages informatifs
            result['file_info']['total_lines'] = total_lines
            result['file_info']['dialogue_lines'] = dialogue_lines
            result['file_info']['patterns_count'] = len(result['patterns_found'])
            
            if result['confidence'] < 50:
                result['warnings'].append("Confiance faible - pourrait ne pas être un fichier Ren'Py standard")
            
            log_message("INFO", f"Validation fichier: {os.path.basename(filepath)} - Confiance: {result['confidence']}%")
            
        except Exception as e:
            result['errors'].append(f"Erreur lors de la validation: {str(e)}")
            log_message("ERREUR", f"Erreur validation fichier {filepath}", e)
        
        return result

class BackupManager:
    """Gestionnaire de sauvegardes automatiques"""
    
    @staticmethod
    def create_backup(filepath, backup_suffix=".backup"):
        """
        Crée une sauvegarde du fichier
        
        Args:
            filepath (str): Chemin du fichier à sauvegarder
            backup_suffix (str): Suffixe pour le fichier de sauvegarde
            
        Returns:
            dict: Résultat de la sauvegarde
        """
        result = {
            'success': False,
            'backup_path': None,
            'error': None
        }
        
        try:
            if not os.path.exists(filepath):
                result['error'] = "Fichier source introuvable"
                return result
            
            # Générer un nom de backup unique
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(filepath)[0]
            backup_path = f"{base_name}_{timestamp}{backup_suffix}"
            
            # Créer la sauvegarde
            shutil.copy2(filepath, backup_path)
            
            result['success'] = True
            result['backup_path'] = backup_path
            
            log_message("INFO", f"Sauvegarde créée: {os.path.basename(backup_path)}")
            
        except Exception as e:
            result['error'] = str(e)
            log_message("ERREUR", f"Impossible de créer la sauvegarde de {filepath}", e)
        
        return result
    
    @staticmethod
    def restore_backup(backup_path, original_path):
        """
        Restaure un fichier depuis sa sauvegarde
        
        Args:
            backup_path (str): Chemin de la sauvegarde
            original_path (str): Chemin du fichier à restaurer
            
        Returns:
            dict: Résultat de la restauration
        """
        result = {
            'success': False,
            'error': None
        }
        
        try:
            if not os.path.exists(backup_path):
                result['error'] = "Fichier de sauvegarde introuvable"
                return result
            
            shutil.copy2(backup_path, original_path)
            result['success'] = True
            
            log_message("INFO", f"Fichier restauré depuis: {os.path.basename(backup_path)}")
            
        except Exception as e:
            result['error'] = str(e)
            log_message("ERREUR", f"Impossible de restaurer {backup_path}", e)
        
        return result
    
    @staticmethod
    def list_backups(filepath):
        """
        Liste toutes les sauvegardes disponibles pour un fichier
        
        Args:
            filepath (str): Chemin du fichier original
            
        Returns:
            list: Liste des sauvegardes avec métadonnées
        """
        backups = []
        
        try:
            directory = os.path.dirname(filepath)
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            
            # Chercher tous les fichiers de sauvegarde
            for file in os.listdir(directory):
                if file.startswith(base_name) and 'backup' in file.lower():
                    backup_path = os.path.join(directory, file)
                    try:
                        stats = os.stat(backup_path)
                        backups.append({
                            'path': backup_path,
                            'name': os.path.basename(backup_path),
                            'size': stats.st_size,
                            'created': datetime.datetime.fromtimestamp(stats.st_ctime),
                            'modified': datetime.datetime.fromtimestamp(stats.st_mtime)
                        })
                    except:
                        continue
            
            # Trier par date de création (plus récent en premier)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            log_message("WARNING", f"Erreur lors de la liste des sauvegardes pour {filepath}", e)
        
        return backups

class TranslationValidator:
    """Validateur pour les correspondances de traduction"""
    
    @staticmethod
    def validate_file_correspondence(extracted_count, translation_file_path):
        """
        Valide qu'un fichier de traduction correspond aux textes extraits
        
        Args:
            extracted_count (int): Nombre de textes extraits
            translation_file_path (str): Chemin du fichier de traduction
            
        Returns:
            dict: Résultat de la validation
        """
        result = {
            'valid': True,
            'translation_count': 0,
            'missing_count': 0,
            'extra_count': 0,
            'empty_lines': 0,
            'warnings': [],
            'errors': []
        }
        
        try:
            if not os.path.exists(translation_file_path):
                result['valid'] = False
                result['errors'].append(f"Fichier de traduction introuvable: {translation_file_path}")
                return result
            
            # Lire le fichier de traduction
            with open(translation_file_path, 'r', encoding='utf-8') as f:
                translation_lines = f.readlines()
            
            # Analyser le contenu
            non_empty_lines = []
            empty_lines = 0
            
            for i, line in enumerate(translation_lines):
                content = line.rstrip('\n\r')
                if content.strip():
                    non_empty_lines.append((i + 1, content))
                else:
                    empty_lines += 1
            
            result['translation_count'] = len(non_empty_lines)
            result['empty_lines'] = empty_lines
            
            # Vérifier la correspondance
            if result['translation_count'] != extracted_count:
                result['valid'] = False
                
                if result['translation_count'] < extracted_count:
                    result['missing_count'] = extracted_count - result['translation_count']
                    result['errors'].append(
                        f"Traductions manquantes: {result['missing_count']} "
                        f"(attendu: {extracted_count}, trouvé: {result['translation_count']})"
                    )
                else:
                    result['extra_count'] = result['translation_count'] - extracted_count
                    result['warnings'].append(
                        f"Traductions supplémentaires: {result['extra_count']} "
                        f"(attendu: {extracted_count}, trouvé: {result['translation_count']})"
                    )
            
            # Vérifications de qualité
            if empty_lines > 0:
                result['warnings'].append(f"{empty_lines} lignes vides détectées")
            
            # Détecter les placeholders non traduits
            untranslated_count = 0
            for line_num, content in non_empty_lines:
                if re.search(r'\(\d{2}\)', content):
                    untranslated_count += 1
            
            if untranslated_count > 0:
                result['warnings'].append(
                    f"{untranslated_count} lignes contiennent encore des placeholders non traduits"
                )
            
                # SUPPRESSION de ce log verbeux :
                # log_message("INFO", f"Validation traduction: {result['translation_count']}/{extracted_count} lignes")
                
                # Le garder uniquement en cas d'erreur
                if not result['valid']:
                    log_message("WARNING", f"Validation échouée: {result['translation_count']}/{extracted_count} lignes dans {translation_file_path}")
                
                return result
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Erreur lors de la validation: {str(e)}")
            log_message("ERREUR", f"Erreur validation traduction {translation_file_path}", e)
        
        return result
    
    @staticmethod
    def validate_all_files(file_base, extracted_count, asterix_count=0, empty_count=0):
        """
        Valide tous les fichiers de traduction d'un projet
        
        Args:
            file_base (str): Nom de base du projet
            extracted_count (int): Nombre de textes principaux extraits
            asterix_count (int): Nombre d'astérisques extraites
            empty_count (int): Nombre de textes vides extraits
            
        Returns:
            dict: Résultat complet de la validation
        """
        # Initialisation complète des résultats
        validation_results = {
            'overall_valid': True,
            'main_file': None,
            'asterix_file': None,
            'empty_file': None,
            'summary': {
                'total_expected': extracted_count + asterix_count + empty_count,
                'total_found': 0,
                'files_validated': 0,
                'validation_success': True
            }
        }
        
        try:
            # Valider le fichier principal
            main_file = f"{file_base}.txt"
            if os.path.exists(main_file):
                validation_results['main_file'] = TranslationValidator.validate_file_correspondence(
                    extracted_count, main_file
                )
                validation_results['summary']['files_validated'] += 1
                validation_results['summary']['total_found'] += validation_results['main_file']['translation_count']
                
                if not validation_results['main_file']['valid']:
                    validation_results['overall_valid'] = False
                    validation_results['summary']['validation_success'] = False
            else:
                validation_results['overall_valid'] = False
                validation_results['summary']['validation_success'] = False
                validation_results['main_file'] = {
                    'valid': False,
                    'translation_count': 0,
                    'errors': [f"Fichier principal manquant: {main_file}"]
                }
            
            # Valider le fichier astérisques si nécessaire
            if asterix_count > 0:
                asterix_file = f"{file_base}_asterix.txt"
                if os.path.exists(asterix_file):
                    validation_results['asterix_file'] = TranslationValidator.validate_file_correspondence(
                        asterix_count, asterix_file
                    )
                    validation_results['summary']['files_validated'] += 1
                    validation_results['summary']['total_found'] += validation_results['asterix_file']['translation_count']
                    
                    if not validation_results['asterix_file']['valid']:
                        validation_results['overall_valid'] = False
                        validation_results['summary']['validation_success'] = False
                else:
                    # Fichier astérisques attendu mais manquant
                    validation_results['asterix_file'] = {
                        'valid': False,
                        'translation_count': 0,
                        'errors': [f"Fichier astérisques manquant: {asterix_file}"]
                    }
                    validation_results['overall_valid'] = False
                    validation_results['summary']['validation_success'] = False
            
            # Valider le fichier textes vides si nécessaire
            if empty_count > 0:
                empty_file = f"{file_base}_empty.txt"
                if os.path.exists(empty_file):
                    validation_results['empty_file'] = TranslationValidator.validate_file_correspondence(
                        empty_count, empty_file
                    )
                    validation_results['summary']['files_validated'] += 1
                    validation_results['summary']['total_found'] += validation_results['empty_file']['translation_count']
                    
                    if not validation_results['empty_file']['valid']:
                        validation_results['overall_valid'] = False
                        validation_results['summary']['validation_success'] = False
                else:
                    # Fichier vides attendu mais manquant
                    validation_results['empty_file'] = {
                        'valid': False,
                        'translation_count': 0,
                        'errors': [f"Fichier textes vides manquant: {empty_file}"]
                    }
                    validation_results['overall_valid'] = False
                    validation_results['summary']['validation_success'] = False
            
            # Log du résultat final
            log_message("INFO", f"Validation complète: {validation_results['summary']['total_found']}/{validation_results['summary']['total_expected']} éléments validés")
            
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de la validation des fichiers pour {file_base}", e)
            validation_results['overall_valid'] = False
            validation_results['summary']['validation_success'] = False
            if not validation_results.get('main_file'):
                validation_results['main_file'] = {
                    'valid': False,
                    'translation_count': 0,
                    'errors': [f"Erreur de validation: {str(e)}"]
                }
        
        return validation_results

# Fonctions utilitaires
def validate_before_extraction(filepath):
    """
    Validation complète avant extraction
    
    Args:
        filepath (str): Chemin du fichier à valider
        
    Returns:
        dict: Résultat de la validation avec recommandations
    """
    try:
        validator = FileValidator()
        validation = validator.is_renpy_file(filepath)
        
        # Ajouter des recommandations
        if validation['is_valid']:
            if validation['confidence'] < 70:
                validation['warnings'].append(
                    "Confiance modérée - vérifiez le résultat de l'extraction"
                )
        else:
            validation['errors'].append(
                "Ce fichier ne semble pas être un fichier Ren'Py valide"
            )
        
        return validation
        
    except Exception as e:
        log_message("ERREUR", f"Erreur lors de la validation avant extraction de {filepath}", e)
        return {
            'is_valid': False,
            'confidence': 0,
            'patterns_found': [],
            'file_info': {},
            'warnings': [],
            'errors': [f"Erreur de validation: {str(e)}"]
        }

def create_safety_backup(filepath):
    """
    Crée une sauvegarde de sécurité avant traitement
    
    Args:
        filepath (str): Chemin du fichier à sauvegarder
        
    Returns:
        dict: Résultat de la sauvegarde
    """
    try:
        backup_manager = BackupManager()
        return backup_manager.create_backup(filepath, ".safety_backup")
    except Exception as e:
        log_message("ERREUR", f"Erreur lors de la création de la sauvegarde de sécurité pour {filepath}", e)
        return {
            'success': False,
            'backup_path': None,
            'error': str(e)
        }

def validate_before_reconstruction(file_base, extracted_count, asterix_count=0, empty_count=0):
    """
    Validation complète avant reconstruction
    
    Args:
        file_base (str): Nom de base du projet
        extracted_count (int): Nombre de textes extraits
        asterix_count (int): Nombre d'astérisques
        empty_count (int): Nombre de textes vides
        
    Returns:
        dict: Résultat de la validation
    """
    try:
        validator = TranslationValidator()
        return validator.validate_all_files(file_base, extracted_count, asterix_count, empty_count)
    except Exception as e:
        log_message("ERREUR", f"Erreur lors de la validation avant reconstruction pour {file_base}", e)
        return {
            'overall_valid': False,
            'main_file': {
                'valid': False,
                'translation_count': 0,
                'errors': [f"Erreur de validation: {str(e)}"]
            },
            'asterix_file': None,
            'empty_file': None,
            'summary': {
                'total_expected': extracted_count + asterix_count + empty_count,
                'total_found': 0,
                'files_validated': 0,
                'validation_success': False
            }
        }