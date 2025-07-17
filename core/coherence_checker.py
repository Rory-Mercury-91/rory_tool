# core/coherence_checker.py
# Coherence Checker Module
# Created for Traducteur Ren'Py Pro v2.4.1

"""
Module de vérification de la cohérence entre lignes OLD et NEW
"""

import re
import os
from utils.logging import log_message

class CoherenceChecker:
    """Vérificateur de cohérence OLD/NEW"""
    
    def __init__(self):
        self.issues = []
        self.checked_lines = 0
        
    def check_file_coherence(self, filepath):
        """
        Vérifie la cohérence d'un fichier .rpy traduit
        
        Args:
            filepath (str): Chemin du fichier à vérifier
            
        Returns:
            dict: Résultats de la vérification
        """
        result = {
            'success': True,
            'issues_found': 0,
            'issues': [],
            'checked_lines': 0,
            'warning_file': None
        }
        
        try:
            if not os.path.exists(filepath):
                result['success'] = False
                result['issues'].append({
                    'line': 0,
                    'type': 'FILE_ERROR',
                    'description': f"Fichier non trouvé: {filepath}"
                })
                return result
            
            # Lire le fichier
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Analyser ligne par ligne
            self._analyze_lines(lines, result)
            
            # Créer le fichier d'avertissement si nécessaire
            if result['issues']:
                warning_file = self._create_warning_file(filepath, result['issues'])
                result['warning_file'] = warning_file
            
            log_message("INFO", f"Contrôle cohérence: {result['issues_found']} problèmes détectés sur {result['checked_lines']} lignes")
            
        except Exception as e:
            log_message("ERREUR", f"Erreur lors du contrôle de cohérence de {filepath}", e)
            result['success'] = False
            result['issues'].append({
                'line': 0,
                'type': 'SYSTEM_ERROR',
                'description': f"Erreur système: {str(e)}"
            })
        
        return result
    
    def _analyze_lines(self, lines, result):
        """Analyse les lignes - VERSION CORRIGÉE pour strings"""
        old_line = None
        old_line_num = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Détecter les lignes OLD
            if self._is_old_line(stripped):
                old_line = stripped
                old_line_num = i
                continue
            
            # Détecter les lignes NEW
            if self._is_new_line(stripped):
                result['checked_lines'] += 1
                
                if old_line:
                    # Vérifier la cohérence entre OLD et NEW
                    issues = self._check_line_coherence(old_line, stripped, old_line_num, i)
                    result['issues'].extend(issues)
                    
                    # Reset pour la prochaine paire
                    old_line = None
                    old_line_num = 0
                else:
                    # CORRECTION : Vérifier si on est dans une section strings
                    if self._is_in_strings_section(i, lines):
                        # Dans strings, c'est normal d'avoir NEW sans OLD commenté
                        continue
                    
                    # CORRECTION : Vérifier si c'est vraiment un problème
                    if self._is_missing_old_problematic(stripped, lines, i):
                        result['issues'].append({
                            'line': i,
                            'type': 'MISSING_OLD',
                            'description': f"Ligne NEW sans OLD correspondant",
                            'content': stripped[:100] + '...' if len(stripped) > 100 else stripped
                        })
        
        result['issues_found'] = len(result['issues'])

    def _is_missing_old_problematic(self, new_line, all_lines, line_index):
        """
        Vérifie si l'absence de ligne OLD est vraiment problématique - VERSION CORRIGÉE
        
        Args:
            new_line (str): La ligne NEW actuelle
            all_lines (list): Toutes les lignes du fichier
            line_index (int): Index de la ligne actuelle (1-based)
            
        Returns:
            bool: True si c'est vraiment un problème
        """
        try:
            # CORRECTION PRIORITAIRE : Vérifier si on est dans une section strings
            if self._is_in_strings_section(line_index, all_lines):
                return False  # Dans une section strings, c'est normal d'avoir NEW sans OLD commenté
            
            # CORRECTION 1: Ignorer les lignes dans des blocs de traduction normaux
            # Chercher les lignes précédentes pour contexte
            context_range = max(0, line_index - 10)
            previous_lines = all_lines[context_range:line_index-1]
            
            # Si on trouve un bloc de traduction standard, ce n'est pas un problème
            for prev_line in reversed(previous_lines):
                prev_stripped = prev_line.strip()
                
                # Si on trouve un "translate french" récent, c'est normal
                if prev_stripped.startswith('translate ') and ':' in prev_stripped:
                    return False
                
                # CORRECTION : Support de tous les types de commentaires de fichier
                if (prev_stripped.startswith('# game/') or 
                    prev_stripped.startswith('# renpy/') or 
                    prev_stripped.startswith('# common/')) and '.rpy:' in prev_stripped:
                    return False
            
            # CORRECTION 2: Ignorer les lignes très simples ou vides
            new_content = new_line.strip()
            
            # Lignes vides ou très courtes = pas problématique
            if len(new_content) <= 5:
                return False
            
            # Lignes avec seulement des variables ou codes = pas problématique
            if self._is_mostly_code(new_content):
                return False
            
            # CORRECTION 3: Ignorer les sections menu et autres structures spéciales
            for prev_line in reversed(previous_lines):
                prev_stripped = prev_line.strip()
                
                # Section strings (double vérification)
                if 'translate french strings:' in prev_stripped:
                    return False
                if prev_stripped.startswith('translate ') and 'strings' in prev_stripped:
                    return False
                
                # Sections menu
                if prev_stripped.startswith('translate ') and 'menu' in prev_stripped:
                    return False
            
            # CORRECTION 4: Ignorer les lignes qui commencent par new (cas non commenté)
            if new_content.startswith('new ') and '"' in new_content:
                # C'est une ligne NEW non commentée, vérifier s'il y a un OLD correspondant juste avant
                if line_index > 1:
                    prev_line = all_lines[line_index - 2].strip()  # line_index est 1-based
                    if prev_line.startswith('old ') and '"' in prev_line:
                        return False  # Il y a bien un OLD correspondant
            
            # Si aucune exception trouvée, c'est potentiellement problématique
            return True
            
        except Exception:
            # En cas d'erreur, ne pas signaler comme problématique
            return False

    def _is_mostly_code(self, text):
        """Vérifie si une ligne contient principalement du code/variables"""
        try:
            # Compter les caractères de code vs texte normal
            code_chars = 0
            total_chars = len(text)
            
            if total_chars == 0:
                return True
            
            # Compter les variables [], {}, %(), etc.
            import re
            
            # Variables et codes
            variables = re.findall(r'\[[^\]]*\]|\{[^}]*\}|%\([^)]*\)|%[a-zA-Z_]|\(\d+\)', text)
            for var in variables:
                code_chars += len(var)
            
            # Séquences d'échappement
            escapes = re.findall(r'\\[a-zA-Z]', text)
            for esc in escapes:
                code_chars += len(esc)
            
            # Si plus de 40% du texte est du code, considérer comme "principalement code"
            code_ratio = code_chars / total_chars
            return code_ratio > 0.4
            
        except Exception:
            return False

    def _is_old_line(self, line):
        """Vérifie si une ligne est une ligne OLD - VERSION CORRIGÉE"""
        stripped = line.strip()
        
        # Cas 1: OLD non commenté dans les sections strings
        if stripped.startswith('old ') and '"' in stripped:
            return True
        
        # Cas 2: OLD commenté classique
        if not stripped.startswith('# '):
            return False
        
        # Doit contenir des guillemets ou "old"
        has_quotes = '"' in stripped
        has_old_keyword = 'old ' in stripped.lower()
        
        # CORRECTION : Supporter tous les types de chemins de fichiers
        is_file_comment = (stripped.startswith('# game/') or 
                        stripped.startswith('# renpy/') or    # ← NOUVEAU
                        stripped.startswith('# common/') or   # ← NOUVEAU  
                        '.rpy:' in stripped)
        is_todo_comment = 'TODO:' in stripped or 'Translation updated' in stripped
        
        return (has_quotes or has_old_keyword) and not is_file_comment and not is_todo_comment

    def _is_new_line(self, line):
        """Vérifie si une ligne est une ligne NEW - VERSION CORRIGÉE"""
        stripped = line.strip()
        
        if stripped.startswith('#'):
            return False
        
        # CORRECTION : Exclure les lignes OLD non commentées
        if stripped.startswith('old '):
            return False
        
        # CORRECTION : Détecter les lignes NEW non commentées dans strings
        if stripped.startswith('new ') and '"' in stripped:
            return True
        
        # Doit contenir des guillemets pour les lignes classiques
        if '"' not in stripped:
            return False
        
        # Exclure les lignes de structure Ren'Py
        if stripped.lower().startswith('translate '):
            return False
        
        # Exclure les labels et définitions
        if ':' in stripped and any(keyword in stripped.lower() for keyword in ['label ', 'menu:', 'if ', 'else:', 'elif ']):
            return False
        
        return True

    def _is_in_strings_section(self, line_index, all_lines):
        """
        Détecte si on est dans une section translate strings
        
        Args:
            line_index (int): Index de la ligne actuelle (1-based)
            all_lines (list): Toutes les lignes du fichier
            
        Returns:
            bool: True si on est dans une section strings
        """
        try:
            # Chercher en arrière jusqu'à 50 lignes pour trouver le début de section
            search_start = max(0, line_index - 50)
            
            for i in range(search_start, line_index):
                line = all_lines[i].strip()
                
                # Trouvé une section strings
                if line.startswith('translate ') and line.endswith('strings:'):
                    return True
                    
                # Trouvé une autre section translate (dialogue normal)
                if (line.startswith('translate ') and 
                    not line.endswith('strings:') and 
                    ':' in line and
                    'strings' not in line):
                    return False
            
            return False
            
        except Exception:
            return False

    def _check_line_coherence(self, old_line, new_line, old_line_num, new_line_num):
        """Vérifie la cohérence entre une ligne OLD et NEW"""
        issues = []
        
        try:
            # Extraire les contenus entre guillemets
            old_content = self._extract_quoted_content(old_line)
            new_content = self._extract_quoted_content(new_line)
            
            if not old_content or not new_content:
                return issues
            
            # Vérifier chaque paire de contenus
            for old_text, new_text in zip(old_content, new_content):
                issues.extend(self._check_content_coherence(
                    old_text, new_text, old_line_num, new_line_num
                ))
            
            # Vérifier que le nombre de guillemets correspond
            if len(old_content) != len(new_content):
                issues.append({
                    'line': new_line_num,
                    'type': 'QUOTE_COUNT_MISMATCH',
                    'description': f"Nombre de guillemets différent (OLD: {len(old_content)}, NEW: {len(new_content)})",
                    'old_line': old_line_num,
                    'old_content': old_line,
                    'new_content': new_line
                })
        
        except Exception as e:
            issues.append({
                'line': new_line_num,
                'type': 'ANALYSIS_ERROR',
                'description': f"Erreur d'analyse: {str(e)}",
                'old_line': old_line_num
            })
        
        return issues
    
    def _extract_quoted_content(self, line):
        """Extrait tous les contenus entre guillemets d'une ligne"""
        return re.findall(r'"([^"]*)"', line)
    
    def _check_content_coherence(self, old_text, new_text, old_line_num, new_line_num):
        """Vérifie la cohérence entre deux contenus textuels"""
        issues = []
        
        # 1. Vérifier les balises {}
        old_tags = re.findall(r'\{[^}]*\}', old_text)
        new_tags = re.findall(r'\{[^}]*\}', new_text)
        
        if old_tags != new_tags:
            issues.append({
                'line': new_line_num,
                'type': 'TAG_MISMATCH',
                'description': f"Balises {{}} différentes - OLD: {old_tags}, NEW: {new_tags}",
                'old_line': old_line_num,
                'old_content': old_text,
                'new_content': new_text
            })
        
        # 2. Vérifier les variables []
        old_vars = re.findall(r'\[[^\]]*\]', old_text)
        new_vars = re.findall(r'\[[^\]]*\]', new_text)
        
        if old_vars != new_vars:
            issues.append({
                'line': new_line_num,
                'type': 'VARIABLE_MISMATCH',
                'description': f"Variables [] différentes - OLD: {old_vars}, NEW: {new_vars}",
                'old_line': old_line_num,
                'old_content': old_text,
                'new_content': new_text
            })
        
        # 3. Vérifier les placeholders ()
        old_placeholders = re.findall(r'\(\d+\)', old_text)
        new_placeholders = re.findall(r'\(\d+\)', new_text)
        
        if old_placeholders != new_placeholders:
            issues.append({
                'line': new_line_num,
                'type': 'PLACEHOLDER_MISMATCH',
                'description': f"Placeholders () différents - OLD: {old_placeholders}, NEW: {new_placeholders}",
                'old_line': old_line_num,
                'old_content': old_text,
                'new_content': new_text
            })
        
        # 4. Vérifier les placeholders malformés
        malformed = re.findall(r'\(\d+(?!\))', new_text)
        if malformed:
            issues.append({
                'line': new_line_num,
                'type': 'MALFORMED_PLACEHOLDER',
                'description': f"Placeholders malformés détectés: {malformed}",
                'old_line': old_line_num,
                'old_content': old_text,
                'new_content': new_text
            })
        
        # 5. Vérifier les balises orphelines
        orphan_open = re.findall(r'\{[^}]*$', new_text)
        orphan_close = re.findall(r'^[^{]*\}', new_text)
        
        if orphan_open or orphan_close:
            issues.append({
                'line': new_line_num,
                'type': 'ORPHAN_TAG',
                'description': f"Balises orphelines détectées - Ouvertes: {orphan_open}, Fermées: {orphan_close}",
                'old_line': old_line_num,
                'old_content': old_text,
                'new_content': new_text
            })
        
        # 6. Vérifier les codes spéciaux
        old_special = re.findall(r'\\n|--|%[^%]*%', old_text)
        new_special = re.findall(r'\\n|--|%[^%]*%', new_text)
        
        if old_special != new_special:
            issues.append({
                'line': new_line_num,
                'type': 'SPECIAL_CODE_MISMATCH',
                'description': f"Codes spéciaux différents - OLD: {old_special}, NEW: {new_special}",
                'old_line': old_line_num,
                'old_content': old_text,
                'new_content': new_text
            })
        
        return issues
    
    def _create_warning_file(self, original_filepath, issues):
        """CORRIGÉ : Crée le fichier d'avertissement dans l'arborescence organisée"""
        try:
            from utils.constants import FOLDERS, ensure_folders_exist
            from utils.logging import extract_game_name
            
            # S'assurer que le dossier existe
            ensure_folders_exist()
            
            # ✅ CORRECTION : Structure organisée par jeu
            game_name = extract_game_name(original_filepath)
            warnings_root = FOLDERS["warnings"]
            game_warnings_folder = os.path.join(warnings_root, game_name)
            
            # Créer le dossier d'avertissements du jeu
            os.makedirs(game_warnings_folder, exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(original_filepath))[0]
            warning_file = os.path.join(game_warnings_folder, f"{base_name}_avertissement.txt")
            
            with open(warning_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("RAPPORT DE CONTRÔLE DE COHÉRENCE OLD/NEW\n")
                f.write("=" * 60 + "\n")
                f.write(f"Jeu: {game_name}\n")
                f.write(f"Fichier analysé: {os.path.basename(original_filepath)}\n")
                f.write(f"Date: {self._get_current_datetime()}\n")
                f.write(f"Problèmes détectés: {len(issues)}\n")
                f.write("=" * 60 + "\n\n")
                
                # Grouper par type
                issues_by_type = {}
                for issue in issues:
                    issue_type = issue['type']
                    if issue_type not in issues_by_type:
                        issues_by_type[issue_type] = []
                    issues_by_type[issue_type].append(issue)
                
                # Écrire chaque type
                for issue_type, type_issues in issues_by_type.items():
                    f.write(f"🔸 {self._get_issue_type_name(issue_type)}\n")
                    f.write("-" * 40 + "\n")
                    
                    for issue in type_issues:
                        f.write(f"Ligne {issue['line']}: {issue['description']}\n")
                        
                        if issue.get('old_line'):
                            f.write(f"  OLD (ligne {issue['old_line']}): {issue.get('old_content', 'N/A')}\n")
                        if issue.get('new_content'):
                            f.write(f"  NEW: {issue['new_content']}\n")
                        
                        f.write("\n")
                    
                    f.write("\n")
                
                # Résumé final
                f.write("=" * 60 + "\n")
                f.write("RÉSUMÉ\n")
                f.write("=" * 60 + "\n")
                for issue_type, type_issues in issues_by_type.items():
                    f.write(f"{self._get_issue_type_name(issue_type)}: {len(type_issues)} problème(s)\n")
                
                f.write("\n")
                f.write("⚠️  Ces problèmes peuvent causer des erreurs dans le jeu.\n")
                f.write("💡 Vérifiez et corrigez les incohérences avant de finaliser la traduction.\n")
            
            log_message("INFO", f"Fichier d'avertissement créé: {game_name}/{os.path.basename(warning_file)}")
            return warning_file
            
        except Exception as e:
            log_message("ERREUR", f"Impossible de créer le fichier d'avertissement", e)
            return None
    
    def _get_issue_type_name(self, issue_type):
        """Retourne le nom lisible d'un type de problème"""
        names = {
            'TAG_MISMATCH': 'Balises {} incohérentes',
            'VARIABLE_MISMATCH': 'Variables [] incohérentes', 
            'PLACEHOLDER_MISMATCH': 'Placeholders () incohérents',
            'MALFORMED_PLACEHOLDER': 'Placeholders malformés',
            'ORPHAN_TAG': 'Balises orphelines',
            'SPECIAL_CODE_MISMATCH': 'Codes spéciaux incohérents',
            'QUOTE_COUNT_MISMATCH': 'Nombre de guillemets différent',
            'MISSING_OLD': 'Ligne OLD manquante',
            'FILE_ERROR': 'Erreur de fichier',
            'SYSTEM_ERROR': 'Erreur système',
            'ANALYSIS_ERROR': 'Erreur d\'analyse'
        }
        return names.get(issue_type, issue_type)
    
    def _get_current_datetime(self):
        """Retourne la date/heure actuelle formatée"""
        import datetime
        return datetime.datetime.now().strftime("%d/%m/%Y à %H:%M:%S")

# Fonction utilitaire
def check_file_coherence(filepath):
    """
    Vérifie la cohérence d'un fichier traduit
    
    Args:
        filepath (str): Chemin du fichier à vérifier
        
    Returns:
        dict: Résultats de la vérification
    """
    checker = CoherenceChecker()
    return checker.check_file_coherence(filepath)