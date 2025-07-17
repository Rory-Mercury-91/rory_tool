# ui/tutorial.py
# Enhanced Non-blocking Tutorial System - UPDATED
# Created for Traducteur Ren'Py Pro v2.4.2

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

def check_first_launch():
    """
    Vérifie si c'est le premier lancement de l'application
    
    Returns:
        bool: True si c'est le premier lancement
    """
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
    tutorial_window.title(f"🎓 Guide Complet - Traducteur Ren'Py Pro v{VERSION}")
    tutorial_window.geometry("700x800")
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
        text=f"🎓 Traducteur Ren'Py Pro v{VERSION}",
        font=('Segoe UI Emoji', 18, 'bold'),
        bg=theme["bg"],
        fg=theme["accent"]
    )
    title_tutorial.pack()
    
    subtitle_tutorial = tk.Label(
        header_frame,
        text="Guide complet avec toutes les fonctionnalités actuelles",
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
        text="💡 Cette fenêtre est non-bloquante : vous pouvez utiliser l'application simultanément !",
        font=('Segoe UI Emoji', 10, 'bold'),
        bg=theme["warning"],
        fg='#000000',
        wraplength=800
    )
    notice_label.pack(pady=10)
    
    # ==================== CONTENU DU TUTORIEL ACTUALISÉ ====================
    
    # Section 1: Vue d'ensemble
    create_section(scrollable_frame, theme, "🎯 Vue d'ensemble", [
        "Le Traducteur Ren'Py Pro v2.4.2 est un outil spécialisé pour les traductions de jeux Ren'Py.",
        "Architecture modulaire avec extraction intelligente, protection des codes et reconstruction précise.",
        "Compatible avec les fichiers générés par le SDK Ren'Py (commande generate translations).",
        "Support : fichiers uniques, mode dossier, Drag & Drop, Ctrl+V, et système de glossaire permanent."
    ])
    
    # Section 2: Workflow complet
    create_section(scrollable_frame, theme, "📋 Workflow de traduction", [
        "1️⃣ Générez vos fichiers de traduction avec le SDK Ren'Py (comme d'habitude)",
        "2️⃣ Chargez le fichier .rpy :",
        "   • Boutons '📂 Ouvrir Fichier .rpy' ou '📁 Ouvrir Dossier'",
        "   • Drag & Drop du fichier dans la zone de texte",
        "   • Mode Ctrl+V pour coller du contenu Ren'Py",
        "3️⃣ Cliquez sur '⚡ Extraire' pour créer les fichiers à traduire",
        "4️⃣ Traduisez les fichiers .txt générés avec votre outil préféré",
        "5️⃣ Cliquez sur '🔧 Reconstruire' pour créer le fichier .rpy traduit",
        "💡 La validation automatique vérifie la cohérence OLD/NEW"
    ])
    
    # Section 3: Nouveautés v2.4.2
    create_section(scrollable_frame, theme, "🆕 Nouveautés v2.4.2", [
        "📚 Système de Glossaire permanent :",
        "   • Traduction automatique des termes récurrents (ex: 'Sigh' → 'Soupir')",
        "   • Interface complète : ajout, modification, suppression, recherche",
        "   • Import/Export de glossaires pour partage",
        "   • Protection automatique lors de l'extraction",
        "",
        "🏗️ Architecture refactorisée :",
        "   • Structure organisée par jeu : temporaires/[NomDuJeu]/",
        "   • Modules enhanced pour extraction et reconstruction",
        "   • Suppression de la protection des points de suspension",
        "   • Validation avancée avec détection d'erreurs"
    ])
    
    # Section 4: Structure des fichiers
    create_section(scrollable_frame, theme, "📁 Organisation des fichiers", [
        "📦 Structure automatique organisée par jeu :",
        "",
        "📁 temporaires/[NomDuJeu]/",
        "  ├── 📁 fichiers_a_traduire/",
        "  │   ├── [nom].txt : Textes principaux à traduire",
        "  │   ├── [nom]_asterix.txt : Expressions *entre astérisques*",
        "  │   ├── [nom]_empty.txt : Textes vides et espaces",
        "  │   └── [nom]_glossary.txt : Termes du glossaire (lecture seule)",
        "  └── 📁 fichiers_a_ne_pas_traduire/",
        "      ├── [nom]_mapping.txt : Codes protégés",
        "      ├── [nom]_positions.json : Données de reconstruction",
        "      └── [nom]_glossary_mapping.txt : Mapping du glossaire",
        "",
        "📁 sauvegardes/[NomDuJeu]/ : Sauvegardes automatiques",
        "📁 avertissements/[NomDuJeu]/ : Rapports de validation",
        "📁 dossier_configs/ : Configuration et logs"
    ])
    
    # Section 5: Modes d'entrée
    create_section(scrollable_frame, theme, "🎯 Modes d'entrée disponibles", [
        "📂 Fichier unique : Bouton '📂 Ouvrir Fichier .rpy'",
        "📁 Mode dossier : Bouton '📁 Ouvrir Dossier' pour traitement en lot",
        "",
        "🎯 Mode Drag & Drop (bouton violet '🎯 D&D') :",
        "   • Glissez directement vos fichiers .rpy dans la zone de texte",
        "   • Support dossiers complets",
        "   • Indication visuelle lors du survol",
        "",
        "📋 Mode Ctrl+V (bouton violet '📋 Ctrl+V') :",
        "   • Collez du contenu Ren'Py depuis le presse-papier",
        "   • Idéal pour traductions partielles ou corrections ponctuelles",
        "   • Détection automatique du contenu Ren'Py",
        "",
        "💡 Basculez entre les modes avec le bouton violet dans la barre d'outils"
    ])
    
    # Section 6: Système de Glossaire
    create_section(scrollable_frame, theme, "📚 Système de Glossaire", [
        "🎯 Objectif : Traduire automatiquement les termes récurrents",
        "",
        "📝 Utilisation :",
        "1. Cliquez sur '📚 Glossaire' dans la barre d'outils",
        "2. Ajoutez vos paires Original → Traduction",
        "3. Les termes seront automatiquement protégés lors de l'extraction",
        "4. Ils seront traduits lors de la reconstruction",
        "",
        "🔧 Fonctionnalités :",
        "   • Recherche en temps réel dans les entrées",
        "   • Validation des entrées (détection des problèmes)",
        "   • Import/Export pour partager des glossaires",
        "   • Statistiques complètes",
        "",
        "💡 Exemples d'utilisation :",
        "   • 'Sigh' → 'Soupir'",
        "   • 'Hmm' → 'Hmm'",
        "   • 'Yeah' → 'Ouais'",
        "   • Noms de personnages, lieux récurrents"
    ])
    
    # Section 7: Fonctionnalités avancées
    create_section(scrollable_frame, theme, "🚀 Fonctionnalités avancées", [
        "🛡️ Sauvegardes automatiques :",
        "   • Créées avant chaque extraction dans sauvegardes/[NomDuJeu]/",
        "   • Gestionnaire intégré avec '🛡️ Sauvegardes'",
        "   • Restauration en un clic",
        "",
        "✅ Validation intelligente (activable/désactivable) :",
        "   • Vérification cohérence OLD/NEW",
        "   • Détection balises orphelines, placeholders malformés",
        "   • Rapports détaillés dans avertissements/[NomDuJeu]/",
        "",
        "📊 Statistiques et performance :",
        "   • Temps d'extraction et reconstruction affichés",
        "   • Compteurs de textes, astérisques, vides",
        "   • Logs détaillés dans dossier_configs/",
        "",
        "🎨 Interface adaptative :",
        "   • Thèmes sombre/clair (bouton ☀️/🌙)",
        "   • Auto-Open configurable (bouton '📂 Auto')",
        "   • Messages d'aide contextuels"
    ])
    
    # Section 8: Protection des codes
    create_section(scrollable_frame, theme, "🔒 Protection automatique des codes", [
        "Le traducteur protège automatiquement :",
        "",
        "🏷️ Balises Ren'Py : {b}, {i}, {color=#hex}, {size=20}, etc.",
        "📝 Variables : [player_name], [count], [item], etc.",
        "🔧 Codes spéciaux : \\n, %s, %(variable)s, --, etc.",
        "⭐ Expressions entre astérisques : *action*, *pensée*",
        "📚 Termes du glossaire : Remplacés par (GLO001), (GLO002), etc.",
        "🔳 Textes vides : \"\", \" \", \"  \", guillemets échappés \\\"",
        "",
        "⚠️ IMPORTANT :",
        "• NE JAMAIS modifier les codes (01), (02), (GLO001), (D1), (C1)...",
        "• Ces placeholders sont automatiquement restaurés",
        "• La validation détecte les modifications non autorisées"
    ])
    
    # Section 9: Mode dossier et traitement en lot
    create_section(scrollable_frame, theme, "📁 Mode dossier et traitement en lot", [
        "🎯 Activation : Bouton '📁 Ouvrir Dossier'",
        "",
        "📋 Workflow :",
        "1. Sélectionnez un dossier contenant des fichiers .rpy",
        "2. Le premier fichier s'ouvre automatiquement",
        "3. Effectuez : Extraire → Traduire → Reconstruire",
        "4. Une popup propose d'ouvrir le fichier suivant",
        "5. Répétez jusqu'à traitement complet du dossier",
        "",
        "💡 Avantages :",
        "   • Traitement séquentiel intelligent",
        "   • Compteur de fichiers restants dans le titre",
        "   • Structure organisée maintenue par jeu",
        "   • Possibilité d'interrompre et reprendre"
    ])
    
    # Section 10: Résolution de problèmes
    create_section(scrollable_frame, theme, "🔧 Résolution de problèmes", [
        "❌ 'Fichier non valide' :",
        "   → Vérifiez que c'est un .rpy de traduction Ren'Py (pas un script de jeu)",
        "",
        "❌ 'Validation échouée' :",
        "   → Vérifiez d'avoir traduit TOUTES les lignes des fichiers .txt",
        "   → Consultez le fichier d'avertissement créé",
        "",
        "❌ 'Placeholders malformés' :",
        "   → N'avez pas modifié les codes (01), (02), (GLO001)...",
        "   → Réextrayez le fichier si nécessaire",
        "",
        "❌ 'Drag & Drop ne fonctionne pas' :",
        "   → Votre système ne supporte peut-être pas le D&D",
        "   → Basculez en mode Ctrl+V (bouton violet)",
        "",
        "❌ 'Fichier _empty.txt' problématique :",
        "   → Ce fichier peut contenir des lignes vides - c'est normal",
        "   → Ne supprimez pas les lignes, traduisez-les même si vides",
        "",
        "💡 Diagnostic :",
        "   • Consultez dossier_configs/log.txt pour les détails",
        "   • Utilisez '⚠️ Avertissements' pour voir les rapports",
        "   • Le bouton '🔄 Réinitialiser' nettoie la base de données"
    ])
    
    # Section 11: Raccourcis et astuces
    create_section(scrollable_frame, theme, "⌨️ Raccourcis et astuces", [
        "🖱️ Interface :",
        "   • Double-cliquez sur la zone vide pour ouvrir un fichier",
        "   • Glissez un dossier entier pour activer le mode batch",
        "",
        "🎛️ Boutons utiles :",
        "   • '🔄 Réinitialiser' : Nettoie sans perdre le fichier actuel",
        "   • '📁 Temporaire' : Ouvre le dossier du jeu en cours",
        "   • '⚠️ Avertissements' : Consulte les rapports de validation",
        "",
        "⚙️ Configuration :",
        "   • '📂 Auto' : Active/désactive l'ouverture automatique des fichiers",
        "   • '✅ Valid' : Active/désactive la validation (plus rapide si OFF)",
        "   • '🌙/☀️' : Bascule entre thème sombre et clair",
        "",
        "📚 Glossaire :",
        "   • Configurez d'abord vos termes les plus fréquents",
        "   • Utilisez des mots complets pour éviter les remplacements indésirables",
        "   • Exportez votre glossaire pour le partager ou le sauvegarder",
        "",
        "🎯 Modes d'entrée :",
        "   • D&D pour fichiers complets, Ctrl+V pour extraits",
        "   • Mode Ctrl+V idéal pour mises à jour partielles"
    ])
    
    # ==================== FIN DU CONTENU ====================
    
    # Separator
    separator_frame = tk.Frame(scrollable_frame, bg=theme["bg"], height=2)
    separator_frame.pack(fill='x', pady=15)
    
    # Frame pour les contrôles du bas
    bottom_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    bottom_frame.pack(fill='x', pady=(0, 15))
    
    # Checkbox "Ne plus afficher"
    checkbox_frame = tk.Frame(bottom_frame, bg=theme["bg"])
    checkbox_frame.pack(side='left')
    
    checkbox = tk.Checkbutton(
        checkbox_frame,
        text="Ne plus afficher ce guide au démarrage",
        variable=dont_show_again,
        font=('Segoe UI Emoji', 10),
        bg=theme["bg"],
        fg=theme["fg"],
        selectcolor=theme["frame_bg"],
        activebackground=theme["bg"],
        activeforeground=theme["fg"]
    )
    checkbox.pack()
    
    # Boutons
    buttons_frame = tk.Frame(bottom_frame, bg=theme["bg"])
    buttons_frame.pack(side='right')
    
    def close_tutorial():
        if dont_show_again.get():
            mark_tutorial_shown()
        tutorial_window.destroy()
    
    def open_tutorial_again():
        tutorial_window.destroy()
    
    btn_close = tk.Button(
        buttons_frame,
        text="✅ J'ai compris !",
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
        text="🔄 Revoir plus tard",
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
            tutorial_window.destroy()
        except:
            pass
    
    tutorial_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    log_message("INFO", "Tutoriel v2.4.2 affiché (non-bloquant)")

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
        section_frame = tk.Frame(parent, bg=theme["frame_bg"], relief='solid', bd=1)
        section_frame.pack(fill='x', pady=8, padx=10)
        
        # Titre de section
        section_title = tk.Label(
            section_frame,
            text=title,
            font=('Segoe UI Emoji', 13, 'bold'),
            bg=theme["frame_bg"],
            fg=theme["accent"]
        )
        section_title.pack(anchor='w', padx=15, pady=(12, 8))
        
        # Contenu de la section
        for item in items:
            if item == "":  # Ligne vide pour espacer
                spacer = tk.Frame(section_frame, bg=theme["frame_bg"], height=5)
                spacer.pack()
            else:
                # Déterminer le padding selon le type de contenu
                left_pad = 25 if item.startswith(('•', '├', '└', '─', '   •', '   ├')) else 15
                left_pad = 35 if item.startswith('      ') else left_pad
                
                item_label = tk.Label(
                    section_frame,
                    text=item,
                    font=('Segoe UI Emoji', 10),
                    bg=theme["frame_bg"],
                    fg=theme["fg"],
                    justify='left',
                    wraplength=750,
                    anchor='w'
                )
                item_label.pack(anchor='w', padx=(left_pad, 15), pady=2)
        
        # Espacement final
        spacer = tk.Frame(section_frame, bg=theme["frame_bg"], height=10)
        spacer.pack()
        
    except Exception as e:
        log_message("WARNING", f"Erreur création section tutoriel: {str(e)}")

def show_quick_help(parent, topic=None):
    """Affiche une aide contextuelle"""
    
    help_topics = {
        'glossary': {
            'title': "📚 Système de Glossaire",
            'subtitle': "Traduction automatique des termes récurrents",
            'sections': [
                ("🎯 Objectif", [
                    "Le glossaire permet de traduire automatiquement des termes récurrents",
                    "comme \"Sigh\" → \"Soupir\" dans tous vos projets."
                ]),
                ("📝 Utilisation", [
                    "Ajoutez des paires Original → Traduction",
                    "Protection automatique lors de l'extraction",
                    "Traduction automatique lors de la reconstruction"
                ]),
                ("🔍 Fonctionnalités", [
                    "Recherche en temps réel",
                    "Import/Export de glossaires",
                    "Validation des entrées",
                    "Protection automatique des termes complets"
                ]),
                ("💡 Exemples d'utilisation", [
                    "'Sigh' → 'Soupir'",
                    "'Hmm' → 'Hmm' (conservation)",
                    "'Yeah' → 'Ouais'",
                    "Noms de personnages récurrents"
                ]),
                ("⚠️ Bonnes pratiques", [
                    "Le glossaire est permanent (non réinitialisable)",
                    "Seuls les mots complets sont remplacés",
                    "Utilisez des mots complets",
                    "Évitez les termes trop génériques",
                    "Les termes plus longs sont traités en premier",
                    "Validez régulièrement votre glossaire"
                ])
            ]
        },
        'extraction': {
            'title': "⚡ Extraction améliorée",
            'subtitle': "Analyse et séparation intelligente des textes",
            'sections': [
                ("📝 Séparation des textes", [
                    "[nom].txt : Textes principaux à traduire",
                    "[nom]_asterix.txt : Expressions *entre astérisques*",
                    "[nom]_empty.txt : Textes vides et espaces",
                    "[nom]_glossary.txt : Termes du glossaire (lecture seule)"
                ]),
                ("🔒 Protection automatique", [
                    "Codes Ren'Py : {b}, [player_name], \\n, etc.",
                    "Termes du glossaire avec placeholders (GLO001)…",
                    "Guillemets échappés et textes vides"
                ]),
                ("📁 Structure organisée", [
                    "temporaires/[NomDuJeu]/",
                    "Auto-Open configurable pour ouvrir les fichiers créés"
                ])
            ]
        },
        'reconstruction': {
            'title': "🔗 Aide Reconstruction",
            'subtitle': "Reconstruction avec glossaire et validation",
            'sections': [
                ("⚙️ Processus", [
                    "Chargement des mappings et fichiers de positions",
                    "Injection des traductions principales, astérisques et vides",
                    "Restauration des codes spéciaux et termes de glossaire"
                ]),
                ("💾 Enregistrement", [
                    "Mode 'new_file' ou 'overwrite'",
                    "Nettoyage des fichiers temporaires",
                    "Organisation dans temporaires/[NomDuJeu]/"
                ])
            ]
        },
        'validation': {
            'title': "☑️ Aide Validation",
            'subtitle': "Validation avancée et rapports d'erreurs",
            'sections': [
                ("🔍 Contrôles", [
                    "Détection des patterns Ren'Py (labels, dialogues, menus…)",
                    "Validation de la correspondance nombre de lignes",
                    "Vérification des placeholders non traduits"
                ]),
                ("📝 Rapports", [
                    "Détails des erreurs et warnings",
                    "Statistiques de confiance et de couverture",
                    "Sauvegarde automatique avant modifications"
                ])
            ]
        },
        'files': {
            'title': "📁 Organisation fichiers",
            'subtitle': "Structure organisée par jeu v2.4.2",
            'sections': [
                ("📂 Arborescence", [
                    "dossier_configs : Fichiers principaux de l’outil",
                    "sauvegardes : Archives des backups",
                    "avertissements : Rapports d’erreurs de reconstruction",
                    "temporaires/[NomDuJeu]/fichiers_a_traduire : Textes à traduire",
                    "temporaires/[NomDuJeu]/fichiers_a_ne_pas_traduire : Fichiers de configuration"
                ])
            ]
        }
    }
    
    if topic not in help_topics:
        return
    
    topic_info = help_topics[topic]
    
    # Créer une fenêtre avec le même style
    tutorial_window = tk.Toplevel()
    tutorial_window.title(f"{topic_info['title']} - Traducteur Ren'Py Pro v{VERSION}")
    tutorial_window.geometry("600x500")
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
    
    # Header (MÊME STYLE)
    header_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    header_frame.pack(fill='x', pady=(0, 20))
    
    title_tutorial = tk.Label(
        header_frame,
        text=topic_info['title'],
        font=('Segoe UI Emoji', 18, 'bold'),
        bg=theme["bg"],
        fg=theme["accent"]
    )
    title_tutorial.pack()
    
    subtitle_tutorial = tk.Label(
        header_frame,
        text=topic_info['subtitle'],
        font=('Segoe UI Emoji', 11),
        bg=theme["bg"],
        fg=theme["fg"]
    )
    subtitle_tutorial.pack(pady=(5, 0))
    
    # ========== SECTIONS STYLÉES ==========
    for section_title, section_items in topic_info['sections']:
        create_section(scrollable_frame, theme, section_title, section_items)
    
    # Bouton fermer (MÊME STYLE)
    close_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    close_frame.pack(fill='x', pady=(20, 15))
    
    btn_close = tk.Button(
        close_frame,
        text="✅ Compris !",
        font=('Segoe UI Emoji', 11, 'bold'),
        bg=theme["accent"],
        fg="#000000",
        activebackground='#157347',
        bd=0,
        pady=10,
        padx=25,
        command=tutorial_window.destroy
    )
    btn_close.pack(side='right')
    
    # Configurer canvas et scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Scroll avec molette
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    tutorial_window.bind("<MouseWheel>", on_mousewheel)
    tutorial_window.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    tutorial_window.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    
    btn_close.focus_set()
    tutorial_window.protocol("WM_DELETE_WINDOW", tutorial_window.destroy)
    
    log_message("INFO", f"Aide {topic} affichée avec style harmonisé")

def show_minimal_tutorial():
    """Affiche une version minimale du tutoriel avec le MÊME STYLE que le guide complet"""
    # Créer une fenêtre avec le même style que show_tutorial()
    tutorial_window = tk.Toplevel()
    tutorial_window.title(f"⚡ Guide Express - Traducteur Ren'Py Pro v{VERSION}")
    tutorial_window.geometry("600x600")
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
    
    # Header (MÊME STYLE)
    header_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    header_frame.pack(fill='x', pady=(0, 20))
    
    title_tutorial = tk.Label(
        header_frame,
        text=f"⚡ Guide Express v{VERSION}",
        font=('Segoe UI Emoji', 18, 'bold'),
        bg=theme["bg"],
        fg=theme["accent"]
    )
    title_tutorial.pack()
    
    subtitle_tutorial = tk.Label(
        header_frame,
        text="Version rapide pour utilisateurs expérimentés",
        font=('Segoe UI Emoji', 11),
        bg=theme["bg"],
        fg=theme["fg"]
    )
    subtitle_tutorial.pack(pady=(5, 0))
    
    # ========== CONTENU AVEC SECTIONS STYLÉES ==========
    
    # Section Workflow
    create_section(scrollable_frame, theme, "📋 Workflow rapide", [
        "1. Charger fichier .rpy → 2. ⚡ Extraire → 3. Traduire les .txt → 4. 🔧 Reconstruire"
    ])
    
    # Section Nouveautés
    create_section(scrollable_frame, theme, "🆕 Nouveautés v2.4.2", [
        "📚 Glossaire permanent pour termes récurrents",
        "🏗️ Architecture organisée par jeu (temporaires/[NomDuJeu]/)",
        "✅ Validation avancée avec rapports détaillés",
        "🎨 Interface améliorée et thèmes adaptatifs"
    ])
    
    # Section Raccourcis
    create_section(scrollable_frame, theme, "🔧 Raccourcis utiles", [
        "• Drag & Drop de fichiers/dossiers dans la zone de texte",
        "• Ctrl+V pour coller contenu Ren'Py (bouton violet pour basculer)",
        "• 📚 Glossaire : Gérer termes automatiques",
        "• 🔄 Réinitialiser : Nettoie sans perdre le fichier actuel"
    ])
    
    # Section Configuration
    create_section(scrollable_frame, theme, "⚙️ Configuration", [
        "📂 Auto ON/OFF : Ouvre fichiers automatiquement",
        "✅ Valid ON/OFF : Active validation (plus rapide si OFF)",
        "🌙/☀️ : Thème sombre/clair"
    ])
    
    # Section Important
    create_section(scrollable_frame, theme, "⚠️ Important v2.4.2", [
        "Structure organisée : temporaires/[NomDuJeu]/fichiers_a_traduire/",
        "Ne jamais modifier les codes (01), (02), (GLO001)...",
        "Fichiers _empty.txt peuvent contenir lignes vides",
        "Glossaire protège automatiquement vos termes récurrents"
    ])
    
    # Bouton fermer (MÊME STYLE)
    close_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    close_frame.pack(fill='x', pady=(20, 15))
    
    btn_close = tk.Button(
        close_frame,
        text="✅ J'ai compris !",
        font=('Segoe UI Emoji', 11, 'bold'),
        bg=theme["accent"],
        fg="#000000",
        activebackground='#157347',
        bd=0,
        pady=10,
        padx=25,
        command=tutorial_window.destroy
    )
    btn_close.pack(side='right')
    
    # Configurer canvas et scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Scroll avec molette
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    tutorial_window.bind("<MouseWheel>", on_mousewheel)
    tutorial_window.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    tutorial_window.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    
    btn_close.focus_set()
    tutorial_window.protocol("WM_DELETE_WINDOW", tutorial_window.destroy)
    
    log_message("INFO", "Guide Express v2.4.2 affiché avec style harmonisé")

def show_whats_new():
    """Affiche les nouveautés avec le MÊME STYLE que le guide complet"""
    # Créer une fenêtre avec le même style
    tutorial_window = tk.Toplevel()
    tutorial_window.title(f"🆕 Nouveautés - Traducteur Ren'Py Pro v{VERSION}")
    tutorial_window.geometry("500x650")
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
    
    # Header (MÊME STYLE)
    header_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    header_frame.pack(fill='x', pady=(0, 20))
    
    title_tutorial = tk.Label(
        header_frame,
        text=f"🆕 Nouveautés v{VERSION}",
        font=('Segoe UI Emoji', 18, 'bold'),
        bg=theme["bg"],
        fg=theme["accent"]
    )
    title_tutorial.pack()
    
    subtitle_tutorial = tk.Label(
        header_frame,
        text="Découvrez toutes les améliorations et nouvelles fonctionnalités",
        font=('Segoe UI Emoji', 11),
        bg=theme["bg"],
        fg=theme["fg"]
    )
    subtitle_tutorial.pack(pady=(5, 0))
    
    # ========== CONTENU AVEC SECTIONS STYLÉES ==========
    
    # Section Architecture
    create_section(scrollable_frame, theme, "🏗️ Architecture refactorisée", [
        "📁 Structure organisée par jeu : temporaires/[NomDuJeu]/",
        "🔧 Modules enhanced pour extraction et reconstruction",
        "🛡️ Suppression protection points de suspension",
        "⚡ Performances optimisées pour gros fichiers"
    ])
    
    # Section Glossaire
    create_section(scrollable_frame, theme, "📚 Système de Glossaire Enhanced", [
        "💾 Glossaire permanent (survit réinitialisations)",
        "🔄 Protection automatique termes récurrents",
        "📝 Interface complète : CRUD + recherche + validation",
        "📤 Import/Export pour partage",
        "🎯 Placeholders GLO001, GLO002... pour protection"
    ])
    
    # Section Validation
    create_section(scrollable_frame, theme, "✅ Validation avancée", [
        "🔍 Contrôle cohérence OLD/NEW amélioré",
        "📄 Rapports détaillés dans avertissements/[NomDuJeu]/",
        "🎛️ Activable/désactivable pour performance",
        "🔧 Détection balises orphelines, placeholders malformés"
    ])
    
    # Section Interface
    create_section(scrollable_frame, theme, "🎨 Interface v2.4.2", [
        "🌈 Thèmes sombre/clair vraiment différents",
        "🎯 Modes d'entrée D&D ↔ Ctrl+V avec fallback intelligent",
        "📊 Statistiques temps réel et compteurs",
        "💡 Messages contextuels et tutoriel non-bloquant"
    ])
    
    # Section Protection
    create_section(scrollable_frame, theme, "🔒 Protection améliorée", [
        "📚 Intégration glossaire dans protection automatique",
        "🔳 Gestion guillemets échappés corrigée",
        "⭐ Expressions astérisques avec codes protégés",
        "🛡️ Validation types textes (normal/asterix/empty/glossary)"
    ])
    
    # Section Utilisation
    create_section(scrollable_frame, theme, "💡 Utilisation optimale v2.4.2", [
        "Configurez d'abord votre glossaire avec termes fréquents",
        "Utilisez structure organisée pour multi-projets",
        "Consultez rapports validation pour qualité traduction",
        "Exploitez modes d'entrée selon votre workflow"
    ])
    
    # Bouton fermer (MÊME STYLE)
    close_frame = tk.Frame(scrollable_frame, bg=theme["bg"])
    close_frame.pack(fill='x', pady=(20, 15))
    
    btn_close = tk.Button(
        close_frame,
        text="✅ Compris !",
        font=('Segoe UI Emoji', 11, 'bold'),
        bg=theme["accent"],
        fg="#000000",
        activebackground='#157347',
        bd=0,
        pady=10,
        padx=25,
        command=tutorial_window.destroy
    )
    btn_close.pack(side='right')
    
    # Configurer canvas et scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Scroll avec molette
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    tutorial_window.bind("<MouseWheel>", on_mousewheel)
    tutorial_window.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    tutorial_window.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    
    btn_close.focus_set()
    tutorial_window.protocol("WM_DELETE_WINDOW", tutorial_window.destroy)
    
    log_message("INFO", "Nouveautés v2.4.2 affichées avec style harmonisé")

def create_tutorial_menu():
    """Crée un menu contextuel pour différents types d'aide"""
    def show_menu():
        menu_window = tk.Toplevel()
        menu_window.title("🎓 Centre d'aide v2.4.2")
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
            text="🎓 Centre d'aide - Choisissez votre type d'aide",
            font=('Segoe UI Emoji', 14, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        title_label.pack(pady=20)
        
        # Boutons d'aide
        button_frame = tk.Frame(menu_window, bg=theme["bg"])
        button_frame.pack(fill='both', expand=True, padx=20)
        
        buttons = [
            ("📖 Guide complet v2.4.2", "Guide détaillé avec toutes les fonctionnalités actuelles", show_tutorial),
            ("⚡ Guide express", "Version rapide pour utilisateurs expérimentés", show_minimal_tutorial),
            ("🆕 Nouveautés v2.4.2", "Découvrir les améliorations et nouvelles fonctions", show_whats_new),
            ("📚 Aide Glossaire", "Système de glossaire permanent et protection automatique", lambda: show_quick_help(None, 'glossary')),
            ("⚡ Aide Extraction", "Extraction enhanced avec structure organisée", lambda: show_quick_help(None, 'extraction')),
            ("🔧 Aide Reconstruction", "Reconstruction avec glossaire et validation", lambda: show_quick_help(None, 'reconstruction')),
            ("✅ Aide Validation", "Validation avancée et rapports d'erreurs", lambda: show_quick_help(None, 'validation')),
            ("📁 Organisation fichiers", "Structure organisée par jeu v2.4.2", lambda: show_quick_help(None, 'files'))
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
            text="❌ Fermer",
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