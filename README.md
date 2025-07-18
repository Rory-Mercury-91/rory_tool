# 🎮 RenExtract

[![Version](https://img.shields.io/github/v/release/Rory-Mercury-91/rory_tool?style=for-the-badge)](https://github.com/Rory-Mercury-91/rory_tool/releases)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/github/license/Rory-Mercury-91/rory_tool?style=for-the-badge)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/Rory-Mercury-91/rory_tool/total?style=for-the-badge)](https://github.com/Rory-Mercury-91/rory_tool/releases)

**Outil de traduction avancé pour les scripts Ren'Py avec interface moderne, multilingue et fonctionnalités intelligentes.**

---

## ✨ Fonctionnalités principales

### 🌍 **Internationalisation dynamique (i18n)**
- Interface et guides disponibles en **français, anglais et allemand**
- Changement de langue **en temps réel** sur toute l'interface (boutons, menus, fenêtres d'aide, glossaire...)
- Traductions allemandes complètes et suppression de l'espagnol

### 🎨 **Interface moderne et responsive**
- **Boutons à taille fixe** : affichage uniforme quelle que soit la langue ou la longueur du texte
- **Émojis universels** pour une compatibilité maximale (Windows, Linux, WSL, etc.)
- **Thèmes sombre/clair** vraiment distincts, bascule instantanée sur tous les widgets
- **Mise à jour dynamique** de tous les textes lors du changement de langue ou de thème
- **Accessibilité améliorée** : textes lisibles, raccourcis clavier, navigation optimisée

### 📚 **Gestionnaire de glossaire avancé**
- Ajout, modification, validation, import/export, recherche en temps réel
- Validation intelligente des entrées et persistance du glossaire
- Glossaire et ses fenêtres entièrement traduits

### 💡 **Centre d'aide et guides multilingues**
- Fenêtres d'aide, tutoriels et glossaire traduits et adaptés à la langue choisie
- Navigation non-bloquante, guides contextuels

### 🔔 **Notifications intelligentes**
- Système de notifications toast, statuts, et popups réduites au strict nécessaire
- Messages d'information, de succès et d'erreur traduits

### 🚀 **Extraction intelligente**
- Protection automatique des codes Ren'Py (`{b}`, `[player_name]`, `\n`, etc.)
- Séparation intelligente : textes principaux, expressions `*entre astérisques*`, textes vides
- Structure organisée par jeu : `temporaires/[NomDuJeu]/fichiers_a_traduire/`

### ✅ **Validation avancée**
- Contrôle de cohérence OLD/NEW avec rapports détaillés
- Détection automatique des placeholders malformés
- Rapports d'erreurs dans `avertissements/[NomDuJeu]/`
- Validation désactivable pour plus de rapidité

### 🛡️ **Sécurité et sauvegarde**
- Sauvegardes automatiques avant chaque traitement
- Gestionnaire de sauvegardes intégré avec restauration en un clic
- Structure organisée : `sauvegardes/[NomDuJeu]/`

---

## 📥 Installation

### 💻 **Téléchargement direct (Recommandé)**

Téléchargez la dernière version depuis les [**Releases**](https://github.com/Rory-Mercury-91/rory_tool/releases/latest) :

- **Windows** : `RenExtract-v2.5.0-Windows.zip`
- **Linux** : `RenExtract-v2.5.0-Linux.tar.gz`

### 🚀 **Installation Windows**
1. Téléchargez le fichier `.zip`
2. Extraire l'archive
3. Double-cliquez sur `RenExtract.exe`

### 🐧 **Installation Linux**
```bash
# Télécharger et extraire
tar -xzf RenExtract-v2.5.0-Linux.tar.gz

# Rendre exécutable
chmod +x RenExtract

# Lancer
./RenExtract
```

### 🐍 **Installation depuis le code source**
```bash
# Cloner le repository
git clone https://github.com/Rory-Mercury-91/rory_tool.git
cd rory_tool

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

---

## 🎯 Utilisation rapide

### **Workflow standard**
1. **Générez** vos fichiers de traduction avec le SDK Ren'Py (`generate translations`)
2. **Chargez** le fichier `.rpy` dans l'outil :
   - Drag & Drop du fichier dans la zone de texte
   - Boutons "📂 Ouvrir Fichier .rpy" ou "📁 Ouvrir Dossier"
   - Mode Ctrl+V pour coller du contenu
3. **Cliquez** sur "⚡ Extraire" pour créer les fichiers à traduire
4. **Traduisez** les fichiers `.txt` générés avec votre outil préféré
5. **Cliquez** sur "🔧 Reconstruire" pour créer le fichier `.rpy` traduit

### **Structure des fichiers générés**
```
temporaires/[NomDuJeu]/
├── fichiers_a_traduire/
│   ├── [nom].txt              # Textes principaux à traduire
│   ├── [nom]_asterix.txt      # Expressions *entre astérisques*
│   ├── [nom]_empty.txt        # Textes vides et espaces
│   └── [nom]_glossary.txt     # Termes du glossaire (lecture seule)
└── fichiers_a_ne_pas_traduire/
    ├── [nom]_mapping.txt      # Codes protégés
    ├── [nom]_positions.json   # Données de reconstruction
    └── [nom]_glossary_mapping.txt
```

---

## 📚 Système de glossaire

### **Configuration initiale**
1. Cliquez sur "📚 Glossaire" dans la barre d'outils
2. Ajoutez vos paires `Original → Traduction` :
   - "Sigh" → "Soupir"
   - "Hmm" → "Hmm"
   - "Yeah" → "Ouais"

### **Utilisation automatique**
- Les termes sont **automatiquement protégés** lors de l'extraction
- Ils sont **traduits automatiquement** lors de la reconstruction
- Création d'un fichier `_glossary.txt` en lecture seule

### **Gestion avancée**
- **Import/Export** de glossaires pour partage
- **Recherche en temps réel** dans les entrées
- **Validation** pour détecter les problèmes
- **Persistance** : survit aux réinitialisations
- **Interface et messages du glossaire traduits**

---

## ⚙️ Configuration

### **Options disponibles**
- **📂 Auto ON/OFF** : Ouverture automatique des fichiers générés
- **✅ Valid ON/OFF** : Activation/désactivation de la validation
- **🌙/☀️** : Basculement thème sombre/clair
- **🎯 D&D ↔ 📋 Ctrl+V** : Mode d'entrée (avec fallback intelligent)
- **🇫🇷/🇬🇧/🇩🇪** : Changement de langue instantané

### **Raccourcis utiles**
- **Double-clic** sur la zone vide → Ouvrir un fichier
- **Glisser un dossier** → Activer le mode batch
- **🔄 Réinitialiser** → Nettoie sans perdre le fichier actuel
- **📁 Temporaire** → Ouvre le dossier du jeu en cours

---

## 🆕 Nouveautés v2.5.0

### **Internationalisation et interface**
- **Suppression de l'espagnol** : seules les langues français, anglais et allemand sont supportées
- **Traductions allemandes complètes**
- **Changement de langue dynamique** sur toute l'interface (boutons, guides, glossaire...)
- **Boutons à taille fixe** pour tous les textes, même en allemand
- **Correction de tous les caractères spéciaux/émojis**
- **Thèmes sombre/clair** instantanés et appliqués à toutes les fenêtres
- **Refonte du système de notifications** (toast, statuts, popups réduites)
- **Robustesse accrue** : interface plus stable, gestion dynamique des textes et thèmes

### **Fonctionnalités avancées**
- **Gestionnaire de glossaire** enrichi et multilingue
- **Guides et centre d'aide** traduits et adaptatifs
- **Notifications intelligentes** et messages contextuels
- **Accessibilité et ergonomie** renforcées

### **Technique**
- **Performances optimisées**
- **Pipeline de build** automatisé
- **Exécutables Windows et Linux**
- **Documentation** enrichie

---

## 🔧 Développement

### **Architecture du projet**
```
rory_tool/
├── main.py                    # Point d'entrée principal
├── core/                      # Modules de traitement
│   ├── extraction.py          # Extraction classique
│   ├── extraction_enhanced.py # Extraction avec glossaire
│   ├── reconstruction.py      # Reconstruction classique
│   ├── reconstruction_enhanced.py # Reconstruction avec glossaire
│   ├── validation.py          # Validation et sécurité
│   ├── coherence_checker.py   # Vérification OLD/NEW
│   ├── glossary.py           # Système de glossaire
│   └── file_manager.py       # Gestion des fichiers
├── ui/                       # Interface utilisateur
│   ├── themes.py             # Système de thèmes
│   ├── tutorial.py           # Guide et aide
│   ├── backup_manager.py     # Gestionnaire de sauvegardes
│   ├── glossary_ui.py        # Interface du glossaire
│   └── interface.py          # Composants d'interface
├── utils/                    # Utilitaires
│   ├── config.py             # Gestion de la configuration
│   ├── constants.py          # Constantes et thèmes
│   └── logging.py            # Système de logs
└── requirements.txt          # Dépendances Python
```

### **Contribuer**
1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commiter** vos changements (`git commit -m 'Add: AmazingFeature'`)
4. **Pousser** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

### **Dépendances**
- **Python 3.11+** (testé jusqu'à 3.13)
- **tkinterdnd2** : Support Drag & Drop
- **Modules standard** : tkinter, json, os, re, etc.

---

## 🛠️ Résolution de problèmes

### **Problèmes courants**

**❌ "Fichier non valide"**
→ Vérifiez que c'est un `.rpy` de traduction Ren'Py (pas un script de jeu)

**❌ "Validation échouée"**
→ Vérifiez d'avoir traduit TOUTES les lignes des fichiers `.txt`
→ Consultez le fichier d'avertissement créé

**❌ "Placeholders malformés"**
→ N'avez pas modifié les codes `(01)`, `(02)`, `(GLO001)`...
→ Réextrayez le fichier si nécessaire

**❌ "Drag & Drop ne fonctionne pas"**
→ Votre système ne supporte peut-être pas le D&D
→ Basculez en mode Ctrl+V (bouton violet)

### **Diagnostic**
- **Logs détaillés** : `dossier_configs/log.txt`
- **Rapports d'erreurs** : `avertissements/[NomDuJeu]/`
- **Guide intégré** : Bouton "🎓 Aide" → Centre d'aide

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🤝 Support

- **Issues** : [GitHub Issues](https://github.com/Rory-Mercury-91/rory_tool/issues)
- **Discussions** : [GitHub Discussions](https://github.com/Rory-Mercury-91/rory_tool/discussions)
- **Releases** : [GitHub Releases](https://github.com/Rory-Mercury-91/rory_tool/releases)

---

## ⭐ Remerciements

Merci à tous ceux qui utilisent et contribuent au **RenExtract** !

Si ce projet vous aide, n'hésitez pas à lui donner une ⭐ !

---

<div align="center">

**[⬇️ Télécharger la dernière version](https://github.com/Rory-Mercury-91/rory_tool/releases/latest)**

*Fait avec ❤️ pour la communauté Ren'Py*

</div>