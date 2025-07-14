# ui/themes.py - SYSTÈME DE THÈMES CORRIGÉ
from tkinter import ttk
import tkinter as tk
from utils.constants import THEMES

print("🌙 Mode sombre:")
for key, value in THEMES["dark"].items():
    print(f"  {key}: {value}")

print("\n☀️ Mode clair:")
for key, value in THEMES["light"].items():
    print(f"  {key}: {value}")

class ThemeManager:
    """Gestionnaire de thèmes pour l'application - VERSION CORRIGÉE"""
    
    def __init__(self):
        self.current_theme = "dark"
        self.style = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """S'assure que le gestionnaire est initialisé (lazy loading) - VERSION CORRIGÉE"""
        if not self._initialized:
            try:
                root = tk._default_root
                if root is None:
                    return False
            
                self.style = ttk.Style()
                # ✅ CORRECTION : Marquer comme initialisé AVANT d'appeler setup_styles
                self._initialized = True
                self.setup_styles()  # Maintenant pas de récursion
                return True
            except Exception as e:
                print(f"⚠️ ThemeManager: Impossible d'initialiser TTK: {e}")
                self._initialized = False  # ✅ Remettre à False en cas d'erreur
                return False
        return True
    
    def setup_styles(self):
        """Configure les styles TTK de base"""
        if not self._ensure_initialized():
            return
        
        try:
            self.style.theme_use('clam')
            self.apply_current_theme()
        except Exception as e:
            print(f"⚠️ ThemeManager: Erreur setup_styles: {e}")
    
    def set_theme(self, theme_name):
        """Définit le thème actuel"""
        if theme_name in THEMES:
            self.current_theme = theme_name
            if self._ensure_initialized():
                self.apply_current_theme()
    
    def get_theme(self, theme_name=None):
        """Récupère un thème spécifique ou le thème actuel"""
        if theme_name:
            return THEMES.get(theme_name, THEMES["dark"])
        return THEMES[self.current_theme]
    
    def apply_current_theme(self):
        """Applique le thème actuel aux styles TTK"""
        if not self._ensure_initialized():
            return
        
        try:
            theme = self.get_theme()
            
            # Styles TTK
            self.style.configure('Action.TButton',
                               background=theme["button_bg"],
                               foreground=theme["button_fg"],
                               borderwidth=0,
                               focuscolor='none',
                               padding=(20, 12))
            
            self.style.configure('Success.TButton',
                               background=theme["accent"],
                               foreground=theme["button_fg"],
                               borderwidth=0,
                               focuscolor='none',
                               padding=(20, 12))
            
        except Exception as e:
            print(f"⚠️ ThemeManager: Erreur apply_current_theme: {e}")
    
    def apply_to_widget(self, widget, widget_type="default"):
        """✅ APPLIQUE LE THÈME CORRECTEMENT À TOUS LES WIDGETS"""
        if not widget:
            return
        
        theme = self.get_theme()
        try:
            # —— Widgets Tkinter natifs ——
            if isinstance(widget, tk.Frame) and not isinstance(widget, ttk.Frame):
                widget.configure(bg=theme["frame_bg"])
                
            elif isinstance(widget, tk.Label) and not isinstance(widget, ttk.Label):
                if widget_type == "title":
                    widget.configure(bg=theme["bg"], fg=theme["fg"])
                elif widget_type == "subtitle":
                    widget.configure(bg=theme["bg"], fg=theme["fg"])
                elif widget_type == "path_label":
                    widget.configure(bg=theme["frame_bg"], fg=theme["accent"])
                elif widget_type == "stats_label":
                    widget.configure(bg=theme["frame_bg"], fg=theme["fg"])
                else:
                    widget.configure(bg=theme["bg"], fg=theme["fg"])
                    
            elif isinstance(widget, tk.Text):
                widget.configure(
                    bg=theme["entry_bg"],
                    fg=theme["entry_fg"],
                    selectbackground=theme["select_bg"],
                    selectforeground=theme["select_fg"],
                    insertbackground=theme["entry_fg"],
                    highlightbackground=theme["frame_bg"],
                    highlightcolor=theme["accent"]
                )
                
            elif isinstance(widget, tk.Button) and not isinstance(widget, ttk.Button):
                # ✅ CORRECTION : Adapter les couleurs selon le thème
                current_bg = widget.cget("bg")
                
                # Identifier le type de bouton par sa couleur actuelle
                if current_bg in ['#007bff', '#0d6efd']:  # Boutons bleus
                    new_fg = "#ffffff" if self.current_theme == "dark" else "#000000"
                elif current_bg in ['#28a745', '#198754']:  # Boutons verts
                    new_fg = "#ffffff" if self.current_theme == "dark" else "#000000"
                elif current_bg in ['#dc3545', '#d32f2f']:  # Boutons rouges
                    new_fg = "#ffffff"
                elif current_bg in ['#ffc107', '#ffb74d']:  # Boutons jaunes/orange
                    new_fg = "#000000"
                elif current_bg in ['#17a2b8', '#6f42c1']:  # Boutons spéciaux
                    new_fg = "#ffffff" if self.current_theme == "dark" else "#000000"
                else:
                    # Couleur par défaut selon le thème
                    new_fg = theme["button_fg"]
                
                widget.configure(fg=new_fg)
                
            # ✅ NOUVEAU : Appliquer le thème aux fenêtres principales
            elif isinstance(widget, (tk.Tk, tk.Toplevel)):
                widget.configure(bg=theme["bg"])
                
            # Autres widgets supportant bg
            elif hasattr(widget, 'configure'):
                try:
                    widget.configure(bg=theme.get("bg"))
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ ThemeManager: Erreur apply_to_widget: {e}")
    
    def get_dialog_theme(self):
        """Récupère la configuration de thème pour les dialogues"""
        theme = self.get_theme()
        return {
            'bg': theme["bg"],
            'fg': theme["fg"],
            'frame_bg': theme["frame_bg"],
            'button_bg': theme["button_bg"],
            'button_fg': theme["button_fg"],
            'accent': theme["accent"],
            'warning': theme["warning"],
            'danger': theme["danger"],
        }
    
    def initialize_now(self):
        """Force l'initialisation maintenant"""
        return self._ensure_initialized()
    
    def get_button_colors(self, button_type="default"):
        """✅ NOUVEAU : Récupère les couleurs de bouton selon le thème"""
        theme = self.get_theme()
        
        colors = {
            "blue": {"bg": "#007bff", "fg": "#ffffff" if self.current_theme == "dark" else "#000000"},
            "green": {"bg": "#28a745", "fg": "#ffffff" if self.current_theme == "dark" else "#000000"},
            "red": {"bg": "#dc3545", "fg": "#ffffff"},
            "yellow": {"bg": "#ffc107", "fg": "#000000"},
            "purple": {"bg": "#6f42c1", "fg": "#ffffff"},
            "cyan": {"bg": "#17a2b8", "fg": "#ffffff"},
            "default": {"bg": theme["button_bg"], "fg": theme["button_fg"]}
        }
        
        return colors.get(button_type, colors["default"])

# Instance globale du gestionnaire de thèmes
theme_manager = ThemeManager()