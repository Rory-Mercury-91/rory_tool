# core/coherence_checker.py
# Coherence Checker Module
# Created for Traducteur Ren'Py Pro v1.1.2

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
        """Analyse les lignes pour détecter les incohérences"""
        old_line = None
        old_line_num = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Détecter les lignes OLD commentées
            if self._is_old_line(stripped):
                old_line = stripped
                old_line_num = i
                continue
            
            # Détecter les lignes NEW (traductions)
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
                    # NEW sans OLD correspondant
                    result['issues'].append({
                        'line': i,
                        'type': 'MISSING_OLD',
                        'description': f"Ligne NEW sans OLD correspondant",
                        'content': stripped
                    })
        
        result['issues_found'] = len(result['issues'])
    
    def _is_old_line(self, line):
        """Vérifie si une ligne est une ligne OLD commentée"""
        return (line.startswith('# ') and 
                ('"' in line or 'old "' in line.lower()))
    
    def _is_new_line(self, line):
        """Vérifie si une ligne est une ligne NEW (traduction)"""
        return (not line.startswith('#') and 
                '"' in line and 
                not line.lower().startswith('old ') and
                not line.lower().startswith('translate '))
    
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
        """Crée le fichier d'avertissement avec les problèmes détectés"""
        try:
            base_name = os.path.splitext(os.path.basename(original_filepath))[0]
            warning_file = f"{base_name}_avertissement.txt"
            
            with open(warning_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("RAPPORT DE CONTRÔLE DE COHÉRENCE OLD/NEW\n")
                f.write("=" * 60 + "\n")
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
            
            log_message("INFO", f"Fichier d'avertissement créé: {warning_file}")
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