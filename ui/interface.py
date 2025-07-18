# ui/interface.py
# Interface Components Module
# Created for RenExtract v2.5.0

"""
Composants d'interface utilisateur réutilisables
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import THEMES, VERSION
from utils.config import config_manager
from ui.themes import theme_manager

class SaveModeDialog:
    """Dialogue pour choisir le mode de sauvegarde"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.dialog = None
        self._create_dialog()
    
    def _create_dialog(self):
        """Crée le dialogue de sélection du mode de sauvegarde"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("💾 Mode de sauvegarde")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Appliquer le thème
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        self.dialog.configure(bg=theme["bg"])
        
        # Créer le contenu
        self._create_content(theme)
        
        # Rendre le dialogue modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
    
    def _create_content(self, theme):
        """Crée le contenu du dialogue"""
        # Titre
        title_label = tk.Label(
            self.dialog,
            text="💾 Choisissez le mode de sauvegarde",
            font=('Segoe UI Emoji', 14, 'bold'),
            bg=theme["bg"],
            fg=theme["accent"]
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(
            self.dialog,
            text="Comment souhaitez-vous sauvegarder le fichier traduit ?",
            font=('Segoe UI Emoji', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        desc_label.pack(pady=(0, 20))
        
        # Options
        self._create_option(
            self.dialog, theme,
            "📄 Nouveau fichier",
            "Crée un nouveau fichier avec le suffixe '_traduit'",
            '#28a745', '#ffffff',
            lambda: self._choose_mode('new_file')
        )
        
        self._create_option(
            self.dialog, theme,
            "🔄 Remplacer l'original",
            "Remplace directement le fichier original (sauvegarde automatique)",
            '#dc3545', '#ffffff',
            lambda: self._choose_mode('overwrite')
        )
        
        # Bouton annuler
        cancel_btn = tk.Button(
            self.dialog,
            text="❌ Annuler",
            font=('Segoe UI Emoji', 10),
            bg=theme["danger"],
            fg="#000000",
            activebackground='#b02a37',
            bd=0,
            pady=8,
            command=self._cancel
        )
        cancel_btn.pack(pady=10)
    
    def _create_option(self, parent, theme, title, description, bg_color, fg_color, command):
        """Crée une option de sauvegarde"""
        option_frame = tk.Frame(parent, bg=theme["frame_bg"], relief='solid', bd=1)
        option_frame.pack(fill='x', pady=10)
        
        btn = tk.Button(
            option_frame,
            text=title,
            font=('Segoe UI Emoji', 11, 'bold'),
            bg=bg_color,
            fg=fg_color,
            bd=0,
            pady=15,
            command=command
        )
        btn.pack(fill='x', padx=10, pady=10)
        
        desc = tk.Label(
            option_frame,
            text=description,
            font=('Segoe UI Emoji', 9),
            bg=theme["frame_bg"],
            fg=theme["fg"],
            justify='left'
        )
        desc.pack(pady=(0, 10))
    
    def _choose_mode(self, mode):
        """Enregistre le choix et ferme le dialogue"""
        self.result = mode
        self._safe_destroy()
    
    def _cancel(self):
        """Annule et ferme le dialogue"""
        self.result = None
        self._safe_destroy()
    
    def _safe_destroy(self):
        """Ferme le dialogue de manière sécurisée"""
        if self.dialog is not None:
            try:
                if self.dialog.winfo_exists():
                    self.dialog.destroy()
            except Exception:
                pass
            self.dialog = None
    
    def show(self):
        """Affiche le dialogue et retourne le résultat"""
        if self.dialog is not None:
            self.dialog.wait_window()
        return self.result

class ProgressDialog:
    """Dialogue de progression pour les opérations longues"""
    
    def __init__(self, parent, title="⏳ Traitement en cours..."):
        self.parent = parent
        self.dialog = None
        self.progress_var = None
        self.progress_bar = None
        self._create_dialog(title)
    
    def _create_dialog(self, title):
        """Crée le dialogue de progression"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Appliquer le thème
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        self.dialog.configure(bg=theme["bg"])
        
        # Rendre le dialogue modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Créer le contenu
        self._create_content(theme)
    
    def _create_content(self, theme):
        """Crée le contenu du dialogue de progression"""
        # Titre
        title_label = tk.Label(
            self.dialog,
            text="⏳ Traitement en cours...",
            font=('Segoe UI Emoji', 12, 'bold'),
            bg=theme["bg"],
            fg=theme["accent"]
        )
        title_label.pack(pady=20)
        
        # Barre de progression
        self.progress_var = tk.StringVar(value="Initialisation...")
        self.progress_bar = ttk.Progressbar(
            self.dialog,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        
        # Message de progression
        message_label = tk.Label(
            self.dialog,
            textvariable=self.progress_var,
            font=('Segoe UI Emoji', 9),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        message_label.pack(pady=10)
    
    def update_message(self, message):
        """Met à jour le message affiché"""
        if self.dialog and self.dialog.winfo_exists() and self.progress_var is not None:
            self.progress_var.set(message)
            self.dialog.update()
    
    def close(self):
        """Ferme le dialogue de progression"""
        if self.dialog is not None:
            try:
                if self.progress_bar is not None:
                    self.progress_bar.stop()
                if self.dialog.winfo_exists():
                    self.dialog.destroy()
            except Exception:
                pass
            self.dialog = None

class StatusBar:
    """Barre de statut avancée"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.status_var = tk.StringVar()
        self.time_var = tk.StringVar()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crée les widgets de la barre de statut"""
        # Status principal
        self.status_label = tk.Label(
            self.frame,
            textvariable=self.status_var,
            font=('Segoe UI Emoji', 10),
            anchor='w'
        )
        self.status_label.pack(side='left', padx=(10, 0))
        
        # Séparateur
        separator = ttk.Separator(self.frame, orient='vertical')
        separator.pack(side='right', fill='y', padx=5)
        
        # Temps
        self.time_label = tk.Label(
            self.frame,
            textvariable=self.time_var,
            font=('Segoe UI Emoji', 9),
            anchor='e'
        )
        self.time_label.pack(side='right', padx=(0, 10))
        
        # Appliquer le thème
        self.apply_theme()
    
    def pack(self, **kwargs):
        """Pack la barre de statut"""
        self.frame.pack(**kwargs)
    
    def set_status(self, message):
        """Définit le message de statut"""
        self.status_var.set(message)
    
    def set_time(self, time_info):
        """Définit les informations de temps"""
        self.time_var.set(time_info)
    
    def apply_theme(self):
        """Applique le thème actuel"""
        theme_manager.apply_to_widget(self.frame, "info_frame")
        theme_manager.apply_to_widget(self.status_label, "stats_label")
        theme_manager.apply_to_widget(self.time_label, "stats_label")

class ValidationResultDialog:
    """Dialogue pour afficher les résultats de validation"""
    
    @staticmethod
    def show_validation_result(parent, validation_result, file_type="fichier"):
        """
        Affiche les résultats de validation
        
        Args:
            parent: Fenêtre parente
            validation_result (dict): Résultats de la validation
            file_type (str): Type de fichier validé
        """
        if validation_result['is_valid']:
            # Validation réussie
            message = f"✅ {file_type.capitalize()} validé avec succès !\n\n"
            message += f"Confiance: {validation_result['confidence']}%\n"
            message += f"Patterns détectés: {len(validation_result['patterns_found'])}"
            
            if validation_result['warnings']:
                message += "\n\n⚠️ Avertissements:\n"
                message += "\n".join(f"• {w}" for w in validation_result['warnings'])
            
            messagebox.showinfo("✅ Validation réussie", message)
        else:
            # Validation échouée
            message = f"❌ {file_type.capitalize()} non valide !\n\n"
            
            if validation_result['errors']:
                message += "Erreurs détectées:\n"
                message += "\n".join(f"• {e}" for e in validation_result['errors'])
            
            if validation_result['warnings']:
                message += "\n\nAvertissements:\n"
                message += "\n".join(f"• {w}" for w in validation_result['warnings'])
            
            messagebox.showerror("❌ Validation échouée", message)

class AboutDialog:
    """Dialogue À propos de l'application"""
    
    @staticmethod
    def show(parent):
        """Affiche le dialogue À propos"""
        about_text = f"""🎮 RenExtract

Version: {VERSION}
Développé pour la traduction de scripts Ren'Py

🚀 Fonctionnalités:
• Support multi-projets simultanés
• Extraction intelligente avec protection des codes
• Gestion des expressions spéciales
• Validation automatique des fichiers
• Historique détaillé des performances
• Interface moderne avec thèmes
• Sauvegarde automatique de sécurité

🎯 Nouveautés v2.5.0:
• Architecture refactorisée
• Validation avancée des fichiers Ren'Py
• Contrôle de l'ouverture automatique
• Sauvegardes de sécurité automatiques
• Interface réorganisée et améliorée

© 2024 - Outil de traduction avancé
Architecture modulaire pour une maintenance facilitée"""
        
        messagebox.showinfo("À propos", about_text)

# Fonctions utilitaires pour l'interface
def show_error(message, title="Erreur"):
    """Affiche un message d'erreur standardisé"""
    messagebox.showerror(f"❌ {title}", message)

def show_warning(message, title="Attention"):
    """Affiche un message d'avertissement standardisé"""
    messagebox.showwarning(f"⚠️ {title}", message)

def show_info(message, title="Information"):
    """Affiche un message d'information standardisé"""
    messagebox.showinfo(f"ℹ️ {title}", message)

def show_success(message, title="Succès"):
    """Affiche un message de succès standardisé"""
    messagebox.showinfo(f"✅ {title}", message)

def ask_yes_no(message, title="Confirmation"):
    """Affiche une question oui/non standardisée"""
    return messagebox.askyesno(f"❓ {title}", message)