# ui/glossary_ui.py
# Glossary User Interface
# Created for RenExtract v2.5.0

"""
Interface utilisateur pour la gestion du glossaire
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from collections import OrderedDict
from core.glossary import glossary_manager
from utils.logging import log_message
from utils.constants import FOLDERS
from utils.i18n import i18n, _

class GlossaryDialog:
    """Dialogue de gestion du glossaire"""
    
    def __init__(self, parent, main_app=None):
        self.parent = parent
        self.main_app = main_app  # Instance de l'application principale pour i18n
        self.dialog = None
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # ✅ CORRECTION : Définir les variables dans le bon ordre
        self.glossary_file = os.path.join(FOLDERS["configs"], "glossary.json")
        self.glossary = OrderedDict()
        self.temp_placeholders = {}
        self.placeholder_counter = 0
        
        # Variables pour l'édition
        self.original_var = tk.StringVar()
        self.translation_var = tk.StringVar()
        self.selected_item = None
        
        # Références aux widgets pour mise à jour de langue
        self.title_label = None
        self.search_label = None
        self.list_label = None
        self.edit_label = None
        self.original_label = None
        self.translation_label = None
        self.stats_label = None
        
        # Références aux boutons pour mise à jour de langue
        self.add_btn = None
        self.update_btn = None
        self.delete_btn = None
        self.clear_btn = None
        self.export_btn = None
        self.import_btn = None
        self.validate_btn = None
        self.close_btn = None

    def show(self):
        """Affiche le dialogue du glossaire"""
        # Debug pour vérifier l'état du système i18n

        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(_('glossary.title'))
        self.dialog.geometry("800x700")
        self.dialog.resizable(True, True)
        
        # Rendre la fenêtre non-bloquante
        # self.dialog.transient(self.parent)  # Commenté pour permettre l'utilisation simultanée
        # self.dialog.grab_set()  # Commenté pour permettre l'utilisation simultanée
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Appliquer le thème
        from utils.config import config_manager
        from utils.constants import THEMES
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        self.dialog.configure(bg=theme["bg"])
        
        self.create_interface(theme)
        self.refresh_glossary_list()
        
        # Gestion de la fermeture
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_interface(self, theme):
        """Crée l'interface du gestionnaire de glossaire"""
        # En-tête
        header_frame = tk.Frame(self.dialog, bg=theme["bg"])
        header_frame.pack(fill='x', padx=10, pady=10)
        
        self.title_label = tk.Label(
            header_frame,
            text=_('glossary.title'),
            font=('Segoe UI Emoji', 16, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.title_label.pack(side='left')
        
        # Statistiques
        stats = glossary_manager.get_statistics()
        self.stats_label = tk.Label(
            header_frame,
            text=f"📊 {stats['total_entries']} entrées",
            font=('Segoe UI Emoji', 12),
            bg=theme["bg"],
            fg=theme["accent"]
        )
        self.stats_label.pack(side='right')
        
        # Barre de recherche
        search_frame = tk.Frame(self.dialog, bg=theme["bg"])
        search_frame.pack(fill='x', padx=10, pady=5)
        
        self.search_label = tk.Label(
            search_frame,
            text=_('glossary.search'),
            font=('Segoe UI Emoji', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.search_label.pack(side='left')
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 10),
            bg=theme["entry_bg"],
            fg=theme["entry_fg"],
            relief='flat',
            bd=5
        )
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        # Frame principal avec deux colonnes
        main_frame = tk.Frame(self.dialog, bg=theme["bg"])
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Colonne gauche : Liste du glossaire
        left_frame = tk.Frame(main_frame, bg=theme["bg"])
        left_frame.pack(side='left', fill='both', expand=True)
        
        self.list_label = tk.Label(
            left_frame,
            text=_('glossary.entries_title'),
            font=('Segoe UI Emoji', 12, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.list_label.pack(anchor='w', pady=(0, 5))
        
        # Treeview pour la liste
        self.tree = ttk.Treeview(
            left_frame,
            columns=('original', 'translation'),
            show='headings',
            height=20
        )
        
        # Configuration des colonnes
        self.tree.heading('original', text=_('glossary.original_label'))
        self.tree.heading('translation', text=_('glossary.translation_label'))
        self.tree.column('original', width=200)
        self.tree.column('translation', width=200)
        
        # Scrollbar pour la liste
        tree_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Événements pour la sélection
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        # Colonne droite : Édition
        right_frame = tk.Frame(main_frame, bg=theme["bg"], width=300)
        right_frame.pack(side='right', fill='y', padx=(10, 0))
        right_frame.pack_propagate(False)
        
        self.edit_label = tk.Label(
            right_frame,
            text=_('glossary.edit_title'),
            font=('Segoe UI Emoji', 12, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.edit_label.pack(anchor='w', pady=(0, 10))
        
        # Champs d'édition
        original_frame = tk.Frame(right_frame, bg=theme["bg"])
        original_frame.pack(fill='x', pady=(0, 10))
        
        self.original_label = tk.Label(
            original_frame,
            text=_('glossary.original_label'),
            font=('Segoe UI', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.original_label.pack(anchor='w')
        
        self.original_entry = tk.Entry(
            original_frame,
            textvariable=self.original_var,
            font=('Segoe UI', 10),
            bg=theme["entry_bg"],
            fg=theme["entry_fg"],
            relief='flat',
            bd=5
        )
        self.original_entry.pack(fill='x', pady=(5, 0))
        
        translation_frame = tk.Frame(right_frame, bg=theme["bg"])
        translation_frame.pack(fill='x', pady=(0, 10))
        
        self.translation_label = tk.Label(
            translation_frame,
            text=_('glossary.translation_label'),
            font=('Segoe UI', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.translation_label.pack(anchor='w')
        
        self.translation_entry = tk.Entry(
            translation_frame,
            textvariable=self.translation_var,
            font=('Segoe UI', 10),
            bg=theme["entry_bg"],
            fg=theme["entry_fg"],
            relief='flat',
            bd=5
        )
        self.translation_entry.pack(fill='x', pady=(5, 0))
        
        # Boutons d'action
        button_frame = tk.Frame(right_frame, bg=theme["bg"])
        button_frame.pack(fill='x', pady=(0, 10))
        
        self.add_btn = tk.Button(
            button_frame,
            text=_('glossary.buttons.add'),
            font=('Segoe UI Emoji', 10),
            bg=theme.get("success", "#28a745"),
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.add_entry
        )
        self.add_btn.pack(fill='x', pady=(0, 5))
        
        self.update_btn = tk.Button(
            button_frame,
            text=_('glossary.buttons.modify'),
            font=('Segoe UI Emoji', 10),
            bg=theme.get("warning", "#ffc107"),
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.update_entry
        )
        self.update_btn.pack(fill='x', pady=(0, 5))
        
        self.delete_btn = tk.Button(
            button_frame,
            text=_('glossary.buttons.delete'),
            font=('Segoe UI Emoji', 10),
            bg=theme.get("danger", "#dc3545"),
            fg="#000000",
            relief='flat',
            bd=0,
            pady=8,
            command=self.delete_entry
        )
        self.delete_btn.pack(fill='x', pady=(0, 5))
        
        self.clear_btn = tk.Button(
            button_frame,
            text=_('glossary.buttons.new'),
            font=('Segoe UI Emoji', 10),
            bg='#6c757d',
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.clear_fields
        )
        self.clear_btn.pack(fill='x')
        
        # Séparateur
        separator = ttk.Separator(right_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
        # Boutons d'import/export
        io_frame = tk.Frame(right_frame, bg=theme["bg"])
        io_frame.pack(fill='x', pady=(0, 10))
        
        self.export_btn = tk.Button(
            io_frame,
            text=_('glossary.buttons.export'),
            font=('Segoe UI Emoji', 10),
            bg='#17a2b8',
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.export_glossary
        )
        self.export_btn.pack(fill='x', pady=(0, 5))
        
        self.import_btn = tk.Button(
            io_frame,
            text=_('glossary.buttons.import'),
            font=('Segoe UI Emoji', 10),
            bg='#6f42c1',
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.import_glossary
        )
        self.import_btn.pack(fill='x', pady=(0, 5))
        
        self.validate_btn = tk.Button(
            io_frame,
            text=_('glossary.buttons.validate'),
            font=('Segoe UI Emoji', 10),
            bg='#28a745',
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.validate_glossary
        )
        self.validate_btn.pack(fill='x')
        
        # Boutons de fermeture
        close_frame = tk.Frame(self.dialog, bg=theme["bg"])
        close_frame.pack(fill='x', padx=10, pady=10)
               
        self.close_btn = tk.Button(
            close_frame,
            text=_('glossary.buttons.close'),
            font=('Segoe UI Emoji', 10),
            bg=theme["accent"],
            fg="#000000",
            relief='flat',
            bd=0,
            pady=8,
            padx=15,
            command=self.on_close
        )
        self.close_btn.pack(side='right')
    
    def refresh_glossary_list(self):
        """Actualise la liste du glossaire"""
        # Vider la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ajouter les entrées
        entries = glossary_manager.get_all_entries()
        for original, translation in entries.items():
            self.tree.insert('', 'end', values=(original, translation))
    
    def on_search_change(self, *args):
        """Gestionnaire de changement de recherche"""
        search_term = self.search_var.get()
        
        # Vider la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrer et afficher
        if search_term:
            results = glossary_manager.search_entries(search_term)
            for original, translation in results:
                self.tree.insert('', 'end', values=(original, translation))
        else:
            self.refresh_glossary_list()
    
    def on_item_select(self, event):
        """Gestionnaire de sélection d'élément"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            
            if values:
                self.original_var.set(values[0])
                self.translation_var.set(values[1])
                self.selected_item = values[0]
    
    def on_item_double_click(self, event):
        """Gestionnaire de double-clic"""
        self.update_entry()
    
    def add_entry(self):
        """Ajoute une nouvelle entrée"""
        original = self.original_var.get().strip()
        translation = self.translation_var.get().strip()
        
        if not original or not translation:
            messagebox.showwarning("⚠️ Champs vides", _('glossary.messages.empty_fields'))
            return
        
        if glossary_manager.add_entry(original, translation):
            self.clear_fields()
            self.refresh_glossary_list()
            self.update_stats()
        else:
            messagebox.showwarning("⚠️ Erreur", _('glossary.messages.add_error'))
    
    def update_entry(self):
        """Modifie une entrée existante"""
        if not self.selected_item:
            messagebox.showwarning("⚠️ Sélection", _('glossary.messages.no_selection'))
            return
        
        original = self.original_var.get().strip()
        translation = self.translation_var.get().strip()
        
        if not original or not translation:
            messagebox.showwarning("⚠️ Champs vides", _('glossary.messages.empty_fields'))
            return
        
        # Supprimer l'ancienne entrée
        glossary_manager.remove_entry(self.selected_item)
        
        # Ajouter la nouvelle
        if glossary_manager.add_entry(original, translation):
            self.clear_fields()
            self.refresh_glossary_list()
            self.update_stats()
        else:
            messagebox.showwarning("⚠️ Erreur", _('glossary.messages.modify_error'))
    
    def delete_entry(self):
        """Supprime une entrée"""
        if not self.selected_item:
            messagebox.showwarning("⚠️ Sélection", _('glossary.messages.no_selection_delete'))
            return
        
        result = messagebox.askyesno(
            "🗑️ Confirmer la suppression",
            _('glossary.messages.confirm_delete', original=self.selected_item, translation=self.translation_var.get())
        )
        
        if result:
            if glossary_manager.remove_entry(self.selected_item):
                self.clear_fields()
                self.refresh_glossary_list()
                self.update_stats()
    
    def clear_fields(self):
        """Vide les champs d'édition"""
        self.original_var.set("")
        self.translation_var.set("")
        self.selected_item = None
        self.tree.selection_remove(self.tree.selection())
    
    def export_glossary(self):
        """Exporte le glossaire"""
        file_path = filedialog.asksaveasfilename(
            title="Exporter le glossaire",
            defaultextension=".txt",
            filetypes=[
                ("Fichier texte", "*.txt"),
                ("Tous fichiers", "*.*")
            ]
        )
        
        if file_path:
            if glossary_manager.export_glossary(file_path):
                pass
            else:
                messagebox.showerror("❌ Erreur", _('glossary.messages.export_error'))

    def import_glossary(self):
        """Importe un glossaire"""
        file_path = filedialog.askopenfilename(
            title="Importer un glossaire",
            filetypes=[
                ("Fichier texte", "*.txt"),
                ("Tous fichiers", "*.*")
            ]
        )
        
        if file_path:
            merge = messagebox.askyesno(
                "📥 Mode d'importation",
                _('glossary.messages.import_mode')
            )
            
            if glossary_manager.import_glossary(file_path, merge):              
                self.refresh_glossary_list()
                self.update_stats()
            else:
                messagebox.showerror("❌ Erreur", _('glossary.messages.import_error'))

    def validate_glossary(self):
        """Valide le glossaire"""
        issues = glossary_manager.validate_glossary()
        
        if not issues:
            messagebox.showinfo("✅ Validation", _('glossary.messages.validation_success'))
        else:
            issue_text = "\n".join(f"• {issue}" for issue in issues[:10])
            if len(issues) > 10:
                issue_text += f"\n... et {len(issues) - 10} autres problèmes"
            
            messagebox.showwarning(
                _('glossary.messages.validation_issues', count=len(issues)),
                _('glossary.messages.validation_issues_text', issues=issue_text)
            )
    
    def show_help(self):
        """Affiche l'aide du glossaire"""
        help_text = _('glossary.help.content')
        
        messagebox.showinfo(_('glossary.help.title'), help_text)
    
    def update_stats(self):
        """Met à jour les statistiques affichées"""
        if self.dialog and self.stats_label:
            stats = glossary_manager.get_statistics()
            self.stats_label.config(text=f"📊 {stats['total_entries']} entrées")
    
    def update_language(self):
        """Met à jour l'interface quand la langue change"""
        if not self.dialog:
            return
        
        # Mettre à jour le titre de la fenêtre
        self.dialog.title(_('glossary.title'))
        
        # Mettre à jour les labels
        if self.title_label:
            self.title_label.config(text=_('glossary.title'))
        if self.search_label:
            self.search_label.config(text=_('glossary.search'))
        if self.list_label:
            self.list_label.config(text=_('glossary.entries_title'))
        if self.edit_label:
            self.edit_label.config(text=_('glossary.edit_title'))
        if self.original_label:
            self.original_label.config(text=_('glossary.original_label'))
        if self.translation_label:
            self.translation_label.config(text=_('glossary.translation_label'))
        
        # Mettre à jour les en-têtes du treeview
        self.tree.heading('original', text=_('glossary.original_label'))
        self.tree.heading('translation', text=_('glossary.translation_label'))
        
        # Mettre à jour les boutons
        if self.add_btn:
            new_text = _('glossary.buttons.add')
            self.add_btn.config(text=new_text)
        if self.update_btn:
            new_text = _('glossary.buttons.modify')
            self.update_btn.config(text=new_text)
        if self.delete_btn:
            new_text = _('glossary.buttons.delete')
            self.delete_btn.config(text=new_text)
        if self.clear_btn:
            new_text = _('glossary.buttons.new')
            self.clear_btn.config(text=new_text)
        if self.export_btn:
            new_text = _('glossary.buttons.export')
            self.export_btn.config(text=new_text)
        if self.import_btn:
            new_text = _('glossary.buttons.import')
            self.import_btn.config(text=new_text)
        if self.validate_btn:
            new_text = _('glossary.buttons.validate')
            self.validate_btn.config(text=new_text)
        if self.close_btn:
            new_text = _('glossary.buttons.close')
            self.close_btn.config(text=new_text)
        
        # Mettre à jour les statistiques
        self.update_stats()
    
    def on_close(self):
        """Gestionnaire de fermeture"""
        self._safe_destroy()
        
        # Nettoyer la référence dans l'application principale
        if self.main_app and hasattr(self.main_app, 'glossary_dialog'):
            self.main_app.glossary_dialog = None
    
    def _safe_destroy(self):
        """Destruction sécurisée du dialogue si l'objet n'est pas None"""
        if self.dialog is not None:
            try:
                if self.dialog.winfo_exists():
                    self.dialog.destroy()
            except Exception:
                pass
            self.dialog = None

def show_glossary_manager(parent, main_app=None):
    """Affiche le gestionnaire de glossaire"""
    dialog = GlossaryDialog(parent, main_app)
    dialog.show()