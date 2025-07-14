# core/reconstruction.py
# Reconstruction Functions Module
# Created for Traducteur Ren'Py Pro v1.9.0

"""
Module de reconstruction des fichiers traduits
"""

import os
import re
import time
import json
from collections import OrderedDict
from utils.logging import log_message
from core.extraction import get_file_base_name

class FileReconstructor:
    """Classe principale pour la reconstruction des fichiers"""
    
    def __init__(self):
        self.file_content = []
        self.original_path = None
        self.reconstruction_time = 0
        
        # Données de reconstruction
        self.mapping = {}
        self.asterix_mapping = {}
        self.empty_mapping = {}
        self.positions = []
        self.quote_counts = []
        self.suffixes = []
        self.translations = []
        self.asterix_translations = []
        self.empty_translations = []
    
    def load_file_content(self, file_content, original_path):
        """
        Charge le contenu du fichier à reconstruire
        
        Args:
            file_content (list): Lignes du fichier original
            original_path (str): Chemin du fichier original
        """
        self.file_content = file_content[:]
        self.original_path = original_path
        self._reset_reconstruction_data()
    
    def _reset_reconstruction_data(self):
        """Remet à zéro les données de reconstruction"""
        self.mapping.clear()
        self.asterix_mapping.clear()
        self.empty_mapping.clear()
        self.positions.clear()
        self.quote_counts.clear()
        self.suffixes.clear()
        self.translations.clear()
        self.asterix_translations.clear()
        self.empty_translations.clear()
        self.reconstruction_time = 0
    
    def reconstruct_file(self, save_mode='new_file'):
        """
        Fonction principale de reconstruction
        
        Args:
            save_mode (str): 'overwrite' ou 'new_file'
            
        Returns:
            dict: Résultats de la reconstruction
        """
        if not self.file_content or not self.original_path:
            raise ValueError("Contenu du fichier ou chemin original manquant")
        
        start_time = time.time()
        
        try:
            # Charger les fichiers de configuration
            self._load_mapping_files()
            self._load_translation_files()
            
            # Reconstruire le contenu
            reconstructed_content = self._rebuild_content()
            
            # Sauvegarder le fichier
            save_path = self._save_reconstructed_file(reconstructed_content, save_mode)
            
            # Nettoyer les fichiers temporaires
            self._cleanup_temp_files()
            
            # Calcul du temps
            self.reconstruction_time = time.time() - start_time
            
            result = {
                'save_path': save_path,
                'reconstruction_time': self.reconstruction_time,
                'save_mode': save_mode
            }
            
            log_message("INFO", f"Reconstruction réussie en {self.reconstruction_time:.2f}s")
            return result
            
        except Exception as e:
            log_message("ERREUR", "Erreur critique pendant la reconstruction", e)
            raise
    
    def _load_mapping_files(self):
            """Charge tous les fichiers de mapping depuis le dossier temporaire"""
            from utils.constants import FOLDERS
            
            file_base = get_file_base_name(self.original_path)
            temp_folder = FOLDERS["temp"]
            
            # Vérifier que les fichiers existent dans le dossier temporaire
            mapping_file = os.path.join(temp_folder, f"{file_base}_mapping.txt")
            positions_file = os.path.join(temp_folder, f"{file_base}_positions.json")
            
            if not os.path.exists(mapping_file) or not os.path.exists(positions_file):
                raise FileNotFoundError(
                    f"Fichiers manquants dans {temp_folder}:\n• {os.path.basename(mapping_file)}\n• {os.path.basename(positions_file)}\n\n"
                    f"Assurez-vous d'avoir extrait le texte de ce fichier d'abord."
                )
            
            # Charger le mapping principal
            with open(mapping_file, "r", encoding="utf-8") as mf:
                for line in mf:
                    if " => " in line:
                        placeholder, tag = line.strip().split(" => ", 1)
                        self.mapping[placeholder] = tag
            
            # Charger le mapping des astérisques (si existe)
            asterix_mapping_file = os.path.join(temp_folder, f"{file_base}_asterix_mapping.txt")
            if os.path.exists(asterix_mapping_file):
                with open(asterix_mapping_file, "r", encoding="utf-8") as amf:
                    for line in amf:
                        if " => " in line:
                            placeholder, asterix = line.strip().split(" => ", 1)
                            self.asterix_mapping[placeholder] = asterix
            
            # Charger le mapping des textes vides (si existe)
            empty_mapping_file = os.path.join(temp_folder, f"{file_base}_empty_mapping.txt")
            if os.path.exists(empty_mapping_file):
                with open(empty_mapping_file, "r", encoding="utf-8") as emf:
                    for line in emf:
                        if " => " in line:
                            placeholder, empty = line.strip().split(" => ", 1)
                            self.empty_mapping[placeholder] = empty
            
            # Charger les positions et données
            with open(positions_file, "r", encoding="utf-8") as pf:
                position_data = json.load(pf)
            
            # Gérer l'ancien format (rétrocompatibilité)
            if isinstance(position_data, list):
                self.positions = position_data
                self.quote_counts = [1] * len(self.positions)
                self.suffixes = [""] * len(self.positions)
            else:
                self.positions = position_data['positions']
                self.quote_counts = position_data['quote_counts']
                self.suffixes = position_data.get('suffixes', [""] * len(self.positions))
            
            log_message("INFO", f"Mappings chargés depuis {temp_folder}: {len(self.mapping)} codes, {len(self.asterix_mapping)} astérisques, {len(self.empty_mapping)} vides")
    
    def _load_translation_files(self):
        """Charge tous les fichiers de traduction"""
        file_base = get_file_base_name(self.original_path)
        
        # Charger le fichier principal
        main_trans_file = f"{file_base}.txt"
        trans_path = os.path.join(os.getcwd(), main_trans_file)
        
        if not os.path.exists(trans_path):
            raise FileNotFoundError(f"Fichier de traduction manquant: {main_trans_file}")
        
        self.translations = [line.rstrip("\n") for line in open(trans_path, "r", encoding="utf-8")]
        
        # Charger le fichier astérisques (si existe)
        asterix_trans_file = f"{file_base}_asterix.txt"
        asterix_path = os.path.join(os.getcwd(), asterix_trans_file)
        if os.path.exists(asterix_path):
            self.asterix_translations = [line.rstrip("\n") for line in open(asterix_path, "r", encoding="utf-8")]
        
        # Charger le fichier textes vides (si existe)
        empty_trans_file = f"{file_base}_empty.txt"
        empty_path = os.path.join(os.getcwd(), empty_trans_file)
        if os.path.exists(empty_path):
            self.empty_translations = [line.rstrip("\n") for line in open(empty_path, "r", encoding="utf-8")]
        
        log_message("INFO", f"Traductions chargées: {len(self.translations)} principales, {len(self.asterix_translations)} astérisques, {len(self.empty_translations)} vides")
    
    def _rebuild_content(self):
        """Reconstruit le contenu du fichier avec les traductions"""
        # Créer un mapping des placeholders astérisques vers leurs traductions
        asterix_trans_mapping = {}
        if self.asterix_translations and self.asterix_mapping:
            placeholder_list = list(self.asterix_mapping.keys())
            for i, placeholder in enumerate(placeholder_list):
                if i < len(self.asterix_translations):
                    asterix_content = self.asterix_translations[i]
                    
                    # NOUVEAU : Restaurer les codes protégés dans le contenu astérisque
                    restored_asterix = self._restore_codes_in_asterix(asterix_content)
                    
                    translated_asterix = f"*{restored_asterix}*"
                    asterix_trans_mapping[placeholder] = translated_asterix
        
        # CORRECTION PRINCIPALE : Créer un mapping inverse pour restaurer les placeholders
        restore_mapping = {}
        
        # Restaurer les codes spéciaux normaux
        for placeholder, original in self.mapping.items():
            restore_mapping[placeholder] = original
        
        # Restaurer les placeholders empty (guillemets échappés et textes vides)
        if self.empty_mapping:
            log_message("INFO", "Création du mapping de restauration pour empty_mapping")
            for original, placeholder in self.empty_mapping.items():
                # Inverser : placeholder -> original
                restore_mapping[placeholder] = original
                log_message("INFO", f"Mapping de restauration: {placeholder} -> {original}")
        
        # Traiter les textes vides avec leurs traductions
        empty_text_mapping = {}
        if self.empty_translations and self.empty_mapping:
            # Identifier les placeholders de textes vides (non ESC)
            text_placeholders = {}
            for original, placeholder in self.empty_mapping.items():
                if original != r'\"':  # Pas un guillemet échappé
                    text_placeholders[placeholder] = original
            
            if text_placeholders and self.empty_translations:
                text_items = list(text_placeholders.items())
                text_items.reverse()  # INVERSER L'ORDRE
                
                translation_index = len(self.empty_translations) - 1
                for placeholder, original_pattern in text_items:
                    if translation_index >= 0:
                        empty_content = self.empty_translations[translation_index]
                        translated_empty = f'"{empty_content}"'
                        empty_text_mapping[f'"{placeholder}"'] = translated_empty
                        translation_index -= 1
        
        # Reconstruire ligne par ligne
        output_lines = []
        translation_index = 0
        
        for i, line in enumerate(self.file_content):
            current_line = line
            
            # Si cette ligne correspond à une position extraite
            if i in self.positions:
                pos_index = self.positions.index(i)
                quote_count = self.quote_counts[pos_index]
                suffix = self.suffixes[pos_index]
                
                if translation_index < len(self.translations):
                    # Préparer les traductions pour cette ligne
                    line_translations = []
                    for j in range(quote_count):
                        if translation_index + j < len(self.translations):
                            translation = self.translations[translation_index + j]
                            
                            # CORRECTION : Restaurer TOUS les placeholders dans la traduction
                            for placeholder, original in restore_mapping.items():
                                translation = translation.replace(placeholder, original)
                            
                            # Restaurer les astérisques traduites
                            for asterix_ph, translated_asterix in asterix_trans_mapping.items():
                                translation = translation.replace(asterix_ph, translated_asterix)
                                
                            line_translations.append(translation)
                        else:
                            line_translations.append("")  # Traduction manquante
                    
                    # Construire la nouvelle ligne
                    first_quote_match = re.search(r'"', current_line)
                    if first_quote_match:
                        prefix = current_line[:first_quote_match.start()]
                        
                        # Construire avec toutes les traductions
                        new_line = prefix
                        for j, translation in enumerate(line_translations):
                            new_line += f'"{translation}"'
                            # Ajouter un espace entre les guillemets multiples (sauf pour le dernier)
                            if j < len(line_translations) - 1:
                                new_line += " "
                        
                        # Ajouter le suffixe préservé
                        new_line += suffix
                        
                        # Garder le retour à la ligne si présent
                        if line.endswith('\n'):
                            new_line += '\n'
                        
                        output_lines.append(new_line)
                    else:
                        # Fallback : garder la ligne modifiée
                        output_lines.append(current_line)
                    
                    translation_index += quote_count
                else:
                    # Pas assez de traductions, garder la ligne modifiée
                    output_lines.append(current_line)
            else:
                # Ligne normale : restaurer les placeholders empty qui ne sont pas dans les traductions
                # Traiter d'abord les textes vides traduits
                for pattern, replacement in empty_text_mapping.items():
                    current_line = current_line.replace(pattern, replacement)
                
                # Puis restaurer les autres placeholders (comme les guillemets échappés)
                for placeholder, original in restore_mapping.items():
                    if placeholder.startswith("(ESC"):
                        current_line = current_line.replace(placeholder, original)
                
                output_lines.append(current_line)
        
        return output_lines

    def _restore_codes_in_asterix(self, asterix_content):
        """Restaure les codes protégés dans un texte astérisque traduit"""
        try:
            restored_content = asterix_content
            
            # Restaurer en utilisant le mapping principal (ordre inverse pour éviter les conflits)
            for code, placeholder in reversed(list(self.mapping.items())):
                if placeholder in restored_content:
                    restored_content = restored_content.replace(placeholder, code)
            
            return restored_content
            
        except Exception as e:
            log_message("WARNING", f"Erreur lors de la restauration des codes dans astérisque: {asterix_content}", e)
            return asterix_content  # Retourner l'original en cas d'erreur

    def _save_reconstructed_file(self, content, save_mode):
        """Sauvegarde le fichier reconstruit"""
        # Déterminer le chemin de sauvegarde
        if save_mode == 'overwrite':
            save_path = self.original_path
        else:  # new_file
            save_path = self.original_path.replace(".rpy", "_translated.rpy")
        
        # Sauvegarder le fichier traduit
        with open(save_path, "w", encoding="utf-8", newline='') as wf:
            wf.writelines(content)
        
        # Si mode nouveau fichier, commenter l'original
        if save_mode == 'new_file':
            success = self._comment_original_file()
            if not success:
                log_message("WARNING", "Impossible de commenter le fichier original")
        
        log_message("INFO", f"Fichier reconstruit sauvegardé: {save_path}")
        return save_path
    
    def _comment_original_file(self):
        """Commente toutes les lignes du fichier original"""
        try:
            with open(self.original_path, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            
            commented_lines = []
            for line in original_lines:
                # Si la ligne n'est pas vide, la commenter
                if line.strip():
                    commented_lines.append(f"# {line}")
                else:
                    commented_lines.append(line)
            
            # Sauvegarder le fichier commenté
            with open(self.original_path, 'w', encoding='utf-8', newline='') as f:
                f.writelines(commented_lines)
            
            return True
        except Exception as e:
            log_message("ERREUR", f"Impossible de commenter le fichier original: {str(e)}", e)
            return False
    
    def _cleanup_temp_files(self):
        """Nettoie les fichiers temporaires"""
        file_base = get_file_base_name(self.original_path)
        
        temp_files = [
            f"{file_base}_mapping.txt",
            f"{file_base}_positions.json",
            f"{file_base}_asterix_mapping.txt",
            f"{file_base}_empty_mapping.txt"
        ]
        
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                log_message("WARNING", f"Impossible de supprimer {temp_file}", e)
        
        log_message("INFO", f"Fichiers temporaires nettoyés pour {file_base}")

# Fonction de validation des traductions
def validate_translations(original_count, translation_count, asterix_count=0, empty_count=0):
    """
    Valide que le nombre de traductions correspond aux textes extraits
    
    Args:
        original_count (int): Nombre de textes extraits
        translation_count (int): Nombre de traductions fournies
        asterix_count (int): Nombre d'astérisques
        empty_count (int): Nombre de textes vides
        
    Returns:
        dict: Résultats de la validation
    """
    validation_result = {
        'valid': True,
        'warnings': [],
        'errors': []
    }
    
    # Vérification principale
    if translation_count != original_count:
        validation_result['valid'] = False
        validation_result['errors'].append(
            f"Nombre de traductions incorrect: {translation_count} fourni, {original_count} attendu"
        )
    
    # Vérifications secondaires
    if asterix_count > 0:
        validation_result['warnings'].append(
            f"{asterix_count} expressions entre astérisques détectées - vérifiez asterix.txt"
        )
    
    if empty_count > 0:
        validation_result['warnings'].append(
            f"{empty_count} textes vides/espaces détectés - vérifiez empty.txt"
        )
    
    return validation_result

# Fonction utilitaire pour compatibilité
def reconstruire_fichier(file_content, original_path, save_mode='new_file'):
    """
    Fonction de reconstruction compatible avec l'ancienne interface
    
    Args:
        file_content (list): Contenu du fichier original
        original_path (str): Chemin du fichier original
        save_mode (str): Mode de sauvegarde
        
    Returns:
        dict: Résultats de la reconstruction
    """
    reconstructor = FileReconstructor()
    reconstructor.load_file_content(file_content, original_path)
    return reconstructor.reconstruct_file(save_mode)