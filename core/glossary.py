# core/glossary.py
# Glossary Management System
# Created for Traducteur Ren'Py Pro v2.4.1

"""
Système de gestion du glossaire pour la traduction automatique
"""

import os
import json
import re
from collections import OrderedDict
from utils.constants import FOLDERS
from utils.logging import log_message

class GlossaryManager:
    """Gestionnaire principal du glossaire"""
    
    def __init__(self):
        self.glossary_file = os.path.join(FOLDERS["configs"], "glossary.json")
        self.glossary = OrderedDict()
        self.temp_placeholders = {}
        self.placeholder_counter = 0
        self.load_glossary()
    
    def load_glossary(self):
        """Charge le glossaire depuis le fichier JSON"""
        try:
            if os.path.exists(self.glossary_file):
                with open(self.glossary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Trier par longueur décroissante pour traiter les termes les plus longs en premier
                    self.glossary = OrderedDict(sorted(data.items(), key=lambda x: len(x[0]), reverse=True))
                log_message("INFO", f"Glossaire chargé: {len(self.glossary)} entrées")
            else:
                self.glossary = OrderedDict()
                self.save_glossary()
                log_message("INFO", "Nouveau glossaire créé")
        except Exception as e:
            log_message("ERREUR", f"Erreur lors du chargement du glossaire", e)
            self.glossary = OrderedDict()
    
    def save_glossary(self):
        """Sauvegarde le glossaire dans le fichier JSON"""
        try:
            os.makedirs(os.path.dirname(self.glossary_file), exist_ok=True)
            with open(self.glossary_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.glossary), f, ensure_ascii=False, indent=2)
            log_message("INFO", f"Glossaire sauvegardé: {len(self.glossary)} entrées")
            return True
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de la sauvegarde du glossaire", e)
            return False
    
    def add_entry(self, original, translation):
        """Ajoute une entrée au glossaire"""
        try:
            if not original or not translation:
                return False
            
            original = original.strip()
            translation = translation.strip()
            
            if original in self.glossary:
                # Mettre à jour l'entrée existante
                old_translation = self.glossary[original]
                self.glossary[original] = translation
                log_message("INFO", f"Entrée mise à jour: '{original}' -> '{translation}' (était: '{old_translation}')")
            else:
                # Nouvelle entrée
                self.glossary[original] = translation
                log_message("INFO", f"Nouvelle entrée ajoutée: '{original}' -> '{translation}'")
            
            # Retrier par longueur
            self.glossary = OrderedDict(sorted(self.glossary.items(), key=lambda x: len(x[0]), reverse=True))
            
            return self.save_glossary()
            
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de l'ajout d'entrée au glossaire", e)
            return False
    
    def remove_entry(self, original):
        """Supprime une entrée du glossaire"""
        try:
            if original in self.glossary:
                translation = self.glossary.pop(original)
                log_message("INFO", f"Entrée supprimée: '{original}' -> '{translation}'")
                return self.save_glossary()
            return False
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de la suppression d'entrée du glossaire", e)
            return False
    
    def get_all_entries(self):
        """Retourne toutes les entrées du glossaire"""
        return dict(self.glossary)
    
    def search_entries(self, search_term):
        """Recherche des entrées dans le glossaire"""
        try:
            search_term = search_term.lower()
            results = []
            
            for original, translation in self.glossary.items():
                if (search_term in original.lower() or 
                    search_term in translation.lower()):
                    results.append((original, translation))
            
            return results
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de la recherche dans le glossaire", e)
            return []
    
    def get_statistics(self):
        """Retourne les statistiques du glossaire"""
        return {
            'total_entries': len(self.glossary),
            'average_length': sum(len(key) for key in self.glossary.keys()) / max(len(self.glossary), 1),
            'longest_term': max(self.glossary.keys(), key=len) if self.glossary else "",
            'shortest_term': min(self.glossary.keys(), key=len) if self.glossary else ""
        }
    
    def protect_glossary_terms(self, file_content):
        """Protège les termes du glossaire dans le contenu avec des placeholders"""
        try:
            if not self.glossary:
                return file_content, {}
            
            protected_content = file_content[:]
            glossary_mapping = {}
            self.placeholder_counter = 0
            
            # Traiter chaque ligne
            for i, line in enumerate(protected_content):
                # Ignorer les lignes commentées
                if line.strip().startswith('#'):
                    continue
                
                # Pour chaque terme du glossaire (du plus long au plus court)
                for original, translation in self.glossary.items():
                    if original in line:
                        # Créer un placeholder unique
                        self.placeholder_counter += 1
                        placeholder = f"(GLOSS{self.placeholder_counter:03d})"
                        
                        # Stocker le mapping
                        glossary_mapping[placeholder] = {
                            'original': original,
                            'translation': translation
                        }
                        
                        # Remplacer dans la ligne
                        protected_content[i] = protected_content[i].replace(original, placeholder)
                        
                        log_message("INFO", f"Terme protégé: '{original}' -> {placeholder}")
            
            return protected_content, glossary_mapping
            
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de la protection des termes du glossaire", e)
            return file_content, {}
    
    def validate_glossary(self):
        """Valide le glossaire et retourne une liste des problèmes"""
        issues = []
        
        try:
            for original, translation in self.glossary.items():
                # Vérifier les entrées vides
                if not original.strip():
                    issues.append("Terme original vide détecté")
                
                if not translation.strip():
                    issues.append(f"Traduction vide pour '{original}'")
                
                # Vérifier les doublons (même traduction)
                duplicates = [k for k, v in self.glossary.items() if v == translation and k != original]
                if duplicates:
                    issues.append(f"Traduction dupliquée '{translation}' pour '{original}' et {duplicates}")
                
                # Vérifier les termes trop courts (potentiellement problématiques)
                if len(original) <= 2:
                    issues.append(f"Terme très court: '{original}' (peut causer des remplacements indésirables)")
                
                # Vérifier les caractères spéciaux
                if re.search(r'[{}[\]()"]', original):
                    issues.append(f"Terme contenant des caractères spéciaux: '{original}'")
        
        except Exception as e:
            issues.append(f"Erreur lors de la validation: {str(e)}")
        
        return issues
    
    def export_glossary(self, file_path):
        """Exporte le glossaire vers un fichier texte"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# Glossaire Traducteur Ren'Py Pro\n")
                f.write("# Format: Original => Traduction\n\n")
                
                for original, translation in self.glossary.items():
                    f.write(f"{original} => {translation}\n")
            
            log_message("INFO", f"Glossaire exporté vers: {file_path}")
            return True
            
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de l'export du glossaire", e)
            return False
    
    def import_glossary(self, file_path, merge=True):
        """Importe un glossaire depuis un fichier texte"""
        try:
            if not merge:
                self.glossary.clear()
            
            imported_count = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Ignorer les commentaires et lignes vides
                    if not line or line.startswith('#'):
                        continue
                    
                    # Format: "Original => Traduction"
                    if ' => ' in line:
                        parts = line.split(' => ', 1)
                        if len(parts) == 2:
                            original = parts[0].strip()
                            translation = parts[1].strip()
                            
                            if original and translation:
                                self.glossary[original] = translation
                                imported_count += 1
                    else:
                        log_message("WARNING", f"Ligne ignorée (format incorrect) ligne {line_num}: {line}")
            
            # Retrier par longueur
            self.glossary = OrderedDict(sorted(self.glossary.items(), key=lambda x: len(x[0]), reverse=True))
            
            success = self.save_glossary()
            if success:
                log_message("INFO", f"Glossaire importé: {imported_count} entrées depuis {file_path}")
            
            return success
            
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de l'import du glossaire", e)
            return False

# Instance globale du gestionnaire de glossaire
glossary_manager = GlossaryManager()