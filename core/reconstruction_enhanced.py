# core/reconstruction_enhanced.py
# Enhanced Reconstruction with Glossary Support
# Created for Traducteur Ren'Py Pro v2.3.0

"""
Reconstruction améliorée avec support du glossaire
"""

import os
import re
import time
import json
from collections import OrderedDict
from utils.logging import log_message


class EnhancedFileReconstructor:
    """Classe principale pour la reconstruction des fichiers avec support du glossaire"""
    
    def __init__(self):
        self.file_content = []
        self.original_path = None
        self.reconstruction_time = 0
        
        # Données de reconstruction
        self.mapping = {}
        self.asterix_mapping = {}
        self.empty_mapping = {}
        self.glossary_mapping = {}  # ✅ NOUVEAU : Mapping du glossaire
        self.positions = []
        self.quote_counts = []
        self.suffixes = []
        self.translations = []
        self.asterix_translations = []
        self.empty_translations = []
        self.glossary_translations = []  # ✅ NOUVEAU : Traductions du glossaire
    
    def load_file_content(self, file_content, original_path):
        """Charge le contenu avec extraction du nom de jeu"""
        from utils.logging import extract_game_name
        from utils.constants import FOLDERS

        self.file_content = file_content[:]
        self.original_path = original_path

        # Extraire et stocker le nom du jeu
        self.game_name = extract_game_name(original_path)
        temp_root = FOLDERS["temp"]
        self.mapping_folder = os.path.join(temp_root, self.game_name, "fichiers_a_ne_pas_traduire")
        self.translate_folder = os.path.join(temp_root, self.game_name, "fichiers_a_traduire")

        # S'assurer que les dossiers existent
        from utils.constants import ensure_game_structure
        ensure_game_structure(self.game_name)

        self._reset_reconstruction_data()
    
    def _reset_reconstruction_data(self):
        """Remet à zéro les données de reconstruction"""
        self.mapping.clear()
        self.asterix_mapping.clear()
        self.empty_mapping.clear()
        self.glossary_mapping.clear()  # ✅ NOUVEAU
        self.positions.clear()
        self.quote_counts.clear()
        self.suffixes.clear()
        self.translations.clear()
        self.asterix_translations.clear()
        self.empty_translations.clear()
        self.glossary_translations.clear()  # ✅ NOUVEAU
        self.reconstruction_time = 0
    
    def reconstruct_file(self, save_mode='new_file'):
        """
        Fonction principale de reconstruction avec support du glossaire
        
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
            
            log_message("INFO", f"Reconstruction avec glossaire réussie en {self.reconstruction_time:.2f}s")
            return result
            
        except Exception as e:
            log_message("ERREUR", "Erreur critique pendant la reconstruction avec glossaire", e)
            raise
    
    def _load_mapping_files(self):
        """Charge les mappings depuis la nouvelle structure (avec glossaire)"""
        from utils.constants import FOLDERS
        from core.extraction_enhanced import get_file_base_name
        from utils.logging import extract_game_name

        file_base = get_file_base_name(self.original_path)
        game_name = extract_game_name(self.original_path)
        
        # Utiliser la nouvelle structure
        temp_root = FOLDERS["temp"]
        mapping_folder = os.path.join(temp_root, game_name, "fichiers_a_ne_pas_traduire")

        # Vérifier que les fichiers existent
        mapping_file = os.path.join(mapping_folder, f"{file_base}_mapping.txt")
        positions_file = os.path.join(mapping_folder, f"{file_base}_positions.json")

        if not os.path.exists(mapping_file) or not os.path.exists(positions_file):
            raise FileNotFoundError(
                f"Fichiers manquants dans {mapping_folder} :\n"
                f"• {os.path.basename(mapping_file)}\n"
                f"• {os.path.basename(positions_file)}\n\n"
                "Assurez-vous d'avoir extrait le texte de ce fichier d'abord."
            )

        # Charger le mapping principal
        with open(mapping_file, "r", encoding="utf-8") as mf:
            for line in mf:
                if " => " in line:
                    placeholder, tag = line.strip().split(" => ", 1)
                    self.mapping[placeholder] = tag

        # Charger le mapping des astérisques (si existe)
        asterix_file = os.path.join(mapping_folder, f"{file_base}_asterix_mapping.txt")
        if os.path.exists(asterix_file):
            with open(asterix_file, "r", encoding="utf-8") as amf:
                for line in amf:
                    if " => " in line:
                        placeholder, asterix = line.strip().split(" => ", 1)
                        self.asterix_mapping[placeholder] = asterix

        # Charger le mapping des textes vides (si existe)
        empty_file = os.path.join(mapping_folder, f"{file_base}_empty_mapping.txt")
        if os.path.exists(empty_file):
            with open(empty_file, "r", encoding="utf-8") as emf:
                for line in emf:
                    if " => " in line:
                        placeholder, empty = line.strip().split(" => ", 1)
                        self.empty_mapping[placeholder] = empty

        # ✅ NOUVEAU : Charger le mapping du glossaire (si existe)
        glossary_file = os.path.join(mapping_folder, f"{file_base}_glossary_mapping.txt")
        if os.path.exists(glossary_file):
            with open(glossary_file, "r", encoding="utf-8") as gmf:
                for line in gmf:
                    if " => " in line:
                        parts = line.strip().split(" => ")
                        if len(parts) >= 3:
                            placeholder = parts[0]
                            original = parts[1]
                            translation = parts[2]
                            self.glossary_mapping[placeholder] = {
                                'original': original,
                                'translation': translation
                            }

        # Charger les positions et données
        with open(positions_file, "r", encoding="utf-8") as pf:
            position_data = json.load(pf)

        # Rétrocompatibilité ancien format
        if isinstance(position_data, list):
            self.positions = position_data
            self.quote_counts = [1] * len(self.positions)
            self.suffixes = [""] * len(self.positions)
        else:
            self.positions = position_data['positions']
            self.quote_counts = position_data['quote_counts']
            self.suffixes = position_data.get('suffixes', [""] * len(self.positions))

        log_message("INFO", f"Mappings chargés depuis {mapping_folder} (avec glossaire: {len(self.glossary_mapping)} termes)")
    
    def _load_translation_files(self):
        """Charge les traductions depuis la nouvelle structure (avec glossaire)"""
        from utils.constants import FOLDERS
        from core.extraction_enhanced import get_file_base_name
        from utils.logging import extract_game_name

        file_base = get_file_base_name(self.original_path)
        game_name = extract_game_name(self.original_path)
        
        # Utiliser la nouvelle structure
        temp_root = FOLDERS["temp"]
        translate_folder = os.path.join(temp_root, game_name, "fichiers_a_traduire")

        # Fichier principal
        main_trans_path = os.path.join(translate_folder, f"{file_base}.txt")
        if not os.path.exists(main_trans_path):
            raise FileNotFoundError(f"Fichier de traduction manquant : {main_trans_path}")
        
        with open(main_trans_path, "r", encoding="utf-8") as mf:
            self.translations = [line.rstrip("\n") for line in mf]

        # Fichier astérisques (si présent)
        asterix_trans_path = os.path.join(translate_folder, f"{file_base}_asterix.txt")
        if os.path.exists(asterix_trans_path):
            with open(asterix_trans_path, "r", encoding="utf-8") as af:
                self.asterix_translations = [line.rstrip("\n") for line in af]
        else:
            self.asterix_translations = []

        # Fichier vides (si présent)
        empty_trans_path = os.path.join(translate_folder, f"{file_base}_empty.txt")
        if os.path.exists(empty_trans_path):
            with open(empty_trans_path, "r", encoding="utf-8") as ef:
                self.empty_translations = [line.rstrip("\n") for line in ef]
        else:
            self.empty_translations = []

        # ✅ NOUVEAU : Fichier glossaire (si présent)
        glossary_trans_path = os.path.join(translate_folder, f"{file_base}_glossary.txt")
        if os.path.exists(glossary_trans_path):
            with open(glossary_trans_path, "r", encoding="utf-8") as gf:
                # Ignorer les lignes de commentaire
                for line in gf:
                    line = line.rstrip("\n")
                    if not line.startswith('#') and line.strip():
                        self.glossary_translations.append(line)
        else:
            self.glossary_translations = []

        log_message("INFO", f"Traductions chargées depuis {translate_folder} (glossaire: {len(self.glossary_translations)} termes)")
    
    def _rebuild_content(self):
        """Reconstruit le contenu du fichier avec les traductions et le glossaire"""
        # Créer un mapping des placeholders astérisques vers leurs traductions
        asterix_trans_mapping = {}
        if self.asterix_translations and self.asterix_mapping:
            placeholder_list = list(self.asterix_mapping.keys())
            for i, placeholder in enumerate(placeholder_list):
                if i < len(self.asterix_translations):
                    asterix_content = self.asterix_translations[i]
                    
                    # Restaurer les codes protégés dans le contenu astérisque
                    restored_asterix = self._restore_codes_in_asterix(asterix_content)
                    
                    translated_asterix = f"*{restored_asterix}*"
                    asterix_trans_mapping[placeholder] = translated_asterix
        
        # ✅ NOUVEAU : Créer un mapping des placeholders de glossaire vers leurs traductions
        glossary_trans_mapping = {}
        if self.glossary_translations and self.glossary_mapping:
            placeholder_list = list(self.glossary_mapping.keys())
            for i, placeholder in enumerate(placeholder_list):
                if i < len(self.glossary_translations):
                    # Utiliser la traduction du fichier glossaire
                    glossary_trans_mapping[placeholder] = self.glossary_translations[i]
        
        # Créer un mapping inverse pour restaurer les placeholders
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
                text_items.reverse()  # Inverser l'ordre
                
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
                            
                            # Restaurer TOUS les placeholders dans la traduction
                            for placeholder, original in restore_mapping.items():
                                translation = translation.replace(placeholder, original)
                            
                            # Restaurer les astérisques traduites
                            for asterix_ph, translated_asterix in asterix_trans_mapping.items():
                                translation = translation.replace(asterix_ph, translated_asterix)
                            
                            # ✅ NOUVEAU : Restaurer les termes du glossaire traduits
                            for glossary_ph, glossary_translation in glossary_trans_mapping.items():
                                translation = translation.replace(glossary_ph, glossary_translation)
                                
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
                
                # ✅ NOUVEAU : Restaurer les termes du glossaire dans les lignes non extraites
                for glossary_ph, glossary_translation in glossary_trans_mapping.items():
                    current_line = current_line.replace(glossary_ph, glossary_translation)
                
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
        """Nettoie les fichiers temporaires dans la nouvelle structure"""
        from utils.constants import FOLDERS
        from core.extraction_enhanced import get_file_base_name
        from utils.logging import extract_game_name

        file_base = get_file_base_name(self.original_path)
        game_name = extract_game_name(self.original_path)
        
        # Nettoyer dans la nouvelle structure
        temp_root = FOLDERS["temp"]
        mapping_folder = os.path.join(temp_root, game_name, "fichiers_a_ne_pas_traduire")
        
        temp_files = [
            os.path.join(mapping_folder, f"{file_base}_mapping.txt"),
            os.path.join(mapping_folder, f"{file_base}_positions.json"),
            os.path.join(mapping_folder, f"{file_base}_asterix_mapping.txt"),
            os.path.join(mapping_folder, f"{file_base}_empty_mapping.txt"),
            os.path.join(mapping_folder, f"{file_base}_glossary_mapping.txt")  # ✅ NOUVEAU
        ]
        
        cleaned_count = 0
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    cleaned_count += 1
            except Exception as e:
                log_message("WARNING", f"Impossible de supprimer {temp_file}", e)
        
        log_message("INFO", f"Fichiers temporaires nettoyés pour {file_base}: {cleaned_count} fichiers")

# Fonction utilitaire pour compatibilité
def reconstruire_fichier_enhanced(file_content, original_path, save_mode='new_file'):
    """
    Fonction de reconstruction avec support du glossaire
    
    Args:
        file_content (list): Contenu du fichier original
        original_path (str): Chemin du fichier original
        save_mode (str): Mode de sauvegarde
        
    Returns:
        dict: Résultats de la reconstruction
    """
    reconstructor = EnhancedFileReconstructor()
    reconstructor.load_file_content(file_content, original_path)
    return reconstructor.reconstruct_file(save_mode)