# ui/tutorial.py
# Tutorial System Module
# Created for Traducteur Ren'Py Pro v2.2.0

"""
Module du système de tutoriel intégré avec guide complet
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
    # ✅ CORRECTION : Utiliser le nouveau chemin avec FILE_NAMES
    tutorial_flag_file = FILE_NAMES["tutorial_flag"]
    return not os.path.exists(tutorial_flag_file)

def mark_tutorial_shown():
    """
    Marque que le tutoriel a été affiché
    """
    try:
        # ✅ CORRECTION : S'assurer que le dossier existe
        ensure_folders_exist()
        
        # ✅ CORRECTION : Utiliser le nouveau chemin
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
    """Affiche la fenêtre de tutoriel complète et détaillée"""
    import tkinter as tk
    from tkinter import ttk
    
    # Vérifier et utiliser la fenêtre principale existante
    root = tk._default_root
    if not root:
        log_message("WARNING", "Impossible d'afficher le tutoriel - pas de fenêtre principale")
        root = tk.Tk()
        root.withdraw()
        temporary_root = True
    else:
        temporary_root = False
    
    tutorial_window = tk.Toplevel(root)
    tutorial_window.title(f"🎓 Guide Complet - Traducteur Ren'Py Pro v{VERSION}")
    tutorial_window.geometry("800x700")
    tutorial_window.resizable(True, True)
    
    if not temporary_root:
        tutorial_window.transient(root)
        tutorial_window.grab_set()
    else:
        def close_tutorial_and_root():
            tutorial_window.destroy()
            if temporary_root:
                root.destroy()
        tutorial_window.protocol("WM_DELETE_WINDOW", close_tutorial_and_root)
        tutorial_window.grab_set()
    
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
        text="Guide complet pour traduire vos scripts Ren'Py efficacement",
        font=('Segoe UI Emoji', 11),
        bg=theme["bg"],
        fg=theme["fg"]
    )
    subtitle_tutorial.pack(pady=(5, 0))
    
    # ==================== CONTENU DU TUTORIEL ====================
    
    # Section 1: Vue d'ensemble
    create_section(scrollable_frame, theme, "🎯 Vue d'ensemble", [
        "Le Traducteur Ren'Py Pro est un outil spécialisé pour gérer les traductions de jeux Ren'Py.",
        "Il extrait intelligemment les textes, protège les codes spéciaux, et reconstruit les fichiers traduits.",
        "Compatible avec les fichiers générés par le SDK Ren'Py (commande generate translations).",
        "Supporte le traitement par lots, les modes multiples d'entrée, et la validation automatique."
    ])
    
    # Section 2: Workflow complet de traduction
    create_section(scrollable_frame, theme, "📋 Workflow complet de traduction", [
        "1️⃣ Générez vos fichiers de traduction avec le SDK Ren'Py (comme d'habitude)",
        "2️⃣ Ouvrez le fichier .rpy dans le Traducteur (bouton bleu ou glisser-déposer)",
        "3️⃣ Cliquez sur 'Extraire' pour créer les fichiers de texte à traduire",
        "4️⃣ Traduisez les fichiers .txt avec l'outil de votre choix (IA, CAT tool, manuellement)",
        "5️⃣ Collez/remplacez le contenu traduit dans les mêmes fichiers .txt",
        "6️⃣ Cliquez sur 'Reconstruire' pour générer le fichier .rpy traduit final",
        "💡 Les codes (01), (02)... sont automatiquement restaurés à leur forme originale"
    ])
    
    # Section : Traduction partielle
    create_section(scrollable_frame, theme, "⚡ Traduction partielle (mise à jour ciblée)", [
        "Pour traduire uniquement des sections spécifiques :",
        "1️⃣ Copiez la section modifiée depuis votre fichier .rpy",
        "2️⃣ Basculez en mode Ctrl+V (bouton violet)",
        "3️⃣ Collez le contenu avec Ctrl+V",
        "4️⃣ Procédez normalement : Extraire → Traduire → Reconstruire",
        "5️⃣ Les nouvelles traductions s'ajoutent au fichier traduit existant",
        "💡 Idéal pour les mises à jour de jeu ou corrections ponctuelles"
    ])
    
    # Section 4: Modes d'entrée
    create_section(scrollable_frame, theme, "🎯 Modes d'entrée disponibles", [
        "📂 Fichier unique : Ouvrez un seul fichier .rpy à la fois",
        "📁 Mode dossier : Traitez tous les fichiers .rpy d'un dossier en séquence",
        "🎯 Drag & Drop : Glissez directement vos fichiers dans la zone de texte",
        "📋 Mode Ctrl+V : Collez du contenu Ren'Py depuis le presse-papier",
        "💡 Basculez entre D&D et Ctrl+V avec le bouton violet",
        "⚡ Mode partiel : Copiez seulement les sections modifiées pour une traduction ciblée"
    ])
    
    # Section 5: Organisation des fichiers
    create_section(scrollable_frame, theme, "📁 Organisation intelligente des fichiers", [
        "📦 Structure automatique : temporaires/[NomDuJeu]/",
        "├── 📁 fichiers_a_traduire/ : Contient les .txt à traduire",
        "├── 📁 fichiers_a_ne_pas_traduire/ : Mappings et données techniques",
        "📁 avertissement/ : Rapports de validation",
        "📁 dossier_configs/ : Configuration, logs et paramètres",
        "",
        "🎯 Fichiers créés lors de l'extraction :",
        "• [nom].txt : Textes principaux à traduire",
        "• [nom]_asterix.txt : Expressions *entre astérisques* (narration, pensées)",
        "• [nom]_empty.txt : Textes vides et espaces (si présents)",
        "• [nom]_mapping.txt : Table de conversion des codes protégés"
    ])
    
    # Section 6: Fonctionnalités avancées
    create_section(scrollable_frame, theme, "🚀 Fonctionnalités avancées", [
        "🛡️ Sauvegardes automatiques : Créées avant chaque extraction",
        "✅ Validation intelligente : Vérifie la cohérence OLD/NEW",
        "⚠️ Détection d'erreurs : Balises orphelines, placeholders manquants",
        "📊 Statistiques détaillées : Temps de traitement, nombre de textes",
        "🔄 Mode écrasement ou nouveau fichier selon votre choix",
        "📂 Auto-Open : Ouvre automatiquement les fichiers créés (désactivable)",
        "🌙 Thème sombre/clair adaptatif"
    ])
    
    # Section 7: Protection des codes
    create_section(scrollable_frame, theme, "🔒 Protection automatique des codes", [
        "Le traducteur protège automatiquement :",
        "• Les balises {b}, {i}, {color=#hex}, etc.",
        "• Les variables [player_name], [count], etc.",
        "• Les codes spéciaux \\n, %s, %(variable)s",
        "• Les expressions conditionnelles et placeholders",
        "⚠️ NE JAMAIS modifier les codes (01), (02), (D1), (C1) dans vos traductions !",
        "✅ Ils seront automatiquement restaurés lors de la reconstruction"
    ])
    
    # Section 8: Résolution de problèmes
    create_section(scrollable_frame, theme, "🔧 Résolution de problèmes courants", [
        "❌ 'Fichier non valide' : Vérifiez que c'est bien un .rpy de traduction Ren'Py",
        "❌ 'Nombre de traductions incorrect' : Assurez-vous d'avoir traduit TOUTES les lignes",
        "❌ 'Placeholders malformés' : Ne modifiez pas les codes (01), (02)...",
        "❌ 'Drag & Drop ne fonctionne pas' : Basculez en mode Ctrl+V",
        "❌ 'Validation échouée fichier _empty.txt' : Ce fichier peut contenir des lignes vides",
        "💡 Consultez le dossier 'avertissements' pour les rapports détaillés",
        "💡 Les fichiers logs sont dans le dossier 'dossier_configs' pour le débogage"
    ])
    
    # Section 9: Raccourcis et astuces
    create_section(scrollable_frame, theme, "⌨️ Raccourcis et astuces", [
        "• Double-cliquez sur la zone de texte vide pour ouvrir un fichier",
        "• Glissez un dossier entier pour activer le mode batch",
        "• Utilisez 'Réinitialiser' pour nettoyer la base de données",
        "• Le bouton 'Temporaire' ouvre le dossier du jeu en cours",
        "• Les temps de traitement sont sauvegardés dans dossier_configs",
        "• Activez/désactivez la validation pour un traitement plus rapide",
        "• Les fichiers _empty.txt peuvent contenir des lignes vides - c'est normal"
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
        if temporary_root:
            try:
                root.destroy()
            except:
                pass
    
    def open_tutorial_again():
        tutorial_window.destroy()
        if temporary_root:
            try:
                root.destroy()
            except:
                pass
    
    btn_close = tk.Button(
        buttons_frame,
        text="✅ J'ai compris !",
        font=('Segoe UI Emoji', 11, 'bold'),
        bg=theme["accent"],
        fg=theme["button_fg"],
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
    
    log_message("INFO", "Tutoriel complet affiché")

def create_section(parent, theme, title, items):
    """
    Crée une section du tutoriel avec un style amélioré
    
    Args:
        parent: Widget parent
        theme: Thème de couleurs
        title: Titre de la section
        items: Liste des éléments de la section
    """
    try:
        section_frame = tk.Frame(parent, bg=theme["frame_bg"], relief='solid', bd=1)
        section_frame.pack(fill='x', pady=8, padx=10)
        
        # Titre de section avec icône
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
                left_pad = 25 if item.startswith(('•', '├', '└', '─')) else 15
                left_pad = 35 if item.startswith('  ') else left_pad
                
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
    """
    Affiche une aide contextuelle rapide pour un sujet spécifique
    
    Args:
        parent: Widget parent
        topic: Sujet spécifique ('extraction', 'reconstruction', 'validation', etc.)
    """
    help_topics = {
        'extraction': {
            'title': "⚡ Aide - Extraction",
            'content': [
                "L'extraction analyse votre fichier .rpy et sépare :",
                "• Les textes à traduire dans des fichiers .txt",
                "• Les codes spéciaux sont protégés par des placeholders",
                "• Les expressions *entre astérisques* vont dans un fichier séparé",
                "",
                "💡 Les fichiers créés s'ouvrent automatiquement si Auto-Open est activé"
            ]
        },
        'reconstruction': {
            'title': "🔧 Aide - Reconstruction",
            'content': [
                "La reconstruction assemble vos traductions :",
                "• Lit les fichiers .txt traduits",
                "• Restaure tous les codes protégés",
                "• Crée le fichier .rpy final",
                "",
                "⚠️ Assurez-vous d'avoir traduit TOUTES les lignes",
                "💡 Choisissez entre écraser ou créer un nouveau fichier"
            ]
        },
        'validation': {
            'title': "✅ Aide - Validation",
            'content': [
                "La validation vérifie la cohérence OLD/NEW :",
                "• Détecte les balises manquantes ou malformées",
                "• Vérifie les placeholders et variables",
                "• Crée un rapport dans le dossier avertissements",
                "",
                "💡 Désactivez la validation pour un traitement plus rapide",
                "💡 Les fichiers _empty.txt peuvent contenir des lignes vides"
            ]
        }
    }
    
    if topic and topic in help_topics:
        info = help_topics[topic]
        messagebox.showinfo(info['title'], '\n'.join(info['content']))
    else:
        # Afficher le tutoriel complet si pas de topic spécifique
        show_tutorial()