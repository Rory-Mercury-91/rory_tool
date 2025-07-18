# utils/i18n.py
import json
import os
from utils.constants import FOLDERS
from utils.logging import log_message

class I18nManager:
    SUPPORTED_LANGUAGES = {'fr': 'Français', 'en': 'English', 'de': 'Deutsch'}

    def __init__(self):
        self.current_language = 'fr'
        self.translations = {}
        self.language_file = os.path.join(FOLDERS["configs"], "languages.json")
        self.load_translations()

    def load_translations(self):
        try:
            if os.path.exists(self.language_file):
                with open(self.language_file, 'r', encoding='utf-8') as f:
                    loaded_translations = json.load(f)
                    default_translations = self._get_default_translations()
                    for lang in self.SUPPORTED_LANGUAGES:
                        if lang not in loaded_translations:
                            loaded_translations[lang] = default_translations[lang]
                        else:
                            for key, value in default_translations[lang].items():
                                if key not in loaded_translations[lang]:
                                    loaded_translations[lang][key] = value
                    self.translations = loaded_translations
            else:
                self.translations = self._get_default_translations()
                self.save_translations()
        except Exception as e:
            log_message("WARNING", f"Erreur chargement traductions: {e}")
            self.translations = self._get_default_translations()

    def save_translations(self):
        try:
            os.makedirs(os.path.dirname(self.language_file), exist_ok=True)
            with open(self.language_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_message("WARNING", f"Erreur sauvegarde traductions: {e}")

    def get_text(self, key, **kwargs):
        try:
            keys = key.split('.')
            text = self.translations.get(self.current_language, {})
            for k in keys:
                text = text.get(k, key)
                if isinstance(text, str):
                    break
            if text == key and self.current_language != 'fr':
                text = self.translations.get('fr', {})
                for k in keys:
                    text = text.get(k, key)
                    if isinstance(text, str):
                        break
            if isinstance(text, str) and kwargs:
                try:
                    text = text.format(**kwargs)
                except (KeyError, ValueError):
                    pass
            return text if isinstance(text, str) else key
        except Exception as e:
            log_message("WARNING", f"Erreur traduction '{key}': {e}")
            return key

    def set_language(self, language_code):
        if language_code in self.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            return True
        return False

    def get_current_language(self):
        return self.current_language

    def get_language_name(self, code=None):
        code = code or self.current_language
        return self.SUPPORTED_LANGUAGES.get(code, code)

    def _get_default_translations(self):
        return {
            'fr': {
                'window': {
                    'title': '🎮 RenExtract v{version}',
                    'subtitle': 'Extraction intelligente de scripts Ren-Py'
                },
                'buttons': {
                    'extract': '⚡ Extraire',
                    'reconstruct': '🔗 Reconstruire',
                    'drag_drop': '© D&D',
                    'glossary': '📖 Glossaire',
                    'clean': '🧹 Nettoyer',
                    'temporary': '📁 Temporaire',
                    'warnings': '⚠ Avertissements',
                    'auto_open': '🗃️ Auto : {status}',
                    'validation': '✅ Valid : {status}',
                    'help': '💡 Aide',
                    'theme': 'Mode Clair',
                    'theme_dark': 'Mode Sombre',
                    'language': 'Français',
                    'quit': 'Quitter',
                    'close': '❌ Fermer',
                    'open_file': '📂 Ouvrir Fichier .rpy',
                    'open_folder': '📁 Ouvrir Dossier',
                    'backups': '🛡️ Sauvegardes',
                    'reset': '🔄 Réinitialiser',
                    'input_mode': '⌨️ {mode}'
                },
                'help': {
                    'title': '🎓 Centre d\'aide v{version}',
                    'subtitle': '🎓 Centre d\'aide - Choisissez votre type d\'aide',
                    'buttons': {
                        'complete_guide': '📖 Guide complet v{version}',
                        'express_guide': '⚡ Guide express',
                        'whats_new': '🆕 Nouveautés v{version}',
                        'glossary_help': '📚 Aide Glossaire',
                        'extraction_help': '⚡ Aide Extraction',
                        'reconstruction_help': '🔧 Aide Reconstruction',
                        'validation_help': '✅ Aide Validation',
                        'file_organization': '📁 Organisation fichiers'
                    },
                    'descriptions': {
                        'complete_guide': 'Guide détaillé avec toutes les fonctionnalités actuelles',
                        'express_guide': 'Version rapide pour utilisateurs expérimentés',
                        'whats_new': 'Découvrir les améliorations et nouvelles fonctions',
                        'glossary_help': 'Système de glossaire permanent et protection automatique',
                        'extraction_help': 'Extraction enhanced avec structure organisée',
                        'reconstruction_help': 'Reconstruction avec glossaire et validation',
                        'validation_help': 'Validation avancée et rapports d\'erreurs',
                        'file_organization': 'Structure organisée par jeu v{version}'
                    }
                },
                'glossary': {
                    'title': '📚 Gestionnaire de Glossaire',
                    'subtitle': 'Gérez votre glossaire de traduction permanent',
                    'search': '🔍 Rechercher:',
                    'entries_title': '📝 Entrées du glossaire',
                    'edit_title': '✏️ Édition',
                    'original_label': 'Original:',
                    'translation_label': 'Traduction:',
                    'buttons': {
                        'add': '➕ Ajouter',
                        'modify': '✏️ Modifier',
                        'delete': '🗑️ Supprimer',
                        'new': '🆕 Nouveau',
                        'export': '📤 Exporter',
                        'import': '📥 Importer',
                        'validate': '✅ Valider',
                        'close': '✅ Fermer'
                    },
                    'messages': {
                        'empty_fields': 'Veuillez remplir les deux champs.',
                        'no_selection': 'Veuillez sélectionner une entrée à modifier.',
                        'no_selection_delete': 'Veuillez sélectionner une entrée à supprimer.',
                        'confirm_delete': 'Voulez-vous vraiment supprimer cette entrée ?\n\n\'{original}\' → \'{translation}\'',
                        'add_error': 'Impossible d\'ajouter l\'entrée.',
                        'modify_error': 'Impossible de modifier l\'entrée.',
                        'export_error': 'Impossible d\'exporter le glossaire.',
                        'import_error': 'Impossible d\'importer le glossaire.',
                        'import_mode': 'Voulez-vous fusionner avec le glossaire existant ?\n\n• Oui = Ajouter aux entrées existantes\n• Non = Remplacer complètement le glossaire',
                        'validation_issues': '⚠️ {count} problème(s) détecté(s)',
                        'validation_issues_text': 'Problèmes trouvés:\n\n{issues}',
                        'validation_success': '✅ Glossaire validé sans problème'
                    }
                },
                'tutorial': {
                    'title': 'Guide Complet - RenExtract v{version}',
                    'subtitle': 'Bienvenue dans RenExtract !',
                    'express_title': 'Guide Express - RenExtract v{version}',
                    'whats_new_title': 'Nouveautés - RenExtract v{version}',
                    'non_blocking_notice': '💡 Cette fenêtre est non-bloquante : vous pouvez utiliser l\'application simultanément !',
                    'dont_show_again': 'Ne plus afficher ce guide au démarrage',
                    'understood_button': '✅ J\'ai compris !',
                    'review_later_button': '🔄 Revoir plus tard',
                    'sections': {
                        'overview': '�� Vue d\'ensemble',
                        'workflow': '🔄 Workflow de traduction',
                        'features': '✨ Nouvelles fonctionnalités',
                        'quick_workflow': '⚡ Workflow rapide',
                        'new_features': '�� Nouvelles fonctionnalités',
                        'shortcuts': '⌨️ Raccourcis',
                        'i18n_system': '🌍 Système d\'internationalisation',
                        'smart_notifications': '🔕 Notifications intelligentes',
                        'improved_ux': '🎨 Interface améliorée'
                    },
                    'content': {
                        'quick_steps': '1️⃣ Chargez un fichier .rpy\n2️⃣ Cliquez "⚡ Extraire"\n3️⃣ Traduisez les fichiers .txt\n4️⃣ Cliquez "🔗 Reconstruire"\n�� Validation automatique incluse',
                        'glossary_brief': '📚 Glossaire permanent avec traduction automatique',
                        'architecture_brief': '��️ Structure organisée par jeu',
                        'notifications_brief': '🔕 Moins de popups, plus de notifications discrètes',
                        'drag_drop_info': '📁 Glissez-déposez des fichiers .rpy',
                        'ctrl_v_info': '�� Ctrl+V pour coller du contenu Ren\'Py',
                        'buttons_info': '�� Boutons avec états dynamiques',
                        'i18n_dynamic': 'Changement de langue en temps réel',
                        'i18n_support': 'Support complet français, anglais, allemand',
                        'i18n_realtime': 'Mise à jour instantanée de l\'interface',
                        'popup_reduction': 'Réduction drastique des popups intrusifs',
                        'toast_system': 'Notifications toast discrètes',
                        'status_bar': 'Barre de statut informative',
                        'critical_only': 'Popups uniquement pour les erreurs critiques',
                        'theme_integration': 'Thèmes sombre/clair harmonisés',
                        'dynamic_buttons': 'Boutons avec états dynamiques',
                        'language_menu': 'Menu de langue intégré'
                    }
                },
                'help_specialized': {
                    'extraction': {
                        'title': '⚡ Extraction améliorée',
                        'subtitle': 'Analyse et séparation intelligente des textes',
                        'understood_button': '✅ Compris !',
                        'sections': {
                            'text_separation': {
                                'title': '📝 Séparation des textes',
                                'content': {
                                    '0': '[nom].txt : Textes principaux à traduire',
                                    '1': '[nom]_asterix.txt : Expressions *entre astérisques*',
                                    '2': '[nom]_empty.txt : Textes vides et espaces',
                                    '3': '[nom]_glossary.txt : Termes du glossaire (lecture seule)'
                                }
                            },
                            'automatic_protection': {
                                'title': '�� Protection automatique',
                                'content': {
                                    '0': 'Codes Ren\'Py : {b}, [player_name], \\n, etc.',
                                    '1': 'Termes du glossaire avec placeholders (GLO001)…',
                                    '2': 'Guillemets échappés et textes vides'
                                }
                            },
                            'organized_structure': {
                                'title': '📁 Structure organisée',
                                'content': {
                                    '0': 'temporaires/[NomDuJeu]/',
                                    '1': 'Auto-Open configurable pour ouvrir les fichiers créés'
                                }
                            }
                        }
                    },
                    'reconstruction': {
                        'title': '🔗 Aide Reconstruction',
                        'subtitle': 'Reconstruction avec glossaire et validation',
                        'understood_button': '✅ Compris !',
                        'sections': {
                            'process': {
                                'title': '⚙️ Processus',
                                'content': {
                                    '0': 'Chargement des mappings et fichiers de positions',
                                    '1': 'Injection des traductions principales, astérisques et vides',
                                    '2': 'Restauration des codes spéciaux et termes de glossaire'
                                }
                            },
                            'saving': {
                                'title': '💾 Enregistrement',
                                'content': {
                                    '0': 'Mode \'new_file\' ou \'overwrite\'',
                                    '1': 'Nettoyage des fichiers temporaires',
                                    '2': 'Organisation dans temporaires/[NomDuJeu]/'
                                }
                            }
                        }
                    },
                    'validation': {
                        'title': '☑️ Aide Validation',
                        'subtitle': 'Validation avancée et rapports d\'erreurs',
                        'understood_button': '✅ Compris !',
                        'sections': {
                            'controls': {
                                'title': '🔍 Contrôles',
                                'content': {
                                    '0': 'Détection des patterns Ren\'Py (labels, dialogues, menus…)',
                                    '1': 'Validation de la correspondance nombre de lignes',
                                    '2': 'Vérification des placeholders non traduits'
                                }
                            },
                            'reports': {
                                'title': '📝 Rapports',
                                'content': {
                                    '0': 'Détails des erreurs et warnings',
                                    '1': 'Statistiques de confiance et de couverture',
                                    '2': 'Sauvegarde automatique avant modifications'
                                }
                            }
                        }
                    },
                    'files': {
                        'title': '📁 Organisation fichiers',
                        'subtitle': 'Structure organisée par jeu v{version}',
                        'understood_button': '✅ Compris !',
                        'sections': {
                            'file_tree': {
                                'title': '📂 Arborescence',
                                'content': {
                                    '0': 'dossier_configs : Fichiers principaux de l\'outil',
                                    '1': 'sauvegardes : Archives des backups',
                                    '2': 'avertissements : Rapports d\'erreurs de reconstruction',
                                    '3': 'temporaires/[NomDuJeu]/fichiers_a_traduire : Textes à traduire',
                                    '4': 'temporaires/[NomDuJeu]/fichiers_a_ne_pas_traduire : Fichiers de configuration'
                                }
                            }
                        }
                    },
                    'glossary': {
                        'title': '�� Gestionnaire de Glossaire',
                        'subtitle': 'Gérez votre glossaire de traduction permanent',
                        'understood_button': '✅ Compris !',
                        'sections': {
                            'objective': {
                                'title': '🎯 Objectif',
                                'content': {
                                    '0': 'Le glossaire permet de traduire automatiquement des termes récurrents',
                                    '1': 'comme "Sigh" → "Soupir" dans tous vos projets.'
                                }
                            },
                            'usage': {
                                'title': '📝 Utilisation',
                                'content': {
                                    '0': 'Ajoutez des entrées: Original → Traduction',
                                    '1': 'Protection automatique lors de l\'extraction',
                                    '2': 'Traduction automatique lors de la reconstruction'
                                }
                            },
                            'features': {
                                'title': '�� Fonctionnalités',
                                'content': {
                                    '0': 'Recherche en temps réel',
                                    '1': 'Import/Export de glossaires',
                                    '2': 'Validation des entrées',
                                    '3': 'Protection automatique des termes complets'
                                }
                            },
                            'examples': {
                                'title': '💡 Exemples d\'utilisation',
                                'content': {
                                    '0': '\'Sigh\' → \'Soupir\'',
                                    '1': '\'Hmm\' → \'Hmm\' (conservation)',
                                    '2': '\'Yeah\' → \'Ouais\'',
                                    '3': 'Noms de personnages courants'
                                }
                            },
                            'best_practices': {
                                'title': '⚠️ Bonnes pratiques',
                                'content': {
                                    '0': 'Le glossaire est permanent (non réinitialisable)',
                                    '1': 'Seuls les mots complets sont remplacés',
                                    '2': 'Utilisez des mots complets',
                                    '3': 'Évitez les termes trop génériques',
                                    '4': 'Les termes plus longs sont traités en premier',
                                    '5': 'Validez régulièrement votre glossaire'
                                }
                            }
                        }
                    }
                },
                'reconstruction': {
                    'no_extraction': 'Effectuez d\'abord l\'extraction du fichier',
                    'clipboard_success_opened': 'Fichier {filename} créé et ouvert ! ⏱️ {time:.2f}s',
                    'clipboard_success_created': 'Fichier {filename} créé avec succès ! ⏱️ {time:.2f}s',
                    'file_success_opened': 'Fichier {filename} créé et ouvert ! ⏱️ {time:.2f}s',
                    'file_success_created': 'Fichier {filename} créé avec succès ! ⏱️ {time:.2f}s',
                    'ellipsis_fixed': '{count} [...] → ... corrigés',
                    'error_general': 'Erreur lors de la reconstruction',
                    'error_title': 'Erreur de reconstruction',
                    'error_occurred': 'Erreur lors de la reconstruction:\n{error}',
                    'error_status': 'Erreur lors de la reconstruction'
                },
                'validation': {
                    'failed_title': 'Validation échouée',
                    'failed_message': 'Validation échouée:\n\n{errors}\n\nContinuer quand même ?',
                    'more_errors': 'et {count} autres erreurs'
                },
                'coherence': {
                    'title': 'Problèmes de cohérence',
                    'issues_detected': '{count} problème(s) de cohérence détecté(s)',
                    'detailed_message': '{count} problème(s) détecté(s) dans la traduction.\n\nFichier d\'avertissement créé: {warning_file}\n\nOuvrir le rapport ?'
                },
                'reset': {
                    'confirm_title': 'Confirmer la réinitialisation',
                    'confirm_with_data': 'Voulez-vous vraiment réinitialiser ?\n\n⏱️ Temps session:\n• Extraction: {extraction_time:.2f}s\n• Reconstruction: {reconstruction_time:.2f}s\n• Total: {total_time:.2f}s\n\n🔄 Action: Nettoie base de données et dossier temporaire',
                    'confirm_simple': 'Voulez-vous vraiment réinitialiser la base de données ?',
                    'success_message': 'Base de données nettoyée avec succès',
                    'error_title': 'Erreur de réinitialisation',
                    'error_occurred': 'Erreur lors de la réinitialisation:\n{error}'
                },
                'clean': {
                    'confirm_title': 'Confirmer le nettoyage',
                    'confirm_with_data': 'Voulez-vous vraiment nettoyer ?\n\n⏱️ Temps session:\n• Extraction: {extraction_time:.2f}s\n• Reconstruction: {reconstruction_time:.2f}s\n• Total: {total_time:.2f}s\n\n🧹 Action: Vide la page actuelle',
                    'confirm_simple': 'Voulez-vous vraiment nettoyer la page ?',
                    'success_message': 'Page nettoyée avec succès',
                    'error_title': 'Erreur de nettoyage',
                    'error_occurred': 'Erreur lors du nettoyage:\n{error}'
                },
                'theme': {
                    'dark_mode': 'Mode Sombre',
                    'light_mode': 'Mode Clair',
                    'changed_to': 'Thème changé vers {theme}',
                    'error_title': 'Erreur de thème',
                    'error_occurred': 'Erreur lors du changement de thème:\n{error}'
                },
                'status': {
                    'no_file': 'Aucun fichier sélectionné',
                    'ready': 'Prêt',
                    'extracting': '⚙️ Extraction en cours...',
                    'texts_extracted': '✅ {count} textes extraits en {time:.2f}s',
                    'reconstruction_completed': 'Reconstruction terminée | ⏱️ {time:.2f}s',
                    'lines_loaded': '{count} lignes chargées'
                },
                'messages': {
                    'success': {
                        'extraction': '✅ Extraction terminée en {time:.2f}s !'
                    },
                    'info': {
                        'title': 'Information',
                        'language_changed': 'Langue changée vers {language}'
                    },
                    'confirm': {
                        'title': 'Confirmation'
                    }
                },
                'drag_drop': {
                    'available': 'Glissez un fichier .rpy ici pour le charger',
                    'unavailable': 'Votre système ne supporte pas le Drag & Drop',
                    'ctrl_v': 'Utilisez Ctrl+V pour coller du contenu Ren\'Py'
                }
            },
            'en': {
                'window': {
                    'title': '🎮 RenExtract v{version}',
                    'subtitle': 'Intelligent Ren-Py Script Extraction'
                },
                'buttons': {
                    'extract': '⚡ Extract',
                    'reconstruct': '🔗 Reconstruct',
                    'drag_drop': '© D&D',
                    'glossary': '�� Glossary',
                    'clean': '🧹 Clean',
                    'temporary': '📁 Temporary',
                    'warnings': '⚠ Warnings',
                    'auto_open': '🗃️ Auto : {status}',
                    'validation': '✅ Valid : {status}',
                    'help': '💡 Help',
                    'theme': 'Light Mode',
                    'theme_dark': 'Dark Mode',
                    'language': 'English',
                    'quit': 'Quit',
                    'close': '❌ Close',
                    'open_file': '📂 Open .rpy File',
                    'open_folder': '📁 Open Folder',
                    'backups': '💾 Backups',
                    'reset': '🔄 Reset',
                    'input_mode': '�� {mode}'
                },
                'help': {
                    'title': '🎓 Help Center v{version}',
                    'subtitle': '🎓 Help Center - Choose your help type',
                    'buttons': {
                        'complete_guide': '📖 Complete Guide v{version}',
                        'express_guide': '⚡ Express Guide',
                        'whats_new': '🆕 What\'s New v{version}',
                        'glossary_help': '📚 Glossary Help',
                        'extraction_help': '⚡ Extraction Help',
                        'reconstruction_help': '🔧 Reconstruction Help',
                        'validation_help': '✅ Validation Help',
                        'file_organization': '📁 File Organization'
                    },
                    'descriptions': {
                        'complete_guide': 'Detailed guide with all current features',
                        'express_guide': 'Quick version for experienced users',
                        'whats_new': 'Discover improvements and new functions',
                        'glossary_help': 'Permanent glossary system and automatic protection',
                        'extraction_help': 'Enhanced extraction with organized structure',
                        'reconstruction_help': 'Reconstruction with glossary and validation',
                        'validation_help': 'Advanced validation and error reports',
                        'file_organization': 'Structure organized by game v{version}'
                    }
                },
                'glossary': {
                    'title': '📚 Glossary Manager',
                    'subtitle': 'Manage your permanent translation glossary',
                    'search': '🔍 Search:',
                    'entries_title': '📝 Glossary entries',
                    'edit_title': '✏️ Edit',
                    'original_label': 'Original:',
                    'translation_label': 'Translation:',
                    'buttons': {
                        'add': '➕ Add',
                        'modify': '✏️ Modify',
                        'delete': '🗑️ Delete',
                        'new': '🆕 New',
                        'export': '📤 Export',
                        'import': '📥 Import',
                        'validate': '✅ Validate',
                        'close': '✅ Close'
                    },
                    'messages': {
                        'empty_fields': 'Please fill in both fields.',
                        'no_selection': 'Please select an entry to modify.',
                        'no_selection_delete': 'Please select an entry to delete.',
                        'confirm_delete': 'Do you really want to delete this entry?\n\n\'{original}\' → \'{translation}\'',
                        'add_error': 'Unable to add entry.',
                        'modify_error': 'Unable to modify entry.',
                        'export_error': 'Unable to export glossary.',
                        'import_error': 'Unable to import glossary.',
                        'import_mode': 'Do you want to merge with the existing glossary?\n\n• Yes = Add to existing entries\n• No = Completely replace the glossary',
                        'validation_issues': '⚠️ {count} issue(s) detected',
                        'validation_issues_text': 'Issues found:\n\n{issues}',
                        'validation_success': '✅ Glossary validated without issues'
                    }
                },
                'tutorial': {
                    'title': 'Complete Guide - RenExtract v{version}',
                    'subtitle': 'Welcome to RenExtract !',
                    'express_title': 'Express Guide - RenExtract v{version}',
                    'whats_new_title': 'What\'s New - RenExtract v{version}',
                    'non_blocking_notice': '�� This window is non-blocking: you can use the application simultaneously!',
                    'dont_show_again': 'Do not show this guide on startup',
                    'understood_button': '✅ I understood!',
                    'review_later_button': '🔄 Review later',
                    'sections': {
                        'overview': '📋 Overview',
                        'workflow': '🔄 Translation Workflow',
                        'features': '✨ New Features',
                        'quick_workflow': '⚡ Quick Workflow',
                        'new_features': '🆕 New Features',
                        'shortcuts': '⌨️ Shortcuts',
                        'i18n_system': '🌍 Internationalization System',
                        'smart_notifications': '🔕 Smart Notifications',
                        'improved_ux': '�� Improved Interface'
                    },
                    'content': {
                        'quick_steps': '1️⃣ Load a .rpy file\n2️⃣ Click "⚡ Extract"\n3️⃣ Translate the .txt files\n4️⃣ Click "🔗 Reconstruct"\n💡 Automatic validation included',
                        'glossary_brief': '�� Permanent glossary with automatic translation',
                        'architecture_brief': '🏗️ Organized structure by game',
                        'notifications_brief': '�� Fewer popups, more discrete notifications',
                        'drag_drop_info': '📁 Drag & drop .rpy files',
                        'ctrl_v_info': '📋 Ctrl+V to paste Ren\'Py content',
                        'buttons_info': '🎯 Buttons with dynamic states',
                        'i18n_dynamic': 'Real-time language switching',
                        'i18n_support': 'Complete French, English, German support',
                        'i18n_realtime': 'Instant interface updates',
                        'popup_reduction': 'Drastic reduction of intrusive popups',
                        'toast_system': 'Discrete toast notifications',
                        'status_bar': 'Informative status bar',
                        'critical_only': 'Popups only for critical errors',
                        'theme_integration': 'Harmonized dark/light themes',
                        'dynamic_buttons': 'Buttons with dynamic states',
                        'language_menu': 'Integrated language menu'
                    }
                },
                'help_specialized': {
                    'extraction': {
                        'title': '⚡ Enhanced Extraction',
                        'subtitle': 'Intelligent text analysis and separation',
                        'understood_button': '✅ Understood!',
                        'sections': {
                            'text_separation': {
                                'title': '📝 Text Separation',
                                'content': {
                                    '0': '[name].txt: Main texts to translate',
                                    '1': '[name]_asterix.txt: Expressions *between asterisks*',
                                    '2': '[name]_empty.txt: Empty texts and spaces',
                                    '3': '[name]_glossary.txt: Glossary terms (read-only)'
                                }
                            },
                            'automatic_protection': {
                                'title': '🔒 Automatic Protection',
                                'content': {
                                    '0': 'Ren\'Py codes: {b}, [player_name], \\n, etc.',
                                    '1': 'Glossary terms with placeholders (GLO001)…',
                                    '2': 'Escaped quotes and empty texts'
                                }
                            },
                            'organized_structure': {
                                'title': '📁 Organized Structure',
                                'content': {
                                    '0': 'temporaries/[GameName]/',
                                    '1': 'Auto-Open configurable to open created files'
                                }
                            }
                        }
                    },
                    'reconstruction': {
                        'title': '🔗 Reconstruction Help',
                        'subtitle': 'Reconstruction with glossary and validation',
                        'understood_button': '✅ Understood!',
                        'sections': {
                            'process': {
                                'title': '⚙️ Process',
                                'content': {
                                    '0': 'Loading mappings and position files',
                                    '1': 'Injecting main translations, asterisks, and empty spaces',
                                    '2': 'Restoring special codes and glossary terms'
                                }
                            },
                            'saving': {
                                'title': '💾 Saving',
                                'content': {
                                    '0': '\'new_file\' or \'overwrite\' mode',
                                    '1': 'Cleaning up temporary files',
                                    '2': 'Organizing in temporaries/[GameName]/'
                                }
                            }
                        }
                    },
                    'validation': {
                        'title': '☑️ Validation Help',
                        'subtitle': 'Advanced validation and error reports',
                        'understood_button': '✅ Understood!',
                        'sections': {
                            'controls': {
                                'title': '🔍 Controls',
                                'content': {
                                    '0': 'Detection of Ren\'Py patterns (labels, dialogues, menus…)',
                                    '1': 'Validation of line number correspondence',
                                    '2': 'Checking for untranslated placeholders'
                                }
                            },
                            'reports': {
                                'title': '📝 Reports',
                                'content': {
                                    '0': 'Error and warning details',
                                    '1': 'Confidence and coverage statistics',
                                    '2': 'Automatic saving before modifications'
                                }
                            }
                        }
                    },
                    'files': {
                        'title': '📁 File Organization',
                        'subtitle': 'Structure organized by game v{version}',
                        'understood_button': '✅ Understood!',
                        'sections': {
                            'file_tree': {
                                'title': '📂 File Tree',
                                'content': {
                                    '0': 'dossier_configs: Main tool files',
                                    '1': 'sauvegardes: Backup archives',
                                    '2': 'avertissements: Reconstruction error reports',
                                    '3': 'temporaires/[GameName]/fichiers_a_traduire: Texts to translate',
                                    '4': 'temporaires/[GameName]/fichiers_a_ne_pas_traduire: Configuration files'
                                }
                            }
                        }
                    },
                    'glossary': {
                        'title': '📚 Glossary Manager',
                        'subtitle': 'Manage your permanent translation glossary',
                        'understood_button': '✅ Understood!',
                        'sections': {
                            'objective': {
                                'title': '🎯 Objective',
                                'content': {
                                    '0': 'The glossary allows you to automatically translate common terms',
                                    '1': 'like "Sigh" → "Sigh" in all your projects.'
                                }
                            },
                            'usage': {
                                'title': '📝 Usage',
                                'content': {
                                    '0': 'Add Original → Translation pairs',
                                    '1': 'Automatic protection during extraction',
                                    '2': 'Automatic translation during reconstruction'
                                }
                            },
                            'features': {
                                'title': '🔍 Features',
                                'content': {
                                    '0': 'Real-time search',
                                    '1': 'Import/Export glossaries',
                                    '2': 'Input validation',
                                    '3': 'Automatic protection of full terms'
                                }
                            },
                            'examples': {
                                'title': '💡 Example Usage',
                                'content': {
                                    '0': '\'Sigh\' → \'Sigh\'',
                                    '1': '\'Hmm\' → \'Hmm\' (conservation)',
                                    '2': '\'Yeah\' → \'Yeah\'',
                                    '3': 'Common character names'
                                }
                            },
                            'best_practices': {
                                'title': '⚠️ Best Practices',
                                'content': {
                                    '0': 'The glossary is permanent (non-resettable)',
                                    '1': 'Only full words are replaced',
                                    '2': 'Use full words',
                                    '3': 'Avoid overly generic terms',
                                    '4': 'Longer terms are processed first',
                                    '5': 'Regularly validate your glossary'
                                }
                            }
                        }
                    }
                },
                'reconstruction': {
                    'no_extraction': 'Please extract the file first',
                    'clipboard_success_opened': 'File {filename} created and opened! ⏱️ {time:.2f}s',
                    'clipboard_success_created': 'File {filename} created successfully! ⏱️ {time:.2f}s',
                    'file_success_opened': 'File {filename} created and opened! ⏱️ {time:.2f}s',
                    'file_success_created': 'File {filename} created successfully! ⏱️ {time:.2f}s',
                    'ellipsis_fixed': '{count} [...] → ... fixed',
                    'error_general': 'Error during reconstruction',
                    'error_title': 'Reconstruction Error',
                    'error_occurred': 'Error during reconstruction:\n{error}',
                    'error_status': 'Error during reconstruction'
                },
                'validation': {
                    'failed_title': 'Validation Failed',
                    'failed_message': 'Validation failed:\n\n{errors}\n\nContinue anyway?',
                    'more_errors': 'and {count} other errors'
                },
                'coherence': {
                    'title': 'Coherence Issues',
                    'issues_detected': '{count} coherence issue(s) detected',
                    'detailed_message': '{count} issue(s) detected in translation.\n\nWarning file created: {warning_file}\n\nOpen report?'
                },
                'reset': {
                    'confirm_title': 'Confirm Reset',
                    'confirm_with_data': 'Do you really want to reset?\n\n⏱️ Session time:\n• Extraction: {extraction_time:.2f}s\n• Reconstruction: {reconstruction_time:.2f}s\n• Total: {total_time:.2f}s\n\n🔄 Action: Cleans database and temporary folder',
                    'confirm_simple': 'Do you really want to reset the database?',
                    'success_message': 'Database cleaned successfully',
                    'error_title': 'Reset Error',
                    'error_occurred': 'Error during reset:\n{error}'
                },
                'clean': {
                    'confirm_title': 'Confirm Clean',
                    'confirm_with_data': 'Do you really want to clean?\n\n⏱️ Session time:\n• Extraction: {extraction_time:.2f}s\n• Reconstruction: {reconstruction_time:.2f}s\n• Total: {total_time:.2f}s\n\n🧹 Action: Clears current page',
                    'confirm_simple': 'Do you really want to clean the page?',
                    'success_message': 'Page cleaned successfully',
                    'error_title': 'Clean Error',
                    'error_occurred': 'Error during clean:\n{error}'
                },
                'theme': {
                    'dark_mode': 'Dark Mode',
                    'light_mode': 'Light Mode',
                    'changed_to': 'Theme changed to {theme}',
                    'error_title': 'Theme Error',
                    'error_occurred': 'Error during theme change:\n{error}'
                },
                'status': {
                    'no_file': 'No file selected',
                    'ready': 'Ready',
                    'extracting': '⚙️ Extracting...',
                    'texts_extracted': '✅ {count} texts extracted in {time:.2f}s',
                    'reconstruction_completed': 'Reconstruction completed | ⏱️ {time:.2f}s',
                    'lines_loaded': '{count} lines loaded'
                },
                'messages': {
                    'success': {
                        'extraction': '✅ Extraction completed in {time:.2f}s !'
                    },
                    'info': {
                        'title': 'Information',
                        'language_changed': 'Language changed to {language}'
                    },
                    'confirm': {
                        'title': 'Confirmation'
                    }
                },
                'drag_drop': {
                    'available': 'Drag an .rpy file here to load it',
                    'unavailable': 'Your system doesn\'t support Drag & Drop',
                    'ctrl_v': 'Use Ctrl+V to paste Ren\'Py content'
                }
            },
            'de': {
                'window': {
                    'title': '🎮 RenExtract v{version}',
                    'subtitle': 'Intelligente Skript-Extraktion und Übersetzung'
                },
                'buttons': {
                    'extract': '⚡ Extrahieren',
                    'reconstruct': '🔗 Rekonstruieren',
                    'drag_drop': '© D&D',
                    'glossary': '📖 Glossar',
                    'clean': '🧹 Bereinigen',
                    'temporary': '📁 Temporär',
                    'warnings': '⚠ Warnungen',
                    'auto_open': '🗃️ Auto : {status}',
                    'validation': '✅ Valid : {status}',
                    'help': '💡 Hilfe',
                    'theme': 'Heller Modus',
                    'theme_dark': 'Dunkler Modus',
                    'language': 'Deutsch',
                    'quit': 'Beenden',
                    'close': '❌ Schließen',
                    'open_file': '📂 .rpy Datei öffnen',
                    'open_folder': '📁 Ordner öffnen',
                    'backups': '💾 Backups',
                    'reset': '🔄 Zurücksetzen',
                    'input_mode': '⌨️ {mode}'
                },
                'help': {
                    'title': '🎓 Hilfecenter v{version}',
                    'subtitle': '🎓 Hilfecenter - Wählen Sie Ihren Hilfetyp',
                    'buttons': {
                        'complete_guide': '📖 Vollständige Anleitung v{version}',
                        'express_guide': '⚡ Express-Anleitung',
                        'whats_new': '🆕 Neuigkeiten v{version}',
                        'glossary_help': '📚 Glossar-Hilfe',
                        'extraction_help': '⚡ Extraktions-Hilfe',
                        'reconstruction_help': '🔧 Rekonstruktions-Hilfe',
                        'validation_help': '✅ Validierungs-Hilfe',
                        'file_organization': '📁 Dateiorganisation'
                    },
                    'descriptions': {
                        'complete_guide': 'Detaillierte Anleitung mit allen aktuellen Funktionen',
                        'express_guide': 'Schnelle Version für erfahrene Benutzer',
                        'whats_new': 'Entdecken Sie Verbesserungen und neue Funktionen',
                        'glossary_help': 'Permanentes Glossar-System und automatischer Schutz',
                        'extraction_help': 'Erweiterte Extraktion mit organisierter Struktur',
                        'reconstruction_help': 'Rekonstruktion mit Glossar und Validierung',
                        'validation_help': 'Erweiterte Validierung und Fehlerberichte',
                        'file_organization': 'Nach Spiel organisierte Struktur v{version}'
                    }
                },
                'glossary': {
                    'title': '📚 Glossar-Manager',
                    'subtitle': 'Verwalten Sie Ihr permanentes Übersetzungsglossar',
                    'search': '🔍 Suchen:',
                    'entries_title': '📝 Glossareinträge',
                    'edit_title': '✏️ Bearbeitung',
                    'original_label': 'Original:',
                    'translation_label': 'Übersetzung:',
                    'buttons': {
                        'add': '➕ Hinzufügen',
                        'modify': '✏️ Ändern',
                        'delete': '🗑️ Löschen',
                        'new': '🆕 Neu',
                        'export': '📤 Exportieren',
                        'import': '📥 Importieren',
                        'validate': '✅ Validieren',
                        'close': '✅ Schließen'
                    },
                    'messages': {
                        'empty_fields': 'Bitte füllen Sie beide Felder aus.',
                        'no_selection': 'Bitte wählen Sie einen Eintrag zum Ändern aus.',
                        'no_selection_delete': 'Bitte wählen Sie einen Eintrag zum Löschen aus.',
                        'confirm_delete': 'Möchten Sie diesen Eintrag wirklich löschen?\n\n\'{original}\' → \'{translation}\'',
                        'add_error': 'Eintrag konnte nicht hinzugefügt werden.',
                        'modify_error': 'Eintrag konnte nicht geändert werden.',
                        'export_error': 'Glossar konnte nicht exportiert werden.',
                        'import_error': 'Glossar konnte nicht importiert werden.',
                        'import_mode': 'Möchten Sie mit dem bestehenden Glossar zusammenführen?\n\n• Ja = Zu bestehenden Einträgen hinzufügen\n• Nein = Glossar vollständig ersetzen',
                        'validation_issues': '⚠️ {count} Problem(e) erkannt',
                        'validation_issues_text': 'Gefundene Probleme:\n\n{issues}',
                        'validation_success': '✅ Glossar ohne Probleme validiert'
                    }
                },
                'tutorial': {
                    'title': 'Vollständige Anleitung - RenExtract v{version}',
                    'subtitle': 'Willkommen bei RenExtract !',
                    'express_title': 'Express-Anleitung - RenExtract v{version}',
                    'whats_new_title': 'Neuigkeiten - RenExtract v{version}',
                    'non_blocking_notice': '💡 Dieses Fenster ist nicht blockierend: Sie können die Anwendung gleichzeitig verwenden!',
                    'dont_show_again': 'Diesen Leitfaden beim Start nicht mehr anzeigen',
                    'understood_button': '✅ Verstanden!',
                    'review_later_button': '🔄 Später überprüfen',
                    'sections': {
                        'overview': '📋 Übersicht',
                        'workflow': '🔄 Übersetzungsworkflow',
                        'features': '✨ Neue Funktionen',
                        'quick_workflow': '⚡ Schneller Workflow',
                        'new_features': '✨ Neue Funktionen',
                        'shortcuts': '⌨️ Tastenkombinationen',
                        'i18n_system': '🌍 Internationalisierungssystem',
                        'smart_notifications': '🔕 Intelligente Benachrichtigungen',
                        'improved_ux': '🎨 Verbesserte Benutzeroberfläche'
                    },
                    'content': {
                        'quick_steps': '1️⃣ Laden Sie eine .rpy-Datei\n2️⃣ Klicken Sie "⚡ Extrahieren"\n3️⃣ Übersetzen Sie die .txt-Dateien\n4️⃣ Klicken Sie "🔗 Rekonstruieren"\n�� Automatische Validierung inbegriffen',
                        'glossary_brief': '📚 Permanentes Glossar mit automatischer Übersetzung',
                        'architecture_brief': '��️ Organisierte Struktur nach Spiel',
                        'notifications_brief': '🔕 Weniger Popups, mehr diskrete Benachrichtigungen',
                        'drag_drop_info': '📁 Drag & Drop von .rpy-Dateien',
                        'ctrl_v_info': '📋 Strg+V zum Einfügen von Ren\'Py-Inhalt',
                        'buttons_info': '🎯 Schaltflächen mit dynamischen Zuständen',
                        'i18n_dynamic': 'Echtzeit-Sprachwechsel',
                        'i18n_support': 'Vollständige Unterstützung für Französisch, Englisch, Deutsch',
                        'i18n_realtime': 'Sofortige Interface-Updates',
                        'popup_reduction': 'Drastische Reduzierung aufdringlicher Popups',
                        'toast_system': 'Diskrete Toast-Benachrichtigungen',
                        'status_bar': 'Informative Statusleiste',
                        'critical_only': 'Popups nur für kritische Fehler',
                        'theme_integration': 'Harmonisierte dunkle/helle Themes',
                        'dynamic_buttons': 'Schaltflächen mit dynamischen Zuständen',
                        'language_menu': 'Integriertes Sprachmenü'
                    }
                },
                'help_specialized': {
                    'extraction': {
                        'title': '⚡ Erweiterte Extraktion',
                        'subtitle': 'Intelligentanalyse und -trennung von Texten',
                        'understood_button': '✅ Verstanden!',
                        'sections': {
                            'text_separation': {
                                'title': '📝 Texttrennung',
                                'content': {
                                    '0': '[name].txt: Haupttexte zum Übersetzen',
                                    '1': '[name]_asterix.txt: Ausdrücke *zwischen Sternchen*',
                                    '2': '[name]_empty.txt: Leere Texte und Leerzeichen',
                                    '3': '[name]_glossary.txt: Glossarbegriffe (nur Lesezeichen)'
                                }
                            },
                            'automatic_protection': {
                                'title': '🔒 Automatischer Schutz',
                                'content': {
                                    '0': 'Ren\'Py-Codes: {b}, [player_name], \\n, etc.',
                                    '1': 'Glossarbegriffe mit Platzhaltern (GLO001)…',
                                    '2': 'Entkommene Anführungszeichen und leere Texte'
                                }
                            },
                            'organized_structure': {
                                'title': '📁 Organisierte Struktur',
                                'content': {
                                    '0': 'temporaries/[GameName]/',
                                    '1': 'Automatischer Öffnen konfigurierbar, um erstellte Dateien zu öffnen'
                                }
                            }
                        }
                    },
                    'reconstruction': {
                        'title': '�� Rekonstruktionshilfe',
                        'subtitle': 'Rekonstruktion mit Glossar und Validierung',
                        'understood_button': '✅ Verstanden!',
                        'sections': {
                            'process': {
                                'title': '⚙️ Prozess',
                                'content': {
                                    '0': 'Laden von Zuordnungen und Positionen-Dateien',
                                    '1': 'Einfügen von Hauptübersetzungen, Sternchen und leeren Zeichen',
                                    '2': 'Wiederherstellen spezieller Codes und Glossarbegriffe'
                                }
                            },
                            'saving': {
                                'title': '💾 Speichern',
                                'content': {
                                    '0': '\'new_file\' oder \'overwrite\'-Modus',
                                    '1': 'Aufräumen von temporären Dateien',
                                    '2': 'Organisieren in temporaries/[GameName]/'
                                }
                            }
                        }
                    },
                    'validation': {
                        'title': '☑️ Validierungs-Hilfe',
                        'subtitle': 'Erweiterte Validierung und Fehlerberichte',
                        'understood_button': '✅ Verstanden!',
                        'sections': {
                            'controls': {
                                'title': '🔍 Kontrollen',
                                'content': {
                                    '0': 'Erkennung von Ren\'Py-Mustern (Labels, Dialoge, Menüs…)',
                                    '1': 'Validierung der Zeilenzahl-Korrespondenz',
                                    '2': 'Überprüfung fehlender Übersetzungen'
                                }
                            },
                            'reports': {
                                'title': '📝 Berichte',
                                'content': {
                                    '0': 'Fehler- und Warnungsdetails',
                                    '1': 'Vertrauens- und Abdeckungsstatistiken',
                                    '2': 'Automatische Speicherung vor Änderungen'
                                }
                            }
                        }
                    },
                    'files': {
                        'title': '📁 Dateiorganisation',
                        'subtitle': 'Nach Spiel organisierte Struktur v{version}',
                        'understood_button': '✅ Verstanden!',
                        'sections': {
                            'file_tree': {
                                'title': '📂 Dateibaum',
                                'content': {
                                    '0': 'dossier_configs: Hauptdateien des Tools',
                                    '1': 'sauvegardes: Sicherungsarchive',
                                    '2': 'avertissements: Rekonstruktionsfehlerberichte',
                                    '3': 'temporaires/[GameName]/fichiers_a_traduire: Zu übersetzende Texte',
                                    '4': 'temporaires/[GameName]/fichiers_a_ne_pas_traduire: Konfigurationsdateien'
                                }
                            }
                        }
                    },
                    'glossary': {
                        'title': '📚 Glossar-Manager',
                        'subtitle': 'Verwalten Sie Ihr permanentes Übersetzungsglossar',
                        'understood_button': '✅ Verstanden!',
                        'sections': {
                            'objective': {
                                'title': '🎯 Ziel',
                                'content': {
                                    '0': 'Das Glossar ermöglicht die automatische Übersetzung häufiger Begriffe',
                                    '1': 'wie "Sigh" → "Sigh" in allen Ihren Projekten.'
                                }
                            },
                            'usage': {
                                'title': '📝 Verwendung',
                                'content': {
                                    '0': 'Fügen Sie Original → Übersetzungspaare hinzu',
                                    '1': 'Automatische Schutz während der Extraktion',
                                    '2': 'Automatische Übersetzung während der Rekonstruktion'
                                }
                            },
                            'features': {
                                'title': '🔍 Funktionen',
                                'content': {
                                    '0': 'Echtzeit-Suche',
                                    '1': 'Import/Export von Glossaren',
                                    '2': 'Eingabevalidierung',
                                    '3': 'Automatischer Schutz vollständiger Begriffe'
                                }
                            },
                            'examples': {
                                'title': '�� Beispielverwendung',
                                'content': {
                                    '0': '\'Sigh\' → \'Sigh\'',
                                    '1': '\'Hmm\' → \'Hmm\' (Konservierung)',
                                    '2': '\'Yeah\' → \'Yeah\'',
                                    '3': 'Häufige Charakternamen'
                                }
                            },
                            'best_practices': {
                                'title': '⚠️ Best Practices',
                                'content': {
                                    '0': 'Das Glossar ist dauerhaft (nicht zurücksetzbar)',
                                    '1': 'Nur vollständige Wörter werden ersetzt',
                                    '2': 'Verwenden Sie vollständige Wörter',
                                    '3': 'Vermeiden Sie zu allgemeinen Begriffe',
                                    '4': 'Längere Begriffe werden zuerst verarbeitet',
                                    '5': 'Validieren Sie Ihr Glossar regelmäßig'
                                }
                            }
                        }
                    }
                },
                'reconstruction': {
                    'no_extraction': 'Bitte extrahieren Sie zuerst die Datei',
                    'clipboard_success_opened': 'Datei {filename} erstellt und geöffnet! ⏱️ {time:.2f}s',
                    'clipboard_success_created': 'Datei {filename} erfolgreich erstellt! ⏱️ {time:.2f}s',
                    'file_success_opened': 'Datei {filename} erstellt und geöffnet! ⏱️ {time:.2f}s',
                    'file_success_created': 'Datei {filename} erfolgreich erstellt! ⏱️ {time:.2f}s',
                    'ellipsis_fixed': '{count} [...] → ... korrigiert',
                    'error_general': 'Fehler bei der Rekonstruktion',
                    'error_title': 'Rekonstruktionsfehler',
                    'error_occurred': 'Fehler bei der Rekonstruktion:\n{error}',
                    'error_status': 'Fehler bei der Rekonstruktion'
                },
                'validation': {
                    'failed_title': 'Validierung fehlgeschlagen',
                    'failed_message': 'Validierung fehlgeschlagen:\n\n{errors}\n\nTrotzdem fortfahren?',
                    'more_errors': 'und {count} weitere Fehler'
                },
                'coherence': {
                    'title': 'Kohärenzprobleme',
                    'issues_detected': '{count} Kohärenzproblem(e) erkannt',
                    'detailed_message': '{count} Problem(e) in der Übersetzung erkannt.\n\nWarnungsdatei erstellt: {warning_file}\n\nBericht öffnen?'
                },
                'reset': {
                    'confirm_title': 'Zurücksetzen bestätigen',
                    'confirm_with_data': 'Möchten Sie wirklich zurücksetzen?\n\n⏱️ Sitzungszeit:\n• Extraktion: {extraction_time:.2f}s\n• Rekonstruktion: {reconstruction_time:.2f}s\n• Gesamt: {total_time:.2f}s\n\n🔄 Aktion: Bereinigt Datenbank und temporären Ordner',
                    'confirm_simple': 'Möchten Sie wirklich die Datenbank zurücksetzen?',
                    'success_message': 'Datenbank erfolgreich bereinigt',
                    'error_title': 'Zurücksetzfehler',
                    'error_occurred': 'Fehler beim Zurücksetzen:\n{error}'
                },
                'clean': {
                    'confirm_title': 'Bereinigung bestätigen',
                    'confirm_with_data': 'Möchten Sie wirklich bereinigen?\n\n⏱️ Sitzungszeit:\n• Extraktion: {extraction_time:.2f}s\n• Rekonstruktion: {reconstruction_time:.2f}s\n• Gesamt: {total_time:.2f}s\n\n🧹 Aktion: Leert aktuelle Seite',
                    'confirm_simple': 'Möchten Sie wirklich die Seite bereinigen?',
                    'success_message': 'Seite erfolgreich bereinigt',
                    'error_title': 'Bereinigungsfehler',
                    'error_occurred': 'Fehler bei der Bereinigung:\n{error}'
                },
                'theme': {
                    'dark_mode': 'Dunkler Modus',
                    'light_mode': 'Heller Modus',
                    'changed_to': 'Theme geändert zu {theme}',
                    'error_title': 'Theme-Fehler',
                    'error_occurred': 'Fehler beim Theme-Wechsel:\n{error}'
                },
                'status': {
                    'no_file': 'Keine Datei ausgewählt',
                    'ready': 'Bereit',
                    'extracting': '⚙️ Extrahiere...',
                    'texts_extracted': '✅ {count} Texte in {time:.2f}s extrahiert',
                    'reconstruction_completed': 'Rekonstruktion abgeschlossen | ⏱️ {time:.2f}s',
                    'lines_loaded': '{count} Zeilen geladen'
                },
                'messages': {
                    'success': {
                        'extraction': '✅ Extraktion in {time:.2f}s abgeschlossen !'
                    },
                    'info': {
                        'title': 'Information',
                        'language_changed': 'Sprache geändert zu {language}'
                    },
                    'confirm': {
                        'title': 'Bestätigung'
                    }
                },
                'drag_drop': {
                    'available': 'Ziehen Sie eine .rpy-Datei hierher, um sie zu laden',
                    'unavailable': 'Ihr System unterstützt Drag & Drop nicht',
                    'ctrl_v': 'Verwenden Sie Strg+V, um Ren\'Py-Inhalt einzufügen'
                }
            }
        }

i18n = I18nManager()
def _(key, **kwargs):
    return i18n.get_text(key, **kwargs)

# =============================================================================
# SYSTÈME DE NOTIFICATION INTELLIGENT (RÉDUCTION DES POPUPS)
# =============================================================================

class NotificationManager:
    """Gestionnaire intelligent de notifications pour réduire les popups"""
    
    NOTIFICATION_TYPES = {
        'STATUS': 'status_bar',      # Barre de statut uniquement
        'TOAST': 'toast',            # Notification discrète temporaire
        'MODAL': 'modal',            # Popup modal (à utiliser avec parcimonie)
        'CONFIRM': 'confirm'         # Confirmation nécessaire
    }
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.toast_queue = []
        self.last_notifications = {}
        
    def notify(self, message, notification_type='STATUS', duration=3000, title=None):
        """
        Système de notification intelligent
        
        Args:
            message (str): Message à afficher
            notification_type (str): Type de notification
            duration (int): Durée d'affichage en ms
            title (str): Titre optionnel
        """
        try:
            if notification_type == 'STATUS':
                self._update_status_bar(message)
            
            elif notification_type == 'TOAST':
                self._show_toast(message, duration)
            
            elif notification_type == 'MODAL':
                self._show_modal(message, title)
            
            elif notification_type == 'CONFIRM':
                return self._show_confirmation(message, title)
                
        except Exception as e:
            print(f"Erreur notification: {e}")
    
    def _update_status_bar(self, message):
        """Met à jour la barre de statut"""
        if hasattr(self.app, 'label_stats') and self.app.label_stats:
            self.app.label_stats.config(text=f"📊 {message}")
    
    def _show_toast(self, message, duration):
        """Affiche une notification toast non-intrusive"""
        try:
            # Créer un label temporaire pour toast
            import tkinter as tk
            from ui.themes import theme_manager
            
            theme = theme_manager.get_theme()
            
            toast = tk.Label(
                self.app.root,
                text=f"💡 {message}",
                font=('Segoe UI Emoji', 10),
                bg=theme["accent"],
                fg="#000000",
                padx=15,
                pady=8,
                relief='solid',
                bd=1
            )
            
            # Positionner en bas à droite
            toast.place(relx=0.98, rely=0.95, anchor='se')
            
            # Programmer la destruction
            self.app.root.after(duration, toast.destroy)
            
        except Exception as e:
            print(f"Erreur toast: {e}")
    
    def _show_modal(self, message, title):
        """Affiche une popup modal (usage limité)"""
        from tkinter import messagebox
        messagebox.showinfo(title or _('messages.info.title'), message)
    
    def _show_confirmation(self, message, title):
        """Affiche une confirmation nécessaire"""
        from tkinter import messagebox
        return messagebox.askyesno(title or _('messages.confirm.title'), message)

# =============================================================================
# INTÉGRATION AVEC L'APPLICATION PRINCIPALE
# =============================================================================

def setup_i18n_in_main(main_app):
    """Configure l'i18n dans l'application principale"""
    
    # Ajouter le gestionnaire de notifications
    main_app.notifications = NotificationManager(main_app)
    
    # Ajouter méthode de changement de langue
    def change_language(language_code):
        """Change la langue et met à jour l'interface"""
        if i18n.set_language(language_code):
            # Sauvegarder dans la config
            from utils.config import config_manager
            config_manager.set('language', language_code)
            
            # Mettre à jour l'interface
            update_interface_language(main_app)
            
            # Notification discrète
            lang_name = i18n.get_language_name(language_code)
            main_app.notifications.notify(
                _('messages.info.language_changed', language=lang_name),
                'TOAST'
            )
            
            return True
        return False
    
    main_app.change_language = change_language
    
    # Charger la langue depuis la config
    from utils.config import config_manager
    saved_lang = config_manager.get('language', 'fr')
    if saved_lang in I18nManager.SUPPORTED_LANGUAGES:
        i18n.set_language(saved_lang)

def update_interface_language(app):
    """Met à jour tous les textes de l'interface"""
    try:
        from utils.constants import VERSION
        
        # Titre de la fenêtre
        app.root.title(_('window.title', version=VERSION))
        
        # Labels principaux
        if hasattr(app, 'title_label') and app.title_label:
            app.title_label.config(text=_('window.title', version=VERSION))
        
        if hasattr(app, 'subtitle_label') and app.subtitle_label:
            app.subtitle_label.config(text=_('window.subtitle'))
        
        # Boutons avec logique conditionnelle
        update_button_texts(app)
        
        # Zone de texte selon le mode
        update_text_area_content(app)
        
        # Statut par défaut
        if hasattr(app, 'label_stats') and app.label_stats:
            app.label_stats.config(text=f"📊 {_('status.ready')}")
        
        # Mettre à jour la fenêtre du glossaire si elle est ouverte
        if hasattr(app, 'glossary_dialog') and app.glossary_dialog:
            try:
                app.glossary_dialog.update_language()
            except Exception as e:
                print(f"Erreur mise à jour glossaire: {e}")
        
    except Exception as e:
        print(f"Erreur mise à jour langue: {e}")

def update_button_texts(app):
    """Met à jour les textes des boutons avec état dynamique"""
    try:
        from utils.config import config_manager
        
        # Boutons avec états dynamiques
        if hasattr(app, 'bouton_auto_open') and app.bouton_auto_open:
            status = "ON" if config_manager.is_auto_open_enabled() else "OFF"
            app.bouton_auto_open.config(text=_('buttons.auto_open', status=status))
        
        if hasattr(app, 'bouton_validation') and app.bouton_validation:
            status = "ON" if config_manager.is_validation_enabled() else "OFF"
            app.bouton_validation.config(text=_('buttons.validation', status=status))
        
        if hasattr(app, 'bouton_theme') and app.bouton_theme:
            if config_manager.is_dark_mode_enabled():
                app.bouton_theme.config(text=_('buttons.theme'))
            else:
                app.bouton_theme.config(text=_('buttons.theme_dark'))
        
        if hasattr(app, 'bouton_input_mode') and app.bouton_input_mode:
            mode = "D&D" if app.input_mode == "drag_drop" else "Ctrl+V"
            app.bouton_input_mode.config(text=_('buttons.input_mode', mode=mode))
        
        if hasattr(app, 'bouton_language') and app.bouton_language:
            lang_name = i18n.get_language_name()
            app.bouton_language.config(text=_('buttons.language', lang=lang_name))
        
    except Exception as e:
        print(f"Erreur mise à jour boutons: {e}")

def update_text_area_content(app):
    """Met à jour le contenu de la zone de texte selon le mode"""
    try:
        if not hasattr(app, 'text_area') or not app.text_area:
            return
        
        # Si aucun fichier chargé, mettre à jour le message d'invitation
        if not app.file_content or app.file_content == []:
            app._update_drag_drop_display()
            
    except Exception as e:
        print(f"Erreur mise à jour zone texte: {e}")

# =============================================================================
# FONCTIONS D'INTÉGRATION POUR LES POPUPS EXISTANTS
# =============================================================================

def smart_message(app, message_key, notification_type='TOAST', **kwargs):
    """Affiche un message intelligent selon le contexte"""
    message = _(message_key, **kwargs)
    
    if hasattr(app, 'notifications'):
        app.notifications.notify(message, notification_type)
    else:
        # Fallback
        if notification_type == 'CONFIRM':
            from tkinter import messagebox
            return messagebox.askyesno("Confirmation", message)
        else:
            print(f"Smart message: {message}")

def smart_success(app, operation, time=None):
    """Affiche un message de succès intelligent"""
    if time:
        message = _(f'messages.success.{operation}', time=time)
    else:
        message = _(f'messages.success.{operation}')
    
    smart_message(app, 'messages.success.' + operation, 'TOAST', time=time)