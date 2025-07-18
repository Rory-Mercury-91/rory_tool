# ui/tutorial.py
# Enhanced Non-blocking Tutorial System - UPDATED
# Created for RenExtract v2.5.0

"""
Système de tutoriel amélioré aligné avec les fonctionnalités actuelles
"""

import os
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from utils.constants import VERSION, THEMES, FILE_NAMES, ensure_folders_exist
from utils.config import config_manager
from utils.logging import log_message
from utils.i18n import i18n, _

def check_first_launch():
    """Vérifie si c'est le premier lancement (pas de changement)"""
    tutorial_flag_file = FILE_NAMES["tutorial_flag"]
    return not os.path.exists(tutorial_flag_file)

def mark_tutorial_shown():
    """
    Marque que le tutoriel a été affiché
    """
    try:
        ensure_folders_exist()
        tutorial_flag_file = FILE_NAMES["tutorial_flag"]
        
        with open(tutorial_flag_file, "w", encoding="utf-8") as f:
            f.write(f"Tutorial shown on: {datetime.datetime.now().isoformat()}\n")
            f.write(f"Version: {VERSION}\n")
            f.write("This file prevents the tutorial from showing again.\n")
            f.write("Delete this file to show the tutorial on next launch.\n")
        log_message("INFO", f"Tutoriel marqué comme affiché dans {tutorial_flag_file}")
    except Exception as e:
        log_message("WARNING", "Impossible de marquer le tutoriel comme affiché", e)

def show_tutorial():
    """Affiche la fenêtre de tutoriel NON-BLOQUANTE avec contenu mis à jour"""
    import tkinter as tk
    from tkinter import ttk
    
    # Créer une fenêtre indépendante NON-BLOQUANTE
    tutorial_window = tk.Toplevel()
    tutorial_window.title(f"🎓 Guide Complet - RenExtract v{VERSION}")
    
    # Taille adaptative selon la langue
    lang = i18n.get_current_language()
    if lang == 'de':
        tutorial_window.geometry("850x750")  # Allemand = plus large
    elif lang == 'en':
        tutorial_window.geometry("800x700")  # Anglais = moyen
    else:
        tutorial_window.geometry("750x650")  # Français = plus compact
    
    tutorial_window.resizable(True, True)
    
    # Centrer la fenêtre
    tutorial_window.update_idletasks()
    x = (tutorial_window.winfo_screenwidth() // 2) - (tutorial_window.winfo_width() // 2)
    y = (tutorial_window.winfo_screenheight() // 2) - (tutorial_window.winfo_height() // 2)
    tutorial_window.geometry(f"+{x}+{y}")
    
    # Appliquer le thème
    theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
    tutorial_window.configure(bg=theme["bg"])
    
    # Variable pour la checkbox
    dont_show_again = tk.BooleanVar()
    
    # Frame principal avec scrollbar
    main_frame = tk.Frame(tutorial_window, bg=theme["bg"])
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Canvas et scrollbar
    canvas = tk.Canvas(main_frame, bg=theme["bg"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=theme["bg"])
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Header
    header_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    header_frame.pack(fill='x', pady=(0, 20))
    
    title_tutorial = tk.Label(
        header_frame,
        text=_('tutorial.title', version=VERSION),
        font=('Segoe UI Emoji', 18, 'bold'),
        bg=theme["bg"],
        fg=theme["accent"]
    )
    title_tutorial.pack()
    
    subtitle_tutorial = tk.Label(
        header_frame,
        text=_('tutorial.subtitle'),
        font=('Segoe UI Emoji', 11),
        bg=theme["bg"],
        fg=theme["fg"]
    )
    subtitle_tutorial.pack(pady=(5, 0))
    
    # Notification de non-blocage
    notice_frame = tk.Frame(scrollable_frame, bg=theme["warning"], relief='solid', bd=2)
    notice_frame.pack(fill='x', pady=(0, 20))
    
    notice_label = tk.Label(
        notice_frame,
        text=_('tutorial.non_blocking_notice'),
        font=('Segoe UI Emoji', 10, 'bold'),
        bg=theme["warning"],
        fg='#000000',
        wraplength=800
    )
    notice_label.pack(pady=10)
    
    # Contenu traduit dynamiquement
    def get_tutorial_content():
        """Contenu du tutoriel traduit selon la langue actuelle"""
        lang = i18n.get_current_language()
        
        # Contenu de base multilingue
        base_content = {
            'fr': [
                (_('tutorial.sections.overview'), [
                    "Le RenExtract v2.5.0 est un outil spécialisé pour les traductions de jeux Ren'Py.",
                    "Architecture modulaire avec extraction intelligente, protection des codes et reconstruction précise.",
                    "Compatible avec les fichiers générés par le SDK Ren'Py (commande generate translations).",
                    "Support : fichiers uniques, mode dossier, Drag & Drop, Ctrl+V, et système de glossaire permanent."
                ]),
                (_('tutorial.sections.workflow'), [
                    "1️⃣ Générez vos fichiers de traduction avec le SDK Ren'Py",
                    "2️⃣ Chargez le fichier .rpy avec les boutons ou Drag & Drop",
                    "3️⃣ Cliquez sur '⚡ Extraire' pour créer les fichiers à traduire",
                    "4️⃣ Traduisez les fichiers .txt générés",
                    "5️⃣ Cliquez sur '🔧 Reconstruire' pour créer le fichier traduit",
                    "💡 La validation automatique vérifie la cohérence"
                ]),
                (_('tutorial.sections.features'), [
                    "📚 Système de Glossaire permanent :",
                    "   • Traduction automatique des termes récurrents",
                    "   • Interface complète de gestion",
                    "   • Import/Export pour partage",
                    "",
                    "🏗️ Architecture organisée :",
                    "   • Structure par jeu : temporaires/[NomDuJeu]/",
                    "   • Validation avancée avec rapports détaillés",
                    "   • Notifications intelligentes (moins de popups !)"
                ])
            ],
            'en': [
                (_('tutorial.sections.overview'), [
                    "RenExtract v2.5.0 is a specialized tool for Ren'Py game translations.",
                    "Modular architecture with smart extraction, code protection and precise reconstruction.",
                    "Compatible with files generated by Ren'Py SDK (generate translations command).",
                    "Support: single files, folder mode, Drag & Drop, Ctrl+V, and permanent glossary system."
                ]),
                (_('tutorial.sections.workflow'), [
                    "1️⃣ Generate your translation files with Ren'Py SDK",
                    "2️⃣ Load the .rpy file with buttons or Drag & Drop",
                    "3️⃣ Click '⚡ Extract' to create files to translate",
                    "4️⃣ Translate the generated .txt files",
                    "5️⃣ Click '🔧 Reconstruct' to create the translated file",
                    "💡 Automatic validation checks consistency"
                ]),
                (_('tutorial.sections.features'), [
                    "📚 Permanent Glossary System:",
                    "   • Automatic translation of recurring terms",
                    "   • Complete management interface",
                    "   • Import/Export for sharing",
                    "",
                    "🏗️ Organized Architecture:",
                    "   • Structure by game: temporary/[GameName]/",
                    "   • Advanced validation with detailed reports",
                    "   • Smart notifications (fewer popups!)"
                ])
            ],
            'de': [
                (_('tutorial.sections.overview'), [
                    "RenExtract v2.5.0 ist ein spezialisiertes Tool für Ren'Py-Spielübersetzungen.",
                    "Modulare Architektur mit intelligentem Extrahieren, Codeschutz und präziser Rekonstruktion.",
                    "Kompatibel mit Dateien, die vom Ren'Py SDK generiert wurden (generate translations Befehl).",
                    "Unterstützung: einzelne Dateien, Ordner-Modus, Drag & Drop, Ctrl+V und permanentes Glossar-System."
                ]),
                (_('tutorial.sections.workflow'), [
                    "1️⃣ Generieren Sie Ihre Übersetzungsdateien mit dem Ren'Py SDK",
                    "2️⃣ Laden Sie die .rpy-Datei mit den Schaltflächen oder Drag & Drop",
                    "3️⃣ Klicken Sie auf '⚡ Extrahieren', um zu übersetzende Dateien zu erstellen",
                    "4️⃣ Übersetzen Sie die generierten .txt-Dateien",
                    "5️⃣ Klicken Sie auf '🔧 Rekonstruieren', um die übersetzte Datei zu erstellen",
                    "💡 Die automatische Validierung überprüft die Konsistenz"
                ]),
                (_('tutorial.sections.features'), [
                    "📚 Permanentes Glossar-System:",
                    "   • Automatische Übersetzung wiederkehrender Begriffe",
                    "   • Vollständige Verwaltungsoberfläche",
                    "   • Import/Export zum Teilen",
                    "",
                    "🏗️ Organisierte Architektur:",
                    "   • Struktur nach Spiel: temporär/[SpielName]/",
                    "   • Erweiterte Validierung mit detaillierten Berichten",
                    "   • Intelligente Benachrichtigungen (weniger Popups!)"
                ])
            ]
        }
        
        return base_content.get(lang, base_content['fr'])

    tutorial_content = get_tutorial_content()
    
    # Créer les sections avec l'ancienne méthode simple
    for section_title, section_items in tutorial_content:
        # Frame de section
        section_frame = tk.Frame(scrollable_frame, bg=theme["frame_bg"], relief='solid', bd=1)
        section_frame.pack(fill='x', pady=8, padx=10)
        
        # Titre de section
        section_title_label = tk.Label(
            section_frame,
            text=section_title,
            font=('Segoe UI Emoji', 13, 'bold'),
            bg=theme["frame_bg"],
            fg=theme["accent"]
        )
        section_title_label.pack(anchor='w', padx=15, pady=(12, 8))
        
        # Contenu de la section
        for item in section_items:
            if item == "":  # Ligne vide pour espacer
                spacer = tk.Frame(section_frame, bg=theme["frame_bg"], height=5)
                spacer.pack()
            else:
                item_label = tk.Label(
                    section_frame,
                    text=item,
                    font=('Segoe UI Emoji', 10),
                    bg=theme["frame_bg"],
                    fg=theme["fg"],
                    justify='left',
                    wraplength=650
                )
                item_label.pack(anchor='w', padx=25, pady=2)
        
        # Espacement final
        spacer = tk.Frame(section_frame, bg=theme["frame_bg"], height=10)
        spacer.pack()

    # Separator
    separator_frame = tk.Frame(scrollable_frame, bg=theme["bg"], height=2)
    separator_frame.pack(fill='x', pady=15)
    
    # Checkbox "Ne plus afficher" - AU-DESSUS des boutons
    checkbox_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    checkbox_frame.pack(fill='x', pady=(20, 10))
    
    checkbox = tk.Checkbutton(
        checkbox_frame,
        text=_('tutorial.dont_show_again'),
        variable=dont_show_again,
        font=('Segoe UI Emoji', 10),
        bg=theme["bg"],
        fg=theme["fg"],
        selectcolor=theme["frame_bg"],
        activebackground=theme["bg"],
        activeforeground=theme["fg"]
    )
    checkbox.pack(anchor='w', padx=10)
    
    # Frame pour les contrôles du bas (boutons)
    bottom_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    bottom_frame.pack(fill='x', pady=(0, 15))
    
    # Boutons
    buttons_frame = tk.Frame(bottom_frame, bg=theme["bg"])
    buttons_frame.pack(side='left', padx=10)
    
    def close_tutorial():
        mark_tutorial_shown()
        if tutorial_window is not None:
            try:
                if tutorial_window.winfo_exists():
                    tutorial_window.destroy()
            except Exception:
                pass
    
    def open_tutorial_again():
        if tutorial_window is not None:
            try:
                if tutorial_window.winfo_exists():
                    tutorial_window.destroy()
            except Exception:
                pass
    
    btn_close = tk.Button(
        buttons_frame,
        text=_('tutorial.understood_button'),
        font=('Segoe UI Emoji', 11, 'bold'),
        bg=theme["accent"],
        fg="#000000",
        activebackground='#157347',
        bd=0,
        pady=10,
        padx=25,
        command=close_tutorial
    )
    btn_close.pack(side='right', padx=(10, 0))
    
    btn_later = tk.Button(
        buttons_frame,
        text=_('tutorial.review_later_button'),
        font=('Segoe UI Emoji', 10),
        bg=theme["warning"],
        fg='#000000',
        activebackground='#ffcc02',
        bd=0,
        pady=8,
        padx=15,
        command=open_tutorial_again
    )
    btn_later.pack(side='right')
    
    # Configurer le canvas et scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Permettre le scroll avec la molette
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    tutorial_window.bind("<MouseWheel>", on_mousewheel)
    
    # Bind pour les systèmes Linux
    def on_button_4(event):
        canvas.yview_scroll(-1, "units")
    
    def on_button_5(event):
        canvas.yview_scroll(1, "units")
    
    tutorial_window.bind("<Button-4>", on_button_4)
    tutorial_window.bind("<Button-5>", on_button_5)
    
    # Focus sur le bouton principal
    btn_close.focus_set()
    
    # Gestionnaire de fermeture
    def on_closing():
        try:
            if tutorial_window is not None:
                if tutorial_window.winfo_exists():
                    tutorial_window.destroy()
        except:
            pass
    
    tutorial_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    log_message("INFO", "Tutoriel v2.5.0 affiché (non-bloquant)")

def create_section(parent, theme, title, items):
    """
    Crée une section du tutoriel avec style amélioré
    
    Args:
        parent: Widget parent
        theme: Thème de couleurs
        title: Titre de la section
        items: Liste des éléments de la section
    """
    try:
        # Créer un frame conteneur pour centrer la section
        container_frame = tk.Frame(parent, bg=theme["bg"])
        container_frame.pack(fill='x', pady=8)
        
        # Largeur uniforme pour tous les cadres
        section_frame = tk.Frame(container_frame, bg=theme["frame_bg"], relief='solid', bd=1, width=750)
        section_frame.pack(anchor='w', padx=10)
        
        # Titre de section
        section_title = tk.Label(
            section_frame,
            text=title,
            font=('Segoe UI Emoji', 13, 'bold'),
            bg=theme["frame_bg"],
            fg=theme["accent"]
        )
        section_title.pack(anchor='center', padx=15, pady=(12, 8))
        
        # Contenu de la section
        for item in items:
            if item == "":  # Ligne vide pour espacer
                spacer = tk.Frame(section_frame, bg=theme["frame_bg"], height=5)
                spacer.pack()
            else:
                # Créer un frame pour centrer le contenu
                item_frame = tk.Frame(section_frame, bg=theme["frame_bg"])
                item_frame.pack(fill='x', pady=2)
                
                item_label = tk.Label(
                    item_frame,
                    text=item,
                    font=('Segoe UI Emoji', 10),
                    bg=theme["frame_bg"],
                    fg=theme["fg"],
                    justify='left',
                    wraplength=700
                )
                item_label.pack(anchor='w', padx=15)
        
        # Espacement final
        spacer = tk.Frame(section_frame, bg=theme["frame_bg"], height=10)
        spacer.pack()
        
    except Exception as e:
        log_message("WARNING", f"Erreur création section tutoriel: {str(e)}")

def show_quick_help(parent, topic=None):
    """Affiche une aide contextuelle traduite avec centrage dynamique"""
    
    if topic not in ['glossary', 'extraction', 'reconstruction', 'validation', 'files']:
        return
    
    # Créer une fenêtre avec le même style
    tutorial_window = tk.Toplevel()
    tutorial_window.title(f"{_('help_specialized.' + topic + '.title')} - RenExtract v{VERSION}")
    
    # ✅ NOUVEAU : Taille dynamique selon le contenu
    # Estimation de la taille selon le topic et la langue
    lang = i18n.get_current_language()
    if topic == 'glossary':
        # Glossaire a plus de sections, donc plus grand
        width, height = 650, 600
    elif topic == 'extraction':
        width, height = 600, 500
    elif topic == 'reconstruction':
        width, height = 600, 450
    elif topic == 'validation':
        width, height = 600, 450
    elif topic == 'files':
        width, height = 600, 400
    
    # Ajuster selon la langue (allemand = plus long)
    if lang == 'de':
        width += 50
    elif lang == 'en':
        width += 20
    
    tutorial_window.geometry(f"{width}x{height}")
    tutorial_window.resizable(True, True)
    
    # Centrer la fenêtre
    tutorial_window.update_idletasks()
    x = (tutorial_window.winfo_screenwidth() // 2) - (tutorial_window.winfo_width() // 2)
    y = (tutorial_window.winfo_screenheight() // 2) - (tutorial_window.winfo_height() // 2)
    tutorial_window.geometry(f"+{x}+{y}")
    
    # Appliquer le thème
    theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
    tutorial_window.configure(bg=theme["bg"])
    
    # Frame principal avec scrollbar (MÊME STRUCTURE)
    main_frame = tk.Frame(tutorial_window, bg=theme["bg"])
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Canvas et scrollbar
    canvas = tk.Canvas(main_frame, bg=theme["bg"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=theme["bg"])
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # ✅ NOUVEAU : Centrage dynamique du contenu
    def center_content():
        """Centre dynamiquement le contenu selon la largeur"""
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        scrollable_width = scrollable_frame.winfo_reqwidth()
        
        if scrollable_width < canvas_width:
            # Centrer le contenu horizontalement
            x_offset = (canvas_width - scrollable_width) // 2
            canvas.coords(canvas.find_withtag("all")[0], x_offset, 0)
    
    # Header (MÊME STYLE) avec centrage
    header_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    header_frame.pack(fill='x', pady=(0, 20))
    
    title_tutorial = tk.Label(
        header_frame,
        text=_('help_specialized.' + topic + '.title'),
        font=('Segoe UI Emoji', 18, 'bold'),
        bg=theme["bg"],
        fg=theme["accent"]
    )
    title_tutorial.pack(anchor='center')
    
    subtitle_tutorial = tk.Label(
        header_frame,
        text=_('help_specialized.' + topic + '.subtitle'),
        font=('Segoe UI Emoji', 11),
        bg=theme["bg"],
        fg=theme["fg"]
    )
    subtitle_tutorial.pack(anchor='center', pady=(5, 0))
    
    # ========== SECTIONS STYLÉES ==========
    # Définir les sections selon le topic avec leur contenu traduit
    if topic == 'glossary':
        sections = [
            (_('help_specialized.glossary.sections.objective.title'), [
                _('help_specialized.glossary.sections.objective.content.0'),
                _('help_specialized.glossary.sections.objective.content.1')
            ]),
            (_('help_specialized.glossary.sections.usage.title'), [
                _('help_specialized.glossary.sections.usage.content.0'),
                _('help_specialized.glossary.sections.usage.content.1'),
                _('help_specialized.glossary.sections.usage.content.2')
            ]),
            (_('help_specialized.glossary.sections.features.title'), [
                _('help_specialized.glossary.sections.features.content.0'),
                _('help_specialized.glossary.sections.features.content.1'),
                _('help_specialized.glossary.sections.features.content.2'),
                _('help_specialized.glossary.sections.features.content.3')
            ]),
            (_('help_specialized.glossary.sections.examples.title'), [
                _('help_specialized.glossary.sections.examples.content.0'),
                _('help_specialized.glossary.sections.examples.content.1'),
                _('help_specialized.glossary.sections.examples.content.2'),
                _('help_specialized.glossary.sections.examples.content.3')
            ]),
            (_('help_specialized.glossary.sections.best_practices.title'), [
                _('help_specialized.glossary.sections.best_practices.content.0'),
                _('help_specialized.glossary.sections.best_practices.content.1'),
                _('help_specialized.glossary.sections.best_practices.content.2'),
                _('help_specialized.glossary.sections.best_practices.content.3'),
                _('help_specialized.glossary.sections.best_practices.content.4'),
                _('help_specialized.glossary.sections.best_practices.content.5')
            ])
        ]
    elif topic == 'extraction':
        sections = [
            (_('help_specialized.extraction.sections.text_separation.title'), [
                _('help_specialized.extraction.sections.text_separation.content.0'),
                _('help_specialized.extraction.sections.text_separation.content.1'),
                _('help_specialized.extraction.sections.text_separation.content.2'),
                _('help_specialized.extraction.sections.text_separation.content.3')
            ]),
            (_('help_specialized.extraction.sections.automatic_protection.title'), [
                _('help_specialized.extraction.sections.automatic_protection.content.0'),
                _('help_specialized.extraction.sections.automatic_protection.content.1'),
                _('help_specialized.extraction.sections.automatic_protection.content.2')
            ]),
            (_('help_specialized.extraction.sections.organized_structure.title'), [
                _('help_specialized.extraction.sections.organized_structure.content.0'),
                _('help_specialized.extraction.sections.organized_structure.content.1')
            ])
        ]
    elif topic == 'reconstruction':
        sections = [
            (_('help_specialized.reconstruction.sections.process.title'), [
                _('help_specialized.reconstruction.sections.process.content.0'),
                _('help_specialized.reconstruction.sections.process.content.1'),
                _('help_specialized.reconstruction.sections.process.content.2')
            ]),
            (_('help_specialized.reconstruction.sections.saving.title'), [
                _('help_specialized.reconstruction.sections.saving.content.0'),
                _('help_specialized.reconstruction.sections.saving.content.1'),
                _('help_specialized.reconstruction.sections.saving.content.2')
            ])
        ]
    elif topic == 'validation':
        sections = [
            (_('help_specialized.validation.sections.controls.title'), [
                _('help_specialized.validation.sections.controls.content.0'),
                _('help_specialized.validation.sections.controls.content.1'),
                _('help_specialized.validation.sections.controls.content.2')
            ]),
            (_('help_specialized.validation.sections.reports.title'), [
                _('help_specialized.validation.sections.reports.content.0'),
                _('help_specialized.validation.sections.reports.content.1'),
                _('help_specialized.validation.sections.reports.content.2')
            ])
        ]
    elif topic == 'files':
        sections = [
            (_('help_specialized.files.sections.file_tree.title'), [
                _('help_specialized.files.sections.file_tree.content.0'),
                _('help_specialized.files.sections.file_tree.content.1'),
                _('help_specialized.files.sections.file_tree.content.2'),
                _('help_specialized.files.sections.file_tree.content.3'),
                _('help_specialized.files.sections.file_tree.content.4')
            ])
        ]
    
    # Créer les sections avec centrage
    for section_title, content_items in sections:
        create_section(scrollable_frame, theme, section_title, content_items)
    
    # Bouton fermer (MÊME STYLE) avec centrage
    close_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    close_frame.pack(fill='x', pady=(20, 15))
    
    btn_close = tk.Button(
        close_frame,
        text=_('help_specialized.' + topic + '.understood_button'),
        font=('Segoe UI Emoji', 11, 'bold'),
        bg=theme["accent"],
        fg="#000000",
        activebackground='#157347',
        bd=0,
        pady=10,
        padx=25,
        command=lambda: tutorial_window.destroy() if tutorial_window is not None and tutorial_window.winfo_exists() else None
    )
    btn_close.pack(anchor='center')
    
    # Configurer canvas et scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # ✅ NOUVEAU : Centrage après chargement
    tutorial_window.after(100, center_content)
    
    # Scroll avec molette
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    tutorial_window.bind("<MouseWheel>", on_mousewheel)
    tutorial_window.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    tutorial_window.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    
    # ✅ NOUVEAU : Centrage lors du redimensionnement
    tutorial_window.bind("<Configure>", lambda e: tutorial_window.after(50, center_content))
    
    btn_close.focus_set()
    tutorial_window.protocol("WM_DELETE_WINDOW", tutorial_window.destroy)
    
    log_message("INFO", f"Aide {topic} affichée avec style harmonisé, traductions et centrage dynamique")

def show_minimal_tutorial():
    """✅ MODIFIÉ : Guide express traduit avec réduction de contenu"""
    tutorial_window = tk.Toplevel()
    tutorial_window.title(_('tutorial.express_title', version=VERSION))
    tutorial_window.geometry("600x500")  # ✅ Plus petit
    tutorial_window.resizable(True, True)
    
    # Centrer la fenêtre
    tutorial_window.update_idletasks()
    x = (tutorial_window.winfo_screenwidth() // 2) - (tutorial_window.winfo_width() // 2)
    y = (tutorial_window.winfo_screenheight() // 2) - (tutorial_window.winfo_height() // 2)
    tutorial_window.geometry(f"+{x}+{y}")
    
    # Appliquer le thème
    theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
    tutorial_window.configure(bg=theme["bg"])
    
    # Frame principal avec scrollbar (MÊME STRUCTURE que show_tutorial)
    main_frame = tk.Frame(tutorial_window, bg=theme["bg"])
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Canvas et scrollbar
    canvas = tk.Canvas(main_frame, bg=theme["bg"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=theme["bg"])
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # ✅ NOUVEAU : Centrage dynamique du contenu
    def center_content():
        """Centre dynamiquement le contenu selon la largeur"""
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        scrollable_width = scrollable_frame.winfo_reqwidth()
        if scrollable_width < canvas_width:
            x_offset = (canvas_width - scrollable_width) // 2
            canvas.coords(canvas.find_withtag("all")[0], x_offset, 0)

    # Header (MÊME STYLE)
    header_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    header_frame.pack(fill='x', pady=(0, 20))
    
    title_tutorial = tk.Label(
        header_frame,
        text=_('tutorial.express_title', version=VERSION),
        font=('Segoe UI Emoji', 18, 'bold'),
        bg=theme["bg"],
        fg=theme["accent"]
    )
    title_tutorial.pack(anchor='center')
    
    subtitle_tutorial = tk.Label(
        header_frame,
        text=_('help.descriptions.express_guide'),
        font=('Segoe UI Emoji', 11),
        bg=theme["bg"],
        fg=theme["fg"]
    )
    subtitle_tutorial.pack(anchor='center', pady=(5, 0))
    
    # ========== CONTENU AVEC SECTIONS STYLÉES ==========
    
    # ✅ CONTENU RÉDUIT et traduit
    express_content = [
        (_('tutorial.sections.quick_workflow'), [
            _('tutorial.content.quick_steps')
        ]),
        (_('tutorial.sections.new_features'), [
            _('tutorial.content.glossary_brief'),
            _('tutorial.content.architecture_brief'),
            _('tutorial.content.notifications_brief')
        ]),
        (_('tutorial.sections.shortcuts'), [
            _('tutorial.content.drag_drop_info'),
            _('tutorial.content.ctrl_v_info'),
            _('tutorial.content.buttons_info')
        ])
    ]
    
    for section_title, section_items in express_content:
        create_section(scrollable_frame, theme, section_title, section_items)
    
    # Bouton fermer (MÊME STYLE)
    close_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    close_frame.pack(fill='x', pady=(20, 15))
    
    btn_close = tk.Button(
        close_frame,
        text=_('tutorial.understood_button'),
        font=('Segoe UI Emoji', 11, 'bold'),
        bg=theme["accent"],
        fg="#000000",
        activebackground='#157347',
        bd=0,
        pady=10,
        padx=25,
        command=tutorial_window.destroy
    )
    btn_close.pack(anchor='center')
    
    # Configurer canvas et scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ✅ Centrage après chargement
    tutorial_window.after(100, center_content)
    # ✅ Centrage lors du redimensionnement
    tutorial_window.bind("<Configure>", lambda e: tutorial_window.after(50, center_content))
    
    # Scroll avec molette
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    tutorial_window.bind("<MouseWheel>", on_mousewheel)
    tutorial_window.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    tutorial_window.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    
    btn_close.focus_set()
    tutorial_window.protocol("WM_DELETE_WINDOW", tutorial_window.destroy)
    
    log_message("INFO", "Guide Express v2.5.0 affiché avec style harmonisé")

def show_whats_new():
    """✅ MODIFIÉ : Nouveautés traduites avec focus sur réduction popups"""
    tutorial_window = tk.Toplevel()
    tutorial_window.title(_('tutorial.whats_new_title', version=VERSION))
    tutorial_window.geometry("500x600")  # ✅ Plus compact
    tutorial_window.resizable(True, True)
    
    # Centrer la fenêtre
    tutorial_window.update_idletasks()
    x = (tutorial_window.winfo_screenwidth() // 2) - (tutorial_window.winfo_width() // 2)
    y = (tutorial_window.winfo_screenheight() // 2) - (tutorial_window.winfo_height() // 2)
    tutorial_window.geometry(f"+{x}+{y}")
    
    # Appliquer le thème
    theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
    tutorial_window.configure(bg=theme["bg"])
    
    # Frame principal avec scrollbar (MÊME STRUCTURE)
    main_frame = tk.Frame(tutorial_window, bg=theme["bg"])
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Canvas et scrollbar
    canvas = tk.Canvas(main_frame, bg=theme["bg"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=theme["bg"])
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # ✅ NOUVEAU : Centrage dynamique du contenu
    def center_content():
        """Centre dynamiquement le contenu selon la largeur"""
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        scrollable_width = scrollable_frame.winfo_reqwidth()
        if scrollable_width < canvas_width:
            x_offset = (canvas_width - scrollable_width) // 2
            canvas.coords(canvas.find_withtag("all")[0], x_offset, 0)

    # Header (MÊME STYLE)
    header_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    header_frame.pack(fill='x', pady=(0, 20))
    
    title_tutorial = tk.Label(
        header_frame,
        text=_('tutorial.whats_new_title', version=VERSION),
        font=('Segoe UI Emoji', 18, 'bold'),
        bg=theme["bg"],
        fg=theme["accent"]
    )
    title_tutorial.pack(anchor='center')
    
    subtitle_tutorial = tk.Label(
        header_frame,
        text=_('help.descriptions.whats_new'),
        font=('Segoe UI Emoji', 11),
        bg=theme["bg"],
        fg=theme["fg"]
    )
    subtitle_tutorial.pack(anchor='center', pady=(5, 0))
    
    # ========== CONTENU AVEC SECTIONS STYLÉES ==========
    
    # ✅ FOCUS sur les vraies nouveautés importantes
    whats_new_content = [
        (_('tutorial.sections.i18n_system'), [
            "🌍 " + _('tutorial.content.i18n_dynamic'),
            "🎯 " + _('tutorial.content.i18n_support'),
            "⚡ " + _('tutorial.content.i18n_realtime')
        ]),
        (_('tutorial.sections.smart_notifications'), [
            "🔕 " + _('tutorial.content.popup_reduction'),
            "💡 " + _('tutorial.content.toast_system'),
            "📊 " + _('tutorial.content.status_bar'),
            "⚠️ " + _('tutorial.content.critical_only')
        ]),
        (_('tutorial.sections.improved_ux'), [
            "🎨 " + _('tutorial.content.theme_integration'),
            "⚙️ " + _('tutorial.content.dynamic_buttons'),
            "🌐 " + _('tutorial.content.language_menu')
        ])
    ]
    
    for section_title, section_items in whats_new_content:
        create_section(scrollable_frame, theme, section_title, section_items)
    
    # Bouton fermer (MÊME STYLE)
    close_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    close_frame.pack(fill='x', pady=(20, 15))
    
    btn_close = tk.Button(
        close_frame,
        text=_('tutorial.understood_button'),
        font=('Segoe UI Emoji', 11, 'bold'),
        bg=theme["accent"],
        fg="#000000",
        activebackground='#157347',
        bd=0,
        pady=10,
        padx=25,
        command=tutorial_window.destroy
    )
    btn_close.pack(anchor='center')
    
    # Configurer canvas et scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ✅ Centrage après chargement
    tutorial_window.after(100, center_content)
    # ✅ Centrage lors du redimensionnement
    tutorial_window.bind("<Configure>", lambda e: tutorial_window.after(50, center_content))
    
    # Scroll avec molette
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    tutorial_window.bind("<MouseWheel>", on_mousewheel)
    tutorial_window.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    tutorial_window.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    
    btn_close.focus_set()
    tutorial_window.protocol("WM_DELETE_WINDOW", tutorial_window.destroy)
    
    log_message("INFO", "Nouveautés v2.5.0 affichées avec style harmonisé")

def create_tutorial_menu():
    """Crée un menu contextuel pour différents types d'aide"""
    def show_menu():
        # ✅ S'assurer que le système i18n est initialisé
        try:
            i18n.load_translations()
            
        except Exception as e:
            print(f"⚠️ Erreur initialisation i18n: {e}")
        
        menu_window = tk.Toplevel()
        menu_window.title(_('help.title', version=VERSION))
        menu_window.geometry("500x800")
        
        # Centrer la fenêtre
        menu_window.update_idletasks()
        x = (menu_window.winfo_screenwidth() // 2) - (menu_window.winfo_width() // 2)
        y = (menu_window.winfo_screenheight() // 2) - (menu_window.winfo_height() // 2)
        menu_window.geometry(f"+{x}+{y}")
        
        # Appliquer le thème
        theme = THEMES["dark"] if config_manager.is_dark_mode_enabled() else THEMES["light"]
        menu_window.configure(bg=theme["bg"])
        
        # Titre
        title_label = tk.Label(
            menu_window,
            text=_('help.subtitle'),
            font=('Segoe UI Emoji', 14, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        title_label.pack(pady=20)
        
        # Boutons d'aide
        button_frame = tk.Frame(menu_window, bg=theme["bg"])
        button_frame.pack(fill='both', expand=True, padx=20)
        
        buttons = [
            (_('help.buttons.complete_guide', version=VERSION), _('help.descriptions.complete_guide'), show_tutorial),
            (_('help.buttons.express_guide'), _('help.descriptions.express_guide'), show_minimal_tutorial),
            (_('help.buttons.whats_new', version=VERSION), _('help.descriptions.whats_new'), show_whats_new),
            (_('help.buttons.glossary_help'), _('help.descriptions.glossary_help'), lambda: show_quick_help(None, 'glossary')),
            (_('help.buttons.extraction_help'), _('help.descriptions.extraction_help'), lambda: show_quick_help(None, 'extraction')),
            (_('help.buttons.reconstruction_help'), _('help.descriptions.reconstruction_help'), lambda: show_quick_help(None, 'reconstruction')),
            (_('help.buttons.validation_help'), _('help.descriptions.validation_help'), lambda: show_quick_help(None, 'validation')),
            (_('help.buttons.file_organization', version=VERSION), _('help.descriptions.file_organization', version=VERSION), lambda: show_quick_help(None, 'files'))
        ]
        
        for i, (text, desc, command) in enumerate(buttons):
            btn_frame = tk.Frame(button_frame, bg=theme["frame_bg"], relief='solid', bd=1)
            btn_frame.pack(fill='x', pady=3)
            
            btn = tk.Button(
                btn_frame,
                text=text,
                font=('Segoe UI Emoji', 10, 'bold'),
                bg=theme["accent"],
                fg="#000000",
                relief='flat',
                bd=0,
                pady=8,
                command=lambda cmd=command: [cmd(), menu_window.destroy()]
            )
            btn.pack(fill='x', padx=8, pady=4)
            
            desc_label = tk.Label(
                btn_frame,
                text=desc,
                font=('Segoe UI Emoji', 8),
                bg=theme["frame_bg"],
                fg=theme["fg"]
            )
            desc_label.pack(pady=(0, 4))
        
        # Bouton fermer
        close_btn = tk.Button(
            menu_window,
            text=_('buttons.close'),
            font=('Segoe UI Emoji', 10),
            bg=theme["danger"],
            fg="#000000",
            relief='flat',
            bd=0,
            pady=8,
            command=menu_window.destroy
        )
        close_btn.pack(pady=10)
    
    return show_menu

def show_help_menu():
    """Affiche le menu d'aide principal"""
    menu_func = create_tutorial_menu()
    menu_func()

# Export des fonctions principales
__all__ = [
    'show_tutorial',
    'show_quick_help', 
    'show_help_menu',
    'check_first_launch',
    'mark_tutorial_shown',
    'show_minimal_tutorial',
    'show_whats_new'
]