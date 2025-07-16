#!/usr/bin/env python3
# Script de test pour vérifier le système de sauvegardes

import os
import sys
import shutil
from datetime import datetime

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.constants import FOLDERS, ensure_folders_exist
from utils.logging import extract_game_name, log_message, initialize_log
from core.validation import BackupManager

def test_backup_system():
    """Test complet du système de sauvegardes"""
    print("🧪 Test du système de sauvegardes")
    print("=" * 50)
    
    # Initialiser les logs
    initialize_log()
    
    # S'assurer que les dossiers existent
    ensure_folders_exist()
    
    # Chemin de test (simuler votre fichier)
    test_filepath = r"C:\Users\Rory Mercury 91\Documents\GuiltyPleasure-0.49-pc\game\tl\fr_zenpy_DeepL_andric31\script_translated.rpy"
    
    # Test 1: Extraction du nom du jeu
    print("\n📋 Test 1: Extraction du nom du jeu")
    game_name = extract_game_name(test_filepath)
    print(f"✅ Nom du jeu détecté: {game_name}")
    
    # Test 2: Structure des dossiers
    print("\n📁 Test 2: Structure des dossiers")
    backup_folder = os.path.join(FOLDERS["backup"], game_name)
    print(f"📂 Dossier de sauvegarde: {backup_folder}")
    
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder, exist_ok=True)
        print("✅ Dossier créé")
    else:
        print("✅ Dossier existe déjà")
    
    # Test 3: Créer une sauvegarde fictive (si le fichier n'existe pas)
    print("\n💾 Test 3: Création d'une sauvegarde fictive")
    if not os.path.exists(test_filepath):
        print("⚠️ Fichier test non trouvé, création d'un fichier fictif...")
        
        # Créer les dossiers nécessaires
        os.makedirs(os.path.dirname(test_filepath), exist_ok=True)
        
        # Créer un fichier fictif
        with open(test_filepath, 'w', encoding='utf-8') as f:
            f.write('# Fichier test pour les sauvegardes\n')
            f.write('translate french test_label:\n')
            f.write('    old "Hello"\n')
            f.write('    new "Bonjour"\n')
        
        print("✅ Fichier test créé")
    
    # Test 4: Créer une sauvegarde avec BackupManager
    print("\n🛡️ Test 4: Création d'une sauvegarde")
    backup_manager = BackupManager()
    backup_result = backup_manager.create_backup(test_filepath)
    
    if backup_result['success']:
        print(f"✅ Sauvegarde créée: {backup_result['backup_path']}")
    else:
        print(f"❌ Erreur de sauvegarde: {backup_result['error']}")
    
    # Test 5: Lister les sauvegardes
    print("\n📋 Test 5: Listage des sauvegardes")
    backups = backup_manager.list_backups(test_filepath)
    
    if backups:
        print(f"✅ {len(backups)} sauvegarde(s) trouvée(s):")
        for i, backup in enumerate(backups, 1):
            print(f"  {i}. {backup['name']}")
            print(f"     📅 Créée: {backup['created'].strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"     📦 Taille: {backup['size'] / 1024:.1f} KB")
            print(f"     🎮 Jeu: {backup.get('game', 'N/A')}")
    else:
        print("❌ Aucune sauvegarde trouvée")
    
    # Test 6: Vérifier la structure complète
    print("\n🏗️ Test 6: Vérification de la structure complète")
    
    expected_structure = {
        "temporaires": FOLDERS["temp"],
        "sauvegardes": FOLDERS["backup"],
        "avertissements": FOLDERS["warnings"],
        "dossier_configs": FOLDERS["configs"]
    }
    
    for name, folder in expected_structure.items():
        if os.path.exists(folder):
            print(f"✅ {name}: {folder}")
        else:
            print(f"❌ {name}: {folder} (manquant)")
    
    print("\n🎯 Structure attendue:")
    print(f"📁 {FOLDERS['backup']}/{game_name}/")
    
    if os.path.exists(os.path.join(FOLDERS['backup'], game_name)):
        files = os.listdir(os.path.join(FOLDERS['backup'], game_name))
        if files:
            for file in files:
                print(f"  📄 {file}")
        else:
            print("  (vide)")
    
    print("\n✅ Test terminé!")

if __name__ == "__main__":
    test_backup_system()