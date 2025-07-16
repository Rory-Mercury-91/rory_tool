# ui/glossary_ui.py
# Glossary User Interface
# Created for Traducteur Ren'Py Pro v2.3.0

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

class GlossaryDialog:
    """Dialogue de gestion du glossaire"""
    
    def __init__(self, parent):
        self.parent = parent
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

    def show(self):
        """Affiche le dialogue du glossaire"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("📚 Gestionnaire de Glossaire")
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
        
        title_label = tk.Label(
            header_frame,
            text="📚 Gestionnaire de Glossaire",
            font=('Segoe UI Emoji', 16, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        title_label.pack(side='left')
        
        # Statistiques
        stats = glossary_manager.get_statistics()
        stats_label = tk.Label(
            header_frame,
            text=f"📊 {stats['total_entries']} entrées",
            font=('Segoe UI Emoji', 12),
            bg=theme["bg"],
            fg=theme["accent"]
        )
        stats_label.pack(side='right')
        
        # Barre de recherche
        search_frame = tk.Frame(self.dialog, bg=theme["bg"])
        search_frame.pack(fill='x', padx=10, pady=5)
        
        search_label = tk.Label(
            search_frame,
            text="🔍 Rechercher:",
            font=('Segoe UI Emoji', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        search_label.pack(side='left')
        
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
        
        list_label = tk.Label(
            left_frame,
            text="📝 Entrées du glossaire",
            font=('Segoe UI Emoji', 12, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        list_label.pack(anchor='w', pady=(0, 5))
        
        # Treeview pour la liste
        self.tree = ttk.Treeview(
            left_frame,
            columns=('original', 'translation'),
            show='headings',
            height=20
        )
        
        # Configuration des colonnes
        self.tree.heading('original', text='Original')
        self.tree.heading('translation', text='Traduction')
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
        
        edit_label = tk.Label(
            right_frame,
            text="✏️ Édition",
            font=('Segoe UI Emoji', 12, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        edit_label.pack(anchor='w', pady=(0, 10))
        
        # Champ Original
        original_label = tk.Label(
            right_frame,
            text="Original:",
            font=('Segoe UI', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        original_label.pack(anchor='w')
        
        self.original_entry = tk.Entry(
            right_frame,
            textvariable=self.original_var,
            font=('Segoe UI', 10),
            bg=theme["entry_bg"],
            fg=theme["entry_fg"],
            relief='flat',
            bd=5
        )
        self.original_entry.pack(fill='x', pady=(0, 10))
        
        # Champ Traduction
        translation_label = tk.Label(
            right_frame,
            text="Traduction:",
            font=('Segoe UI', 10),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        translation_label.pack(anchor='w')
        
        self.translation_entry = tk.Entry(
            right_frame,
            textvariable=self.translation_var,
            font=('Segoe UI', 10),
            bg=theme["entry_bg"],
            fg=theme["entry_fg"],
            relief='flat',
            bd=5
        )
        self.translation_entry.pack(fill='x', pady=(0, 15))
        
        # Boutons d'édition
        button_frame = tk.Frame(right_frame, bg=theme["bg"])
        button_frame.pack(fill='x', pady=(0, 10))
        
        add_btn = tk.Button(
            button_frame,
            text="➕ Ajouter",
            font=('Segoe UI Emoji', 10),
            bg=theme["accent"],
            fg="#000000",
            relief='flat',
            bd=0,
            pady=8,
            command=self.add_entry
        )
        add_btn.pack(fill='x', pady=(0, 5))
        
        update_btn = tk.Button(
            button_frame,
            text="✏️ Modifier",
            font=('Segoe UI Emoji', 10),
            bg=theme.get("warning", "#ffc107"),
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.update_entry
        )
        update_btn.pack(fill='x', pady=(0, 5))
        
        delete_btn = tk.Button(
            button_frame,
            text="🗑️ Supprimer",
            font=('Segoe UI Emoji', 10),
            bg=theme.get("danger", "#dc3545"),
            fg="#000000",
            relief='flat',
            bd=0,
            pady=8,
            command=self.delete_entry
        )
        delete_btn.pack(fill='x', pady=(0, 5))
        
        clear_btn = tk.Button(
            button_frame,
            text="🆕 Nouveau",
            font=('Segoe UI Emoji', 10),
            bg='#6c757d',
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.clear_fields
        )
        clear_btn.pack(fill='x')
        
        # Séparateur
        separator = ttk.Separator(right_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
        # Boutons d'import/export
        io_frame = tk.Frame(right_frame, bg=theme["bg"])
        io_frame.pack(fill='x', pady=(0, 10))
        
        export_btn = tk.Button(
            io_frame,
            text="📤 Exporter",
            font=('Segoe UI Emoji', 10),
            bg='#17a2b8',
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.export_glossary
        )
        export_btn.pack(fill='x', pady=(0, 5))
        
        import_btn = tk.Button(
            io_frame,
            text="📥 Importer",
            font=('Segoe UI Emoji', 10),
            bg='#6f42c1',
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.import_glossary
        )
        import_btn.pack(fill='x', pady=(0, 5))
        
        validate_btn = tk.Button(
            io_frame,
            text="✅ Valider",
            font=('Segoe UI Emoji', 10),
            bg='#28a745',
            fg='#000000',
            relief='flat',
            bd=0,
            pady=8,
            command=self.validate_glossary
        )
        validate_btn.pack(fill='x')
        
        # Boutons de fermeture
        close_frame = tk.Frame(self.dialog, bg=theme["bg"])
        close_frame.pack(fill='x', padx=10, pady=10)
        
        # help_btn = tk.Button(
        #     close_frame,
        #     text="❓ Aide",
        #     font=('Segoe UI Emoji', 10),
        #     bg='#ffc107',
        #     fg='#000000',
        #     relief='flat',
        #     bd=0,
        #     pady=8,
        #     padx=15,
        #     command=self.show_help
        # )
        # help_btn.pack(side='left')
        
        close_btn = tk.Button(
            close_frame,
            text="✅ Fermer",
            font=('Segoe UI Emoji', 10),
            bg=theme["accent"],
            fg="#000000",
            relief='flat',
            bd=0,
            pady=8,
            padx=15,
            command=self.on_close
        )
        close_btn.pack(side='right')
    
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
            messagebox.showwarning("⚠️ Champs vides", "Veuillez remplir les deux champs.")
            return
        
        if glossary_manager.add_entry(original, translation):
            messagebox.showinfo("✅ Ajouté", f"Entrée ajoutée:\n'{original}' → '{translation}'")
            self.clear_fields()
            self.refresh_glossary_list()
            self.update_stats()
        else:
            messagebox.showwarning("⚠️ Erreur", "Impossible d'ajouter l'entrée.")
    
    def update_entry(self):
        """Modifie une entrée existante"""
        if not self.selected_item:
            messagebox.showwarning("⚠️ Sélection", "Veuillez sélectionner une entrée à modifier.")
            return
        
        original = self.original_var.get().strip()
        translation = self.translation_var.get().strip()
        
        if not original or not translation:
            messagebox.showwarning("⚠️ Champs vides", "Veuillez remplir les deux champs.")
            return
        
        # Supprimer l'ancienne entrée
        glossary_manager.remove_entry(self.selected_item)
        
        # Ajouter la nouvelle
        if glossary_manager.add_entry(original, translation):
            messagebox.showinfo("✅ Modifié", f"Entrée modifiée:\n'{original}' → '{translation}'")
            self.clear_fields()
            self.refresh_glossary_list()
            self.update_stats()
        else:
            messagebox.showwarning("⚠️ Erreur", "Impossible de modifier l'entrée.")
    
    def delete_entry(self):
        """Supprime une entrée"""
        if not self.selected_item:
            messagebox.showwarning("⚠️ Sélection", "Veuillez sélectionner une entrée à supprimer.")
            return
        
        result = messagebox.askyesno(
            "🗑️ Confirmer la suppression",
            f"Voulez-vous vraiment supprimer cette entrée ?\n\n'{self.selected_item}' → '{self.translation_var.get()}'"
        )
        
        if result:
            if glossary_manager.remove_entry(self.selected_item):
                messagebox.showinfo("✅ Supprimé", "Entrée supprimée avec succès.")
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
                messagebox.showinfo("✅ Export réussi", f"Glossaire exporté vers:\n{file_path}")
            else:
                messagebox.showerror("❌ Erreur", "Impossible d'exporter le glossaire.")
    
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
                "Voulez-vous fusionner avec le glossaire existant ?\n\n"
                "• Oui = Ajouter aux entrées existantes\n"
                "• Non = Remplacer complètement le glossaire"
            )
            
            if glossary_manager.import_glossary(file_path, merge):
                messagebox.showinfo("✅ Import réussi", "Glossaire importé avec succès.")
                self.refresh_glossary_list()
                self.update_stats()
            else:
                messagebox.showerror("❌ Erreur", "Impossible d'importer le glossaire.")
    
    def validate_glossary(self):
        """Valide le glossaire"""
        issues = glossary_manager.validate_glossary()
        
        if not issues:
            messagebox.showinfo("✅ Validation réussie", "Le glossaire ne contient aucun problème.")
        else:
            issue_text = "\n".join(f"• {issue}" for issue in issues[:10])
            if len(issues) > 10:
                issue_text += f"\n... et {len(issues) - 10} autres problèmes"
            
            messagebox.showwarning(
                f"⚠️ {len(issues)} problème(s) détecté(s)",
                f"Problèmes trouvés:\n\n{issue_text}"
            )
    
    def show_help(self):
        """Affiche l'aide du glossaire"""
        help_text = """📚 Gestionnaire de Glossaire - Aide

🎯 Objectif:
Le glossaire permet de traduire automatiquement des termes récurrents comme "Sigh" → "Soupir" dans tous vos projets.

📝 Utilisation:
1. Ajoutez des entrées: Original → Traduction
2. Les termes seront automatiquement protégés lors de l'extraction
3. Ils seront traduits lors de la reconstruction

🔍 Fonctionnalités:
• Recherche en temps réel
• Import/Export de glossaires
• Validation des entrées
• Protection automatique des termes complets

⚠️ Important:
• Le glossaire est permanent (non réinitialisable)
• Seuls les mots complets sont remplacés
• Les termes plus longs sont traités en premier

💡 Astuces:
• Utilisez des termes courants (Sigh, Hmm, etc.)
• Évitez les termes trop génériques
• Validez régulièrement votre glossaire"""
        
        messagebox.showinfo("❓ Aide - Glossaire", help_text)
    
    def update_stats(self):
        """Met à jour les statistiques affichées"""
        # Trouver et mettre à jour le label de stats
        # (Implémentation simplifiée - en production, stocker la référence)
        pass
    
    def on_close(self):
        """Gestionnaire de fermeture"""
        self.dialog.destroy()

def show_glossary_manager(parent):
    """Affiche le gestionnaire de glossaire"""
    dialog = GlossaryDialog(parent)
    dialog.show()