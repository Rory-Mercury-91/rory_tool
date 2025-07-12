# ui/tutorial.py
# Tutorial System Module
# Created for Traducteur Ren'Py Pro v1.1.2

"""
Module du système de tutoriel intégré
"""

import os
import datetime
import tkinter as tk
from tkinter import messagebox
from utils.constants import VERSION, THEMES
from utils.config import config_manager
from utils.logging import log_message

def check_first_launch():
    """
    Vérifie si c'est le premier lancement de l'application
    
    Returns:
        bool: True si c'est le premier lancement
    """
    tutorial_config_file = "tutorial_shown.flag"
    return not os.path.exists(tutorial_config_file)

def mark_tutorial_shown():
    """
    Marque que le tutoriel a été affiché
    """
    try:
        with open("tutorial_shown.flag", "w", encoding="utf-8") as f:
            f.write(f"Tutorial shown on: {datetime.datetime.now().isoformat()}\n")
            f.write("This file prevents the tutorial from showing again.\n")
        log_message("INFO", "Tutoriel marqué comme affiché")
    except Exception as e:
        log_message("WARNING", "Impossible de marquer le tutoriel comme affiché", e)

def show_tutorial():
    """Affiche la fenêtre de tutoriel simplifiée"""
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
    tutorial_window.title(f"🎓 Tutoriel - Traducteur Ren'Py Pro v{VERSION}")
    tutorial_window.geometry("650x600")  # RÉDUIT : 650x600 au lieu de 750x750
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
        font=('Segoe UI', 16, 'bold'),
        bg=theme["bg"],
        fg=theme["accent"]
    )
    title_tutorial.pack()
    
    subtitle_tutorial = tk.Label(
        header_frame,
        text="Guide rapide pour traduire vos scripts Ren'Py",
        font=('Segoe UI', 10),
        bg=theme["bg"],
        fg=theme["fg"]
    )
    subtitle_tutorial.pack(pady=(5, 0))
    
    # Section 1: Interface (CORRIGÉE)
    create_section(scrollable_frame, theme, "🎨 Interface", [
        "📂  Boutons bleus : Ouvrir un fichier .rpy ou un dossier",  # Ajout d'un espace après emoji
        "🛡️  Boutons rouges : Gérer les sauvegardes et réinitialiser",
        "⚡  Boutons verts : Extraire les textes et reconstruire le fichier", 
        "🛠️  Boutons jaunes : Nettoyer, voir les temps, options et tutoriel"
    ])

    # Section 2: Processus de traduction (CORRIGÉE - sans carrés)
    create_section(scrollable_frame, theme, "🚀 Comment traduire", [
        "1. Ouvrez votre fichier .rpy avec le bouton bleu",  # SUPPRIMÉ les carrés ☐
        "2. Cliquez sur 'Extraire' (vert) pour créer les fichiers de traduction",
        "3. Traduisez dans les fichiers .txt générés (ne touchez pas aux codes (01), (02)...)", 
        "4. Cliquez sur 'Reconstruire' (vert) pour finaliser",
        "5. Choisissez 'Nouveau fichier' pour garder l'original ou 'Écraser' pour le remplacer"
    ])

    # Section 3: Fonctionnalités principales (CORRIGÉE)
    create_section(scrollable_frame, theme, "⭐ Fonctionnalités", [
        "🎯  Drag & Drop : Glissez directement un fichier .rpy dans la zone de texte",
        "📁  Mode dossier : Traitez plusieurs fichiers .rpy d'un coup",
        "🛡️  Sauvegardes automatiques : Vos fichiers originaux sont protégés",
        "🔍  Validation : Contrôle automatique de la cohérence des traductions",
        "⭐  Gestion des codes spéciaux : Variables [mc], balises {i}, textes *astérisques*"
    ])

    # Section 4: Conseils pratiques (CORRIGÉE)
    create_section(scrollable_frame, theme, "💡 Conseils", [
        "✅  Utilisez 'Nouveau fichier' pour garder l'original intact",
        "✅  Ne modifiez jamais les codes (01), (02)... dans vos traductions",
        "✅  Les textes entre *astérisques* sont extraits dans un fichier séparé",
        "✅  'Nettoyer' vide tout, 'Réinitialiser' ne vide que les données de session",
        "✅  Le mode dossier mémorise votre choix de sauvegarde pour tous les fichiers"
    ])

    # Section 5: Problèmes courants (CORRIGÉE)
    create_section(scrollable_frame, theme, "🔧 En cas de problème", [
        "❌  'Fichier non valide' → Vérifiez que c'est bien un script .rpy de jeu",
        "❌  'Nombre incorrect' → Comptez vos lignes de traduction, une ligne = une traduction",
        "❌  Variables mal restaurées → Refaites une extraction propre et ne touchez pas aux (01)...",
        "❌  Auto-ouverture ne marche pas → Ouvrez manuellement les fichiers depuis l'explorateur"
    ])
    
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
        text="Ne plus afficher au démarrage",
        variable=dont_show_again,
        font=('Segoe UI', 9),
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
        text="✅ Compris !",
        font=('Segoe UI', 10, 'bold'),
        bg=theme["accent"],
        fg=theme["button_fg"],
        activebackground='#157347',
        bd=0,
        pady=10,
        padx=20,
        command=close_tutorial
    )
    btn_close.pack(side='right', padx=(10, 0))
    
    btn_later = tk.Button(
        buttons_frame,
        text="🔄 Plus tard",
        font=('Segoe UI', 9),
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
    
    log_message("INFO", "Tutoriel simplifié affiché")

def create_section(parent, theme, title, items):
    """
    Crée une section du tutoriel avec espacement amélioré
    
    Args:
        parent: Widget parent
        theme: Thème de couleurs
        title: Titre de la section
        items: Liste des éléments de la section
    """
    try:
        section_frame = tk.Frame(parent, bg=theme["frame_bg"], relief='solid', bd=1)
        section_frame.pack(fill='x', pady=8, padx=10)  # RÉDUIT : pady=8 au lieu de 10
        
        section_title = tk.Label(
            section_frame,
            text=title,
            font=('Segoe UI', 12, 'bold'),
            bg=theme["frame_bg"],
            fg=theme["accent"]
        )
        section_title.pack(anchor='w', padx=15, pady=(12, 8))  # AJUSTÉ : padding titre
        
        for item in items:
            item_label = tk.Label(
                section_frame,
                text=item,
                font=('Segoe UI', 9),
                bg=theme["frame_bg"],
                fg=theme["fg"],
                justify='left',
                wraplength=580,  # RÉDUIT : 580 au lieu de 600
                anchor='w'  # AJOUTÉ : ancrage à gauche
            )
            item_label.pack(anchor='w', padx=15, pady=2)  # AJUSTÉ : pady=2 pour moins d'espace
        
        # Espacement final réduit
        spacer = tk.Frame(section_frame, bg=theme["frame_bg"], height=6)  # RÉDUIT : 6 au lieu de 8
        spacer.pack()
        
    except Exception as e:
        log_message("WARNING", f"Erreur création section tutoriel: {str(e)}")