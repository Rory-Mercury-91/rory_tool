# core/extraction_enhanced.py
# Enhanced Extraction with Glossary Support
# Created for Traducteur Ren'Py Pro v2.4.1

"""
Modification de l'extraction pour intégrer le glossaire
"""

import os
import re
import time
import json
from collections import OrderedDict
from utils.constants import SPECIAL_CODES, PROTECTION_ORDER
from utils.logging import log_message, anonymize_path

# ✅ CORRECTION : Créer PROTECTION_ORDER_NO_ELLIPSIS correctement
PROTECTION_ORDER_NO_ELLIPSIS = [
    (r'\"', 'Guillemets échappés'),  # EN PREMIER !
    ('""', 'Chaînes vides'),
    ('" "', 'Un espace'),
    ('"  "', 'Deux espaces'),
    ('"   "', 'Trois espaces')
    # ✅ Points de suspension supprimés
]

def get_file_base_name(filepath):
    """
    Récupère le nom de base du fichier sans extension pour créer des fichiers uniques
    
    Args:
        filepath (str): Chemin du fichier
        
    Returns:
        str: Nom de base sécurisé
    """
    if not filepath:
        return "vierge"  # Fallback par défaut
    
    filename = os.path.basename(filepath)
    base_name = os.path.splitext(filename)[0]
    
    # Nettoyer le nom pour éviter les caractères problématiques
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', base_name)
    
    return safe_name

class EnhancedTextExtractor:
    """Classe principale pour l'extraction des textes avec support du glossaire"""
    
    def __init__(self):
        self.file_content = []
        self.original_path = None
        self.extraction_time = 0
        self.extracted_count = 0
        self.asterix_count = 0
        self.empty_count = 0
        
        # Données d'extraction
        self.mapping = OrderedDict()
        self.asterix_mapping = OrderedDict()
        self.empty_mapping = OrderedDict()
        self.glossary_mapping = OrderedDict()  # ✅ NOUVEAU : Mapping du glossaire
        self.positions = []
        self.extracted_texts = []
        self.line_quote_counts = []
        self.line_suffixes = []
        self.asterix_texts = []
        self.empty_texts = []
    
    def load_file_content(self, file_content, original_path):
        """
        Charge le contenu du fichier à traiter
        
        Args:
            file_content (list): Lignes du fichier
            original_path (str): Chemin du fichier original
        """
        self.file_content = file_content[:]  # Copie pour éviter la modification de l'original
        self.original_path = original_path
        self._reset_extraction_data()
    
    def _reset_extraction_data(self):
        """Remet à zéro les données d'extraction"""
        self.mapping.clear()
        self.asterix_mapping.clear()
        self.empty_mapping.clear()
        self.glossary_mapping.clear()  # ✅ NOUVEAU
        self.positions.clear()
        self.extracted_texts.clear()
        self.line_quote_counts.clear()
        self.line_suffixes.clear()
        self.asterix_texts.clear()
        self.empty_texts.clear()
        
        self.extraction_time = 0
        self.extracted_count = 0
        self.asterix_count = 0
        self.empty_count = 0
    
    def extract_texts(self):
        """
        Fonction principale d'extraction des textes avec support du glossaire
        
        Returns:
            dict: Résultats de l'extraction avec chemins des fichiers créés
        """
        if not self.file_content:
            raise ValueError("Aucun contenu de fichier chargé")
        
        start_time = time.time()
        log_message("INFO", f"Début d'extraction avec glossaire pour {anonymize_path(self.original_path) if self.original_path else 'fichier_inconnu'}")
        
        try:
            # ✅ NOUVEAU : Étape 1 - Protection des termes du glossaire
            self._apply_glossary_protection()
            
            # Étapes d'extraction existantes
            self._build_code_mapping()
            self._build_asterix_mapping()
            self._apply_empty_text_protection()
            self._extract_dialogue_texts()
            
            # Calcul du temps
            self.extraction_time = time.time() - start_time
            
            # Sauvegarde des fichiers
            result = self._save_extraction_files()
            
            # Statistiques finales
            self.extracted_count = len(self.extracted_texts)
            self.asterix_count = len(self.asterix_texts)
            self.empty_count = len(self.empty_texts)
            
            log_message("INFO", f"Extraction avec glossaire réussie en {self.extraction_time:.2f}s: {self.extracted_count} textes, {self.asterix_count} astérisques, {self.empty_count} vides, {len(self.glossary_mapping)} termes de glossaire")
            
            return result
            
        except Exception as e:
            log_message("ERREUR", "Erreur critique pendant l'extraction avec glossaire", e)
            raise
    
    def _apply_glossary_protection(self):
        """Applique la protection du glossaire avec import local"""
        try:
            # Import local pour éviter les imports circulaires
            from .glossary import glossary_manager
            
            # Appliquer la protection du glossaire
            protected_lines, glossary_mapping = glossary_manager.protect_glossary_terms(self.file_content)
            
            # Mettre à jour le contenu et stocker le mapping
            self.file_content = protected_lines
            self.glossary_mapping = glossary_mapping
            
            if glossary_mapping:
                log_message("INFO", f"Glossaire appliqué: {len(glossary_mapping)} termes protégés")
            
        except Exception as e:
            log_message("WARNING", f"Erreur lors de l'application du glossaire: {e}")
            # Continuer sans le glossaire en cas d'erreur
    
    def _build_code_mapping(self):
        """Construit le mapping des codes spéciaux Ren'Py à protéger"""
        try:
            for line in self.file_content:
                # Rechercher les balises classiques {}, []
                for tag in re.findall(r'(\{[^}]+\}|\[[^\]]+\])', line):
                    if tag not in self.mapping:
                        self.mapping[tag] = f"({len(self.mapping)+1:02d})"
                
                # Appliquer chaque pattern de code spécial
                for pattern in SPECIAL_CODES:
                    for match in re.finditer(pattern, line):
                        code = match.group(0)
                        if code not in self.mapping:
                            self.mapping[code] = f"({len(self.mapping)+1:02d})"
            
            log_message("INFO", f"Codes spéciaux détectés: {len(self.mapping)} éléments")
        except Exception as e:
            log_message("ERREUR", "Erreur lors de la création du mapping", e)
            raise
    
    def _build_asterix_mapping(self):
        """Construit le mapping des textes entre astérisques avec protection des codes"""
        try:
            asterix_counter = 1
            
            log_message("INFO", "Détection et protection des expressions entre astérisques")
            
            for line in self.file_content:
                # Ignorer les lignes commentées et les lignes old
                stripped_line = line.strip()
                if (stripped_line.startswith('#') or 
                    stripped_line.lower().startswith('old "')):
                    continue
                    
                # Rechercher les textes entre astérisques seulement dans les lignes valides
                asterix_matches = re.findall(r'\*([^*]+)\*', line)
                for asterix_text in asterix_matches:
                    full_asterix = f"*{asterix_text}*"
                    
                    if full_asterix not in self.asterix_mapping:
                        placeholder = f"(D{asterix_counter})"
                        self.asterix_mapping[full_asterix] = placeholder
                        
                        # Protéger les codes DANS le texte entre astérisques
                        protected_content = self._protect_codes_in_asterix(asterix_text)
                        self.asterix_texts.append(protected_content + '\n')
                        
                        asterix_counter += 1
                        log_message("INFO", f"Expression astérisque détectée et protégée: {full_asterix} -> {placeholder}")
            
            if len(self.asterix_texts) > 0:
                log_message("INFO", f"Expressions entre astérisques: {len(self.asterix_texts)} détectées avec codes protégés")

        except Exception as e:
            log_message("ERREUR", "Erreur lors de la détection des astérisques", e)
            raise

    def _protect_codes_in_asterix(self, asterix_content):
        """Protège les codes spéciaux dans un texte entre astérisques en utilisant le mapping principal"""
        try:
            protected_content = asterix_content
            
            # Utiliser le même mapping que pour le texte principal
            for code, placeholder in self.mapping.items():
                if code in protected_content:
                    protected_content = protected_content.replace(code, placeholder)
            
            return protected_content
            
        except Exception as e:
            log_message("WARNING", f"Erreur lors de la protection des codes dans astérisque: {asterix_content}", e)
            return asterix_content  # Retourner l'original en cas d'erreur

    def _apply_empty_text_protection(self):
        """Applique la protection complète des guillemets échappés et textes vides (SANS points de suspension)"""
        try:
            empty_counter = 1
            
            # Variable pour le placeholder des guillemets échappés
            escape_placeholder = None
            
            log_message("INFO", "Protection des codes spéciaux et guillemets échappés")
            
            # Parcourir chaque ligne pour appliquer la protection dans l'ordre
            for i, line in enumerate(self.file_content):
                # Ignorer les lignes commentées
                stripped_line = line.strip()
                if (stripped_line.startswith('#') or 
                    stripped_line.lower().startswith('old "')):
                    continue
                
                # ✅ CORRECTION : Utiliser PROTECTION_ORDER_NO_ELLIPSIS au lieu de PROTECTION_ORDER
                for pattern, description in PROTECTION_ORDER_NO_ELLIPSIS:
                    # Traitement spécial pour les guillemets échappés
                    if pattern == r'\"':
                        # Créer le placeholder UNE SEULE FOIS
                        if escape_placeholder is None:
                            escape_placeholder = f"(ESC{empty_counter})"
                            self.empty_mapping[escape_placeholder] = r'\"'
                            empty_counter += 1
                            log_message("INFO", f"Placeholder créé pour guillemets échappés: {escape_placeholder}")
                        
                        # Remplacer TOUTES les occurrences avec LE MÊME placeholder
                        while r'\"' in self.file_content[i]:
                            self.file_content[i] = self.file_content[i].replace(r'\"', escape_placeholder, 1)
                    
                    else:
                        # Traitement normal pour les autres patterns
                        while pattern in self.file_content[i]:
                            if pattern not in self.empty_mapping:
                                placeholder = f"(C{empty_counter})"
                                self.empty_mapping[pattern] = placeholder
                                # Stocker le contenu réel pour la reconstruction
                                content = pattern[1:-1]  # Enlever les guillemets externes
                                self.empty_texts.append(content + '\n')
                                empty_counter += 1
                            
                            # Remplacer UNE SEULE occurrence à la fois
                            self.file_content[i] = self.file_content[i].replace(pattern, f'"{self.empty_mapping[pattern]}"', 1)
            
            protected_count = len(self.empty_texts) + (1 if escape_placeholder else 0)
            log_message("INFO", f"Protection terminée: {protected_count} éléments protégés")
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de la protection: {str(e)}", e)
            # En cas d'erreur, réinitialiser
            self.empty_texts = []
            self.empty_mapping = OrderedDict()
            log_message("WARNING", "Protection complète désactivée suite à l'erreur")
    
    def _extract_dialogue_texts(self):
        """Extrait les textes de dialogue et stocke les positions"""
        try:
            extracted_lines = 0
            
            for idx, line in enumerate(self.file_content):
                # Remplacer TOUS les codes spéciaux par des placeholders
                ph_line = line
                
                # D'abord remplacer les balises classiques
                for tag, ph in self.mapping.items():
                    ph_line = ph_line.replace(tag, ph)
                
                # Puis remplacer les textes entre astérisques par des placeholders
                for asterix, placeholder in self.asterix_mapping.items():
                    ph_line = ph_line.replace(asterix, placeholder)
                
                stripped = ph_line.strip()
                
                # Ignorer TOUTES les lignes qui commencent par #
                if stripped.startswith('#'):
                    continue
                    
                # Ignorer aussi translate et old
                if (stripped.lower().startswith('translate ') or 
                    stripped.lower().startswith('old "')):
                    continue
                
                # Extraire TOUS les contenus entre guillemets ET protéger le suffixe
                quote_matches = re.findall(r'"([^"]*)"', stripped)
                
                if quote_matches:
                    # Filtrer les contenus pour ne garder que ceux qui ne sont pas des placeholders vides
                    non_empty_quotes = []
                    for content in quote_matches:
                        # ✅ CORRECTION : Corriger l'expression régulière
                        if not re.match(r'^\(C\d+\)$', content.strip()) and not re.match(r'^\(ESC\d+\)$', content.strip()):
                            if content.strip():  # Ne pas extraire les lignes vides
                                non_empty_quotes.append(content)
                    
                    if non_empty_quotes:
                        self.positions.append(idx)
                        self.line_quote_counts.append(len(non_empty_quotes))
                        
                        # Extraire le suffixe après la dernière guillemet fermante
                        last_quote_pos = -1
                        in_escape = False
                        for i, char in enumerate(stripped):
                            if char == '\\':
                                in_escape = True
                                continue
                            elif char == '"' and not in_escape:
                                last_quote_pos = i
                            in_escape = False
                        
                        # Extraire tout ce qui suit la dernière guillemet
                        suffix = ""
                        if last_quote_pos != -1 and last_quote_pos + 1 < len(stripped):
                            suffix = stripped[last_quote_pos + 1:]
                        
                        self.line_suffixes.append(suffix)
                        
                        # Ajouter chaque contenu entre guillemets
                        for content in non_empty_quotes:
                            self.extracted_texts.append(content + '\n')
                        
                        extracted_lines += 1
            
            log_message("INFO", f"Extraction terminée: {len(self.extracted_texts)} textes extraits de {extracted_lines} lignes")
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors de l'extraction des textes", e)
            raise

    def _save_extraction_files(self):
        """Sauvegarde tous les fichiers d'extraction avec la nouvelle structure organisée"""
        from utils.constants import FOLDERS, ensure_folders_exist
        from utils.logging import extract_game_name
        
        # S'assurer que les dossiers existent
        ensure_folders_exist()
        
        file_base = get_file_base_name(self.original_path)
        game_name = extract_game_name(self.original_path)
        
        result = {
            'file_base': file_base,
            'main_file': None,
            'asterix_file': None,
            'empty_file': None,
            'glossary_file': None,  # ✅ NOUVEAU
            'mapping_files': []
        }
        
        try:
            # Créer la structure complète du dossier temporaire pour ce jeu
            temp_folder = os.path.join(FOLDERS["temp"], game_name)
            folders_to_create = [
                temp_folder,
                os.path.join(temp_folder, "fichiers_a_traduire"),
                os.path.join(temp_folder, "fichiers_a_ne_pas_traduire"),
            ]
            
            for folder in folders_to_create:
                os.makedirs(folder, exist_ok=True)
            
            # Sauvegarder les mappings dans le dossier fichiers_a_ne_pas_traduire
            mapping_folder = os.path.join(temp_folder, "fichiers_a_ne_pas_traduire")
            mapping_files = [
                os.path.join(mapping_folder, f'{file_base}_mapping.txt'),
                os.path.join(mapping_folder, f'{file_base}_asterix_mapping.txt'),
                os.path.join(mapping_folder, f'{file_base}_empty_mapping.txt'),
                os.path.join(mapping_folder, f'{file_base}_glossary_mapping.txt')  # ✅ NOUVEAU
            ]
            
            # Mapping principal
            with open(mapping_files[0], 'w', encoding='utf-8', newline='') as mf:
                for tag, ph in self.mapping.items():
                    mf.write(f"{ph} => {tag}\n")
            
            # Mapping astérisques
            with open(mapping_files[1], 'w', encoding='utf-8', newline='') as amf:
                for asterix, placeholder in self.asterix_mapping.items():
                    amf.write(f"{placeholder} => {asterix}\n")
            
            # Mapping textes vides
            with open(mapping_files[2], 'w', encoding='utf-8', newline='') as emf:
                for empty, placeholder in self.empty_mapping.items():
                    emf.write(f"{placeholder} => {empty}\n")
            
            # ✅ NOUVEAU : Mapping glossaire
            with open(mapping_files[3], 'w', encoding='utf-8', newline='') as gmf:
                for placeholder, term_info in self.glossary_mapping.items():
                    gmf.write(f"{placeholder} => {term_info['original']} => {term_info['translation']}\n")
            
            result['mapping_files'] = mapping_files
            
            # Sauvegarder les positions dans le même dossier
            position_data = {
                'positions': self.positions,
                'quote_counts': self.line_quote_counts,
                'suffixes': self.line_suffixes
            }
            
            positions_file = os.path.join(mapping_folder, f'{file_base}_positions.json')
            with open(positions_file, 'w', encoding='utf-8', newline='') as pf:
                json.dump(position_data, pf, ensure_ascii=False)
            
            result['positions_file'] = positions_file
            
            # Écrire les fichiers de textes dans fichiers_a_traduire
            translate_folder = os.path.join(temp_folder, "fichiers_a_traduire")
            
            # Fichier principal
            main_file = os.path.join(translate_folder, f'{file_base}.txt')
            with open(main_file, 'w', encoding='utf-8', newline='') as vf:
                vf.writelines(self.extracted_texts)
            result['main_file'] = main_file
            
            # Créer fichier astérisques seulement s'il y a du contenu
            if self.asterix_texts:
                asterix_file = os.path.join(translate_folder, f'{file_base}_asterix.txt')
                with open(asterix_file, 'w', encoding='utf-8', newline='') as af:
                    af.writelines(self.asterix_texts)
                result['asterix_file'] = asterix_file
            
            # Créer fichier textes vides seulement s'il y a du contenu
            if self.empty_texts:
                empty_file = os.path.join(translate_folder, f'{file_base}_empty.txt')
                with open(empty_file, 'w', encoding='utf-8', newline='') as ef:
                    ef.writelines(self.empty_texts)
                result['empty_file'] = empty_file
            
            # ✅ NOUVEAU : Créer fichier glossaire seulement s'il y a du contenu
            if self.glossary_mapping:
                glossary_file = os.path.join(translate_folder, f'{file_base}_glossary.txt')
                with open(glossary_file, 'w', encoding='utf-8', newline='') as gf:
                    gf.write("# Fichier des termes du glossaire\n")
                    gf.write("# Ces termes seront automatiquement traduits\n")
                    gf.write("# NE PAS MODIFIER ce fichier\n\n")
                    for placeholder, term_info in self.glossary_mapping.items():
                        gf.write(f"{term_info['translation']}\n")
                result['glossary_file'] = glossary_file
            
            log_message("INFO", f"Fichiers d'extraction créés dans temporaires/{game_name}/")
            return result
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors de la création des fichiers d'extraction", e)
            raise

# Fonction utilitaire pour compatibilité avec l'ancienne interface
def extraire_textes_enhanced(file_content, original_path):
    """
    Fonction d'extraction avec support du glossaire
    
    Args:
        file_content (list): Contenu du fichier
        original_path (str): Chemin du fichier original
        
    Returns:
        dict: Résultats de l'extraction
    """
    # 1) Validation avant extraction
    from core.validation import validate_before_extraction, create_safety_backup
    validate_before_extraction(original_path)
    create_safety_backup(original_path)

    # 2) Lancer l'extraction avec glossaire
    extractor = EnhancedTextExtractor()
    extractor.load_file_content(file_content, original_path)
    return extractor.extract_texts()