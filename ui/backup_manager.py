# ui/backup_manager.py
# Backup Management Interface
# Created for Traducteur Ren'Py Pro v1.9.0

"""
Module d'interface pour la gestion des sauvegardes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import datetime
from core.validation import BackupManager
from utils.logging import log_message
from ui.themes import theme_manager

class BackupDialog:
    """Dialogue de gestion des sauvegardes"""
    
    def __init__(self, parent, filepath=None):
        self.parent = parent
        self.filepath = filepath
        self.dialog = None
        self.backups = []
        self.backup_manager = BackupManager()
    
    def show(self):
        """Affiche le dialogue de gestion des sauvegardes"""
        if not self.filepath or not os.path.exists(self.filepath):
            messagebox.showwarning(
                "⚠️ Aucun fichier", 
                "Chargez d'abord un fichier .rpy pour voir ses sauvegardes."
            )
            return
        
        self.dialog = tk.Toplevel(self.parent)
        filename = os.path.basename(self.filepath)
        self.dialog.title(f"🛡️ Sauvegardes de {filename}")
        self.dialog.geometry("600x400")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Appliquer le thème
        theme = theme_manager.get_dialog_theme()
        self.dialog.configure(bg=theme["bg"])
        
        self._create_content(theme)
        self._load_backups()
    
    def _create_content(self, theme):
        """Crée le contenu du dialogue"""
        # En-tête
        header_frame = tk.Frame(self.dialog, bg=theme["bg"])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title_label = tk.Label(
            header_frame,
            text=f"🛡️ Sauvegardes de {os.path.basename(self.filepath)}",
            font=('Segoe UI', 14, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        title_label.pack()
        
        info_label = tk.Label(
            header_frame,
            text="Les sauvegardes sont créées automatiquement avant chaque traitement",
            font=('Segoe UI', 9),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        info_label.pack(pady=(5, 0))
        
        # Frame principal avec scrollbar
        main_frame = tk.Frame(self.dialog, bg=theme["bg"])
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Canvas et scrollbar pour la liste des sauvegardes
        canvas = tk.Canvas(main_frame, bg=theme["frame_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=theme["frame_bg"])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Message par défaut
        self.no_backup_label = tk.Label(
            self.scrollable_frame,
            text="🔍 Recherche des sauvegardes...",
            font=('Segoe UI', 11),
            bg=theme["frame_bg"],
            fg=theme["fg"]
        )
        self.no_backup_label.pack(pady=50)
        
        # Boutons en bas
        button_frame = tk.Frame(self.dialog, bg=theme["bg"])
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Bouton actualiser
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Actualiser",
            font=('Segoe UI', 10),
            bg=theme["accent"],
            fg=theme["button_fg"],
            activebackground='#157347',
            bd=0,
            pady=8,
            padx=15,
            command=self._refresh_backups
        )
        refresh_btn.pack(side='left')
        
        # Bouton fermer
        close_btn = tk.Button(
            button_frame,
            text="❌ Fermer",
            font=('Segoe UI', 10),
            bg=theme["danger"],
            fg=theme["button_fg"],
            activebackground='#b02a37',
            bd=0,
            pady=8,
            padx=15,
            command=self.dialog.destroy
        )
        close_btn.pack(side='right')
        
        # Permettre le scroll avec la molette
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.dialog.bind("<MouseWheel>", on_mousewheel)
    
    def _load_backups(self):
        """Charge la liste des sauvegardes"""
        try:
            self.backups = self.backup_manager.list_backups(self.filepath)
            self._update_backup_list()
        except Exception as e:
            log_message("ERREUR", f"Erreur lors du chargement des sauvegardes pour {self.filepath}", e)
            messagebox.showerror("❌ Erreur", f"Impossible de charger les sauvegardes:\n{str(e)}")
    
    def _refresh_backups(self):
        """Actualise la liste des sauvegardes"""
        # Vider la liste actuelle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Afficher le message de chargement
        theme = theme_manager.get_dialog_theme()
        loading_label = tk.Label(
            self.scrollable_frame,
            text="🔄 Actualisation...",
            font=('Segoe UI', 11),
            bg=theme["frame_bg"],
            fg=theme["fg"]
        )
        loading_label.pack(pady=50)
        
        self.dialog.update()
        
        # Recharger
        self._load_backups()
    
    def _update_backup_list(self):
        """Met à jour l'affichage de la liste des sauvegardes"""
        # Vider la liste actuelle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        theme = theme_manager.get_dialog_theme()
        
        if not self.backups:
            # Aucune sauvegarde trouvée
            no_backup_label = tk.Label(
                self.scrollable_frame,
                text="📭 Aucune sauvegarde trouvée\n\nLes sauvegardes seront créées automatiquement\nlors de la prochaine extraction",
                font=('Segoe UI', 11),
                bg=theme["frame_bg"],
                fg=theme["fg"],
                justify='center'
            )
            no_backup_label.pack(pady=50)
            return
        
        # Afficher chaque sauvegarde
        for i, backup in enumerate(self.backups):
            self._create_backup_item(backup, i, theme)
    
    def _create_backup_item(self, backup, index, theme):
        """Crée un élément de sauvegarde dans la liste"""
        # Frame principal pour cette sauvegarde
        item_frame = tk.Frame(
            self.scrollable_frame, 
            bg=theme["bg"], 
            relief='solid', 
            bd=1
        )
        item_frame.pack(fill='x', padx=10, pady=5)
        
        # Frame d'informations
        info_frame = tk.Frame(item_frame, bg=theme["bg"])
        info_frame.pack(fill='x', padx=15, pady=10)
        
        # Icône et nom
        name_frame = tk.Frame(info_frame, bg=theme["bg"])
        name_frame.pack(fill='x')
        
        icon_label = tk.Label(
            name_frame,
            text="📅",
            font=('Segoe UI', 12),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        icon_label.pack(side='left')
        
        name_label = tk.Label(
            name_frame,
            text=backup['name'],
            font=('Segoe UI', 11, 'bold'),
            bg=theme["bg"],
            fg=theme["accent"]
        )
        name_label.pack(side='left', padx=(5, 0))
        
        # Informations détaillées
        details_frame = tk.Frame(info_frame, bg=theme["bg"])
        details_frame.pack(fill='x', pady=(5, 0))
        
        # Date de création
        created_str = backup['created'].strftime("%d/%m/%Y à %H:%M:%S")
        created_label = tk.Label(
            details_frame,
            text=f"📅 Créée: {created_str}",
            font=('Segoe UI', 9),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        created_label.pack(anchor='w')
        
        # Taille du fichier
        size_mb = backup['size'] / (1024 * 1024)
        size_label = tk.Label(
            details_frame,
            text=f"📦 Taille: {size_mb:.2f} MB",
            font=('Segoe UI', 9),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        size_label.pack(anchor='w')
        
        # Ancienneté
        age = datetime.datetime.now() - backup['created']
        if age.days > 0:
            age_str = f"{age.days} jour(s)"
        elif age.seconds > 3600:
            age_str = f"{age.seconds // 3600} heure(s)"
        else:
            age_str = f"{age.seconds // 60} minute(s)"
        
        age_label = tk.Label(
            details_frame,
            text=f"⏰ Il y a: {age_str}",
            font=('Segoe UI', 9),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        age_label.pack(anchor='w')
        
        # Boutons d'action
        action_frame = tk.Frame(item_frame, bg=theme["bg"])
        action_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Bouton restaurer
        restore_btn = tk.Button(
            action_frame,
            text="🔄 Restaurer",
            font=('Segoe UI', 10),
            bg=theme["accent"],
            fg=theme["button_fg"],
            activebackground='#157347',
            bd=0,
            pady=6,
            padx=12,
            command=lambda: self._restore_backup(backup)
        )
        restore_btn.pack(side='left', padx=(0, 10))
        
        # Bouton supprimer
        delete_btn = tk.Button(
            action_frame,
            text="🗑️ Supprimer",
            font=('Segoe UI', 10),
            bg=theme["danger"],
            fg=theme["button_fg"],
            activebackground='#b02a37',
            bd=0,
            pady=6,
            padx=12,
            command=lambda: self._delete_backup(backup)
        )
        delete_btn.pack(side='left')
        
        # Badge "plus récent" pour la première sauvegarde
        if index == 0 and len(self.backups) > 1:
            recent_badge = tk.Label(
                action_frame,
                text="🌟 Plus récent",
                font=('Segoe UI', 9, 'bold'),
                bg=theme["warning"],
                fg='#000000',
                padx=8,
                pady=2
            )
            recent_badge.pack(side='right')
    
    def _restore_backup(self, backup):
        """Restaure une sauvegarde avec gestion complète des erreurs"""
        try:
            # Confirmation de restauration
            result = messagebox.askyesno(
                "🔄 Confirmer la restauration",
                f"Voulez-vous vraiment restaurer cette sauvegarde ?\n\n"
                f"📅 {backup['name']}\n"
                f"🕒 Créée: {backup['created'].strftime('%d/%m/%Y à %H:%M:%S')}\n\n"
                f"⚠️ ATTENTION: Le fichier actuel sera remplacé !"
            )
            
            if not result:
                return
            
            # Restaurer
            restore_result = self.backup_manager.restore_backup(backup['path'], self.filepath)
            
            if restore_result['success']:
                # Confirmation de suppression APRÈS restauration réussie
                delete_backup = messagebox.askyesno(
                    "✅ Restauration réussie",
                    f"La sauvegarde a été restaurée avec succès !\n\n"
                    f"📁 Fichier: {os.path.basename(self.filepath)}\n"
                    f"📅 Sauvegarde: {backup['created'].strftime('%d/%m/%Y à %H:%M:%S')}\n\n"
                    f"❓ Voulez-vous supprimer cette sauvegarde maintenant qu'elle a été utilisée ?"
                )
                
                if delete_backup:
                    try:
                        # Tentative de suppression
                        os.remove(backup['path'])
                        
                        # Succès de la suppression
                        messagebox.showinfo(
                            "🗑️ Sauvegarde supprimée",
                            f"La sauvegarde utilisée a été supprimée :\n📅 {backup['name']}"
                        )
                        
                        # Actualiser la liste
                        self._refresh_backups()
                        
                        log_message("INFO", f"Sauvegarde supprimée après restauration: {backup['name']}")
                        
                    except PermissionError:
                        # Erreur de permission
                        log_message("ERREUR", f"Permission refusée pour supprimer {backup['path']}")
                        messagebox.showerror(
                            "❌ Erreur de permission",
                            f"Impossible de supprimer la sauvegarde :\n\n"
                            f"📅 {backup['name']}\n\n"
                            f"💡 Le fichier est peut-être utilisé par un autre programme.\n"
                            f"Vous pouvez le supprimer manuellement si nécessaire."
                        )
                        
                    except FileNotFoundError:
                        # Fichier déjà supprimé
                        log_message("WARNING", f"Fichier de sauvegarde déjà supprimé: {backup['path']}")
                        messagebox.showwarning(
                            "⚠️ Fichier introuvable",
                            f"La sauvegarde semble déjà avoir été supprimée :\n📅 {backup['name']}"
                        )
                        # Actualiser quand même la liste
                        self._refresh_backups()
                        
                    except OSError as os_error:
                        # Autres erreurs système
                        log_message("ERREUR", f"Erreur système lors de la suppression de {backup['path']}", os_error)
                        messagebox.showerror(
                            "❌ Erreur système",
                            f"Erreur lors de la suppression de la sauvegarde :\n\n"
                            f"📅 {backup['name']}\n"
                            f"🔧 Erreur: {str(os_error)}\n\n"
                            f"💡 Vous pouvez essayer de supprimer le fichier manuellement."
                        )
                        
                    except Exception as delete_error:
                        # Toute autre erreur inattendue
                        log_message("ERREUR", f"Erreur inattendue lors de la suppression de {backup['path']}", delete_error)
                        messagebox.showerror(
                            "❌ Erreur inattendue",
                            f"Une erreur inattendue s'est produite :\n\n"
                            f"📅 {backup['name']}\n"
                            f"🔧 Erreur: {str(delete_error)}\n\n"
                            f"💡 La restauration a réussi, mais la suppression a échoué.\n"
                            f"Vous pouvez supprimer manuellement le fichier si souhaité."
                        )
                
                # Fermer le dialogue et notifier le parent de recharger le fichier
                # (même si la suppression a échoué, la restauration a réussi)
                self.dialog.destroy()
                
                # Notifier le parent de recharger le fichier (si possible)
                if hasattr(self.parent, 'charger_fichier'):
                    try:
                        self.parent.charger_fichier(self.filepath)
                        log_message("INFO", f"Fichier rechargé après restauration: {os.path.basename(self.filepath)}")
                    except Exception as reload_error:
                        log_message("WARNING", f"Impossible de recharger le fichier après restauration", reload_error)
                        # Ne pas afficher d'erreur à l'utilisateur car la restauration a réussi
                
            else:
                # Erreur lors de la restauration
                error_msg = restore_result.get('error', 'Erreur inconnue')
                log_message("ERREUR", f"Échec de la restauration de {backup['path']}: {error_msg}")
                messagebox.showerror(
                    "❌ Erreur de restauration",
                    f"Impossible de restaurer la sauvegarde :\n\n"
                    f"📅 {backup['name']}\n"
                    f"🔧 Erreur: {error_msg}\n\n"
                    f"💡 Vérifiez que le fichier de destination n'est pas verrouillé."
                )
                
        except Exception as e:
            # Erreur générale (problème avec l'interface, etc.)
            log_message("ERREUR", f"Erreur générale lors de la restauration de {backup.get('name', 'sauvegarde inconnue')}", e)
            messagebox.showerror(
                "❌ Erreur critique",
                f"Une erreur critique s'est produite :\n\n"
                f"🔧 Erreur: {str(e)}\n\n"
                f"💡 Veuillez redémarrer l'application si le problème persiste."
            )
    
    def _delete_backup(self, backup):
        """Supprime une sauvegarde"""
        try:
            # Confirmation
            result = messagebox.askyesno(
                "🗑️ Confirmer la suppression",
                f"Voulez-vous vraiment supprimer cette sauvegarde ?\n\n"
                f"📅 {backup['name']}\n"
                f"🕒 Créée: {backup['created'].strftime('%d/%m/%Y à %H:%M:%S')}\n"
                f"📦 Taille: {backup['size'] / (1024 * 1024):.2f} MB\n\n"
                f"⚠️ Cette action est irréversible !"
            )
            
            if not result:
                return
            
            # Supprimer le fichier
            os.remove(backup['path'])
            
            messagebox.showinfo(
                "✅ Suppression réussie",
                f"La sauvegarde a été supprimée :\n\n📅 {backup['name']}"
            )
            
            # Actualiser la liste
            self._refresh_backups()
            
        except Exception as e:
            log_message("ERREUR", f"Erreur lors de la suppression de {backup['path']}", e)
            messagebox.showerror("❌ Erreur", f"Erreur lors de la suppression:\n{str(e)}")


# Fonction utilitaire pour l'interface principale
def show_backup_manager(parent, filepath=None):
    """Affiche le gestionnaire de sauvegardes"""
    dialog = BackupDialog(parent, filepath)
    dialog.show()