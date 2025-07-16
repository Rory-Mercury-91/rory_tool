# core/validation.py
# Validation and Security Module
# Created for Traducteur Ren'Py Pro v2.2.0

"""
Module de validation des fichiers et de sécurité
"""

import os
import re
import shutil
import datetime
from utils.constants import FOLDERS
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
    """CORRIGÉ : Gestionnaire de sauvegardes avec structure organisée"""
    
    @staticmethod
    def create_backup(filepath, backup_suffix=".backup"):
        """Crée une sauvegarde dans l'arborescence organisée"""
        result = {
            'success': False,
            'backup_path': None,
            'error': None
        }
        
        try:
            from utils.constants import FOLDERS, ensure_folders_exist
            from utils.logging import extract_game_name
            
            if not os.path.exists(filepath):
                result['error'] = "Fichier source introuvable"
                return result
            
            # S'assurer que les dossiers existent
            ensure_folders_exist()
            
            # ✅ CORRECTION : Structure organisée par jeu
            game_name = extract_game_name(filepath)
            backup_root = FOLDERS["backup"]
            game_backup_folder = os.path.join(backup_root, game_name)
            
            # Créer le dossier de sauvegarde du jeu
            os.makedirs(game_backup_folder, exist_ok=True)
            
            # Générer un nom de backup unique
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            backup_filename = f"{base_name}_{timestamp}{backup_suffix}"
            backup_path = os.path.join(game_backup_folder, backup_filename)
            
            # Créer la sauvegarde
            shutil.copy2(filepath, backup_path)
            
            result['success'] = True
            result['backup_path'] = backup_path
            
            log_message("INFO", f"Sauvegarde créée: {game_name}/{backup_filename}")
            
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
        ✅ CORRECTION : Liste toutes les sauvegardes disponibles pour un fichier depuis la nouvelle structure
        
        Args:
            filepath (str): Chemin du fichier original
            
        Returns:
            list: Liste des sauvegardes avec métadonnées
        """
        backups = []
        
        try:
            from utils.logging import extract_game_name
            
            # Obtenir le nom du jeu et le dossier de sauvegarde
            game_name = extract_game_name(filepath)
            backup_folder = os.path.join(FOLDERS["backup"], game_name)
            
            # Vérifier que le dossier existe
            if not os.path.exists(backup_folder):
                log_message("INFO", f"Dossier de sauvegarde non trouvé: {backup_folder}")
                return backups
            
            # Obtenir le nom de base du fichier pour filtrer les sauvegardes
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            
            # Lister tous les fichiers dans le dossier de sauvegarde
            for filename in os.listdir(backup_folder):
                if (filename.startswith(base_name) and 
                    ('backup' in filename.lower() or 'safety' in filename.lower())):
                    
                    backup_path = os.path.join(backup_folder, filename)
                    try:
                        stats = os.stat(backup_path)
                        backups.append({
                            'path': backup_path,
                            'name': filename,
                            'size': stats.st_size,
                            'created': datetime.datetime.fromtimestamp(stats.st_ctime),
                            'modified': datetime.datetime.fromtimestamp(stats.st_mtime),
                            'game': game_name
                        })
                    except Exception as e:
                        log_message("WARNING", f"Impossible de lire les stats de {filename}", e)
                        continue
            
            # Trier par date de création (plus récent en premier)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
            log_message("INFO", f"Sauvegardes trouvées pour {base_name}: {len(backups)}")
            
        except Exception as e:
            log_message("WARNING", f"Erreur lors de la liste des sauvegardes pour {filepath}", e)
        
        return backups

class TranslationValidator:
    """Validateur pour les correspondances de traduction"""
    
    @staticmethod
    def validate_file_correspondence(extracted_count, translation_file_path):
        """
        ✅ CORRECTION : Valide qu'un fichier de traduction correspond aux textes extraits
        
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
                result['errors'].append(f"Fichier de traduction manquant: {translation_file_path}")
                return result
            
            # ✅ CORRECTION : Traitement spécial pour les fichiers _empty.txt
            filename = os.path.basename(translation_file_path)
            
            # Lire le fichier de traduction
            with open(translation_file_path, 'r', encoding='utf-8') as f:
                translation_lines = f.readlines()
            
            # ✅ CORRECTION : Pour les fichiers _empty.txt, accepter les lignes vides
            if filename.endswith('_empty.txt'):
                log_message("INFO", f"Validation fichier _empty.txt: {filename}")
                
                # Pour les fichiers empty, on compte toutes les lignes (même vides)
                # car elles peuvent contenir des espaces ou être intentionnellement vides
                total_lines = len(translation_lines)
                
                # Compter les lignes avec du contenu réel
                content_lines = []
                empty_lines = 0
                
                for i, line in enumerate(translation_lines):
                    content = line.rstrip('\n\r')
                    if content or content == '':  # Accepter les lignes vides pour _empty.txt
                        content_lines.append((i + 1, content))
                    else:
                        empty_lines += 1
                
                result['translation_count'] = total_lines  # ✅ CORRECTION : Compter toutes les lignes
                result['empty_lines'] = empty_lines
                
                # ✅ CORRECTION : Validation adaptée pour les fichiers _empty.txt
                if result['translation_count'] != extracted_count:
                    result['valid'] = False
                    
                    if result['translation_count'] < extracted_count:
                        result['missing_count'] = extracted_count - result['translation_count']
                        result['errors'].append(
                            f"Lignes manquantes dans fichier _empty.txt: {result['missing_count']} "
                            f"(attendu: {extracted_count}, trouvé: {result['translation_count']})"
                        )
                    else:
                        result['extra_count'] = result['translation_count'] - extracted_count
                        result['warnings'].append(
                            f"Lignes supplémentaires dans fichier _empty.txt: {result['extra_count']} "
                            f"(attendu: {extracted_count}, trouvé: {result['translation_count']})"
                        )
                
                log_message("INFO", f"Validation _empty.txt: {result['translation_count']}/{extracted_count} lignes")
                
            else:
                # Traitement normal pour les autres fichiers
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
                
                # Vérifications de qualité pour les fichiers normaux
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
    def validate_all_files(game_name, file_base, extracted_count, asterix_count=0, empty_count=0):
        """
        Valide tous les fichiers de traduction d'un projet
        
        Args:
            game_name (str): Nom du jeu
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
            main_file = os.path.join(FOLDERS["temp"], game_name, "fichiers_a_traduire", f"{file_base}.txt")
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
                asterix_file = os.path.join(FOLDERS["temp"], game_name, "fichiers_a_traduire", f"{file_base}_asterix.txt")
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
            
            # ✅ CORRECTION : Valider le fichier textes vides si nécessaire
            if empty_count > 0:
                empty_file = os.path.join(FOLDERS["temp"], game_name, "fichiers_a_traduire", f"{file_base}_empty.txt")
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

    def validate_all_files_with_paths(self, main_file_path, asterix_file_path, empty_file_path,
                                     extracted_count, asterix_count=0, empty_count=0):
        """Valide tous les fichiers avec chemins complets spécifiés"""
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
            if main_file_path and os.path.exists(main_file_path):
                validation_results['main_file'] = self.validate_file_correspondence(
                    extracted_count, main_file_path
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
                    'errors': [f"Fichier principal manquant: {main_file_path}"]
                }
            
            # Valider le fichier astérisques si nécessaire
            if asterix_count > 0:
                if asterix_file_path and os.path.exists(asterix_file_path):
                    validation_results['asterix_file'] = self.validate_file_correspondence(
                        asterix_count, asterix_file_path
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
                        'errors': [f"Fichier astérisques manquant: {asterix_file_path}"]
                    }
                    validation_results['overall_valid'] = False
                    validation_results['summary']['validation_success'] = False
            
            # ✅ CORRECTION : Valider le fichier textes vides si nécessaire
            if empty_count > 0:
                if empty_file_path and os.path.exists(empty_file_path):
                    validation_results['empty_file'] = self.validate_file_correspondence(
                        empty_count, empty_file_path
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
                        'errors': [f"Fichier textes vides manquant: {empty_file_path}"]
                    }
                    validation_results['overall_valid'] = False
                    validation_results['summary']['validation_success'] = False
            
            # Log du résultat final
            log_message("INFO", f"Validation complète: {validation_results['summary']['total_found']}/{validation_results['summary']['total_expected']} éléments validés")
            
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de la validation des fichiers", e)
            validation_results['overall_valid'] = False
            validation_results['summary']['validation_success'] = False
            if not validation_results.get('main_file'):
                validation_results['main_file'] = {
                    'valid': False,
                    'translation_count': 0,
                    'errors': [f"Erreur de validation: {str(e)}"]
                }
        
        return validation_results


# ===== FONCTIONS UTILITAIRES AU NIVEAU RACINE =====
# Ces fonctions sont maintenant accessibles pour l'import direct

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
    """✅ CORRECTION : Validation avec nouvelle structure de fichiers"""
    try:
        # ✅ CORRECTION : Utiliser la structure organisée
        from utils.logging import extract_game_name
        from utils.constants import FOLDERS
        
        # Récupérer le nom du jeu depuis le contexte ou utiliser un fallback
        game_name = "Projet_Inconnu"  # Fallback
        
        # Essayer de récupérer le nom du jeu depuis le contexte global
        try:
            # Si on a accès à l'instance principale
            import main
            if hasattr(main, 'app') and hasattr(main.app, 'original_path'):
                game_name = extract_game_name(main.app.original_path)
        except:
            pass
        
        temp_root = FOLDERS["temp"]
        translate_folder = os.path.join(temp_root, game_name, "fichiers_a_traduire")
        
        validator = TranslationValidator()
        
        # Adapter les chemins pour la nouvelle structure
        main_file = os.path.join(translate_folder, f"{file_base}.txt")
        asterix_file = os.path.join(translate_folder, f"{file_base}_asterix.txt") if asterix_count > 0 else None
        empty_file = os.path.join(translate_folder, f"{file_base}_empty.txt") if empty_count > 0 else None
        
        return validator.validate_all_files_with_paths(
            main_file, asterix_file, empty_file,
            extracted_count, asterix_count, empty_count
        )
        
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