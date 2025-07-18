# main.py
# RenExtract - Interface principale
# v2.5.0 - Internationalisation complète et interface responsive

"""
RenExtract
Outil de traduction avancé pour les scripts Ren'Py
"""
# Imports Python standard
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import os
import sys
import time
import json
import datetime
import re
import subprocess

# Import Drag & Drop avec fallback
try:
    import tkinterdnd2 as dnd2  # type: ignore
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# Modules utilitaires
from utils.config import config_manager
from utils.logging import log_message, anonymize_path
from utils.constants import VERSION, THEMES, WINDOW_CONFIG, MESSAGES, FILE_NAMES
from ui.glossary_ui import show_glossary_manager, GlossaryDialog
from utils.i18n import i18n, _, setup_i18n_in_main, update_interface_language, smart_message, smart_success

# Gestion des fichiers
from core.file_manager import file_manager, FileOpener, TempFileManager

# Extraction & nommage
from core.extraction import (
    TextExtractor,
    get_file_base_name,
)
from utils.logging import extract_game_name

# Reconstruction
from core.reconstruction import FileReconstructor

# Validation & sauvegarde
from core.validation import (
    validate_before_extraction,
    create_safety_backup,
    validate_before_reconstruction,
)
from core.coherence_checker import check_file_coherence

# Interface utilisateur
from ui.backup_manager import show_backup_manager
from ui.interface import SaveModeDialog

# Imports du tutoriel (avec fallback de sécurité)
try:
    from ui.tutorial import show_tutorial, check_first_launch
except ImportError:
    def show_tutorial():
        messagebox.showinfo("Tutoriel", "Module tutoriel non disponible")
    def check_first_launch():
        return False
        return False

# ✅ CORRECTION : Variable globale pour l'instance
app_instance = None

class TraducteurRenPyPro:
    # =============================================================================
    # MÉTHODES D'INITIALISATION ET CONFIGURATION
    # =============================================================================

    def __init__(self):
        print("🚀 Init appelé")

        # 1. Nettoyer toute instance Tkinter existante
        import tkinter as tk
        if tk._default_root:
            try:
                tk._default_root.withdraw()
                tk._default_root.quit()
                tk._default_root.destroy()
            except:
                pass

        # 2. Créer les dossiers et le fichier de log
        from utils.constants import ensure_folders_exist
        ensure_folders_exist()

        from utils.logging import initialize_log
        initialize_log()

        # 3. Créer la fenêtre principale (avec DnD si possible)
        try:
            if DND_AVAILABLE:
                self.root = dnd2.Tk()  # IMPORTANT : Utiliser dnd2.Tk() !
            else:
                self.root = tk.Tk()
        except Exception as e:
            self.root = tk.Tk()  # Fallback
        # 4. NOUVEAU : Initialiser le ThemeManager APRÈS création de la fenêtre
        try:
            from ui.themes import theme_manager
            theme_manager.initialize_now()
        except Exception as e:
            pass

        # ✅ NOUVEAU : Initialiser l'i18n après création de la fenêtre
        setup_i18n_in_main(self)

        # 5. Masquer la fenêtre temporairement pendant l'initialisation
        self.root.withdraw()

        # 6. Configuration de la fenêtre (titre, minsize, icône, protocole fermeture)
        self.setup_window()

        # 7. Initialisation des variables d'état
        self.file_content = []
        self.original_path = None
        self.extraction_results = None
        self.last_extraction_time = 0
        self.last_reconstruction_time = 0
        self._save_mode = None

        # 8. Initialisation des widgets (à None)
        self.label_chemin = None
        self.label_stats = None
        self.text_area = None
        self.bouton_auto_open = None
        self.bouton_validation = None
        self.bouton_theme = None
        self.frame_info = None
        self.title_label = None
        self.subtitle_label = None

        # NOUVEAU : Variables pour le mode texte
        self.text_mode = "empty"  # "file", "clipboard", "manual", "empty"
        self.source_info = None
        self.clipboard_counter = 0
        self.input_mode = "drag_drop"  # "drag_drop" ou "ctrl_v"
        self.bouton_input_mode = None
        # 9. Création de l'interface
        self.create_interface()

        # 10. Application du thème
        from ui.themes import theme_manager
        theme_manager.apply_current_theme()

        # 11. Mise à jour Drag & Drop (si text_area prête)
        if self.text_area:
            try:
                self._update_drag_drop_display()
            except Exception as e:
                pass

        # 12. Réafficher la fenêtre une fois prête
        print("➡️ Avant deiconify")
        self.root.deiconify()

        # 13. Centrage de la fenêtre
        print("➡️ Avant center_window")
        self.center_window()

        # 14. Vérification tutoriel premier lancement
        print("➡️ Avant check_tutorial")
        self.check_tutorial()

        # ✅ CORRECTION : Rendre l'instance accessible globalement
        global app_instance
        app_instance = self

        # 15. Logs finaux

        log_message("INFO", f"=== DÉMARRAGE DU RenExtract v{VERSION} ===")
        log_message("INFO", "Dossiers organisés créés: temporaire, sauvegardes, avertissements, logs")

    def setup_window(self):
        """Configure la fenêtre principale"""
        self.root.title(WINDOW_CONFIG["title"])
        self.root.geometry(WINDOW_CONFIG["geometry"])
        self.root.minsize(*WINDOW_CONFIG["min_size"])
        
        # Icône si disponible
        try:
            self.root.iconbitmap("icone.ico")
        except:
            pass
        
        # Gestion de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.fermer_application)

    def check_imports(self):
        """Vérifie que tous les modules nécessaires sont disponibles"""
        required_modules = [
            'tkinter', 'tkinterdnd2', 'core.extraction', 'core.reconstruction',
            'core.validation', 'core.file_manager', 'core.coherence_checker',
            'ui.backup_manager', 'ui.interface', 'ui.themes', 'ui.tutorial',
            'utils.constants', 'utils.config', 'utils.logging'
        ]
        
        missing = []
        for module in required_modules:
            try:
                if module == 'tkinterdnd2':
                    import tkinterdnd2
                else:
                    __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            print(f"⚠️ Modules manquants: {', '.join(missing)}")
            return False
        return True

    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        try:
            self.root.update_idletasks()

            width = self.root.winfo_width()
            height = self.root.winfo_height()

            # Fallback si width/height trop petits
            if width < 100 or height < 100:
                width, height = 1100, 700  # Valeur par défaut

            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)

            self.root.geometry(f"{width}x{height}+{x}+{y}")
            print(f"✅ Fenêtre centrée à {x},{y} avec taille {width}x{height}")
        except Exception as e:
            print(f"❌ Erreur dans center_window: {e}")
    
    def check_tutorial(self):
        """Vérifie si le tutoriel doit être affiché - VERSION INTELLIGENTE"""
        if check_first_launch():
            log_message("INFO", "Premier lancement détecté - Système intelligent activé")
            # Afficher le tutoriel intelligent après un délai
            self.root.after(500, self._show_first_launch_tutorial_smart)
        else:
            log_message("INFO", "Utilisateur expérimenté détecté - Pas de tutoriel automatique")

    # =============================================================================
    # MÉTHODES DE GESTION DE L'INTERFACE
    # =============================================================================

    def create_interface(self):
        """Crée l'interface utilisateur complète"""
        # Header avec titre
        self.create_header()
        
        # Frame d'information
        self.create_info_frame()
        
        # Frame des boutons d'ouverture
        self.create_open_frame()
        
        # Frame des actions principales
        self.create_actions_frame()
        
        # Zone de contenu principal
        self.create_content_frame()
        
        # Appliquer le thème à tous les widgets créés
        self.apply_theme_to_all_widgets()

    def apply_theme_to_all_widgets(self):
        """Applique le thème manuellement à tous les widgets natifs"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        def apply_to_widget_recursive(widget):
            if not widget:
                return
            
            try:
                # —— Widgets Tkinter natifs ——
                if isinstance(widget, tk.Frame) and not isinstance(widget, ttk.Frame):
                    widget.configure(bg=theme["bg"])
                    
                elif isinstance(widget, tk.Label) and not isinstance(widget, ttk.Label):
                    if hasattr(widget, 'cget') and widget.cget("text") in ["Prêt", "Ready", "Bereit"]:
                        widget.configure(bg=theme["bg"], fg=theme["fg"])
                    else:
                        widget.configure(bg=theme["bg"], fg=theme["fg"])
                        
                elif isinstance(widget, tk.Text):
                    widget.configure(
                        bg=theme["entry_bg"],
                        fg=theme["entry_fg"],
                        selectbackground=theme["select_bg"],
                        selectforeground=theme["select_fg"],
                        insertbackground=theme["entry_fg"],
                        highlightbackground=theme["bg"],
                        highlightcolor=theme["accent"]
                    )
                    
                elif isinstance(widget, tk.Button) and not isinstance(widget, ttk.Button):
                    # Forcer tous les textes des boutons en noir
                    widget.configure(fg="#000000")
                    
                # ✅ NOUVEAU : Appliquer le thème aux fenêtres principales
                elif isinstance(widget, (tk.Tk, tk.Toplevel)):
                    widget.configure(bg=theme["bg"])
                    
                # ✅ NOUVEAU : Appliquer le thème à la scrollbar
                elif isinstance(widget, tk.Scrollbar):
                    widget.configure(
                        bg=theme["bg"],
                        troughcolor=theme["bg"],
                        activebackground=theme["button_bg"],
                        highlightbackground=theme["bg"]
                    )
                    
                # Autres widgets supportant bg
                elif hasattr(widget, 'configure'):
                    try:
                        widget.configure(bg=theme.get("bg"))
                    except:
                        pass
                pass  # Ignorer les erreurs pour éviter les crashs
            except Exception:
                pass
            # Appliquer récursivement aux enfants
            try:
                for child in widget.winfo_children():
                    apply_to_widget_recursive(child)
            except:
                pass
        
        # Appliquer à la fenêtre principale
        apply_to_widget_recursive(self.root)

    # 2. AJOUTER ces nouvelles méthodes dans la classe TraducteurRenPyPro :

    def _show_first_launch_tutorial_smart(self):
        """Version INTELLIGENTE : Maximum 3 tentatives avec messages adaptatifs"""
        try:
            from ui.tutorial import show_tutorial, show_minimal_tutorial, mark_tutorial_shown
            from utils.constants import FILE_NAMES
            
            # Compter les tentatives
            attempts_file = FILE_NAMES["tutorial_flag"].replace(".flag", "_attempts.txt")
            attempts = self._get_tutorial_attempts(attempts_file)
            
            if attempts >= 3:
                # 3 tentatives dépassées → Marquer définitivement comme vu
                mark_tutorial_shown()
                log_message("INFO", "3 tentatives de tutoriel dépassées - Marquage définitif")
                return
            
            # Message adapté selon le nombre de tentatives
            if attempts == 0:
                title = "🎉 Bienvenue dans RenExtract v2.5.0 !"
                message = "C'est votre première utilisation !\n\n🎯 Découvrez toutes les nouveautés et fonctionnalités."
                footer = "💡 Ce guide vous fera gagner du temps"
            elif attempts == 1:
                title = "🎯 Guide RenExtract"
                message = "Nous vous proposons à nouveau le guide.\n\n📚 Architecture refactorisée, glossaire permanent, validation avancée..."
                footer = "💡 Beaucoup de nouveautés utiles à découvrir"
            else:  # attempts == 2
                title = "📚 Dernière proposition de guide"
                message = "Dernière opportunité pour découvrir le guide.\n\n🚀 Après cela, accessible uniquement via le bouton '🎓 Aide'."
                footer = "💡 Tentative 3/3 - Voulez-vous vraiment passer à côté ?"
            
            welcome_result = messagebox.askyesnocancel(
                title,
                f"{message}\n\n"
                "🎓 Que souhaitez-vous faire ?\n\n"
                "• Oui = 📖 Guide complet (toutes les fonctionnalités)\n"
                "• Non = ⚡ Guide express (5 minutes)\n" 
                "• Annuler = 🔄 Reporter au prochain lancement\n\n"
                f"{footer}"
            )
            
            if welcome_result is True:
                # Guide complet consulté → Marquer définitivement
                show_tutorial()
                mark_tutorial_shown()
                log_message("INFO", f"Tentative {attempts + 1}/3 : Guide complet consulté - Marqué définitivement")
                
            elif welcome_result is False:
                # Guide express consulté → Marquer définitivement
                show_minimal_tutorial()
                mark_tutorial_shown()
                log_message("INFO", f"Tentative {attempts + 1}/3 : Guide express consulté - Marqué définitivement")
                
            else:
                # Reporter → Incrémenter compteur
                self._increment_tutorial_attempts(attempts_file)
                self._show_help_reminder_smart(attempts + 1)
                log_message("INFO", f"Tentative {attempts + 1}/3 : Guide reporté")
                
        except Exception as e:
            log_message("WARNING", f"Erreur tutoriel intelligent: {e}")
            # Fallback : Marquer comme vu pour éviter les boucles
            try:
                mark_tutorial_shown()
            except:
                pass

    def _get_tutorial_attempts(self, attempts_file):
        """Récupère le nombre de tentatives de tutoriel"""
        try:
            if os.path.exists(attempts_file):
                with open(attempts_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    return int(content) if content.isdigit() else 0
            return 0
        except Exception as e:
            log_message("WARNING", f"Erreur lecture tentatives: {e}")
            return 0

    def _increment_tutorial_attempts(self, attempts_file):
        """Incrémente le compteur de tentatives"""
        try:
            attempts = self._get_tutorial_attempts(attempts_file) + 1
            
            # S'assurer que le dossier existe
            os.makedirs(os.path.dirname(attempts_file), exist_ok=True)
            
            with open(attempts_file, 'w', encoding='utf-8') as f:
                f.write(str(attempts))
            
            log_message("INFO", f"Compteur tentatives tutoriel: {attempts}/3")
            
        except Exception as e:
            log_message("WARNING", f"Erreur incrément tentatives: {e}")

    def _show_help_reminder_smart(self, attempt_number):
        """Affiche un rappel adaptatif selon le nombre de tentatives"""
        try:
            if attempt_number == 1:
                reminder_text = "💡 Guide disponible via '🎓 Aide' - Vous avez encore 2 chances au prochain lancement"
            elif attempt_number == 2:
                reminder_text = "💡 Guide disponible via '🎓 Aide' - Plus qu'une chance au prochain lancement !"
            else:  # attempt_number == 3
                reminder_text = "💡 Aide toujours disponible via le bouton '🎓 Aide' en haut à droite"
            
            # Afficher dans la barre de statut
            if hasattr(self, 'label_stats') and self.label_stats:
                current_stats = self.label_stats.cget("text")
                self.label_stats.config(text=reminder_text)
                
                # Restaurer après 7 secondes (plus long pour être sûr qu'il soit vu)
                self.root.after(7000, lambda: self.label_stats.config(text=current_stats))
            
        except Exception as e:
            log_message("WARNING", f"Erreur rappel intelligent: {e}")

    def create_header(self):
        """✅ MODIFIÉ : En-tête avec bouton langue"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        frame_header = tk.Frame(self.root, height=80, bg=theme["bg"])
        frame_header.pack(fill='x', padx=20, pady=(20, 10))
        frame_header.pack_propagate(False)
        self.title_label = tk.Label(
            frame_header, 
            text=_('window.title', version=VERSION),
            font=('Segoe UI Emoji', 16, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.title_label.pack(side='left')
        self.subtitle_label = tk.Label(
            frame_header, 
            text=_('window.subtitle'),
            font=('Segoe UI Emoji', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.subtitle_label.pack(side='left', padx=(10, 0))
        
        # Frame pour les boutons (droite)
        frame_buttons = tk.Frame(frame_header, bg=theme["bg"])
        frame_buttons.pack(side='right')
        
        # Bouton quitter
        self.btn_quit = tk.Button(
            frame_buttons,
            text=_('buttons.quit'),
            font=('Segoe UI Emoji', 10, 'bold'),
            bg='#dc3545',
            fg='#000000',
            relief='flat',
            cursor='hand2',
            command=self.fermer_application,
            width=10,  # Largeur fixe augmentée pour accommoder les textes plus longs
            pady=5
        )
        self.btn_quit.pack(side='right', padx=(5, 0))
        
        # Bouton langue
        self.btn_language = tk.Button(
            frame_buttons,
            text=_('buttons.language'),
            font=('Segoe UI Emoji', 10, 'bold'),
            bg='#6f42c1',
            fg='#000000',
            relief='flat',
            cursor='hand2',
            command=self.show_language_menu,
            width=12,  # Largeur fixe augmentée pour accommoder les textes plus longs
            pady=5
        )
        self.btn_language.pack(side='right', padx=(5, 0))
        
        # Bouton thème (Mode Clair/Sombre)
        self.btn_theme = tk.Button(
            frame_buttons,
            text=_('buttons.theme'),
            font=('Segoe UI Emoji', 10, 'bold'),
            bg='#ffc107',
            fg='#000000',
            relief='flat',
            cursor='hand2',
            command=self.toggle_dark_mode,
            width=14,  # Largeur fixe augmentée pour accommoder les textes plus longs
            pady=5
        )
        self.btn_theme.pack(side='right', padx=(5, 0))

    def show_language_menu(self):
        """✅ NOUVEAU : Affiche le menu de sélection de langue"""
        try:
            import tkinter as tk
            from ui.themes import theme_manager
            
            # Créer menu contextuel
            lang_menu = tk.Toplevel(self.root)
            lang_menu.title(_('buttons.language', lang=''))
            lang_menu.geometry("200x250")
            lang_menu.resizable(False, False)
            lang_menu.transient(self.root)
            
            # Centrer le menu
            lang_menu.update_idletasks()
            x = self.root.winfo_x() + self.root.winfo_width() - 220
            y = self.root.winfo_y() + 80
            lang_menu.geometry(f"+{x}+{y}")
            
            # Appliquer le thème
            theme = theme_manager.get_theme()
            lang_menu.configure(bg=theme["bg"])
            
            # Titre
            title_label = tk.Label(
                lang_menu,
                text="🌍 " + _('buttons.language', lang='').replace('🌍 ', ''),
                font=('Segoe UI Emoji', 12, 'bold'),
                bg=theme["bg"],
                fg=theme["fg"]
            )
            title_label.pack(pady=10)
            
            # Boutons de langue
            for code, name in i18n.SUPPORTED_LANGUAGES.items():
                is_current = (code == i18n.get_current_language())
                
                btn_color = theme["accent"] if is_current else theme["button_bg"]
                btn_text = f"{'✓ ' if is_current else ''}{self._get_flag(code)} {name}"
                
                lang_btn = tk.Button(
                    lang_menu,
                    text=btn_text,
                    font=('Segoe UI Emoji', 10, 'bold' if is_current else 'normal'),
                    bg=btn_color,
                    fg='#000000',
                    relief='flat',
                    bd=0,
                    pady=8,
                    command=lambda c=code: self._change_language_and_close(c, lang_menu)
                )
                lang_btn.pack(fill='x', padx=10, pady=2)
            
            # Fermer automatiquement après 5 secondes si pas d'action
            lang_menu.after(5000, lang_menu.destroy)
            
        except Exception as e:
            log_message("ERREUR", "Erreur menu langue", e)

    def _get_flag(self, code):
        """Retourne le drapeau emoji pour un code langue"""
        flags = {
            'fr': '🇫🇷',
            'en': '🇺🇸', 
            'es': '🇪🇸',
            'de': '🇩🇪'
        }
        return flags.get(code, '🌍')

    def _change_language_and_close(self, language_code, menu_window):
        """Change la langue et ferme le menu"""
        try:
            self.change_language(language_code)
            # Détruire tous les widgets enfants de la fenêtre principale
            for widget in self.root.winfo_children():
                widget.destroy()
            self.create_interface()
            from ui.themes import theme_manager
            theme_manager.apply_current_theme()
            self.center_window()
            menu_window.destroy()
        except Exception as e:
            log_message("ERREUR", f"Erreur changement langue: {e}")

    def create_info_frame(self):
        """✅ MODIFIÉ : Frame d'informations avec textes traduits"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        self.frame_info = tk.Frame(
            self.root, 
            bg=theme["frame_bg"], 
            relief='flat', 
            bd=1, 
            padx=8, 
            pady=10
        )
        self.frame_info.pack(fill='x', padx=20, pady=5)
        
        self.label_chemin = tk.Label(
            self.frame_info, 
            text=f"📄 {_('status.no_file')}", 
            font=('Segoe UI Emoji', 9, 'bold'),
            bg=theme["frame_bg"], 
            fg=theme["accent"]
        )
        self.label_chemin.pack(side='left')
        
        self.label_stats = tk.Label(
            self.frame_info, 
            text=f"📊 {_('status.ready')}", 
            font=('Segoe UI Emoji', 10),
            bg=theme["frame_bg"], 
            fg=theme["fg"]
        )
        self.label_stats.pack(side='right')

    def create_open_frame(self):
        """✅ MODIFIÉ : Boutons d'ouverture avec textes traduits"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        frame_open = tk.Frame(self.root, bg=theme["bg"], height=50)
        frame_open.pack(padx=20, pady=5)
        
        for col in range(4):
            frame_open.columnconfigure(col, weight=1, uniform="grp_open")
        
        # Boutons traduits avec largeur fixe augmentée
        btn_fichier = tk.Button(
            frame_open,
            text=_('buttons.open_file'),
            font=('Segoe UI Emoji', 11),
            bg='#007bff',
            fg='#000000',
            activebackground='#0056b3',
            bd=1,
            relief='solid',
            command=self.ouvrir_fichier_unique,
            width=18  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        btn_fichier.grid(row=0, column=0, sticky="nsew", padx=5, pady=8)
        
        btn_dossier = tk.Button(
            frame_open,
            text=_('buttons.open_folder'),
            font=('Segoe UI Emoji', 11),
            bg='#007bff',
            fg='#000000',
            activebackground='#0056b3',
            bd=1,
            relief='solid',
            command=self.ouvrir_dossier,
            width=18  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        btn_dossier.grid(row=0, column=1, sticky="nsew", padx=5, pady=8)
        
        btn_sauvegardes = tk.Button(
            frame_open,
            text=_('buttons.backups'),
            font=('Segoe UI Emoji', 11),
            bg='#dc3545',
            fg='#000000',
            activebackground='#c82333',
            bd=1,
            relief='solid',
            command=self.gerer_sauvegardes,
            width=15  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        btn_sauvegardes.grid(row=0, column=2, sticky="nsew", padx=5, pady=8)
        
        btn_reinit = tk.Button(
            frame_open,
            text=_('buttons.reset'),
            font=('Segoe UI Emoji', 10),
            bg='#dc3545',
            fg='#000000',
            activebackground='#c82333',
            bd=1,
            relief='solid',
            command=self.reinitialiser,
            width=15  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        btn_reinit.grid(row=0, column=3, sticky="nsew", padx=5, pady=8)

    def create_actions_frame(self):
        """✅ MODIFIÉ : Actions avec textes traduits et états dynamiques"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        frame_actions = tk.Frame(self.root, height=80, bg=theme["bg"])
        frame_actions.pack(padx=20, pady=5)
        
        for col in range(10):
            frame_actions.columnconfigure(col, weight=1, uniform="grp_act")
        
        # Boutons principaux avec largeur fixe augmentée
        btn_extraire = tk.Button(
            frame_actions, text=_('buttons.extract'), font=('Segoe UI Emoji', 11),
            bg='#28a745', fg='#000000', activebackground='#1e7e34',
            bd=1, relief='solid', command=self.extraire_textes_enhanced,
            width=14  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        btn_extraire.grid(row=0, column=0, sticky="nsew", padx=5, pady=15)

        btn_reconstruire = tk.Button(
            frame_actions, text=_('buttons.reconstruct'), font=('Segoe UI Emoji', 11),
            bg='#28a745', fg='#000000', activebackground='#1e7e34',
            bd=1, relief='solid', command=self.reconstruire_fichier_enhanced,
            width=14  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        btn_reconstruire.grid(row=0, column=1, sticky="nsew", padx=5, pady=15)

        # Bouton mode d'entrée avec état
        mode_text = "D&D" if getattr(self, 'input_mode', 'drag_drop') == "drag_drop" else "Ctrl+V"
        self.bouton_input_mode = tk.Button(
            frame_actions, text=_('buttons.input_mode', mode=mode_text), font=('Segoe UI Emoji', 10),
            bg='#17a2b8', fg='#000000', activebackground='#138496',
            bd=1, relief='solid', command=self.toggle_input_mode,
            width=12  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        self.bouton_input_mode.grid(row=0, column=2, sticky="nsew", padx=5, pady=15)

        # Bouton Glossaire
        btn_glossaire = tk.Button(
            frame_actions, text=_('buttons.glossary'), font=('Segoe UI Emoji', 10),
            bg='#6f42c1', fg='#000000', activebackground='#5a359a',
            bd=1, relief='solid', command=self.ouvrir_glossaire,
            width=12  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        btn_glossaire.grid(row=0, column=3, sticky="nsew", padx=5, pady=15)

        # Utilitaires avec états dynamiques
        self._create_utility_buttons(frame_actions)

    def _create_utility_buttons(self, frame_actions):
        """Crée les boutons utilitaires avec états dynamiques"""
        # Bouton Auto-Open avec état
        auto_status = "ON" if config_manager.is_auto_open_enabled() else "OFF"
        self.bouton_auto_open = tk.Button(
            frame_actions, text=_('buttons.auto_open', status=auto_status), 
            font=('Segoe UI Emoji', 10), bg='#ffc107', fg='#000000',
            bd=1, relief='solid', command=self.handle_toggle_auto_open,
            width=14  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        self.bouton_auto_open.grid(row=0, column=7, sticky="nsew", padx=5, pady=15)
        
        # Bouton Validation avec état
        valid_status = "ON" if config_manager.is_validation_enabled() else "OFF"
        self.bouton_validation = tk.Button(
            frame_actions, text=_('buttons.validation', status=valid_status),
            font=('Segoe UI Emoji', 10), bg='#ffc107', fg='#000000',
            bd=1, relief='solid', command=self.toggle_validation,
            width=14  # Largeur fixe augmentée pour accommoder les textes plus longs
        )
        self.bouton_validation.grid(row=0, column=8, sticky="nsew", padx=5, pady=15)
        
        # Autres boutons utilitaires
        utilitaires = [
            (_('buttons.clean'), self.nettoyer_page, 4),
            (_('buttons.temporary'), self.ouvrir_dossier_temporaire, 5),
            (_('buttons.warnings'), self.ouvrir_avertissements, 6),
            (_('buttons.help'), self.afficher_aide_intelligente, 9)
        ]
        
        for text, command, col in utilitaires:
            btn = tk.Button(frame_actions, text=text, font=('Segoe UI Emoji', 10),
                        bg='#ffc107', fg='#000000', activebackground='#e0a800',
                        bd=1, relief='solid', command=command,
                        width=12)  # Largeur fixe augmentée pour accommoder les textes plus longs
            btn.grid(row=0, column=col, sticky="nsew", padx=5, pady=15)

    def afficher_aide_intelligente(self):
        """Affiche l'aide selon l'expérience utilisateur - VERSION INTELLIGENTE"""
        try:
            # ✅ MODIFIÉ : Accéder directement au menu d'aide sans popup
            from ui.tutorial import show_help_menu
            show_help_menu()
            log_message("INFO", "Menu d'aide ouvert directement")
                
        except Exception as e:
            log_message("ERREUR", "Erreur aide intelligente", e)
            # Fallback vers le menu d'aide
            try:
                from ui.tutorial import show_help_menu
                show_help_menu()
            except:
                self.afficher_tutoriel()

    def _determine_user_type(self):
        """Détermine le type d'utilisateur selon son ancienneté"""
        try:
            import datetime
            from utils.constants import FILE_NAMES
            
            tutorial_flag_file = FILE_NAMES["tutorial_flag"]
            
            if not os.path.exists(tutorial_flag_file):
                return "nouveau"  # Pas de flag = très nouveau
            
            # Calculer l'ancienneté
            creation_time = os.path.getctime(tutorial_flag_file)
            creation_date = datetime.datetime.fromtimestamp(creation_time)
            now = datetime.datetime.now()
            days_since_first_use = (now - creation_date).days
            
            if days_since_first_use <= 3:
                return "nouveau"        # 0-3 jours
            elif days_since_first_use <= 7:
                return "recent"         # 4-7 jours  
            else:
                return "experimente"    # 8+ jours
            
        except Exception as e:
            log_message("WARNING", f"Erreur détermination type utilisateur: {e}")
            return "experimente"  # Par défaut, traiter comme expérimenté

    def ouvrir_glossaire(self):
        """Ouvre le gestionnaire de glossaire"""
        try:
            # Créer et stocker la référence au dialogue
            self.glossary_dialog = GlossaryDialog(self.root, self)
            self.glossary_dialog.show()
            log_message("INFO", "Gestionnaire de glossaire ouvert")
        except Exception as e:
            log_message("ERREUR", "Erreur lors de l'ouverture du glossaire", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'ouvrir le glossaire:\n{str(e)}")

    def extraire_textes_enhanced(self):
        """✅ NOUVEAU : Extraction avec i18n + notifications intelligentes"""
        if not self.file_content:
            # ✅ RÉDUCTION POPUP : Toast au lieu de popup
            mode_info = _('buttons.input_mode', mode="D&D") if self.input_mode == "drag_drop" else _('buttons.input_mode', mode="Ctrl+V")
            self.notifications.notify(
                f"{_('status.no_file')} - {mode_info}", 
                'TOAST', 
                duration=4000
            )
            return
        
        try:
            # ✅ NOTIFICATION STATUS : Barre de statut au lieu de popup
            self.notifications.notify(_('status.extracting'), 'STATUS')
            self.root.update()
            
            # Sauvegarde de sécurité
            if self.original_path:
                backup_result = create_safety_backup(self.original_path)
                if not backup_result['success']:
                    log_message("WARNING", f"Sauvegarde échouée: {backup_result['error']}")
            
            # Utilisation du TextExtractor
            extractor = TextExtractor()
            extractor.load_file_content(self.file_content, self.original_path)
            results = extractor.extract_texts()
            self.extraction_results = results
            self.last_extraction_time = getattr(extractor, 'extraction_time', 0)
            self.extraction_results['extracted_count'] = getattr(extractor, 'extracted_count', 0)
            self.extraction_results['asterix_count'] = getattr(extractor, 'asterix_count', 0)
            self.extraction_results['empty_count'] = getattr(extractor, 'empty_count', 0)
            
            # Gestion de l'ouverture des fichiers
            files_to_open = [f for f in [
                self.extraction_results.get('main_file'),
                self.extraction_results.get('asterix_file'), 
                self.extraction_results.get('empty_file'),
                self.extraction_results.get('glossary_file')
            ] if f]
            
            auto_open_enabled = config_manager.is_auto_open_enabled()
            
            # ✅ LOGIQUE SIMPLIFIÉE : Ouverture selon préférence
            if auto_open_enabled and files_to_open:
                FileOpener.open_files(files_to_open, True)
                open_status = _('extraction.files_opened_auto', count=len(files_to_open))
            elif not auto_open_enabled and files_to_open:
                # ✅ RÉDUCTION POPUP : Seulement si Auto-Open désactivé ET fichiers créés
                result = self.notifications.notify(
                    _('extraction.confirm_open_files', 
                    extracted=extractor.extracted_count, 
                    files=len(files_to_open)), 
                    'CONFIRM'
                )
                
                if result:
                    FileOpener.open_files(files_to_open, True)
                    open_status = _('extraction.files_opened_manual', count=len(files_to_open))
                else:
                    open_status = _('extraction.files_created_not_opened', count=len(files_to_open))
            else:
                open_status = ""
            
            # ✅ NOUVEAU : Message de succès intelligent et traduit
            success_details = []
            
            # Textes principaux
            success_details.append(_('extraction.texts_extracted', count=extractor.extracted_count))
            
            # Détails optionnels
            if extractor.asterix_count > 0:
                success_details.append(_('extraction.asterix_found', count=extractor.asterix_count))
            
            if extractor.empty_count > 0:
                success_details.append(_('extraction.empty_found', count=extractor.empty_count))
            
            if hasattr(extractor, 'glossary_mapping') and len(extractor.glossary_mapping) > 0:
                success_details.append(_('extraction.glossary_protected', count=len(extractor.glossary_mapping)))
            
            if hasattr(extractor, 'ellipsis_mapping') and len(extractor.ellipsis_mapping) > 0:
                success_details.append(_('extraction.ellipsis_protected', count=len(extractor.ellipsis_mapping)))
            
            # Info sur le mode source
            if hasattr(self, 'text_mode') and self.text_mode == "clipboard":
                success_details.append(_('extraction.source_clipboard'))
            
            # ✅ MISE À JOUR STATUS BAR : Informations principales
            status_msg = _('status.texts_extracted', 
                        count=extractor.extracted_count, 
                        time=self.last_extraction_time)
            
            if self.label_stats is not None:
                self.label_stats.config(text=status_msg)
            
            # ✅ RÉDUCTION POPUP : Toast de succès avec détails
            toast_message = _('messages.success.extraction', time=self.last_extraction_time)
            if open_status:
                toast_message += f" - {open_status}"
            
            self.notifications.notify(toast_message, 'TOAST', duration=5000)
            
            # ✅ POPUP DÉTAILLÉE : Seulement si demandée ou cas spécial
            if self._should_show_detailed_extraction_info(extractor):
                detailed_message = self._build_detailed_extraction_message(
                    extractor, success_details, open_status
                )
                self.notifications.notify(detailed_message, 'MODAL', title=_('extraction.success_title'))
            
        except Exception as e:
            log_message("ERREUR", "Erreur extraction avec glossaire", e)
            # ✅ ERREUR : Toujours en popup modal (critique)
            error_msg = _('extraction.error_occurred', error=str(e))
            self.notifications.notify(error_msg, 'MODAL', title=_('extraction.error_title'))
            
            if self.label_stats is not None:
                self.label_stats.config(text=f"❌ {_('extraction.error_status')}")

    def _should_show_detailed_extraction_info(self, extractor):
        """Détermine si on doit afficher les détails complets de l'extraction"""
        # ✅ RÈGLES INTELLIGENTES : Popup détaillée seulement si :
        return (
            # Première extraction de la session
            self.last_extraction_time == 0 or
            # Beaucoup de types différents détectés
            sum([
                1 if extractor.extracted_count > 0 else 0,
                1 if extractor.asterix_count > 0 else 0,
                1 if extractor.empty_count > 0 else 0,
                1 if hasattr(extractor, 'glossary_mapping') and len(extractor.glossary_mapping) > 0 else 0
            ]) >= 3 or
            # Mode presse-papier (moins familier)
            (hasattr(self, 'text_mode') and self.text_mode == "clipboard")
        )

    def _build_detailed_extraction_message(self, extractor, success_details, open_status):
        """Construit le message détaillé d'extraction"""
        message_parts = [
            _('extraction.success_header', time=self.last_extraction_time),
            "",  # Ligne vide
            "\n".join(success_details)
        ]
        
        if open_status:
            message_parts.extend(["", open_status])
        
        return "\n".join(message_parts)

    def _fix_ellipsis_in_file(self, file_path):
        """✅ SOLUTION SIMPLE : Remplace tous les [...] par ... dans le fichier final"""
        try:
            # Lire le fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Compter les [...] à corriger
            ellipsis_count = content.count('[...]')
            
            if ellipsis_count > 0:
                # Remplacer tous les [...] par ...
                corrected_content = content.replace('[...]', '...')
                
                # Réécrire le fichier
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(corrected_content)
                
                log_message("INFO", f"Correction [...] → ... : {ellipsis_count} remplacements effectués")
                return ellipsis_count
            
            return 0
            
        except Exception as e:
            log_message("WARNING", f"Erreur correction [...] → ... : {e}")
            return 0

    def reconstruire_fichier_enhanced(self):
        """✅ NOUVEAU : Reconstruction avec i18n + notifications intelligentes"""
        if not self.file_content or not self.original_path:
            self.notifications.notify(_('status.no_file'), 'TOAST', duration=4000)
            return
        
        try:
            # Vérifier que les fichiers d'extraction existent
            file_base = get_file_base_name(self.original_path)
            
            if not self.extraction_results:
                self.notifications.notify(_('reconstruction.no_extraction'), 'TOAST', duration=4000)
                return
            
            # ✅ VALIDATION : Popup seulement si activée ET erreurs détectées
            if config_manager.is_validation_enabled():
                extracted_count = self.extraction_results.get('extracted_count', 0)
                asterix_count = self.extraction_results.get('asterix_count', 0)
                empty_count = self.extraction_results.get('empty_count', 0)
                
                validation_result = validate_before_reconstruction(file_base, extracted_count, asterix_count, empty_count)
                
                if not validation_result['overall_valid']:
                    errors = []
                    if validation_result['main_file'] and not validation_result['main_file']['valid']:
                        errors.extend(validation_result['main_file'].get('errors', []))
                    
                    error_summary = "\n".join(f"• {error}" for error in errors[:3])
                    if len(errors) > 3:
                        error_summary += f"\n... {_('validation.more_errors', count=len(errors) - 3)}"
                    
                    # ✅ POPUP CRITIQUE : Validation échouée (importante)
                    full_message = _('validation.failed_message', errors=error_summary)
                    result = self.notifications.notify(full_message, 'CONFIRM', title=_('validation.failed_title'))
                    if not result:
                        return
            
            # Gestion du mode de sauvegarde
            save_mode = 'new_file'
            
            if hasattr(self, 'text_mode') and self.text_mode == "file":
                if not self._save_mode:
                    save_dialog = SaveModeDialog(self.root)
                    self._save_mode = save_dialog.show()
                    
                    if not self._save_mode:
                        return
                save_mode = self._save_mode
            elif hasattr(self, 'text_mode') and self.text_mode == "clipboard":
                save_mode = 'new_file'
            
            # ✅ NOTIFICATION STATUS : Barre de statut
            self.notifications.notify(_('status.reconstructing'), 'STATUS')
            self.root.update()
            
            start_time = time.time()
            reconstructor = FileReconstructor()
            reconstructor.load_file_content(self.file_content, self.original_path)
            result = reconstructor.reconstruct_file(save_mode)
            self.last_reconstruction_time = time.time() - start_time
            
            if result:
                # Correction des [...] → ... 
                try:
                    ellipsis_corrections = self._fix_ellipsis_in_file(result['save_path'])
                    if ellipsis_corrections > 0:
                        log_message("INFO", f"Post-traitement : {ellipsis_corrections} [...] corrigés en ...")
                except Exception as e:
                    log_message("WARNING", f"Erreur correction [...]: {e}")
                
                # ✅ CONTRÔLE COHÉRENCE : Notification intelligente
                if config_manager.is_validation_enabled():
                    coherence_result = check_file_coherence(result['save_path'])
                    
                    if coherence_result['issues_found'] > 0:
                        # ✅ TOAST FIRST : Information discrète
                        warning_msg = _('coherence.issues_detected', count=coherence_result['issues_found'])
                        self.notifications.notify(warning_msg, 'TOAST', duration=6000)
                        
                        # ✅ POPUP OPTIONNELLE : Seulement si l'utilisateur veut les détails
                        detailed_msg = _('coherence.detailed_message', 
                                    count=coherence_result['issues_found'],
                                    warning_file=os.path.basename(coherence_result.get('warning_file', '')))
                        
                        response = self.notifications.notify(detailed_msg, 'CONFIRM', title=_('coherence.title'))
                        
                        if response and coherence_result.get('warning_file'):
                            try:
                                FileOpener.open_files([coherence_result['warning_file']], True)
                            except Exception as e:
                                log_message("WARNING", f"Impossible d'ouvrir le fichier d'avertissement", e)
                
                # ✅ MISE À JOUR STATUS BAR
                status_msg = _('status.reconstruction_completed', time=self.last_reconstruction_time)
                self.notifications.notify(status_msg, 'STATUS')
                
                # Ouvrir le fichier selon préférence
                auto_open_enabled = config_manager.is_auto_open_enabled()
                try:
                    FileOpener.open_files([result['save_path']], auto_open_enabled)
                except:
                    pass
                
                # ✅ MESSAGES ADAPTÉS selon le mode et préférence Auto-Open
                ellipsis_info = f" - {_('reconstruction.ellipsis_fixed', count=ellipsis_corrections)}" if ellipsis_corrections > 0 else ""
                
                if hasattr(self, 'text_mode') and self.text_mode == "clipboard":
                    if auto_open_enabled:
                        toast_msg = _('reconstruction.clipboard_success_opened', 
                                    filename=os.path.basename(result['save_path']),
                                    time=self.last_reconstruction_time) + ellipsis_info
                    else:
                        toast_msg = _('reconstruction.clipboard_success_created',
                                    filename=os.path.basename(result['save_path']),
                                    time=self.last_reconstruction_time) + ellipsis_info
                    
                    self.notifications.notify(toast_msg, 'TOAST', duration=5000)
                else:
                    # Proposer de passer au fichier suivant en mode dossier
                    if file_manager.is_folder_mode:
                        self.handle_next_file()
                    else:
                        if auto_open_enabled:
                            toast_msg = _('reconstruction.file_success_opened',
                                        filename=os.path.basename(result['save_path']),
                                        time=self.last_reconstruction_time) + ellipsis_info
                        else:
                            toast_msg = _('reconstruction.file_success_created',
                                        filename=os.path.basename(result['save_path']),
                                        time=self.last_reconstruction_time) + ellipsis_info
                        
                        self.notifications.notify(toast_msg, 'TOAST', duration=5000)
            else:
                self.notifications.notify(_('reconstruction.error_general'), 'MODAL', title=_('reconstruction.error_title'))
                if self.label_stats is not None:
                    self.label_stats.config(text=f"❌ {_('reconstruction.error_status')}")
                    
        except Exception as e:
            log_message("ERREUR", "Erreur lors de la reconstruction avec glossaire", e)
            error_msg = _('reconstruction.error_occurred', error=str(e))
            self.notifications.notify(error_msg, 'MODAL', title=_('reconstruction.error_title'))
            if self.label_stats is not None:
                self.label_stats.config(text=f"❌ {_('reconstruction.error_status')}")

    def appliquer_theme_enhanced(self):
        """Application du thème avec support simplifié"""
        try:
            from ui.themes import theme_manager
            
            current_mode = "dark" if config_manager.is_dark_mode_enabled() else "light"
            theme_manager.set_theme(current_mode)
            theme = theme_manager.get_theme()
            
            # Appliquer le thème à la fenêtre principale
            self.root.configure(bg=theme["bg"])

            # Widgets principaux
            widgets_to_update = [
                (self.title_label, theme["bg"], theme["fg"]),
                (self.subtitle_label, theme["bg"], theme["fg"]),
                (self.label_chemin, theme["frame_bg"], theme["accent"]),
                (self.label_stats, theme["frame_bg"], theme["fg"])
            ]

            for widget, bg_color, fg_color in widgets_to_update:
                if widget:
                    try:
                        widget.configure(bg=bg_color, fg=fg_color)
                    except Exception as e:
                        pass


            # Frame info
            if self.frame_info:
                try:
                    self.frame_info.configure(bg=theme["frame_bg"])
                except Exception as e:
                    pass
                    

            # Zone de texte simplifiée
            if self.text_area and hasattr(self.text_area, 'set_theme'):
                try:
                    self.text_area.set_theme(current_mode)
                except Exception as e:
                    pass
                    

            # Mise à jour des couleurs de boutons
            self._update_button_text_colors(theme)

            
            
        except Exception as e:
    
            log_message("WARNING", f"Erreur application du thème", e)

    def create_content_frame(self):
        """Crée la zone de contenu - VERSION AMÉLIORÉE avec numéros de ligne"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        frame_content = tk.Frame(self.root, bg=theme["bg"])
        frame_content.pack(expand=True, fill='both', padx=20, pady=(0, 10))
        
        # ScrolledText
        self.text_area = ScrolledText(
            frame_content,
            font=('Cascadia Code', 10),
            bg=theme["entry_bg"],
            fg=theme["entry_fg"]
        )
        self.text_area.pack(expand=True, fill='both')
        # Configuration mode initial
        try:
            self.configure_input_mode()
        except Exception as e:
            pass
        
        self.root.after(500, self._initialize_text_area_display)

    def _initialize_text_area_display(self):
        """Initialise l'affichage de la zone de texte après création complète"""
        try:
            # Vérifier que text_area existe et est prête
            if not hasattr(self, 'text_area') or not self.text_area:
                return
            # Vérifier l'état de file_content (doit être initialisé dans __init__)
            if not hasattr(self, 'file_content'):
                print("⚠️ DEBUG - file_content pas initialisé")
                self.file_content = []  # Initialiser par défaut
            print(f"🔍 DEBUG - État file_content: {len(self.file_content) if self.file_content else 0} éléments")
            # Mettre à jour l'affichage
            self._update_drag_drop_display()
            print("✅ DEBUG - Initialisation affichage terminée")
        except Exception as e:
            print(f"💥 DEBUG - Erreur initialisation affichage: {str(e)}")
            log_message("WARNING", f"Erreur initialisation affichage zone de texte", e)

    # =============================================================================
    # MÉTHODES DE GESTION DES THÈMES
    # =============================================================================

    def toggle_dark_mode(self):
        """✅ NOUVEAU : Basculement thème avec mise à jour langue"""
        try:
            # 1. Met à jour la config
            config_manager.toggle_dark_mode()

            # 2. Appliquer le thème immédiatement au theme_manager
            from ui.themes import theme_manager
            new_theme = "dark" if config_manager.is_dark_mode_enabled() else "light"
            theme_manager.set_theme(new_theme)
            theme = theme_manager.get_theme()

            # 3. Appliquer le thème à la fenêtre principale en premier
            self.root.configure(bg=theme["bg"])

            # 4. Sauvegarder l'état avant de recréer
            current_file_content = self.file_content.copy() if self.file_content else []
            current_original_path = self.original_path
            current_extraction_results = self.extraction_results
            current_last_extraction_time = self.last_extraction_time
            current_last_reconstruction_time = self.last_reconstruction_time
            current_save_mode = self._save_mode
            current_text_mode = getattr(self, 'text_mode', 'empty')
            current_input_mode = getattr(self, 'input_mode', 'drag_drop')
            current_source_info = getattr(self, 'source_info', None)
            current_clipboard_counter = getattr(self, 'clipboard_counter', 0)

            # 5. Détruire et recréer l'interface complètement
            for widget in self.root.winfo_children():
                widget.destroy()

            # 6. Recréer l'interface avec le nouveau thème
            self.create_interface()

            # 7. ✅ NOUVEAU : Forcer l'application du thème à tous les widgets
            self.appliquer_theme_complet()

            # 8. Restaurer l'état complet
            self.file_content = current_file_content
            self.original_path = current_original_path
            self.extraction_results = current_extraction_results
            self.last_extraction_time = current_last_extraction_time
            self.last_reconstruction_time = current_last_reconstruction_time
            self._save_mode = current_save_mode
            self.text_mode = current_text_mode
            self.input_mode = current_input_mode
            self.source_info = current_source_info
            self.clipboard_counter = current_clipboard_counter

            # 9. Restaurer l'affichage si un fichier était chargé
            if self.original_path and self.file_content:
                if self.label_chemin is not None:
                    self.label_chemin.config(text=f"📄 {self.original_path}")
                if self.text_area is not None:
                    self.text_area.delete('1.0', tk.END)
                    self.text_area.insert(tk.END, ''.join(self.file_content))
                line_count = len(self.file_content)
                if self.label_stats is not None:
                    status_msg = _('status.lines_loaded', count=line_count)
                    self.label_stats.config(text=f"📊 {status_msg}")
            
            # 10. ✅ NOUVEAU : Mettre à jour les textes traduits après changement thème
            update_interface_language(self)
            
            # 11. Reconfigurer le mode d'entrée
            try:
                self.configure_input_mode()
                self._update_drag_drop_display()
            except Exception as e:
                print(f"⚠️ DEBUG - Erreur reconfig après toggle theme: {e}")
            
            # 12. ✅ TOAST DISCRET : Confirmation de changement
            theme_name = _('theme.dark_mode') if config_manager.is_dark_mode_enabled() else _('theme.light_mode')
            success_msg = _('theme.changed_to', theme=theme_name)
            self.notifications.notify(success_msg, 'TOAST', duration=3000)
            
            print(f"✅ DEBUG - Basculement vers thème {new_theme} terminé avec succès")
            
        except Exception as e:
            print(f"💥 DEBUG - Erreur toggle_dark_mode: {e}")
            log_message("ERREUR", "Erreur basculement thème", e)
            error_msg = _('theme.error_occurred', error=str(e))
            self.notifications.notify(error_msg, 'MODAL', title=_('theme.error_title'))

    def appliquer_theme_complet(self):
        """✅ Application complète du thème - CORRECTION ERREUR"""
        try:
            from ui.themes import theme_manager
            theme = theme_manager.get_theme()

            # Appliquer à la fenêtre principale
            self.root.configure(bg=theme["bg"])

            # ✅ MISE À JOUR SPÉCIFIQUE DES WIDGETS PRINCIPAUX
            widgets_to_update = [
                (self.title_label, "title"),
                (self.subtitle_label, "subtitle"), 
                (self.label_chemin, "path_label"),
                (self.label_stats, "stats_label")
            ]

            for widget, widget_type in widgets_to_update:
                if widget:
                    theme_manager.apply_to_widget(widget, widget_type)

            # ✅ MISE À JOUR DE LA ZONE DE TEXTE
            if self.text_area:
                self.text_area.configure(
                    bg=theme["entry_bg"],
                    fg=theme["entry_fg"],
                    selectbackground=theme["select_bg"],
                    selectforeground=theme["select_fg"],
                    insertbackground=theme["entry_fg"],
                    highlightbackground=theme["frame_bg"],
                    highlightcolor=theme["accent"]
                )

            # ✅ MISE À JOUR DES FRAMES
            if self.frame_info:
                self.frame_info.configure(bg=theme["frame_bg"])

            print(f"✅ DEBUG - Thème {theme_manager.current_theme} appliqué complètement")

        except Exception as e:
            print(f"⚠️ DEBUG - Erreur appliquer_theme_complet: {e}")

    def _update_button_text_colors(self, theme):
        """✅ NOUVELLE MÉTHODE : Met à jour les couleurs de texte des boutons"""
        try:
            # Définir les couleurs de texte selon le thème
            button_text_color = "#ffffff" if config_manager.is_dark_mode_enabled() else "#000000"
            
            # Liste des boutons avec leurs couleurs spécifiques
            buttons_to_update = [
                # Boutons qui gardent toujours du texte noir
                (self.bouton_theme, "#000000"),  # Toujours noir sur jaune
                (getattr(self, 'bouton_auto_open', None), "#000000"),  # Noir sur jaune
                (getattr(self, 'bouton_validation', None), "#000000"),  # Noir sur jaune
                
                # ✅ CORRECTION : Bouton input_mode TOUJOURS noir
                (getattr(self, 'bouton_input_mode', None), "#000000"),  # ✅ TOUJOURS NOIR
            ]
            
            for button, text_color in buttons_to_update:
                if button:
                    try:
                        button.configure(fg=text_color)
                    except Exception as e:
                        print(f"⚠️ DEBUG - Erreur couleur bouton: {e}")
                        
            print(f"✅ DEBUG - Couleurs boutons mises à jour pour thème {theme}")
            
        except Exception as e:
            print(f"⚠️ DEBUG - Erreur _update_button_text_colors: {e}")

    def _apply_theme_to_all_frames(self, theme):
        """Applique le thème à tous les frames de l'interface"""
        try:
            # Liste de tous les frames à thématiser
            frames_to_theme = []
            
            # Parcourir tous les widgets enfants de la fenêtre principale
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame):
                    frames_to_theme.append(widget)
                    # Parcourir les enfants des frames
                    self._collect_frames_recursive(widget, frames_to_theme)
            
            # Appliquer le thème à tous les frames trouvés
            for frame in frames_to_theme:
                try:
                    frame.configure(bg=theme["bg"])
                except Exception as e:
                    print(f"⚠️ DEBUG - Erreur thème frame: {e}")
            
            print(f"✅ DEBUG - Thème appliqué à {len(frames_to_theme)} frames")
            
        except Exception as e:
            print(f"⚠️ DEBUG - Erreur _apply_theme_to_all_frames: {e}")

    def _collect_frames_recursive(self, parent, frame_list):
        """Collecte récursivement tous les frames enfants"""
        try:
            for child in parent.winfo_children():
                if isinstance(child, tk.Frame):
                    frame_list.append(child)
                    # Récursion pour les enfants
                    self._collect_frames_recursive(child, frame_list)
        except Exception as e:
            print(f"⚠️ DEBUG - Erreur récursion frames: {e}")

    # =============================================================================
    # MÉTHODES DE GESTION DES MODES D'ENTRÉE
    # =============================================================================

    def toggle_input_mode(self):
        """Bascule entre mode Drag & Drop et mode Ctrl+V avec avertissement"""
        try:
            old_mode = self.input_mode
            self.input_mode = "ctrl_v" if self.input_mode == "drag_drop" else "drag_drop"
            
            self.configure_input_mode()
            self.update_input_mode_button()
            
            # Messages adaptés selon la disponibilité
            if self.input_mode == "drag_drop" and not DND_AVAILABLE:
                messagebox.showinfo(
                    "🎯 Mode Drag & Drop",
                    "Mode: Drag & Drop (Non disponible)\n\n"
                    "⚠️ Votre système ne supporte pas le Drag & Drop.\n\n"
                    "💡 Utilisez les boutons bleus pour ouvrir des fichiers\n"
                    "ou basculez en mode Ctrl+V."
                )
            else:
                mode_name = "Drag & Drop" if self.input_mode == "drag_drop" else "Ctrl+V"
                mode_desc = ("Utilisez les boutons pour ouvrir des fichiers" if self.input_mode == "drag_drop" and not DND_AVAILABLE
                            else "Glissez des fichiers .rpy" if self.input_mode == "drag_drop" 
                            else "Utilisez Ctrl+V pour coller")
                
                messagebox.showinfo(f"🎯 Mode {mode_name}",
                    f"Mode: {mode_name}\n💡 {mode_desc}")
            
            log_message("INFO", f"Mode changé: {old_mode} → {self.input_mode}")
            
        except Exception as e:
            log_message("ERREUR", "Erreur basculement mode", e)

    def configure_input_mode(self):
        """Configure selon le mode - VERSION UNIFIÉE"""
        try:
            if not hasattr(self, 'text_area') or not self.text_area:
                return
            
            if self.input_mode == "drag_drop":
                self.configure_drag_drop_mode()
            else:
                self.configure_ctrl_v_mode()
            
            self._update_drag_drop_display()
            
        except Exception as e:
            print(f"⚠️ DEBUG - Erreur config mode: {e}")

    def configure_drag_drop_mode(self):
        """Mode D&D avec fallback intelligent"""
        try:
            # Désactiver Ctrl+V
            for binding in ['<Control-v>', '<Control-V>']:
                if self.text_area is not None:
                    self.text_area.unbind(binding)
                self.root.unbind(binding)
            
            # Essayer d'activer D&D seulement si disponible
            if DND_AVAILABLE:
                print("✅ DEBUG - Configuration Drag & Drop (disponible)")
                self._setup_drag_drop()
            else:
                print("⚠️ DEBUG - Drag & Drop non disponible - Mode boutons uniquement")
                # En mode D&D sans support, on garde juste les boutons
                # et le message d'invitation explique les alternatives
            
        except Exception as e:
            print(f"⚠️ DEBUG - Erreur config D&D: {e}")

    def configure_ctrl_v_mode(self):
        """Mode Ctrl+V seul"""
        try:
            # Désactiver D&D
            try:
                if self.text_area is not None:
                    try:
                        self.text_area.drop_target_unregister('DND_Files')  # type: ignore
                    except Exception:
                        pass
                for event in ['<<Drop>>', '<<DragEnter>>', '<<DragLeave>>']:
                    if self.text_area is not None:
                        self.text_area.unbind(event)
                    self.root.unbind(event)
            except:
                pass
            
            # Activer Ctrl+V
            for binding in ['<Control-v>', '<Control-V>']:
                if self.text_area is not None:
                    self.text_area.bind(binding, self.handle_paste)
                self.root.bind(binding, self.handle_paste)
            
        except Exception as e:
            print(f"⚠️ DEBUG - Erreur config Ctrl+V: {e}")

    def handle_paste(self, event=None):
        """Colle le contenu du presse-papier"""
        try:
            print("📋 DEBUG - handle_paste appelé")
            
            # Vérifier qu'on est bien en mode Ctrl+V
            if hasattr(self, 'input_mode') and self.input_mode != "ctrl_v":
                messagebox.showinfo(
                    "📋 Mode incorrect",
                    f"Mode actuel: Drag & Drop\n\n"
                    f"Pour utiliser Ctrl+V, basculez en mode Ctrl+V\n"
                    f"avec le bouton violet."
                )
                return "break"
            
            # Récupérer le presse-papier
            try:
                clipboard_content = self.root.clipboard_get()
            except tk.TclError:
                messagebox.showinfo("📋 Presse-papier vide", "Le presse-papier ne contient pas de texte.")
                return "break"
            
            if not clipboard_content or not clipboard_content.strip():
                messagebox.showinfo("📋 Presse-papier vide", "Le presse-papier ne contient pas de texte.")
                return "break"
            
            # Vérifier conflit avec contenu existant
            if self.file_content and hasattr(self, 'text_mode') and self.text_mode == "file":
                result = messagebox.askyesno(
                    "📋 Remplacer le contenu",
                    f"Un fichier est déjà chargé.\n\n"
                    f"Voulez-vous le remplacer par le contenu du presse-papier ?"
                )
                if not result:
                    return "break"
            
            # Charger le contenu
            self.load_from_clipboard(clipboard_content)
            
            log_message("INFO", f"Contenu chargé depuis le presse-papier: {len(clipboard_content)} caractères")
            return "break"
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors du collage", e)
            messagebox.showerror("❌ Erreur", f"Erreur lors du collage:\n{str(e)}")
            return "break"

    def load_from_clipboard(self, content):
        """Charge du contenu depuis le presse-papier"""
        try:
            # Convertir en liste de lignes
            lines = content.splitlines(keepends=True)
            
            # Générer un nom unique pour ce contenu
            self.clipboard_counter = getattr(self, 'clipboard_counter', 0) + 1
            timestamp = int(time.time())
            virtual_name = f"clipboard_{self.clipboard_counter}_{timestamp}.rpy"
            
            # Charger le contenu dans les variables
            self.file_content = lines
            self.original_path = virtual_name
            self.text_mode = "clipboard"
            self.source_info = {
                'type': 'clipboard',
                'length': len(content),
                'lines': len(lines),
                'timestamp': timestamp
            }
            
            # Mettre à jour l'interface
            if self.text_area is not None:
                self.text_area.configure(state='normal')
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', content)
            
            # Mise à jour des labels
            self.label_chemin.config(text=f"📋 Contenu du presse-papier ({len(lines)} lignes)")
            self.label_stats.config(text=f"📊 {len(lines)} lignes chargées depuis le presse-papier")
            
            # Message de succès
            auto_status = "activé" if config_manager.is_auto_open_enabled() else "désactivé"
            messagebox.showinfo(
                "📋 Contenu chargé",
                f"Contenu du presse-papier chargé avec succès !\n\n"
                f"📝 Lignes: {len(lines)}\n"
                f"📊 Caractères: {len(content)}\n\n"
                f"💡 Utilisez maintenant le bouton 'Extraire'\n"
                f"📂 Auto-Open: {auto_status}"
            )
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors du chargement depuis le presse-papier", e)
            messagebox.showerror("❌ Erreur", f"Erreur lors du chargement:\n{str(e)}")

    def is_likely_renpy_content(self, content):
        """Vérifie si le contenu ressemble à du code Ren'Py"""
        try:
            # Patterns typiques Ren'Py
            renpy_indicators = [
                'translate ', 'old "', 'new "', 'label ', 'menu:', 'scene ', 'show ', 
                'hide ', 'with ', 'jump ', 'call ', 'return', '"', '# game/', '# renpy/',
                'strings:', 'TODO:', 'Translation updated'
            ]
            
            lines = content.split('\n')
            indicator_count = 0
            
            for line in lines[:20]:  # Vérifier les 20 premières lignes
                line_stripped = line.strip().lower()
                for indicator in renpy_indicators:
                    if indicator.lower() in line_stripped:
                        indicator_count += 1
                        break
            
            # Si au moins 20% des lignes ont des indicateurs Ren'Py
            return indicator_count >= max(1, len(lines[:20]) * 0.2)
            
        except Exception:
            return True  # En cas d'erreur, accepter le contenu

    def update_input_mode_button(self):
        """Met à jour le bouton de mode avec indication de disponibilité"""
        try:
            if not self.bouton_input_mode:
                return
            
            if self.input_mode == "drag_drop":
                if DND_AVAILABLE:
                    self.bouton_input_mode.config(text="🎯 D&D", bg='#17a2b8')
                else:
                    # ✅ INDICATION VISUELLE que D&D n'est pas disponible
                    self.bouton_input_mode.config(text="🎯 D&D ❌", bg='#6c757d')
            else:
                self.bouton_input_mode.config(text="📋 Ctrl+V", bg='#6f42c1')
        except Exception as e:
            print(f"⚠️ DEBUG - Erreur bouton: {e}")

    def _setup_drag_drop(self):
        """Configure le support du Drag & Drop - VERSION CORRIGÉE"""
        print("🔧 DEBUG - Début _setup_drag_drop()")
        
        if not DND_AVAILABLE:
            print("❌ DEBUG - tkinterdnd2 non disponible")
            return

        try:
            print("🔍 DEBUG - Configuration Drag & Drop...")
            
            # Vérifier que text_area existe
            if not hasattr(self, 'text_area') or not self.text_area:
                print("❌ DEBUG - text_area n'existe pas")
                return
            
            # Enregistrer le drop target
            self.text_area.drop_target_register('DND_Files')
            print("✅ DEBUG - drop_target_register réussi")

            def on_drop(event):
                print(f"🎯 DEBUG - DROP EVENT déclenché!")
                print(f"🔍 DEBUG - event.data = '{event.data}'")
                try:
                    files = event.data
                    print(f"📥 DEBUG - Fichiers reçus: {files}")
                    
                    # Nettoyer le chemin de fichier
                    if files.startswith('{') and files.endswith('}'):
                        files = files[1:-1]  # Enlever { }
                    
                    # CORRECTION : Ligne corrigée
                    file_list = [f.strip() for f in files.split('} {') if f.strip()]
                    if not file_list:
                        file_list = [files.strip()]
                    
                    print(f"📋 DEBUG - Fichiers nettoyés: {file_list}")
                    
                    # Traiter le premier fichier .rpy trouvé
                    for filepath in file_list:
                        cleaned_path = filepath.strip('"').strip("'")
                        print(f"🧹 DEBUG - Test fichier: '{cleaned_path}'")
                        
                        if os.path.exists(cleaned_path) and cleaned_path.lower().endswith('.rpy'):
                            print("✅ DEBUG - Fichier .rpy valide trouvé!")
                            self._handle_dropped_file(cleaned_path)
                            return 'copy'
                    
                    # Aucun fichier .rpy valide trouvé
                    print("❌ DEBUG - Aucun fichier .rpy valide")
                    messagebox.showwarning(
                        "⚠️ Fichier non supporté",
                        "Veuillez glisser un fichier .rpy valide."
                    )
                        
                except Exception as e:
                    print(f"💥 DEBUG - Erreur dans on_drop: {e}")
                    messagebox.showerror("❌ Erreur Drop", f"Erreur lors du traitement:\n{str(e)}")
                
                return 'copy'

            def on_drag_enter(event):
                print("🟢 DEBUG - DRAG ENTER")
                self.text_area.configure(highlightbackground='#28a745', highlightthickness=3)
                return 'copy'

            def on_drag_leave(event):
                print("🔴 DEBUG - DRAG LEAVE")
                border_color = '#555555' if config_manager.is_dark_mode_enabled() else '#d0d0d0'
                self.text_area.configure(highlightbackground=border_color, highlightthickness=1)
                return 'copy'

            # Lier les événements
            self.text_area.dnd_bind('<<Drop>>', on_drop)
            self.text_area.dnd_bind('<<DragEnter>>', on_drag_enter)
            self.text_area.dnd_bind('<<DragLeave>>', on_drag_leave)
            
            print("✅ DEBUG - Drag & Drop configuré avec succès")

        except Exception as e:
            print(f"💥 DEBUG - Erreur configuration Drag & Drop: {e}")
            log_message("WARNING", f"Erreur configuration Drag & Drop: {e}")

    def _update_drag_drop_display(self):
        """Met à jour l'affichage - VERSION AVEC FALLBACK INTELLIGENT"""
        try:
            if not hasattr(self, 'text_area') or not self.text_area:
                return
            
            if not self.file_content or self.file_content == []:
                self.text_mode = "empty"
                
                try:
                    self.text_area.configure(state='normal')
                    self.text_area.delete('1.0', tk.END)
                    
                    # Message unifié mode + auto-open + fallback D&D
                    invitation_text = self._get_unified_invitation_text()
                    self.text_area.insert('1.0', invitation_text)
                    
                except Exception as e:
                    print(f"⚠️ DEBUG - Erreur affichage: {e}")
            else:
                try:
                    self.text_area.configure(state='normal')
                except Exception as e:
                    print(f"⚠️ DEBUG - Erreur activation: {e}")
        
        except Exception as e:
            print(f"💥 DEBUG - Erreur _update_drag_drop_display: {e}")

    def _get_unified_invitation_text(self):
        """✅ MODIFIÉ : Message d'invitation traduit"""
        auto_status = "ON" if config_manager.is_auto_open_enabled() else "OFF"
        
        if self.input_mode == "drag_drop":
            if DND_AVAILABLE:
                return f"""



                            🎯 {_('buttons.input_mode', mode='D&D').upper()}
                            
                            {_('drag_drop.available')}
                            
                            📂 Auto-Open: {auto_status}
                            💡 {_('buttons.input_mode', mode='Ctrl+V')}



                """
            else:
                return f"""



                            🎯 {_('buttons.input_mode', mode='D&D')} ❌
                            
                            {_('drag_drop.unavailable')}
                            
                            🔄 Solutions alternatives :
                            • {_('buttons.open_file')}
                            • {_('buttons.input_mode', mode='Ctrl+V')}
                            
                            📂 Auto-Open: {auto_status}



                """
        else:  # ctrl_v
            return f"""



                            📋 {_('buttons.input_mode', mode='Ctrl+V').upper()}
                            
                            {_('drag_drop.ctrl_v')}
                            
                            📂 Auto-Open: {auto_status}
                            💡 {_('buttons.input_mode', mode='D&D')}



            """

    def reconstruire_fichier(self):
        """Reconstruit avec validation corrigée pour nouvelle structure"""
        if not self.file_content or not self.original_path:
            messagebox.showerror("❌ Erreur", MESSAGES["no_file_loaded"])
            return
        
        try:
            # Vérifier que les fichiers d'extraction existent
            file_base = get_file_base_name(self.original_path)
            
            if not self.extraction_results:
                messagebox.showerror("❌ Erreur", "Effectuez d'abord l'extraction du fichier")
                return
            
            # ✅ CORRECTION : Validation avec nouvelle structure
            if config_manager.is_validation_enabled():
                extracted_count = self.extraction_results.get('extracted_count', 0)
                asterix_count = self.extraction_results.get('asterix_count', 0)
                empty_count = self.extraction_results.get('empty_count', 0)
                
                # Construire les chemins avec la nouvelle structure
                from utils.constants import FOLDERS
                
                game_name = extract_game_name(self.original_path)
                temp_root = FOLDERS["temp"]
                translate_folder = os.path.join(temp_root, game_name, "fichiers_a_traduire")
                
                # Chemins des fichiers de traduction
                main_file_path = os.path.join(translate_folder, f"{file_base}.txt")
                asterix_file_path = os.path.join(translate_folder, f"{file_base}_asterix.txt") if asterix_count > 0 else None
                empty_file_path = os.path.join(translate_folder, f"{file_base}_empty.txt") if empty_count > 0 else None
                
                # Validation avec chemins complets
                from core.validation import TranslationValidator
                validator = TranslationValidator()
                validation_result = validator.validate_all_files_with_paths(
                    main_file_path, asterix_file_path, empty_file_path,
                    extracted_count, asterix_count, empty_count
                )
                
                if not validation_result['overall_valid']:
                    errors = []
                    if validation_result['main_file'] and not validation_result['main_file']['valid']:
                        errors.extend(validation_result['main_file'].get('errors', []))
                    
                    error_message = "Validation échouée:\n\n" + "\n".join(f"• {error}" for error in errors[:3])
                    if len(errors) > 3:
                        error_message += f"\n... et {len(errors) - 3} autres erreurs"
                    
                    result = messagebox.askyesno("⚠️ Validation échouée", error_message + "\n\nContinuer quand même ?")
                    if not result:
                        return
            
            # Gestion du mode de sauvegarde
            save_mode = 'new_file'  # Par défaut
            
            # Mode fichier classique : demander le choix
            if hasattr(self, 'text_mode') and self.text_mode == "file":
                if not self._save_mode:
                    save_dialog = SaveModeDialog(self.root)
                    self._save_mode = save_dialog.show()
                    
                    if not self._save_mode:
                        return
                save_mode = self._save_mode
            
            # Mode presse-papier : TOUJOURS nouveau fichier
            elif hasattr(self, 'text_mode') and self.text_mode == "clipboard":
                save_mode = 'new_file'
                print("📋 DEBUG - Mode presse-papier: forcer nouveau fichier")
            
            # ✅ CORRECTION : Reconstruction avec nouvelle structure
            if self.label_stats is not None:
                self.label_stats.config(text="🔧 Reconstruction en cours...")
            self.root.update()
            
            start_time = time.time()
            reconstructor = FileReconstructor()
            reconstructor.load_file_content(self.file_content, self.original_path)
            result = reconstructor.reconstruct_file(save_mode)
            self.last_reconstruction_time = time.time() - start_time
            
            if result:
                # Contrôle de cohérence si validation activée
                if config_manager.is_validation_enabled():
                    coherence_result = check_file_coherence(result['save_path'])
                    
                    if coherence_result['issues_found'] > 0:
                        response = messagebox.askyesnocancel(
                            "⚠️ Problèmes de cohérence détectés",
                            f"{coherence_result['issues_found']} problème(s) détecté(s) dans la traduction.\n\n"
                            f"Un fichier d'avertissement a été créé dans le dossier 'avertissements/{game_name}'.\n\n"
                            f"• Oui = Ouvrir le fichier d'avertissement maintenant\n"
                            f"• Non = Continuer sans ouvrir\n"
                            f"• Annuler = Voir les détails ici"
                        )
                        
                        if response is True:  # Oui - Ouvrir le fichier
                            try:
                                if coherence_result.get('warning_file'):
                                    FileOpener.open_files([coherence_result['warning_file']], True)
                            except Exception as e:
                                log_message("WARNING", f"Impossible d'ouvrir le fichier d'avertissement", e)
                        
                        elif response is None:  # Annuler - Afficher dans une fenêtre
                            self._show_coherence_issues(coherence_result['issues'])
                
                # Logger la performance
                if hasattr(self, 'last_extractor') and self.last_extractor:
                    try:
                        from utils.logging import log_performance
                        log_performance(
                            "Traitement complet",
                            os.path.basename(self.original_path),
                            self.last_extraction_time + self.last_reconstruction_time,
                            {
                                "extraction": f"{self.last_extraction_time:.2f}s",
                                "reconstruction": f"{self.last_reconstruction_time:.2f}s",
                                "textes": self.last_extractor.extracted_count,
                                "asterisques": self.last_extractor.asterix_count,
                                "vides": self.last_extractor.empty_count
                            }
                        )
                    except Exception as e:
                        log_message("WARNING", "Impossible de logger la performance", e)
                
                # Messages de succès selon le mode
                success_msg = MESSAGES["reconstruction_success"].format(time=self.last_reconstruction_time)
                if self.label_stats is not None:
                    self.label_stats.config(text=f"✅ Reconstruction terminée | ⏱️ {self.last_reconstruction_time:.2f}s")
                
                # Ouvrir le fichier reconstruit si demandé
                try:
                    FileOpener.open_files([result['save_path']], config_manager.is_auto_open_enabled())
                except:
                    pass
                
                # Messages adaptés selon le mode
                if hasattr(self, 'text_mode') and self.text_mode == "clipboard":
                    messagebox.showinfo("🎉 Reconstruction terminée", 
                        f"✅ Fichier traduit créé avec succès !\n\n"
                        f"📁 Fichier: {os.path.basename(result['save_path'])}\n"
                        f"📋 Source: Contenu du presse-papier\n"
                        f"⏱️ Temps: {self.last_reconstruction_time:.2f}s\n\n"
                        f"💡 Le fichier a été créé automatiquement (nouveau fichier)")
                else:
                    # Proposer de passer au fichier suivant en mode dossier
                    if file_manager.is_folder_mode:
                        self.handle_next_file()
                    else:
                        messagebox.showinfo("🎉 Reconstruction terminée", 
                            f"✅ Fichier traduit créé avec succès !\n\n"
                            f"📁 Fichier: {os.path.basename(result['save_path'])}\n"
                            f"⏱️ Temps: {self.last_reconstruction_time:.2f}s")
            else:
                if self.label_stats is not None:
                    self.label_stats.config(text="❌ Erreur lors de la reconstruction")
                messagebox.showerror("❌ Erreur", "Erreur lors de la reconstruction")
                
        except Exception as e:
            log_message("ERREUR", "Erreur lors de la reconstruction", e)
            messagebox.showerror("❌ Erreur", f"Erreur lors de la reconstruction:\n{str(e)}")
            if self.label_stats is not None:
                self.label_stats.config(text="❌ Erreur lors de la reconstruction")

    def demander_mode_sauvegarde(self):
        """Demande le mode de sauvegarde à l'utilisateur"""
        # Réutiliser le mode s'il a déjà été choisi
        if self._save_mode:
            return self._save_mode
        
        dialog = tk.Toplevel(self.root)
        dialog.title("💾 Mode de Sauvegarde")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        dialog.configure(bg=theme["bg"])
        
        result = {'mode': None}
        
        # Interface du dialog
        title_frame = tk.Frame(dialog, bg=theme["bg"])
        title_frame.pack(fill='x', padx=20, pady=20)
        
        title_label = tk.Label(title_frame, text="💾 Choisissez le mode de sauvegarde",
                font=('Segoe UI Emoji', 14, 'bold'), bg=theme["bg"], fg=theme["fg"])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Ce choix sera mémorisé pour cette session",
                font=('Segoe UI Emoji', 9), bg=theme["bg"], fg=theme["fg"])
        subtitle_label.pack(pady=(5, 0))
        
        # Options
        options_frame = tk.Frame(dialog, bg=theme["bg"])
        options_frame.pack(fill='both', expand=True, padx=20)
        
        def choisir_mode(mode):
            result['mode'] = mode
            self._save_mode = mode
            dialog.destroy()
        
        # Option 1: Écraser
        option1_frame = tk.Frame(options_frame, bg=theme["frame_bg"], relief='solid', bd=1)
        option1_frame.pack(fill='x', pady=10)
        
        btn_overwrite = tk.Button(option1_frame, text="🔄 Écraser le fichier original",
                 font=('Segoe UI Emoji', 11, 'bold'), bg=theme.get("warning", "#ffc107"), fg='#000000',
                 bd=0, pady=15, command=lambda: choisir_mode('overwrite'))
        btn_overwrite.pack(fill='x', padx=10, pady=10)
        
        label_overwrite = tk.Label(option1_frame, text="⚠️ Le fichier original sera remplacé par la traduction",
                font=('Segoe UI Emoji', 9), bg=theme["frame_bg"], fg=theme["fg"])
        label_overwrite.pack(pady=(0, 10))
        
        # Option 2: Créer nouveau fichier
        option2_frame = tk.Frame(options_frame, bg=theme["frame_bg"], relief='solid', bd=1)
        option2_frame.pack(fill='x', pady=10)
        
        btn_new_file = tk.Button(option2_frame, text="📝 Créer un nouveau fichier",
                 font=('Segoe UI Emoji', 11, 'bold'), bg=theme["accent"], fg='#000000',
                 bd=0, pady=15, command=lambda: choisir_mode('new_file'))
        btn_new_file.pack(fill='x', padx=10, pady=10)
        
        label_new_file = tk.Label(option2_frame, text="✅ Garde l'original et crée un fichier traduit séparé\n💡 L'original sera automatiquement commenté",
                font=('Segoe UI Emoji', 9), bg=theme["frame_bg"], fg=theme["fg"], justify='left')
        label_new_file.pack(pady=(0, 10))
        
        # Bouton annuler
        btn_cancel = tk.Button(dialog, text="❌ Annuler", font=('Segoe UI Emoji', 10),
                 bg=theme.get("danger", "#dc3545"), fg='#000000', bd=0, pady=8,
                 command=dialog.destroy)
        btn_cancel.pack(pady=10)
        
        dialog.wait_window()
        return result['mode']

    def handle_next_file(self):
        """Gère l'ouverture du fichier suivant en mode dossier"""
        if file_manager.is_folder_mode:
            total_time = self.last_extraction_time + self.last_reconstruction_time
            result = messagebox.askyesno(
                "📂 Fichier suivant",
                f"✅ Fichier traité avec succès !\n\n⏱️ Temps de traitement :\n"
                f"• Extraction: {self.last_extraction_time:.2f}s\n"
                f"• Reconstruction: {self.last_reconstruction_time:.2f}s\n"
                f"• Total: {total_time:.2f}s\n\n"
                f"Voulez-vous ouvrir le fichier suivant du dossier ?"
            )
            if result:
                next_info = file_manager.get_next_file()
                if next_info:
                    self.charger_fichier(next_info['file'])
                    self.update_window_title(next_info['remaining'])
                else:
                    messagebox.showinfo("✅ Information", "Tous les fichiers du dossier ont été traités.")
                    self.nettoyer_page()
            else:
                self.nettoyer_page()

    def ouvrir_fichier_unique(self):
        """Ouvre un fichier .rpy unique"""
        try:
            filepath = file_manager.open_single_file()
            if filepath:
                # Validation avant ouverture
                validation = validate_before_extraction(filepath)
                if not validation['is_valid']:
                    result = messagebox.askyesno(
                        "⚠️ Fichier suspect",
                        f"Ce fichier ne semble pas être un fichier Ren'Py valide.\n\n"
                        f"Confiance: {validation['confidence']}%\n\n"
                        f"Voulez-vous continuer quand même ?"
                    )
                    if not result:
                        return
                
                # Charger le fichier
                self.charger_fichier(filepath)
                self.update_window_title()
                
        except Exception as e:
            log_message("ERREUR", "Erreur lors de l'ouverture du fichier unique", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'ouvrir le fichier:\n{str(e)}")

    def ouvrir_dossier(self):
        """Ouvre un dossier contenant des fichiers .rpy"""
        try:
            folder_info = file_manager.open_folder()
            if folder_info:
                # Charger le premier fichier
                self.charger_fichier(folder_info['current_file'])
                self.update_window_title(folder_info['total_files'] - 1)
                
        except Exception as e:
            log_message("ERREUR", "Erreur lors de l'ouverture du dossier", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'ouvrir le dossier:\n{str(e)}")

    def charger_fichier(self, filepath):
        """Charge un fichier dans l'interface"""
        try:
            self.file_content = file_manager.load_file_content(filepath)
            self.original_path = filepath
            
            # Définir le mode
            self.text_mode = "file"
            self.source_info = {
                'type': 'file',
                'path': filepath,
                'lines': len(self.file_content),
                'size': os.path.getsize(filepath) if os.path.exists(filepath) else 0
            }
            
            self.label_chemin.config(text=f"📄 {filepath}")
            
            # Réactiver l'édition et charger le contenu
            if self.text_area is not None:
                self.text_area.configure(state='normal')
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', ''.join(self.file_content))
            
            line_count = len(self.file_content)
            self.label_stats.config(text=f"📊 {line_count} lignes chargées")
            
            # Mettre à jour l'affichage
            self._update_drag_drop_display()
            
            log_message("INFO", f"Fichier chargé: {line_count} lignes")
            
        except Exception as e:
            log_message("ERREUR", f"Impossible de charger le fichier {filepath}", e)
            messagebox.showerror("❌ Erreur", f"Impossible de charger le fichier:\n{str(e)}")

    def _handle_dropped_file(self, filepath):
        """Gère un fichier déposé par Drag & Drop"""
        try:
            print(f"📁 DEBUG - Traitement fichier: '{filepath}'")
            
            # Vérifications basiques
            if not os.path.exists(filepath):
                messagebox.showerror("❌ Fichier introuvable", f"Le fichier n'existe pas:\n{filepath}")
                return
            
            if not filepath.lower().endswith('.rpy'):
                messagebox.showerror("❌ Fichier non supporté", f"Seuls les fichiers .rpy sont acceptés.\n\nFichier: {os.path.basename(filepath)}")
                return
            
            # Vérifier si du contenu est déjà chargé
            if self.file_content and self.file_content != []:
                result = messagebox.askyesno(
                    "🧹 Remplacer le contenu",
                    f"Du contenu est déjà chargé.\n\n"
                    f"Voulez-vous le remplacer par ce fichier :\n{os.path.basename(filepath)} ?"
                )
                if result:
                    self.nettoyer_page()
                else:
                    return
            
            # Charger le fichier
            self.charger_fichier(filepath)
            
            messagebox.showinfo(
                "🎉 Fichier chargé",
                f"Fichier chargé avec succès par Drag & Drop !\n\n"
                f"📄 {os.path.basename(filepath)}\n"
                f"📊 {len(self.file_content)} lignes"
            )
            
            log_message("INFO", f"Fichier chargé par Drag & Drop: {anonymize_path(filepath)}")
            
        except Exception as e:
            print(f"💥 DEBUG - Erreur _handle_dropped_file: {str(e)}")
            log_message("ERREUR", f"Erreur traitement fichier D&D: {filepath}", e)
            messagebox.showerror("❌ Erreur", f"Erreur lors du chargement:\n{str(e)}")

    # =============================================================================
    # MÉTHODES UTILITAIRES
    # =============================================================================

    def gerer_sauvegardes(self):
        """Ouvre le gestionnaire de sauvegardes"""
        try:
            show_backup_manager(self.root, self.original_path)
        except Exception as e:
            log_message("ERREUR", "Erreur lors de l'ouverture du gestionnaire de sauvegardes", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'ouvrir le gestionnaire de sauvegardes:\n{str(e)}")

    def afficher_menu_aide(self):
        """Affiche le menu d'aide contextuel"""
        try:
            from ui.tutorial import show_help_menu
            show_help_menu()
            log_message("INFO", "Menu d'aide contextuel ouvert")
        except Exception as e:
            log_message("ERREUR", "Erreur menu d'aide", e)
            self.afficher_tutoriel()

    def afficher_nouveautes(self):
        """Affiche les nouveautés de la version"""
        try:
            from ui.tutorial import show_whats_new
            show_whats_new()
            log_message("INFO", "Nouveautés v2.5.0 affichées")
        except Exception as e:
            log_message("ERREUR", "Erreur affichage nouveautés", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'afficher les nouveautés:\n{str(e)}")

    def afficher_tutoriel(self):
        """Affiche le tutoriel complet (méthode de compatibilité)"""
        try:
            from ui.tutorial import show_tutorial
            show_tutorial()
            log_message("INFO", "Tutoriel complet affiché (accès direct)")
        except Exception as e:
            log_message("ERREUR", "Erreur affichage tutoriel", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'afficher le tutoriel:\n{str(e)}")

    def toggle_validation(self):
        """✅ MODIFIÉ : Toggle validation avec notification discrète"""
        try:
            new_state = config_manager.toggle_validation()
            
            # Mettre à jour le bouton
            status = "ON" if new_state else "OFF"
            self.bouton_validation.config(text=_('buttons.validation', status=status))
            
            # ✅ RÉDUCTION POPUP : Toast au lieu de popup
            message_key = 'messages.info.validation_enabled' if new_state else 'messages.info.validation_disabled'
            self.notifications.notify(_(message_key), 'TOAST')
            
            return new_state
            
        except Exception as e:
            log_message("ERREUR", "Erreur basculement validation", e)

    def handle_toggle_auto_open(self):
        """✅ MODIFIÉ : Toggle avec notification discrète"""
        try:
            new_value = config_manager.toggle_auto_open()
            
            # Mettre à jour le bouton
            status = "ON" if new_value else "OFF"
            self.bouton_auto_open.config(text=_('buttons.auto_open', status=status))
            
            # ✅ RÉDUCTION POPUP : Toast au lieu de popup
            message_key = 'messages.info.auto_open_enabled' if new_value else 'messages.info.auto_open_disabled'
            self.notifications.notify(_(message_key), 'TOAST')
            
            # Mettre à jour l'affichage si nécessaire
            if hasattr(self, 'text_mode') and self.text_mode == "empty":
                try:
                    self._update_drag_drop_display()
                except Exception as e:
                    print(f"⚠️ DEBUG - Erreur mise à jour affichage: {e}")
            
        except Exception as e:
            log_message("ERREUR", "Erreur basculement Auto-Open", e)

    def ouvrir_dossier_temporaire(self):
        """CORRIGÉ : Ouvre le dossier temporaire avec recherche automatique"""
        try:
            if not self.original_path:
                messagebox.showinfo(
                    "📁 Dossier temporaire",
                    "Aucun fichier n'est chargé.\n\n"
                    "Chargez d'abord un fichier pour accéder à son dossier temporaire."
                )
                return
            
            # ✅ CORRECTION : Utiliser la fonction d'extraction améliorée
            from utils.logging import extract_game_name
            game_name = extract_game_name(self.original_path)
            
            # ✅ CORRECTION : Si pas trouvé, chercher dans les dossiers existants
            if game_name == "Projet_Inconnu":
                from core.extraction import get_file_base_name
                file_base = get_file_base_name(self.original_path)
                
                # Chercher où sont réellement les fichiers
                from utils.constants import FOLDERS
                temp_root = FOLDERS["temp"]
                
                for folder in os.listdir(temp_root):
                    folder_path = os.path.join(temp_root, folder)
                    if os.path.isdir(folder_path):
                        translate_folder = os.path.join(folder_path, "fichiers_a_traduire")
                        if os.path.exists(translate_folder):
                            test_file = os.path.join(translate_folder, f"{file_base}.txt")
                            if os.path.exists(test_file):
                                game_name = folder
                                break
            
            # Construire le chemin complet
            from utils.constants import FOLDERS
            temp_base = FOLDERS["temp"]
            game_folder = os.path.join(temp_base, game_name)
            
            # Créer la structure si elle n'existe pas
            if not os.path.exists(game_folder):
                from utils.constants import ensure_game_structure
                ensure_game_structure(game_name)
            
            # Ouvrir le dossier
            self._open_folder(game_folder)
            
            log_message("INFO", f"Dossier temporaire ouvert: {game_name}")
            
        except Exception as e:
            log_message("ERREUR", f"Erreur ouverture dossier temporaire", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'ouvrir le dossier temporaire:\n{str(e)}")

    def ouvrir_avertissements(self):
        """CORRIGÉ : Ouvre le dossier avertissements avec recherche automatique"""
        from utils.constants import FOLDERS
        import glob
        
        try:
            # ✅ CORRECTION : Même système que pour temporaire
            if self.original_path:
                from utils.logging import extract_game_name
                game_name = extract_game_name(self.original_path)
                
                # Si pas trouvé, chercher dans les dossiers existants
                if game_name == "Projet_Inconnu":
                    warnings_root = FOLDERS["warnings"]
                    if os.path.exists(warnings_root):
                        for folder in os.listdir(warnings_root):
                            folder_path = os.path.join(warnings_root, folder)
                            if os.path.isdir(folder_path):
                                # Chercher des fichiers d'avertissement
                                warning_files = glob.glob(os.path.join(folder_path, "*_avertissement.txt"))
                                if warning_files:
                                    game_name = folder
                                    break
                
                warnings_folder = os.path.join(FOLDERS["warnings"], game_name)
                folder_title = f"avertissements/{game_name}"
            else:
                warnings_folder = FOLDERS["warnings"]
                folder_title = "avertissements"
            
            # Reste du code identique...
            if not os.path.exists(warnings_folder):
                messagebox.showinfo(
                    "📁 Dossier avertissements",
                    f"Le dossier '{folder_title}' n'existe pas encore.\n\n"
                    f"Il sera créé automatiquement lors de la première validation\n"
                    f"qui détecte des problèmes de cohérence."
                )
                return
            
            # Ouvrir le dossier
            self._open_folder(warnings_folder)
                    
        except Exception as e:
            log_message("ERREUR", f"Erreur ouverture dossier avertissements", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'accéder aux avertissements:\n{str(e)}")

    def _open_folder(self, folder_path):
        """Ouvre un dossier avec l'explorateur de fichiers"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', folder_path])
            else:  # Linux
                subprocess.call(['xdg-open', folder_path])
        except Exception as e:
            log_message("WARNING", f"Impossible d'ouvrir le dossier {folder_path}", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'ouvrir le dossier:\n{str(e)}")

    def _show_warning_files_list(self, warning_files, warnings_folder):
        """Affiche la liste des fichiers d'avertissement disponibles"""
        try:
            # Créer une fenêtre pour la liste
            list_window = tk.Toplevel(self.root)
            list_window.title("📄 Fichiers d'avertissement disponibles")
            list_window.geometry("600x400")
            
            # Centrer la fenêtre
            list_window.update_idletasks()
            x = (list_window.winfo_screenwidth() // 2) - (list_window.winfo_width() // 2)
            y = (list_window.winfo_screenheight() // 2) - (list_window.winfo_height() // 2)
            list_window.geometry(f"+{x}+{y}")
            
            # Appliquer le thème
            theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
            list_window.configure(bg=theme["bg"])
            
            # En-tête
            header_frame = tk.Frame(list_window, bg=theme["bg"])
            header_frame.pack(fill='x', padx=10, pady=10)
            
            title_label = tk.Label(
                header_frame,
                text=f"📄 {len(warning_files)} fichier(s) d'avertissement trouvé(s)",
                font=('Segoe UI Emoji', 14, 'bold'),
                bg=theme["bg"],
                fg=theme["fg"]
            )
            title_label.pack()
            
            # Liste
            list_frame = tk.Frame(list_window, bg=theme["bg"])
            list_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            # Listbox avec scrollbar
            listbox_frame = tk.Frame(list_frame, bg=theme["bg"])
            listbox_frame.pack(fill='both', expand=True)
            
            listbox = tk.Listbox(
                listbox_frame,
                font=('Segoe UI Emoji', 10),
                bg=theme["entry_bg"],
                fg=theme["entry_fg"],
                selectbackground=theme.get("select_bg", "#007acc"),
                selectforeground=theme.get("select_fg", "#ffffff")
            )
            
            scrollbar_list = tk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
            listbox.configure(yscrollcommand=scrollbar_list.set)
            
            listbox.pack(side="left", fill="both", expand=True)
            scrollbar_list.pack(side="right", fill="y")
            
            # Remplir la liste
            for warning_file in warning_files:
                file_name = os.path.basename(warning_file)
                # Enlever le suffixe _avertissement.txt pour plus de clarté
                display_name = file_name.replace("_avertissement.txt", "")
                listbox.insert(tk.END, display_name)
            
            # Sélectionner le premier par défaut
            if warning_files:
                listbox.selection_set(0)
            
            # Boutons
            button_frame = tk.Frame(list_window, bg=theme["bg"])
            button_frame.pack(fill='x', padx=10, pady=10)
            
            def open_selected():
                selection = listbox.curselection()
                if selection:
                    selected_file = warning_files[selection[0]]
                    FileOpener.open_files([selected_file], True)
                    list_window.destroy()
            
            def open_folder():
                self._open_folder(warnings_folder)
                list_window.destroy()
            
            btn_open_file = tk.Button(
                button_frame,
                text="📄 Ouvrir le fichier sélectionné",
                font=('Segoe UI Emoji', 10),
                bg=theme["accent"],
                fg="#000000",
                command=open_selected
            )
            btn_open_file.pack(side='left')
            
            btn_open_folder = tk.Button(
                button_frame,
                text="📁 Ouvrir le dossier",
                font=('Segoe UI Emoji', 10),
                command=open_folder
            )
            btn_open_folder.pack(side='left', padx=(10, 0))
            
            btn_close = tk.Button(
                button_frame,
                text="❌ Fermer",
                font=('Segoe UI Emoji', 10),
                bg=theme.get("danger", "#dc3545"),
                fg="#000000",
                command=list_window.destroy
            )
            btn_close.pack(side='right')
            
            # Double-clic pour ouvrir
            listbox.bind('<Double-Button-1>', lambda e: open_selected())
            
        except Exception as e:
            log_message("ERREUR", f"Erreur affichage liste avertissements", e)

    def _show_coherence_issues(self, issues):
        """Affiche les problèmes de cohérence dans une fenêtre non-bloquante"""
        try:
            # Créer une fenêtre pour afficher les problèmes
            issues_window = tk.Toplevel(self.root)
            issues_window.title("⚠️ Problèmes de cohérence détectés")
            issues_window.geometry("900x700")
            
            # Centrer la fenêtre
            issues_window.update_idletasks()
            x = (issues_window.winfo_screenwidth() // 2) - (issues_window.winfo_width() // 2)
            y = (issues_window.winfo_screenheight() // 2) - (issues_window.winfo_height() // 2)
            issues_window.geometry(f"+{x}+{y}")
            
            # Appliquer le thème
            theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
            issues_window.configure(bg=theme["bg"])
            
            # En-tête
            header_frame = tk.Frame(issues_window, bg=theme["bg"])
            header_frame.pack(fill='x', padx=10, pady=10)
            
            title_label = tk.Label(
                header_frame,
                text="⚠️ Problèmes de cohérence détectés",
                font=('Segoe UI Emoji', 16, 'bold'),
                bg=theme["bg"],
                fg=theme.get("danger", "#dc3545")
            )
            title_label.pack()
            
            count_label = tk.Label(
                header_frame,
                text=f"{len(issues)} problème(s) trouvé(s) dans la traduction",
                font=('Segoe UI Emoji', 12),
                bg=theme["bg"],
                fg=theme["fg"]
            )
            count_label.pack(pady=(5, 0))
            
            # Zone de texte avec scrollbar
            text_frame = tk.Frame(issues_window, bg=theme["bg"])
            text_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            text_area = ScrolledText(
                text_frame,
                font=('Courier New', 10),
                wrap=tk.WORD,
                bg=theme["entry_bg"],
                fg=theme["entry_fg"],
                selectbackground=theme.get("select_bg", "#007acc"),
                selectforeground=theme.get("select_fg", "#ffffff")
            )
            text_area.pack(fill='both', expand=True)
            
            # Formater et insérer les problèmes
            content = ""
            issues_by_type = {}
            for issue in issues:
                issue_type = issue['type']
                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = []
                issues_by_type[issue_type].append(issue)
            
            for issue_type, type_issues in issues_by_type.items():
                content += f"🔸 {self._get_issue_type_name(issue_type)}\n"
                content += "-" * 50 + "\n"
                
                for issue in type_issues:
                    content += f"Ligne {issue['line']}: {issue['description']}\n"
                    if issue.get('old_line'):
                        content += f"  OLD (ligne {issue['old_line']}): {issue.get('old_content', 'N/A')}\n"
                    if issue.get('new_content'):
                        content += f"  NEW: {issue['new_content']}\n"
                    content += "\n"
                
                content += "\n"
            
            text_area.insert('1.0', content)
            text_area.configure(state='disabled')  # Lecture seule
            
            # Boutons
            button_frame = tk.Frame(issues_window, bg=theme["bg"])
            button_frame.pack(fill='x', padx=10, pady=10)
            
            info_label = tk.Label(
                button_frame,
                text="💡 Ces problèmes peuvent causer des erreurs dans le jeu",
                font=('Segoe UI Emoji', 9),
                bg=theme["bg"],
                fg=theme["fg"]
            )
            info_label.pack(side='left')
            
            btn_close = tk.Button(
                button_frame,
                text="✅ Compris",
                font=('Segoe UI Emoji', 10),
                bg=theme["accent"],
                fg="#000000",
                command=issues_window.destroy
            )
            btn_close.pack(side='right')
            
        except Exception as e:
            log_message("ERREUR", f"Erreur affichage problèmes cohérence", e)

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

    def reinitialiser(self):
        """✅ NOUVEAU : Réinitialisation avec confirmation intelligente"""
        # ✅ CONFIRMATION ADAPTÉE : Avec ou sans données de session
        if self.last_extraction_time > 0 or self.last_reconstruction_time > 0:
            total_time = self.last_extraction_time + self.last_reconstruction_time
            
            # ✅ POPUP CRITIQUE : Réinitialisation avec données importantes
            confirm_msg = _('reset.confirm_with_data',
                        extraction_time=self.last_extraction_time,
                        reconstruction_time=self.last_reconstruction_time,
                        total_time=total_time)
            
            result = self.notifications.notify(confirm_msg, 'CONFIRM', title=_('reset.confirm_title'))
            if not result:
                return
        else:
            # ✅ TOAST SIMPLE : Pas de données importantes
            confirm_msg = _('reset.confirm_simple')
            result = self.notifications.notify(confirm_msg, 'CONFIRM', title=_('reset.confirm_title'))
            if not result:
                return
        
        try:
            # ✅ NETTOYAGE avec nouvelle structure
            if self.original_path:
                from utils.constants import FOLDERS
                
                game_name = extract_game_name(self.original_path)
                temp_base = FOLDERS["temp"]
                game_folder = os.path.join(temp_base, game_name)
                
                if os.path.exists(game_folder):
                    # Nettoyer le contenu du dossier du jeu
                    import shutil
                    try:
                        for item in os.listdir(game_folder):
                            item_path = os.path.join(game_folder, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                        
                        # Recréer la structure vide
                        from utils.constants import ensure_game_structure
                        ensure_game_structure(game_name)
                        
                        log_message("INFO", f"Dossier temporaire nettoyé pour {game_name}")
                    except Exception as e:
                        log_message("WARNING", f"Erreur lors du nettoyage du dossier temporaire", e)
            
            # Réinitialiser SEULEMENT la base de données
            file_manager.reset()  # Mode dossier, fichiers ouverts, etc.
            
            # Réinitialiser les variables de session
            self._save_mode = None
            self.extraction_results = None
            self.last_extraction_time = 0
            self.last_reconstruction_time = 0
            
            # Remettre le titre par défaut (enlever "Mode Dossier")
            self.root.title(_('window.title', version=VERSION))
            
            # Remettre les stats à "Prêt" mais garder le chemin du fichier
            if self.label_stats is not None:
                self.label_stats.config(text=f"📊 {_('status.ready')}")
            
            # ✅ TOAST DE CONFIRMATION : Succès discret
            success_msg = _('reset.success_message')
            self.notifications.notify(success_msg, 'TOAST', duration=4000)
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors de la réinitialisation", e)
            error_msg = _('reset.error_occurred', error=str(e))
            self.notifications.notify(error_msg, 'MODAL', title=_('reset.error_title'))

    def create_game_structure_on_demand(self, game_name):
        """Crée la structure pour un jeu spécifique à la demande"""
        try:
            from utils.constants import FOLDERS
            
            # Structure par jeu
            game_structure = [
                # Temporaires
                os.path.join(FOLDERS["temp"], game_name),
                os.path.join(FOLDERS["temp"], game_name, "fichiers_a_traduire"),
                os.path.join(FOLDERS["temp"], game_name, "fichiers_a_ne_pas_traduire"),
                
                # Sauvegardes
                os.path.join(FOLDERS["backup"], game_name),
                
                # Avertissements
                os.path.join(FOLDERS["warnings"], game_name)
            ]
            
            created_folders = []
            for folder in game_structure:
                if not os.path.exists(folder):
                    os.makedirs(folder, exist_ok=True)
                    created_folders.append(folder)
            
            if created_folders:
                print(f"✅ Structure créée pour '{game_name}':")
                print(f"📁 temporaires/{game_name}/")
                print(f"  ├── 📁 fichiers_a_traduire/")
                print(f"  ├── 📁 fichiers_a_ne_pas_traduire/")
                print(f"📁 sauvegardes/{game_name}/")
                print(f"📁 avertissements/{game_name}/")
            
            return True
        except Exception as e:
            print(f"❌ Erreur création structure jeu '{game_name}': {e}")
            return False

    def nettoyer_page(self):
        """✅ NOUVEAU : Nettoyage avec confirmation intelligente"""
        # ✅ CONFIRMATION ADAPTÉE : Avec ou sans données de session
        if self.last_extraction_time > 0 or self.last_reconstruction_time > 0:
            total_time = self.last_extraction_time + self.last_reconstruction_time
            
            # ✅ POPUP CRITIQUE : Nettoyage avec données importantes
            confirm_msg = _('clean.confirm_with_data',
                        extraction_time=self.last_extraction_time,
                        reconstruction_time=self.last_reconstruction_time,
                        total_time=total_time)
            
            result = self.notifications.notify(confirm_msg, 'CONFIRM', title=_('clean.confirm_title'))
            if not result:
                return
        else:
            # ✅ TOAST SIMPLE : Pas de données importantes  
            confirm_msg = _('clean.confirm_simple')
            result = self.notifications.notify(confirm_msg, 'CONFIRM', title=_('clean.confirm_title'))
            if not result:
                return
        
        try:
            # Nettoyer les données
            self.file_content = []
            self.original_path = None
            self.extraction_results = None
            
            # Réinitialiser le mode texte
            if hasattr(self, 'text_mode'):
                self.text_mode = "empty"
            if hasattr(self, 'source_info'):
                self.source_info = None
            
            # Nettoyer l'interface
            self.text_area.delete('1.0', tk.END)
            self.label_chemin.config(text=f"📄 {_('status.no_file')}")
            self.label_stats.config(text=f"📊 {_('status.ready')}")
            
            # Restaurer le message d'invitation Drag & Drop
            try:
                self._update_drag_drop_display()
                log_message("INFO", "Interface nettoyée et message Drag & Drop restauré")
            except Exception as e:
                log_message("WARNING", f"Erreur restauration message D&D: {e}")
            
            # ✅ TOAST DE CONFIRMATION : Succès discret
            success_msg = _('clean.success_message')
            self.notifications.notify(success_msg, 'TOAST', duration=3000)
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors du nettoyage", e)
            error_msg = _('clean.error_occurred', error=str(e))
            self.notifications.notify(error_msg, 'MODAL', title=_('clean.error_title'))

    def update_window_title(self, remaining_files=None):
        """Met à jour le titre de la fenêtre"""
        base_title = WINDOW_CONFIG["title"]
        
        if file_manager.is_folder_mode and remaining_files is not None:
            self.root.title(f"{base_title} - Mode Dossier ({remaining_files} fichiers restants)")
        else:
            self.root.title(base_title)

    def fermer_application(self):
        """Ferme proprement l'application"""
        try:
            # Nettoyer les références aux dialogues
            if hasattr(self, 'glossary_dialog') and self.glossary_dialog is not None:
                self.glossary_dialog._safe_destroy()
                self.glossary_dialog = None
            
            # Fermer la fenêtre principale de manière sécurisée
            if self.root is not None:
                try:
                    if self.root.winfo_exists():
                        self.root.quit()
                        self.root.destroy()
                except Exception:
                    pass
                self.root = None
            
            log_message("INFO", "Application fermée proprement")
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors de la fermeture", e)
        finally:
            # Forcer la sortie
            import sys
            sys.exit(0)

    def run(self):
        """Lance la boucle principale de l'application"""
        print("🌀 Lancement de mainloop()")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("🛑 Fermeture manuelle (Ctrl+C)")

    def test_compatibility(self):
        """Teste la compatibilité D&D + Ctrl+V"""
        print("\n🧪 TEST DE COMPATIBILITÉ")
        print("1. Essayez Drag & Drop d'un fichier .rpy")
        print("2. Puis Ctrl+V avec du contenu dans le presse-papier")
        print("3. Les deux doivent fonctionner sans conflit")
        print("4. Vérifiez que Ctrl+V fonctionne même avec le message d'invitation\n")

    def update_button_texts(self):
        """Met à jour dynamiquement les textes des boutons principaux selon la langue courante"""
        # Header
        self.bouton_quitter.config(text=_('buttons.quit'))
        self.bouton_language.config(text=_('buttons.language', lang=i18n.get_language_name()))
        theme_text = _('buttons.theme') if config_manager.is_dark_mode_enabled() else _('buttons.theme_dark')
        self.bouton_theme.config(text=theme_text)
        self.title_label.config(text=_('window.title', version=VERSION))
        self.subtitle_label.config(text=_('window.subtitle'))
        # Actions principales (si elles existent)
        if hasattr(self, 'bouton_input_mode') and self.bouton_input_mode:
            mode_text = "D&D" if getattr(self, 'input_mode', 'drag_drop') == "drag_drop" else "Ctrl+V"
            self.bouton_input_mode.config(text=_('buttons.input_mode', mode=mode_text))
        if hasattr(self, 'bouton_auto_open') and self.bouton_auto_open:
            status = "ON" if config_manager.is_auto_open_enabled() else "OFF"
            self.bouton_auto_open.config(text=_('buttons.auto_open', status=status))
        if hasattr(self, 'bouton_validation') and self.bouton_validation:
            status = "ON" if config_manager.is_validation_enabled() else "OFF"
            self.bouton_validation.config(text=_('buttons.validation', status=status))
        if hasattr(self, 'bouton_theme') and self.bouton_theme:
            theme_text = _('buttons.theme') if config_manager.is_dark_mode_enabled() else _('buttons.theme_dark')
            self.bouton_theme.config(text=theme_text)
        # Boutons d'ouverture (si existants)
        if hasattr(self, 'btn_fichier') and self.btn_fichier:
            self.btn_fichier.config(text=_('buttons.open_file'))
        if hasattr(self, 'btn_dossier') and self.btn_dossier:
            self.btn_dossier.config(text=_('buttons.open_folder'))
        if hasattr(self, 'btn_glossaire') and self.btn_glossaire:
            self.btn_glossaire.config(text=_('buttons.glossary'))
        if hasattr(self, 'btn_sauvegardes') and self.btn_sauvegardes:
            self.btn_sauvegardes.config(text=_('buttons.backups'))
        # ...ajouter ici d'autres boutons à traduire si besoin

# =============================================================================
# FONCTIONS UTILITAIRES GLOBALES
# =============================================================================

def get_current_game_name():
    """Récupère le nom du jeu actuellement chargé"""
    global app_instance
    if app_instance and app_instance.original_path:
        return extract_game_name(app_instance.original_path)
    return "Projet_Inconnu"

def main():
    """Fonction principale"""
    print("🎬 Lancement de main()")
    app = TraducteurRenPyPro()
    print("✅ Classe instanciée")
    app.run()

if __name__ == "__main__":
    try:
        print("🚀 Démarrage du RenExtract...")
        main()
    except Exception as e:
        print(f"❌ ERREUR au démarrage: {e}")
        import traceback
        print("🔍 Détails complets:")
        traceback.print_exc()
        input("Appuyez sur Entrée pour fermer...")