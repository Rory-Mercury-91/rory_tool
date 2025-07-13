# main.py
# Traducteur Ren'Py Pro - Interface principale
# Version 1.1.2 - Corrections finales des erreurs self

"""
Traducteur Ren'Py Pro
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

# Import Drag & Drop avec fallback
try:
    import tkinterdnd2 as dnd2
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# Imports des modules de l'application
from utils.constants import VERSION, THEMES, WINDOW_CONFIG, MESSAGES
from utils.config import config_manager
from utils.logging import log_message, log_temps_performance, envoyer_logs_erreurs, anonymize_path
from core.extraction import TextExtractor
from core.reconstruction import FileReconstructor
from core.validation import validate_before_extraction, create_safety_backup, validate_before_reconstruction
from core.file_manager import file_manager, FileOpener, TempFileManager
from core.coherence_checker import check_file_coherence
from ui.backup_manager import show_backup_manager
from ui.interface import SaveModeDialog
from core.extraction import get_file_base_name

# Imports du tutoriel (avec fallback de sécurité)
try:
    from ui.tutorial import show_tutorial, check_first_launch
except ImportError:
    def show_tutorial():
        messagebox.showinfo("Tutoriel", "Module tutoriel non disponible")
    def check_first_launch():
        return False

class TraducteurRenPyPro:
    """Classe principale de l'application"""
    
    def __init__(self):
        # CORRECTION : Nettoyer les fenêtres Tkinter existantes
        import tkinter as tk
        if tk._default_root:
            try:
                tk._default_root.withdraw()  # Masquer les fenêtres parasites
                tk._default_root.quit()
                tk._default_root.destroy()
            except:
                pass
    
        # NOUVEAU : Créer LA fenêtre principale avec support Drag & Drop
        try:
            import tkinterdnd2 as dnd2
            self.root = dnd2.Tk()  # Fenêtre avec support Drag & Drop
            self.dnd_available = True
            log_message("INFO", "Fenêtre créée avec support Drag & Drop")
        except ImportError:
            self.root = tk.Tk()  # Fenêtre normale si tkinterdnd2 pas disponible
            self.dnd_available = False
            log_message("INFO", "Fenêtre créée sans Drag & Drop (tkinterdnd2 non disponible)")
    
        # CORRECTION : Masquer pendant l'initialisation
        self.root.withdraw()
    
        self.setup_window()
    
        # État de l'application
        self.file_content = []
        self.original_path = None
        self.extraction_results = None
        self.last_extraction_time = 0
        self.last_reconstruction_time = 0
        self._save_mode = None
    
        # Widgets (initialisation à None)
        self.label_chemin = None
        self.label_stats = None
        self.text_area = None
        self.bouton_auto_open = None
        self.bouton_validation = None  # NOUVEAU : Référence bouton validation
        self.bouton_theme = None
        self.frame_info = None
        self.title_label = None
        self.subtitle_label = None
    
        # Créer l'interface
        self.create_interface()
        self.appliquer_theme()
        
        # NOUVEAU : Initialiser l'affichage Drag & Drop APRÈS que text_area existe
        if hasattr(self, 'text_area') and self.text_area:
            try:
                self._update_drag_drop_display()
                print("✅ DEBUG - Affichage initial Drag & Drop configuré")
            except Exception as e:
                print(f"⚠️ DEBUG - Erreur affichage initial D&D: {e}")
        
        # CORRECTION : Réafficher la fenêtre une fois prête
        self.root.deiconify()
        
        # Initialisation
        self.center_window()
        self.check_tutorial()
        print(f"DEBUG - file_content au démarrage: {hasattr(self, 'file_content')}")
        print(f"DEBUG - text_area au démarrage: {hasattr(self, 'text_area')}")
        
        log_message("INFO", f"=== DÉMARRAGE DU TRADUCTEUR REN'PY PRO v{VERSION} ===")
    
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
    
    def fermer_application(self):
        """Gestion de la fermeture propre de l'application"""
        try:
            log_message("INFO", f"=== FERMETURE DU TRADUCTEUR REN'PY PRO v{VERSION} ===")
            
            # Proposer l'envoi des logs d'erreurs s'il y en a eu
            try:
                envoyer_logs_erreurs()
            except:
                pass
            
            # Nettoyer les fichiers temporaires
            try:
                TempFileManager.cleanup_temp_files()
            except:
                pass
            
            self.root.destroy()
        except Exception as e:
            print(f"Erreur lors de la fermeture: {e}")
            self.root.destroy()
    
    # =============================================================================
    # MÉTHODES DE BASCULEMENT DE THÈME
    # =============================================================================
    
    def toggle_dark_mode(self):
        """Bascule entre mode sombre et clair avec recréation complète de l'interface"""
        new_mode = config_manager.toggle_dark_mode()
        
        # Sauvegarder l'état actuel
        current_file_content = self.file_content.copy() if self.file_content else []
        current_original_path = self.original_path
        current_extraction_results = self.extraction_results
        current_last_extraction_time = self.last_extraction_time
        current_last_reconstruction_time = self.last_reconstruction_time
        current_save_mode = self._save_mode
        
        # Détruire tous les widgets enfants
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Recréer complètement l'interface
        self.create_interface()
        
        # Restaurer l'état
        self.file_content = current_file_content
        self.original_path = current_original_path
        self.extraction_results = current_extraction_results
        self.last_extraction_time = current_last_extraction_time
        self.last_reconstruction_time = current_last_reconstruction_time
        self._save_mode = current_save_mode
        
        # Restaurer l'affichage si un fichier était chargé
        if self.original_path and self.file_content:
            self.label_chemin.config(text=f"📄 {self.original_path}")
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, ''.join(self.file_content))
            line_count = len(self.file_content)
            self.label_stats.config(text=f"📊 {line_count} lignes chargées")
        
        # Appliquer le nouveau thème
        self.appliquer_theme()
    
    def toggle_auto_open(self):
        """Bascule l'option d'ouverture automatique"""
        new_state = config_manager.toggle_auto_open()
        if self.bouton_auto_open:
            self.bouton_auto_open.config(text=f"📂 Auto : {'ON' if new_state else 'OFF'}")
    
    # =============================================================================
    # CRÉATION DE L'INTERFACE
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
    
    def create_header(self):
        """Crée l'en-tête de l'application"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        frame_header = tk.Frame(self.root, height=80, bg=theme["bg"])
        frame_header.pack(fill='x', padx=20, pady=(20, 10))
        frame_header.pack_propagate(False)
        
        # Titre principal
        self.title_label = tk.Label(
            frame_header, 
            text=f"🎮 Traducteur Ren'Py Pro v{VERSION}",
            font=('Segoe UI', 16, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.title_label.pack(side='left')
        
        # Sous-titre
        self.subtitle_label = tk.Label(
            frame_header, 
            text="Extraction et traduction intelligente de scripts",
            font=('Segoe UI', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.subtitle_label.pack(side='left', padx=(20, 0))
        
        # Bouton thème
        self.bouton_theme = tk.Button(
            frame_header, 
            text="☀️ Mode Clair" if config_manager.is_dark_mode_enabled() else "🌙 Mode Sombre",
            font=('Segoe UI', 10),
            bg='#ffc107',
            fg='#000000',
            activebackground='#e0a800',
            bd=1,
            relief='solid',
            pady=8,
            padx=10,
            command=self.toggle_dark_mode
        )
        self.bouton_theme.pack(side='right')
    
    def create_info_frame(self):
        """Crée le frame d'informations"""
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
            text="📄 Aucun fichier sélectionné", 
            font=('Segoe UI', 9, 'bold'),
            bg=theme["frame_bg"], 
            fg=theme["accent"]
        )
        self.label_chemin.pack(side='left')
        
        self.label_stats = tk.Label(
            self.frame_info, 
            text="📊 Prêt", 
            font=('Segoe UI', 10),
            bg=theme["frame_bg"], 
            fg=theme["fg"]
        )
        self.label_stats.pack(side='right')
    
    def create_open_frame(self):
        """Crée le frame des boutons d'ouverture"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        frame_open = tk.Frame(self.root, bg=theme["bg"], height=50)
        frame_open.pack(padx=20, pady=5)
        
        # 4 colonnes : 2 boutons bleus, 1 rouge sauvegardes, 1 rouge réinitialiser
        for col in range(4):
            frame_open.columnconfigure(col, weight=1, uniform="grp_open")
        
        # Bouton Ouvrir Fichier .rpy
        btn_fichier = tk.Button(
            frame_open,
            text="📂 Ouvrir Fichier .rpy",
            font=('Segoe UI', 11),
            bg='#007bff',
            fg='#000000',
            activebackground='#0056b3',
            bd=1,
            relief='solid',
            command=self.ouvrir_fichier_unique
        )
        btn_fichier.grid(row=0, column=0, sticky="nsew", padx=5, pady=8)
        
        # Bouton Ouvrir Dossier
        btn_dossier = tk.Button(
            frame_open,
            text="📁 Ouvrir Dossier",
            font=('Segoe UI', 11),
            bg='#007bff',
            fg='#000000',
            activebackground='#0056b3',
            bd=1,
            relief='solid',
            command=self.ouvrir_dossier
        )
        btn_dossier.grid(row=0, column=1, sticky="nsew", padx=5, pady=8)
        
        # NOUVEAU : Bouton Sauvegardes (rouge)
        btn_sauvegardes = tk.Button(
            frame_open,
            text="🛡️ Sauvegardes",
            font=('Segoe UI', 11),
            bg='#dc3545',
            fg='#000000',
            activebackground='#c82333',
            bd=1,
            relief='solid',
            command=self.gerer_sauvegardes
        )
        btn_sauvegardes.grid(row=0, column=2, sticky="nsew", padx=5, pady=8)
        
        # Bouton Réinitialiser (rouge)
        btn_reinit = tk.Button(
            frame_open,
            text="🔄 Réinitialiser",
            font=('Segoe UI', 10),
            bg='#dc3545',
            fg='#000000',
            activebackground='#c82333',
            bd=1,
            relief='solid',
            command=self.reinitialiser
        )
        btn_reinit.grid(row=0, column=3, sticky="nsew", padx=5, pady=8)
    
    def create_actions_frame(self):
        """Crée le frame des actions principales"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        frame_actions = tk.Frame(self.root, height=80, bg=theme["bg"])
        frame_actions.pack(padx=20, pady=5)
        
        # 8 colonnes : 2 boutons verts, 1 séparateur, 5 utilitaires (validation ajoutée)
        frame_actions.columnconfigure(0, weight=1, uniform="grp_act")
        frame_actions.columnconfigure(1, weight=1, uniform="grp_act")
        frame_actions.columnconfigure(2, weight=0)  # séparateur
        for col in range(3, 8):  # 5 boutons utilitaires
            frame_actions.columnconfigure(col, weight=1, uniform="grp_act")
        
        # Boutons verts (col 0, 1 & 2 maintenant)
        btn_extraire = tk.Button(
            frame_actions,
            text="⚡ Extraire",
            font=('Segoe UI', 11),
            bg='#28a745',
            fg='#000000',
            activebackground='#1e7e34',
            bd=1,
            relief='solid',
            command=self.extraire_textes
        )
        btn_extraire.grid(row=0, column=0, sticky="nsew", padx=5, pady=15)

        # NOUVEAU BOUTON
        btn_extract_todo = tk.Button(
            frame_actions,
            text="⚡ TODO",
            font=('Segoe UI', 11),
            bg='#ff8c00',  # Orange pour le distinguer
            fg='#000000',
            activebackground='#e07b00',
            bd=1,
            relief='solid',
            command=self.extraire_textes_avec_selector
        )
        btn_extract_todo.grid(row=0, column=1, sticky="nsew", padx=5, pady=15)

        btn_reconstruire = tk.Button(
            frame_actions,
            text="🔧 Reconstruire",
            font=('Segoe UI', 11),
            bg='#28a745',
            fg='#000000',
            activebackground='#1e7e34',
            bd=1,
            relief='solid',
            command=self.reconstruire_fichier
        )
        btn_reconstruire.grid(row=0, column=2, sticky="nsew", padx=5, pady=15)  # ← Maintenant colonne 2

        # Séparateur visuel (col 3 maintenant)
        separateur = tk.Frame(frame_actions, bg=theme["fg"], width=2)
        separateur.grid(row=0, column=3, sticky="ns", padx=10, pady=10)

        # Utilitaires (col 4 à 8 maintenant)
        # ... reste identique mais décaler les colonnes de +1
        
        # Utilitaires (col 3 à 7) - AVEC le bouton validation
        utilitaires = [
            ("🧹 Nettoyer",     self.nettoyer_page, '#ffc107'),
            ("⏱️ Temps",        self.ouvrir_log_temps, '#ffc107'),  # "Voir Temps" → "Temps"
            (
                f"📂 Auto: {'ON' if config_manager.is_auto_open_enabled() else 'OFF'}",  # "Auto-ouverture" → "Auto"
                self.toggle_auto_open, '#ffc107'
            ),
            (
                f"✅ Valid: {'ON' if config_manager.is_validation_enabled() else 'OFF'}",  # "Validation" → "Valid"
                self.toggle_validation, '#ffc107'
            ),
            ("🎓 Tutoriel",    lambda: show_tutorial(), '#ffc107')
        ]
        
        for idx, (txt, cmd, couleur) in enumerate(utilitaires, start=3):
            btn = tk.Button(
                frame_actions,
                text=txt,
                font=('Segoe UI', 10),
                bg=couleur,
                fg='#000000',
                activebackground='#e0a800',
                bd=1,
                relief='solid',
                command=cmd
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=5, pady=15)
            if cmd == self.toggle_auto_open:
                self.bouton_auto_open = btn
            elif cmd == self.toggle_validation:
                self.bouton_validation = btn
    
    def create_content_frame(self):
        """Crée la zone de contenu principal avec support Drag & Drop"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        frame_content = tk.Frame(self.root, bg=theme["bg"])
        frame_content.pack(expand=True, fill='both', padx=20, pady=(0, 10))
        
        # Frame pour la zone de texte
        text_frame = tk.Frame(frame_content, bg=theme["bg"])
        text_frame.pack(expand=True, fill='both')
        
        self.text_area = ScrolledText(
            text_frame,
            font=('Cascadia Code', 10),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=1,
            bg=theme["entry_bg"],
            fg=theme["entry_fg"],
            selectbackground=theme["select_bg"],
            selectforeground=theme["select_fg"],
            insertbackground=theme["entry_fg"]
        )
        self.text_area.pack(expand=True, fill='both')
        
        # Configuration du Drag & Drop
        try:
            self._setup_drag_drop()
        except Exception as e:
            log_message("WARNING", f"Drag & Drop non disponible: {str(e)}")
        
        # NOUVEAU : Affichage initial après création de text_area
        # Utiliser after() pour s'assurer que tout est bien initialisé
        self.root.after(100, self._initialize_text_area_display)

    def _initialize_text_area_display(self):
        """Initialise l'affichage de la zone de texte après création complète"""
        try:
            print("🔄 DEBUG - Initialisation affichage zone de texte")
            
            # Vérifier que text_area existe et est prête
            if not hasattr(self, 'text_area') or not self.text_area:
                print("⚠️ DEBUG - text_area pas encore créée")
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

    def appliquer_theme(self):
        """Applique le thème sombre ou clair"""
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        
        # Appliquer le thème à la fenêtre principale
        self.root.configure(bg=theme["bg"])
        
        # Mise à jour des couleurs des widgets principaux
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
                except:
                    pass
        
        # Appliquer au frame_info
        if self.frame_info:
            self.frame_info.configure(bg=theme["frame_bg"])
        
        # CORRECTION : Appliquer à la zone de texte avec bordure adaptative
        if self.text_area:
            if config_manager.is_dark_mode_enabled():
                # Mode sombre : bordure subtile
                border_color = '#555555'
            else:
                # Mode clair : bordure plus visible et adaptée aux nouvelles couleurs
                border_color = '#d0d0d0'  # ← CHANGEMENT ICI : Plus visible que #cccccc
            
            self.text_area.configure(
                bg=theme["entry_bg"],
                fg=theme["entry_fg"],
                selectbackground=theme["select_bg"],
                selectforeground=theme["select_fg"],
                insertbackground=theme["entry_fg"],
                highlightthickness=1,
                highlightbackground=border_color,
                highlightcolor=theme["accent"]  # Couleur verte quand focus
            )
        
        # Mettre à jour le bouton thème
        if self.bouton_theme:
            self.bouton_theme.configure(
                text="☀️ Mode Clair" if config_manager.is_dark_mode_enabled() else "🌙 Mode Sombre",
                bg='#ffc107',
                fg='#000000'
            )
        
        # Mettre à jour le bouton auto-ouverture
        if self.bouton_auto_open:
            self.bouton_auto_open.configure(
                text="📂 Auto : ON" if config_manager.is_auto_open_enabled() else "📂 Auto : OFF",
                bg='#ffc107',
                fg='#000000'
            )
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def check_tutorial(self):
        """Vérifie si le tutoriel doit être affiché"""
        if check_first_launch():
            log_message("INFO", "Premier lancement détecté - Affichage du tutoriel")
            self.root.after(500, show_tutorial)
    
    # =============================================================================
    # MÉTHODES D'ACTION
    # =============================================================================

    def _handle_dropped_file(self, filepath):
        """Gère un fichier déposé par Drag & Drop"""
        try:
            print(f"📁 DEBUG - Traitement fichier: '{filepath}'")
            
            # Vérifications basiques (existence, extension)
            if not os.path.exists(filepath):
                print(f"❌ DEBUG - Fichier n'existe pas: '{filepath}'")
                messagebox.showerror(
                    "❌ Fichier introuvable",
                    f"Le fichier n'existe pas :\n\n{filepath}"
                )
                return
            
            if not filepath.lower().endswith('.rpy'):
                print(f"❌ DEBUG - Pas un .rpy: '{filepath}'")
                messagebox.showerror(
                    "❌ Fichier non supporté",
                    f"Seuls les fichiers .rpy sont acceptés.\n\n"
                    f"Fichier: {os.path.basename(filepath)}"
                )
                return
            
            print(f"✅ DEBUG - Fichier valide confirmé: '{filepath}'")
            
            # Vérifier si un fichier est déjà chargé
            if self.file_content and self.file_content != []:
                result = messagebox.askyesno(
                    "🧹 Nettoyer avant ouverture",
                    f"Un fichier est déjà chargé.\n\n"
                    f"Voulez-vous nettoyer la session actuelle\n"
                    f"avant d'ouvrir :\n{os.path.basename(filepath)} ?"
                )
                if result:
                    print(f"🧹 DEBUG - Nettoyage demandé par l'utilisateur")
                    self.nettoyer_page()
                else:
                    print(f"❌ DEBUG - Ouverture annulée par l'utilisateur")
                    return
            
            # Charger le fichier via la méthode existante
            print(f"📂 DEBUG - Chargement via charger_fichier()...")
            self.charger_fichier(filepath)
            
            log_message("INFO", f"Fichier chargé par Drag & Drop: {anonymize_path(filepath)}")
            
            # Feedback utilisateur dans la barre de statut
            if hasattr(self, 'label_stats') and self.label_stats:
                self.label_stats.config(text=f"📂 Fichier chargé par D&D: {os.path.basename(filepath)}")
            
            print(f"🎉 DEBUG - Chargement et affichage terminés avec succès!")
            
        except Exception as e:
            print(f"💥 DEBUG - Erreur dans _handle_dropped_file: {str(e)}")
            log_message("ERREUR", f"Erreur traitement fichier D&D: {filepath}", e)
            messagebox.showerror(
                "❌ Erreur",
                f"Erreur lors du chargement du fichier :\n\n"
                f"Fichier: {os.path.basename(filepath)}\n"
                f"Erreur: {str(e)}"
            )

    def _clean_file_path(self, file_path):
        """Nettoie un chemin de fichier en préservant les caractères légitimes"""
        try:
            path = str(file_path).strip()
            
            # Supprimer SEULEMENT les préfixes URI
            if path.startswith('file:///'):
                path = path[8:]
            elif path.startswith('file://'):
                path = path[7:]
            
            # Supprimer SEULEMENT les caractères vraiment problématiques
            # GARDER: _ - ( ) [ ] qui sont légitimes dans les noms de fichiers
            chars_to_remove = ['"', "'", '{', '}', '\r', '\n', '\t']
            for char in chars_to_remove:
                path = path.replace(char, '')
            
            # Normaliser le chemin (convertit / en \ sur Windows)
            path = os.path.normpath(path)
            
            print(f"🧹 DEBUG - Nettoyage final: '{file_path}' → '{path}'")
            return path
            
        except Exception as e:
            print(f"💥 DEBUG - Erreur nettoyage: {e}")
            return str(file_path)

    def _is_valid_drag_file(self, event):
        """Vérifie si le fichier draggé est un .rpy valide"""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0].strip('{}').strip('"').strip("'")
                return file_path.lower().endswith('.rpy') and os.path.exists(file_path)
        except:
            pass
        return False

    def _setup_drag_drop(self):
        """Configure le support du Drag & Drop - Version unifiée et fonctionnelle"""
        if not DND_AVAILABLE:
            log_message("INFO", "Drag & Drop non disponible")
            self._setup_keyboard_shortcuts()
            return
        
        try:
            # Configurer la zone de texte comme drop target
            self.text_area.drop_target_register(dnd2.DND_FILES)
            
            def on_drop(event):
                try:
                    # Récupérer les données brutes
                    raw_data = event.data
                    print(f"🔍 DEBUG - Données brutes: '{raw_data}'")
                    
                    file_paths = []
                    
                    # Méthode 1 : Reconstruction intelligente pour chemins Windows
                    try:
                        split_parts = self.root.tk.splitlist(raw_data)
                        print(f"🔍 DEBUG - Parties divisées: {split_parts}")
                        
                        if len(split_parts) == 1:
                            # Pas de division
                            file_paths = split_parts
                            print(f"✅ DEBUG - Aucune division détectée")
                        else:
                            # STRATÉGIE SPÉCIALE pour les chemins Windows avec espaces
                            print(f"🔧 DEBUG - Reconstruction pour {len(split_parts)} parties")
                            
                            # Stratégie 1: Reconstruire avec espaces (le plus courant)
                            reconstructed_space = " ".join(split_parts)
                            print(f"🔧 DEBUG - Test avec espaces: '{reconstructed_space}'")
                            if os.path.exists(reconstructed_space):
                                file_paths = [reconstructed_space]
                                print(f"✅ DEBUG - Succès avec espaces!")
                            
                            # Stratégie 2: Si ça commence par C:\ ou D:\, reconstruction intelligente
                            if not file_paths:
                                import re
                                # Trouver la partie qui ressemble à un disque
                                drive_found = False
                                for i, part in enumerate(split_parts):
                                    if re.match(r'^[A-Z]:', part) or ':\\' in part:
                                        # Reconstruire à partir de ce point
                                        if ':\\' not in part:
                                            # Ajouter le :\ si manquant
                                            parts_to_join = [part + ':\\'] + split_parts[i+1:]
                                        else:
                                            parts_to_join = split_parts[i:]
                                        
                                        reconstructed = " ".join(parts_to_join)
                                        print(f"🔧 DEBUG - Reconstruction drive à partir de {i}: '{reconstructed}'")
                                        
                                        if os.path.exists(reconstructed):
                                            file_paths = [reconstructed]
                                            print(f"✅ DEBUG - Succès avec reconstruction drive!")
                                            drive_found = True
                                            break
                                
                                # Stratégie 3: Gestion spéciale pour C:\Users\
                                if not file_paths and not drive_found:
                                    # Détecter les patterns Users
                                    users_patterns = [
                                        'C:\\Users\\',
                                        'C:/Users/',
                                        'Users\\',
                                        'Users/'
                                    ]
                                    
                                    for pattern in users_patterns:
                                        joined = " ".join(split_parts)
                                        if pattern.lower() in joined.lower():
                                            print(f"🔧 DEBUG - Pattern Users détecté dans: '{joined}'")
                                            
                                            # Essayer de reconstruire le chemin Users
                                            if os.path.exists(joined):
                                                file_paths = [joined]
                                                print(f"✅ DEBUG - Succès avec pattern Users!")
                                                break
                            
                            # Stratégie 4: Autres séparateurs si les espaces ne marchent pas
                            if not file_paths:
                                separators = ['_', '-', '.', '\\']
                                for sep in separators:
                                    reconstructed = sep.join(split_parts)
                                    print(f"🔧 DEBUG - Test séparateur '{sep}': '{reconstructed}'")
                                    if os.path.exists(reconstructed):
                                        file_paths = [reconstructed]
                                        print(f"✅ DEBUG - Succès avec séparateur '{sep}'!")
                                        break
                    
                    except Exception as e:
                        print(f"⚠️ DEBUG - Erreur dans reconstruction: {e}")
                    
                    # Méthode 2: Regex pour détecter les chemins Windows complets
                    if not file_paths or not any(os.path.exists(p) for p in file_paths):
                        print(f"🔧 DEBUG - Tentative regex sur: '{raw_data}'")
                        
                        import re
                        # Patterns spécialement adaptés pour Windows
                        patterns = [
                            r'[A-Z]:\\Users\\[^<>:"|?*\n\r]*',           # C:\Users\...
                            r'[A-Z]:\\[^<>:"|?*\n\r]*\.rpy',             # Tout chemin vers .rpy
                            r'[A-Z]:\\[^<>:"|?*\n\r]*',                  # N'importe quel chemin Windows
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, raw_data, re.IGNORECASE)
                            if matches:
                                print(f"🔧 DEBUG - Regex trouvé avec '{pattern}': {matches}")
                                # Prendre le plus long match (probablement le plus complet)
                                longest_match = max(matches, key=len)
                                if os.path.exists(longest_match):
                                    file_paths = [longest_match]
                                    print(f"✅ DEBUG - Match regex valide!")
                                    break
                    
                    # Méthode 3: Fallback avec nettoyage avancé
                    if not file_paths:
                        cleaned = self._advanced_path_clean(raw_data)
                        print(f"🔧 DEBUG - Fallback nettoyage avancé: '{cleaned}'")
                        if os.path.exists(cleaned):
                            file_paths = [cleaned]
                            print(f"✅ DEBUG - Succès avec nettoyage avancé!")
                        else:
                            file_paths = [cleaned]  # On essaiera quand même
                    
                    # Traiter le meilleur chemin trouvé
                    for file_path in file_paths:
                        final_path = self._clean_file_path(file_path)
                        print(f"🧹 DEBUG - Chemin final: '{final_path}'")
                        
                        exists = os.path.exists(final_path)
                        is_rpy = final_path.lower().endswith('.rpy')
                        
                        print(f"🔍 DEBUG - Existe: {exists}, .rpy: {is_rpy}")
                        
                        if exists and is_rpy:
                            print(f"🎉 DEBUG - FICHIER VALIDE TROUVÉ!")
                            self._handle_dropped_file(final_path)
                            return dnd2.COPY
                        elif exists:
                            print(f"📁 DEBUG - Dossier valide, mais pas de fichier .rpy")
                            # Si c'est un dossier, on pourrait proposer de l'ouvrir
                            if os.path.isdir(final_path):
                                result = messagebox.askyesno(
                                    "📁 Dossier détecté",
                                    f"Vous avez glissé un dossier :\n{os.path.basename(final_path)}\n\n"
                                    f"Voulez-vous ouvrir ce dossier en mode dossier ?"
                                )
                                if result:
                                    # Simuler l'ouverture de dossier
                                    self.ouvrir_dossier_direct(final_path)
                                    return dnd2.COPY
                    
                    # Aucun fichier/dossier valide
                    messagebox.showerror(
                        "❌ Drag & Drop impossible",
                        f"Impossible de traiter l'élément glissé.\n\n"
                        f"Données reçues: {raw_data[:100]}{'...' if len(raw_data) > 100 else ''}\n\n"
                        f"💡 Problème probable:\n"
                        f"• Nom d'utilisateur Windows avec espaces\n"
                        f"• Chemin trop complexe pour tkinterdnd2\n\n"
                        f"🔧 Solutions:\n"
                        f"• Utilisez le bouton 'Ouvrir Fichier'\n"
                        f"• Ou copiez le fichier dans un dossier plus simple"
                    )
                    
                    return dnd2.COPY
                    
                except Exception as e:
                    print(f"💥 DEBUG - Erreur critique: {str(e)}")
                    log_message("ERREUR", f"Erreur Drag & Drop: {str(e)}", e)
                    return dnd2.COPY
            
            def on_drag_enter(event):
                theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
                self.text_area.configure(highlightbackground='#28a745', highlightthickness=3)
                return dnd2.COPY
            
            def on_drag_leave(event):
                theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
                border_color = '#555555' if config_manager.is_dark_mode_enabled() else '#d0d0d0'
                self.text_area.configure(highlightbackground=border_color, highlightthickness=1)
            
            self.text_area.dnd_bind('<<Drop>>', on_drop)
            self.text_area.dnd_bind('<<DragEnter>>', on_drag_enter)
            self.text_area.dnd_bind('<<DragLeave>>', on_drag_leave)
            
            log_message("INFO", "Drag & Drop configuré pour chemins utilisateur Windows")
            
        except Exception as e:
            log_message("WARNING", f"Erreur configuration Drag & Drop: {str(e)}")
            self._setup_keyboard_shortcuts()

    def _setup_keyboard_shortcuts(self):
        """Configure des raccourcis clavier en complément ou alternative au Drag & Drop"""
        try:
            # Raccourcis utiles même avec Drag & Drop
            self.root.bind('<Control-o>', lambda e: self.ouvrir_fichier_unique())
            self.root.bind('<Control-O>', lambda e: self.ouvrir_fichier_unique())
            self.root.bind('<Control-d>', lambda e: self.ouvrir_dossier())
            self.root.bind('<Control-D>', lambda e: self.ouvrir_dossier())
            
            # Clic sur zone vide si pas de Drag & Drop
            if not DND_AVAILABLE:
                self.text_area.bind('<Button-1>', self._on_text_click)
            
            log_message("INFO", "Raccourcis clavier configurés: Ctrl+O (fichier), Ctrl+D (dossier)")
            
        except Exception as e:
            log_message("WARNING", f"Configuration des raccourcis échouée: {str(e)}")

    def _on_text_click(self, event):
        """Gère les clics sur la zone de texte (si vide, propose d'ouvrir un fichier)"""
        # Si aucun fichier n'est chargé, proposer d'en ouvrir un
        if not self.file_content or self.file_content == []:
            # Mais seulement si le clic est dans la zone centrale
            try:
                # Vérifier que la zone de texte est vide (contient juste le message d'invitation)
                content = self.text_area.get('1.0', tk.END).strip()
                if "Glissez un fichier .rpy ici" in content or "Cliquez ici" in content or not content:
                    result = messagebox.askyesno(
                        "📂 Ouvrir un fichier",
                        "Aucun fichier n'est chargé.\n\n"
                        "Voulez-vous ouvrir un fichier .rpy ?\n\n"
                        "💡 Astuce: Vous pouvez aussi utiliser Ctrl+O"
                    )
                    if result:
                        self.ouvrir_fichier_unique()
            except:
                pass  # Si erreur, ne rien faire

    def ouvrir_dossier_direct(self, folder_path):
        """Ouvre un dossier directement (pour le drag & drop de dossiers)"""
        try:
            print(f"📁 DEBUG - Ouverture dossier direct: '{folder_path}'")
            
            # Utiliser le file_manager existant
            from core.file_manager import file_manager
            import glob
            
            # Chercher les fichiers .rpy dans ce dossier
            rpy_files = glob.glob(os.path.join(folder_path, "*.rpy"))
            
            if not rpy_files:
                messagebox.showwarning(
                    "⚠️ Aucun fichier .rpy",
                    f"Aucun fichier .rpy trouvé dans :\n{os.path.basename(folder_path)}"
                )
                return
            
            # Nettoyer si nécessaire
            if self.file_content and self.file_content != []:
                result = messagebox.askyesno(
                    "🧹 Nettoyer avant ouverture",
                    f"Un fichier est déjà chargé.\n\n"
                    f"Voulez-vous nettoyer avant d'ouvrir le dossier :\n{os.path.basename(folder_path)} ?"
                )
                if result:
                    self.nettoyer_page()
                else:
                    return
            
            # Configurer le mode dossier
            file_manager.selected_folder_path = folder_path
            file_manager.is_folder_mode = True
            file_manager.opened_files.clear()
            
            # Charger le premier fichier
            first_file = rpy_files[0]
            file_manager.opened_files.add(first_file)
            
            # Charger dans l'interface
            self.charger_fichier(first_file)
            
            log_message("INFO", f"Mode dossier activé par Drag & Drop: {len(rpy_files)} fichiers dans {anonymize_path(folder_path)}")
            
            # Feedback utilisateur
            if hasattr(self, 'label_stats') and self.label_stats:
                self.label_stats.config(text=f"📁 Mode dossier: {len(rpy_files)} fichiers trouvés")
            
            messagebox.showinfo(
                "📁 Dossier ouvert",
                f"Mode dossier activé :\n\n"
                f"📁 Dossier: {os.path.basename(folder_path)}\n"
                f"📄 Fichiers .rpy: {len(rpy_files)}\n"
                f"🎯 Premier fichier: {os.path.basename(first_file)}"
            )
            
            print(f"🎉 DEBUG - Mode dossier activé avec succès!")
            
        except Exception as e:
            print(f"💥 DEBUG - Erreur ouverture dossier direct: {str(e)}")
            log_message("ERREUR", f"Erreur ouverture dossier par Drag & Drop: {folder_path}", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'ouvrir le dossier:\n{str(e)}")

    def _advanced_path_clean(self, raw_path):
        """Nettoyage avancé spécialement pour les chemins Windows complexes"""
        try:
            path = str(raw_path).strip()
            
            # Supprimer les préfixes URI
            prefixes = ['file:///', 'file://', 'file:']
            for prefix in prefixes:
                if path.startswith(prefix):
                    path = path[len(prefix):]
                    break
            
            # Décoder les URL encoding si présent (%20 = espace, etc.)
            import urllib.parse
            try:
                path = urllib.parse.unquote(path)
            except:
                pass
            
            # Supprimer seulement les caractères vraiment problématiques
            chars_to_remove = ['"', "'", '{', '}', '\r', '\n', '\t']
            for char in chars_to_remove:
                path = path.replace(char, '')
            
            # Normaliser les séparateurs
            path = path.replace('/', '\\')  # Windows utilise \
            path = os.path.normpath(path)
            
            print(f"🧹 DEBUG - Nettoyage avancé: '{raw_path}' → '{path}'")
            return path
            
        except Exception as e:
            print(f"💥 DEBUG - Erreur nettoyage avancé: {e}")
            return str(raw_path)

    def _update_drag_drop_display(self):
        """Met à jour l'affichage selon l'état du fichier chargé"""
        try:
            # Vérifier que text_area existe
            if not hasattr(self, 'text_area') or not self.text_area:
                print("⚠️ DEBUG - text_area n'existe pas encore")
                return
            
            print(f"🔍 DEBUG - file_content: {len(self.file_content) if self.file_content else 0} éléments")
            print(f"🔍 DEBUG - État actuel text_area: {self.text_area.cget('state')}")
            
            if not self.file_content or self.file_content == []:
                # Aucun fichier chargé - Afficher l'invitation
                print(f"🔄 DEBUG - Affichage invitation Drag & Drop")
                
                # Activer temporairement pour pouvoir modifier
                self.text_area.configure(state='normal')
                
                # Effacer le contenu actuel
                self.text_area.delete('1.0', tk.END)
                
                # Message d'invitation selon disponibilité D&D
                if DND_AVAILABLE:
                    invitation_text = """



                    🎯 Glissez un fichier .rpy ici

                    ou utilisez Ctrl+O / boutons ci-dessus
                        pour commencer la traduction



    """
                else:
                    invitation_text = """



                    🎯 Cliquez ici ou utilisez Ctrl+O

                        pour ouvrir un fichier .rpy
                        et commencer la traduction



    """
                
                # Insérer le message
                self.text_area.insert(tk.END, invitation_text)
                
                # Désactiver l'édition pour le message d'invitation
                self.text_area.configure(state='disabled')
                print(f"✅ DEBUG - Message d'invitation affiché et zone désactivée")
                
            else:
                # Fichier chargé - S'assurer que l'édition est activée
                print(f"🔄 DEBUG - Fichier chargé - Activation de l'édition")
                
                # Réactiver l'édition
                self.text_area.configure(state='normal')
                print(f"✅ DEBUG - Zone de texte réactivée pour édition")
                
                # NOTE: Le contenu a déjà été chargé par charger_fichier()
                # On ne fait que s'assurer que l'édition est possible
            
            print(f"✅ DEBUG - Mise à jour affichage terminée - État final: {self.text_area.cget('state')}")
            
        except Exception as e:
            print(f"💥 DEBUG - Erreur dans _update_drag_drop_display: {str(e)}")
            log_message("WARNING", f"Erreur mise à jour affichage Drag & Drop", e)

    # Nouvelles méthodes pour les boutons
    def gerer_sauvegardes(self):
        """Ouvre le gestionnaire de sauvegardes"""
        try:
            show_backup_manager(self.root, self.original_path)
        except Exception as e:
            log_message("ERREUR", "Erreur lors de l'ouverture du gestionnaire de sauvegardes", e)
            messagebox.showerror("❌ Erreur", f"Impossible d'ouvrir le gestionnaire de sauvegardes:\n{str(e)}")

    def toggle_validation(self):
        """Bascule le mode de validation"""
        new_state = config_manager.toggle_validation()
        
        # Mettre à jour le bouton
        if self.bouton_validation:
            self.bouton_validation.configure(
                text=f"✅ Valid : {'ON' if new_state else 'OFF'}"
            )
        
        status = "activée" if new_state else "désactivée"
        log_message("INFO", f"Validation {status}")
        
        return new_state

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
            
            self.label_chemin.config(text=f"📄 {filepath}")
            
            # IMPORTANT : Réactiver l'édition AVANT d'insérer le contenu
            self.text_area.configure(state='normal')
            
            # Vider et insérer le nouveau contenu
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, ''.join(self.file_content))
            
            line_count = len(self.file_content)
            self.label_stats.config(text=f"📊 {line_count} lignes chargées")
            
            # NOUVEAU : Mettre à jour l'affichage pour sortir du mode "invitation"
            try:
                self._update_drag_drop_display()
                print("✅ DEBUG - Affichage mis à jour après chargement")
            except Exception as e:
                print(f"⚠️ DEBUG - Erreur mise à jour affichage: {e}")
            
            log_message("INFO", f"Fichier chargé: {line_count} lignes")
            
        except Exception as e:
            log_message("ERREUR", f"Impossible de charger le fichier {filepath}", e)
            messagebox.showerror("❌ Erreur", f"Impossible de charger le fichier:\n{str(e)}")

    def extraire_textes_avec_selector(self):
        """Extrait les textes avec sélecteur de date TODO"""
        if not self.file_content:
            messagebox.showwarning("⚠️ Erreur", "Chargez d'abord un fichier .rpy")
            return
        
        try:
            # Afficher le sélecteur de TODO
            selector = TodoSelectorDialog(self.root, self.file_content)
            selection = selector.show()
            
            if selection is None:
                return  # Annulé par l'utilisateur
            
            # Animation de progression
            self.label_stats.config(text="⚙️ Extraction en cours...")
            self.root.update()
            
            # Créer une sauvegarde de sécurité
            if self.original_path:
                backup_result = create_safety_backup(self.original_path)
                if not backup_result['success']:
                    log_message("WARNING", f"Impossible de créer la sauvegarde: {backup_result['error']}")
            
            # Extraction avec filtre
            extractor = TextExtractor()
            
            if selection == "all":
                # Extraction complète
                extractor.load_file_content(self.file_content, self.original_path)
                mode_message = "Extraction complète"
            else:
                # Extraction depuis une date TODO (pour l'instant, extraction complète)
                extractor.load_file_content(self.file_content, self.original_path)
                mode_message = f"Extraction depuis le {selection['date'].strftime('%d/%m/%Y')}"
            
            self.extraction_results = extractor.extract_texts()
            self.last_extraction_time = extractor.extraction_time
            self.last_extractor = extractor
            
            # Ajouter les compteurs dans extraction_results
            self.extraction_results['extracted_count'] = extractor.extracted_count
            self.extraction_results['asterix_count'] = extractor.asterix_count
            self.extraction_results['empty_count'] = extractor.empty_count
            
            # Ouvrir les fichiers si demandé
            files_to_open = [self.extraction_results['main_file']]
            if self.extraction_results['asterix_file']:
                files_to_open.append(self.extraction_results['asterix_file'])
            if self.extraction_results['empty_file']:
                files_to_open.append(self.extraction_results['empty_file'])
            
            FileOpener.open_files(files_to_open, config_manager.is_auto_open_enabled())
            
            # Message de succès avec info sur le mode
            message = f"✅ {mode_message} terminée en {self.last_extraction_time:.2f}s !"
            message += f"\n\n📝 {extractor.extracted_count} textes extraits dans {self.extraction_results['main_file']}"
            
            if extractor.asterix_count > 0:
                message += f"\n⭐ {extractor.asterix_count} expressions entre astérisques dans {self.extraction_results['asterix_file']}"
            
            if extractor.empty_count > 0:
                message += f"\n🔳 {extractor.empty_count} textes vides/espaces dans {self.extraction_results['empty_file']}"
            
            self.label_stats.config(text=f"📊 {extractor.extracted_count} textes extraits | ⏱️ {self.last_extraction_time:.2f}s")
            messagebox.showinfo("🎉 Extraction terminée", message)
            
        except Exception as e:
            log_message("ERREUR", "Erreur critique pendant l'extraction avec sélecteur", e)
            messagebox.showerror("❌ Erreur", f"Erreur pendant l'extraction:\n{str(e)}")
            self.label_stats.config(text="❌ Erreur lors de l'extraction")

    def extraire_textes(self):
        """Extrait les textes du fichier chargé"""
        if not self.file_content:
            messagebox.showwarning("⚠️ Erreur", "Chargez d'abord un fichier .rpy")
            return
        
        try:
            # Animation de progression
            self.label_stats.config(text="⚙️ Extraction en cours...")
            self.root.update()
            
            # Créer une sauvegarde de sécurité
            if self.original_path:
                backup_result = create_safety_backup(self.original_path)
                if not backup_result['success']:
                    log_message("WARNING", f"Impossible de créer la sauvegarde: {backup_result['error']}")
            
            # Extraction
            extractor = TextExtractor()
            extractor.load_file_content(self.file_content, self.original_path)
            self.extraction_results = extractor.extract_texts()
            self.last_extraction_time = extractor.extraction_time
            
            # CORRECTION : Sauvegarder l'extracteur et les compteurs
            self.last_extractor = extractor
            
            # Ajouter les compteurs dans extraction_results
            self.extraction_results['extracted_count'] = extractor.extracted_count
            self.extraction_results['asterix_count'] = extractor.asterix_count
            self.extraction_results['empty_count'] = extractor.empty_count
            
            # Ouvrir les fichiers si demandé
            files_to_open = [self.extraction_results['main_file']]
            if self.extraction_results['asterix_file']:
                files_to_open.append(self.extraction_results['asterix_file'])
            if self.extraction_results['empty_file']:
                files_to_open.append(self.extraction_results['empty_file'])
            
            FileOpener.open_files(files_to_open, config_manager.is_auto_open_enabled())
            
            # Message de succès
            message = f"✅ Extraction terminée en {self.last_extraction_time:.2f}s !"
            message += f"\n\n📝 {extractor.extracted_count} textes extraits dans {self.extraction_results['main_file']}"
            
            if extractor.asterix_count > 0:
                message += f"\n⭐ {extractor.asterix_count} expressions entre astérisques extraites dans {self.extraction_results['asterix_file']}"
            
            if extractor.empty_count > 0:
                message += f"\n🔳 {extractor.empty_count} textes vides/espaces protégés dans {self.extraction_results['empty_file']}"
            
            self.label_stats.config(text=f"📊 {extractor.extracted_count} textes extraits | ⏱️ {self.last_extraction_time:.2f}s")
            messagebox.showinfo("🎉 Extraction terminée", message)
            
        except Exception as e:
            log_message("ERREUR", "Erreur critique pendant l'extraction", e)
            messagebox.showerror("❌ Erreur", f"Erreur pendant l'extraction:\n{str(e)}")
    
    def reconstruire_fichier(self):
        """Reconstruit le fichier avec les traductions"""
        if not self.file_content or not self.original_path:
            messagebox.showerror("❌ Erreur", MESSAGES["no_file_loaded"])
            return
        
        try:
            # ... code de validation existant ...
            
            # Demander le mode de sauvegarde
            if not self._save_mode:
                save_dialog = SaveModeDialog(self.root)
                self._save_mode = save_dialog.show()
                
                if not self._save_mode:
                    return
            
            # Reconstruction
            from core.reconstruction import reconstruire_fichier as reconstruct_func
            
            self.label_stats.config(text="🔧 Reconstruction en cours...")
            self.root.update()
            
            start_time = time.time()
            result = reconstruct_func(self.file_content, self.original_path, self._save_mode)
            reconstruction_time = time.time() - start_time
            
            if result:
                # NOUVEAU : Contrôle de cohérence si validation activée
                if config_manager.is_validation_enabled():
                    coherence_result = check_file_coherence(result['save_path'])
                    
                    if coherence_result['issues_found'] > 0:
                        messagebox.showwarning(
                            "⚠️ Problèmes de cohérence détectés",
                            f"{coherence_result['issues_found']} problème(s) détecté(s) dans la traduction.\n\n"
                            f"Un fichier d'avertissement a été créé :\n{coherence_result.get('warning_file', 'avertissement.txt')}\n\n"
                            f"Voulez-vous consulter les détails ?"
                        )
                        
                        if coherence_result.get('warning_file'):
                            try:
                                import subprocess
                                subprocess.run(['notepad.exe', coherence_result['warning_file']], check=False)
                            except:
                                pass
                
                # Messages de succès habituels...
                success_msg = MESSAGES["reconstruction_success"].format(time=reconstruction_time)
                self.label_stats.config(text=success_msg)
                
                # ... reste du code existant ...
            
        except Exception as e:
            log_message("ERREUR", "Erreur lors de la reconstruction", e)
            messagebox.showerror("❌ Erreur", f"Erreur lors de la reconstruction:\n{str(e)}")
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
                font=('Segoe UI', 14, 'bold'), bg=theme["bg"], fg=theme["fg"])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Ce choix sera mémorisé pour cette session",
                font=('Segoe UI', 9), bg=theme["bg"], fg=theme["fg"])
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
                 font=('Segoe UI', 11, 'bold'), bg=theme["warning"], fg='#000000',
                 bd=0, pady=15, command=lambda: choisir_mode('overwrite'))
        btn_overwrite.pack(fill='x', padx=10, pady=10)
        
        label_overwrite = tk.Label(option1_frame, text="⚠️ Le fichier original sera remplacé par la traduction",
                font=('Segoe UI', 9), bg=theme["frame_bg"], fg=theme["fg"])
        label_overwrite.pack(pady=(0, 10))
        
        # Option 2: Créer nouveau fichier
        option2_frame = tk.Frame(options_frame, bg=theme["frame_bg"], relief='solid', bd=1)
        option2_frame.pack(fill='x', pady=10)
        
        btn_new_file = tk.Button(option2_frame, text="📝 Créer un nouveau fichier",
                 font=('Segoe UI', 11, 'bold'), bg=theme["accent"], fg='#000000',
                 bd=0, pady=15, command=lambda: choisir_mode('new_file'))
        btn_new_file.pack(fill='x', padx=10, pady=10)
        
        label_new_file = tk.Label(option2_frame, text="✅ Garde l'original et crée un fichier traduit séparé\n💡 L'original sera automatiquement commenté",
                font=('Segoe UI', 9), bg=theme["frame_bg"], fg=theme["fg"], justify='left')
        label_new_file.pack(pady=(0, 10))
        
        # Bouton annuler
        btn_cancel = tk.Button(dialog, text="❌ Annuler", font=('Segoe UI', 10),
                 bg=theme["danger"], fg='#000000', bd=0, pady=8,
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
    
    def reinitialiser(self):
        """Réinitialise la base de données des fichiers UNIQUEMENT"""
        if self.last_extraction_time > 0 or self.last_reconstruction_time > 0:
            total_time = self.last_extraction_time + self.last_reconstruction_time
            result = messagebox.askyesno(
                "🔄 Confirmer la réinitialisation",
                f"Voulez-vous vraiment réinitialiser la base de données ?\n\n⏱️ Temps de la dernière session :\n"
                f"• Extraction: {self.last_extraction_time:.2f}s\n"
                f"• Reconstruction: {self.last_reconstruction_time:.2f}s\n"
                f"• Total: {total_time:.2f}s\n\n"
                f"🔄 Cette action va réinitialiser :\n"
                f"• Mode dossier et fichiers ouverts\n"
                f"• Mode de sauvegarde mémorisé\n"
                f"• Temps d'extraction/reconstruction\n\n"
                f"📄 Le fichier actuellement affiché sera CONSERVÉ."
            )
            if not result:
                return
        
        # Réinitialiser SEULEMENT la base de données
        file_manager.reset()  # Mode dossier, fichiers ouverts, etc.
        
        # Réinitialiser les variables de session
        self._save_mode = None
        self.extraction_results = None
        self.last_extraction_time = 0
        self.last_reconstruction_time = 0
        
        # CONSERVER le fichier actuel : NE PAS toucher à file_content et original_path
        # self.file_content = []  ← SUPPRIMÉ
        # self.original_path = None  ← SUPPRIMÉ
        
        # Remettre le titre par défaut (enlever "Mode Dossier")
        self.root.title(WINDOW_CONFIG["title"])
        
        # Remettre les stats à "Prêt" mais garder le chemin du fichier
        self.label_stats.config(text="📊 Prêt")
        
        # PAS de _update_drag_drop_display() car on garde le fichier !
        
        messagebox.showinfo(
            "🔄 Réinitialisation", 
            "Base de données nettoyée :\n\n"
            "✅ Mode dossier réinitialisé\n"
            "✅ Mode de sauvegarde oublié\n"
            "✅ Temps de session remis à zéro\n\n"
            "📄 Le fichier actuel reste chargé."
        )
    
    def nettoyer_page(self):
        """Nettoie la page actuelle"""
        if self.last_extraction_time > 0 or self.last_reconstruction_time > 0:
            total_time = self.last_extraction_time + self.last_reconstruction_time
            result = messagebox.askyesno(
                "🧹 Confirmer le nettoyage",
                f"Voulez-vous vraiment nettoyer ?\n\n⏱️ Temps de la dernière session :\n"
                f"• Extraction: {self.last_extraction_time:.2f}s\n"
                f"• Reconstruction: {self.last_reconstruction_time:.2f}s\n"
                f"• Total: {total_time:.2f}s\n\n"
                f"Ces informations seront perdues."
            )
            if not result:
                return
        
        # Nettoyer les données
        self.file_content = []
        self.original_path = None
        
        # Nettoyer l'interface
        self.text_area.delete('1.0', tk.END)
        self.label_chemin.config(text="📄 Aucun fichier sélectionné")
        self.label_stats.config(text="📊 Prêt")
        
        # NOUVEAU : Restaurer le message d'invitation Drag & Drop
        try:
            self._update_drag_drop_display()
            print("✅ DEBUG - Message Drag & Drop restauré après nettoyage")
        except Exception as e:
            print(f"⚠️ DEBUG - Erreur restauration message D&D: {e}")
        
        messagebox.showinfo("🧹 Nettoyage", "Page nettoyée.")
    
    def ouvrir_log_temps(self):
        """Ouvre le fichier temps.txt s'il existe"""
        if os.path.exists('temps.txt'):
            try:
                FileOpener.open_files(['temps.txt'])
            except Exception as e:
                messagebox.showerror("❌ Erreur", f"Impossible d'ouvrir temps.txt:\n{str(e)}")
        else:
            messagebox.showinfo("📊 Log des temps", "Aucun fichier temps.txt trouvé.\nTraitez d'abord un fichier pour générer l'historique.")
    
    def update_window_title(self, remaining_files=None):
        """Met à jour le titre de la fenêtre"""
        base_title = WINDOW_CONFIG["title"]
        
        if file_manager.is_folder_mode and remaining_files is not None:
            self.root.title(f"{base_title} - Mode Dossier ({remaining_files} fichiers restants)")
        else:
            self.root.title(base_title)
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

class TodoSelectorDialog:
    """Dialogue pour sélectionner à partir de quelle date TODO extraire"""
    
    def __init__(self, parent, file_content):
        self.parent = parent
        self.file_content = file_content
        self.result = None
        self.dialog = None
        self.todo_dates = []
    
    def show(self):
        """Affiche le dialogue et retourne la date sélectionnée"""
        # D'abord analyser les TODO
        self._analyze_todo_dates()
        
        if not self.todo_dates:
            messagebox.showinfo(
                "ℹ️ Aucun TODO trouvé",
                "Aucune ligne TODO avec date trouvée dans ce fichier.\n\n"
                "L'extraction complète sera effectuée."
            )
            return None
        
        # Créer le dialogue
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("📅 Sélectionner la date TODO")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Thème
        from utils.config import config_manager
        from utils.constants import THEMES
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        self.dialog.configure(bg=theme["bg"])
        
        self._create_content(theme)
        
        # Attendre la réponse
        self.dialog.wait_window()
        return self.result
    
    def _analyze_todo_dates(self):
        """Analyse le fichier pour trouver toutes les dates TODO"""
        self.todo_dates = []
        
        for i, line in enumerate(self.file_content):
            stripped = line.strip()
            
            # Détecter les lignes TODO avec date
            if stripped.startswith('# TODO:') and 'Translation updated at' in stripped:
                todo_date = self._extract_todo_date(stripped)
                
                if todo_date:
                    # Compter les lignes de traduction dans cette section
                    line_count = self._count_lines_in_section(i)
                    
                    self.todo_dates.append({
                        'date': todo_date,
                        'line_number': i + 1,
                        'raw_line': stripped,
                        'line_count': line_count,
                        'is_today': todo_date == datetime.date.today()
                    })
        
        # Trier par date (plus récent en premier)
        self.todo_dates.sort(key=lambda x: x['date'], reverse=True)
    
    def _extract_todo_date(self, todo_line):
        """Extrait la date d'une ligne TODO"""
        try:
            # Patterns de date possibles
            patterns = [
                r'(\d{4})-(\d{2})-(\d{2})',      # 2025-01-15
                r'(\d{2})/(\d{2})/(\d{4})',      # 15/01/2025
                r'(\d{2})-(\d{2})-(\d{4})',      # 15-01-2025
            ]
            
            for pattern in patterns:
                match = re.search(pattern, todo_line)
                if match:
                    groups = match.groups()
                    
                    if pattern.startswith(r'(\d{4})'):  # Format YYYY-MM-DD
                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                    else:  # Formats DD/MM/YYYY ou DD-MM-YYYY
                        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                    
                    return datetime.date(year, month, day)
            
            return None
            
        except Exception:
            return None
    
    def _count_lines_in_section(self, todo_line_index):
        """Compte approximativement les lignes de traduction dans une section TODO"""
        count = 0
        start_index = todo_line_index + 1
        
        # Chercher jusqu'à la prochaine ligne TODO ou fin de fichier
        for i in range(start_index, len(self.file_content)):
            line = self.file_content[i].strip()
            
            # Arrêter à la prochaine ligne TODO
            if line.startswith('# TODO:') and 'Translation updated at' in line:
                break
            
            # Compter les lignes qui semblent être des traductions
            if (line and 
                not line.startswith('#') and 
                '"' in line and 
                not line.lower().startswith(('translate ', 'old '))):
                count += 1
        
        return count
    
    def _create_content(self, theme):
        """Crée le contenu du dialogue"""
        # En-tête
        header_frame = tk.Frame(self.dialog, bg=theme["bg"])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title_label = tk.Label(
            header_frame,
            text="📅 Sélectionner la date TODO",
            font=('Segoe UI', 14, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Choisissez à partir de quelle mise à jour extraire les textes",
            font=('Segoe UI', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Liste des TODO
        list_frame = tk.Frame(self.dialog, bg=theme["bg"])
        list_frame.pack(fill='both', expand=True, padx=20)
        
        # Treeview pour afficher les TODO
        columns = ("Date", "Lignes", "État")
        self.todo_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        self.todo_tree.heading("Date", text="📅 Date de mise à jour")
        self.todo_tree.heading("Lignes", text="📝 Lignes (~)")
        self.todo_tree.heading("État", text="⏰ État")
        
        self.todo_tree.column("Date", width=200)
        self.todo_tree.column("Lignes", width=100)
        self.todo_tree.column("État", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.todo_tree.yview)
        self.todo_tree.configure(yscrollcommand=scrollbar.set)
        
        self.todo_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Remplir la liste
        for i, todo_info in enumerate(self.todo_dates):
            date_str = todo_info['date'].strftime("%d/%m/%Y")
            line_count = f"~{todo_info['line_count']}"
            state = "🟢 Aujourd'hui" if todo_info['is_today'] else "📝 Ancienne"
            
            item = self.todo_tree.insert("", "end", values=(date_str, line_count, state))
            
            # Sélectionner automatiquement la plus récente
            if i == 0:
                self.todo_tree.selection_set(item)
                self.todo_tree.focus(item)
        
        # Options
        options_frame = tk.Frame(self.dialog, bg=theme["bg"])
        options_frame.pack(fill='x', padx=20, pady=10)
        
        # Option "Tout extraire"
        self.extract_all_var = tk.BooleanVar()
        extract_all_check = tk.Checkbutton(
            options_frame,
            text="📦 Extraire tout (ignorer la sélection)",
            variable=self.extract_all_var,
            font=('Segoe UI', 10),
            bg=theme["bg"],
            fg=theme["fg"],
            selectcolor=theme["frame_bg"],
            activebackground=theme["bg"],
            activeforeground=theme["fg"]
        )
        extract_all_check.pack(anchor='w')
        
        # Boutons
        button_frame = tk.Frame(self.dialog, bg=theme["bg"])
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Info sur la sélection
        self.info_label = tk.Label(
            button_frame,
            text="💡 Sélectionnez une date dans la liste ci-dessus",
            font=('Segoe UI', 9),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.info_label.pack(side='left')
        
        # Bouton Annuler
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Annuler",
            font=('Segoe UI', 10),
            bg=theme["danger"],
            fg=theme["button_fg"],
            command=self._cancel
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        # Bouton Extraire
        extract_btn = tk.Button(
            button_frame,
            text="⚡ Extraire",
            font=('Segoe UI', 10, 'bold'),
            bg=theme["accent"],
            fg=theme["button_fg"],
            command=self._extract
        )
        extract_btn.pack(side='right')
        
        # Bind pour la sélection
        self.todo_tree.bind('<<TreeviewSelect>>', self._on_selection_change)
        
        # Mettre à jour l'info initiale
        self._on_selection_change(None)
    
    def _on_selection_change(self, event):
        """Met à jour l'info quand la sélection change"""
        try:
            if self.extract_all_var.get():
                self.info_label.config(text="📦 Mode extraction complète sélectionné")
                return
            
            selection = self.todo_tree.selection()
            if selection:
                item = selection[0]
                values = self.todo_tree.item(item, 'values')
                date_str = values[0]
                line_count = values[1]
                
                self.info_label.config(
                    text=f"📅 Extraire depuis le {date_str} ({line_count} lignes environ)"
                )
            else:
                self.info_label.config(text="💡 Sélectionnez une date dans la liste")
                
        except Exception:
            pass
    
    def _extract(self):
        """Lance l'extraction avec la date sélectionnée"""
        try:
            if self.extract_all_var.get():
                # Extraction complète
                self.result = "all"
            else:
                # Extraction depuis une date TODO
                selection = self.todo_tree.selection()
                if not selection:
                    messagebox.showwarning(
                        "⚠️ Aucune sélection",
                        "Veuillez sélectionner une date TODO ou cocher 'Extraire tout'."
                    )
                    return
                
                # Trouver l'index de la date sélectionnée
                item_index = self.todo_tree.index(selection[0])
                selected_todo = self.todo_dates[item_index]
                self.result = selected_todo
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("❌ Erreur", f"Erreur lors de la sélection:\n{str(e)}")
    
    def _cancel(self):
        """Annule la sélection"""
        self.result = None
        self.dialog.destroy()

# =============================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# =============================================================================

def main():
    """Point d'entrée principal de l'application"""
    try:
        # CORRECTION : Nettoyer toute instance Tkinter existante
        import tkinter as tk
        if tk._default_root:
            try:
                tk._default_root.withdraw()
                tk._default_root.quit() 
                tk._default_root.destroy()
            except:
                pass
        
        # Créer et lancer l'application
        app = TraducteurRenPyPro()
        app.run()
        
    except Exception as e:
        # Gestion d'erreur de dernier recours
        import traceback
        error_msg = f"Erreur critique au démarrage:\n{str(e)}\n\n{traceback.format_exc()}"
        
        try:
            log_message("ERREUR", f"Erreur critique au démarrage: {str(e)}")
        except:
            pass
        
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror("❌ Erreur critique", error_msg)
        except:
            print(error_msg)
        
        sys.exit(1)

if __name__ == "__main__":
    try:
        print("🚀 Démarrage du Traducteur Ren'Py Pro...")
        main()
    except Exception as e:
        print(f"❌ ERREUR au démarrage: {e}")
        import traceback
        print("🔍 Détails complets:")
        traceback.print_exc()
        input("Appuyez sur Entrée pour fermer...")