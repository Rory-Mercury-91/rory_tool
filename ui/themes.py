from tkinter import ttk
import tkinter as tk
from utils.constants import THEMES

class ThemeManager:
    """Gestionnaire de thèmes pour l'application"""
    
    def __init__(self):
        self.current_theme = "dark"
        self.style = ttk.Style()
        self.setup_styles()
    
    def setup_styles(self):
        """Configure les styles TTK de base"""
        self.style.theme_use('clam')
        self.apply_current_theme()
    
    def set_theme(self, theme_name):
        """
        Définit le thème actuel
        
        Args:
            theme_name (str): Nom du thème ('light' ou 'dark')
        """
        if theme_name in THEMES:
            self.current_theme = theme_name
            self.apply_current_theme()
    
    def get_theme(self, theme_name=None):
        """
        Récupère un thème spécifique ou le thème actuel
        
        Args:
            theme_name (str, optional): Nom du thème
            
        Returns:
            dict: Configuration du thème
        """
        if theme_name:
            return THEMES.get(theme_name, THEMES["dark"])
        return THEMES[self.current_theme]
    
    def apply_current_theme(self):
        """Applique le thème actuel aux styles TTK"""
        theme = self.get_theme()
        
        # Style des boutons TTK
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
        
        self.style.configure('Warning.TButton',
                           background=theme["warning"],
                           foreground='#000000',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(15, 12))
        
        self.style.configure('Danger.TButton',
                           background=theme["danger"],
                           foreground=theme["button_fg"],
                           borderwidth=0,
                           focuscolor='none',
                           padding=(15, 12))
        
        # Style des frames TTK
        self.style.configure('Card.TFrame',
                           background=theme["frame_bg"],
                           relief='flat',
                           borderwidth=1)
        
        # Style des labels TTK
        self.style.configure('Title.TLabel',
                           background=theme["bg"],
                           foreground=theme["fg"],
                           font=('Segoe UI', 16, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background=theme["bg"],
                           foreground=theme["fg"],
                           font=('Segoe UI', 10))
        
        self.style.configure('Path.TLabel',
                           background=theme["frame_bg"],
                           foreground=theme["accent"],
                           font=('Segoe UI', 9, 'bold'))
    
    def apply_to_widget(self, widget, widget_type="default"):
        """
        Applique le thème à un widget spécifique.
        Gère les widgets TK et TTK selon leur type et role.
        
        Args:
            widget: Widget à themer
            widget_type (str): Type de widget pour style spécifique
        """
        theme = self.get_theme()
        try:
            # —— Widgets Tkinter natifs ——
            if isinstance(widget, tk.Frame) and not isinstance(widget, ttk.Frame):
                widget.configure(bg=theme["frame_bg"])
            elif isinstance(widget, tk.Label) and not isinstance(widget, ttk.Label):
                # config labels natifs selon role
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
                )
            elif isinstance(widget, tk.Button) and not isinstance(widget, ttk.Button):
                # boutons colorés natifs — conservent leur bg, texte noir
                widget.configure(
                    fg="#000000",
                    bg=widget.cget("bg"),
                    activebackground=widget.cget("activebackground"),
                    activeforeground=widget.cget("activeforeground"),
                )
            # —— Widgets TTK ——
            elif isinstance(widget, ttk.Frame):
                widget.configure(style="Card.TFrame")
            elif isinstance(widget, ttk.Label):
                style_map = {
                    "title":    "Title.TLabel",
                    "subtitle": "Subtitle.TLabel",
                    "path_label":  "Path.TLabel",
                    "stats_label":"Subtitle.TLabel"
                }
                style_name = style_map.get(widget_type, "Subtitle.TLabel")
                widget.configure(style=style_name)
            elif isinstance(widget, ttk.Button):
                style_map = {
                    "action":  "Action.TButton",
                    "success": "Success.TButton",
                    "warning": "Warning.TButton",
                    "danger":  "Danger.TButton"
                }
                style_name = style_map.get(widget_type, "Action.TButton")
                widget.configure(style=style_name)
            # autres widgets supportant bg
            elif hasattr(widget, 'configure'):
                widget.configure(bg=theme.get("bg"))
        except Exception:
            pass
    
    def get_dialog_theme(self):
        """
        Récupère la configuration de thème pour les dialogues
        
        Returns:
            dict: Configuration spécifique aux dialogues
        """
        theme = self.get_theme()
        return {
            'bg':       theme["bg"],
            'fg':       theme["fg"],
            'frame_bg': theme["frame_bg"],
            'button_bg':theme["button_bg"],
            'button_fg':theme["button_fg"],
            'accent':   theme["accent"],
            'warning':  theme["warning"],
            'danger':   theme["danger"],
        }

# Instance globale du gestionnaire de thèmes
theme_manager = ThemeManager()