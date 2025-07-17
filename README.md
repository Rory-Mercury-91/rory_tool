# 🎮 Traducteur Ren'Py Pro

[![Version](https://img.shields.io/github/v/release/Rory-Mercury-91/rory_tool?style=for-the-badge)](https://github.com/Rory-Mercury-91/rory_tool/releases)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/github/license/Rory-Mercury-91/rory_tool?style=for-the-badge)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/Rory-Mercury-91/rory_tool/total?style=for-the-badge)](https://github.com/Rory-Mercury-91/rory_tool/releases)

**Outil de traduction avancé pour les scripts Ren'Py avec interface moderne et fonctionnalités intelligentes.**

---

## ✨ Fonctionnalités principales

### 🚀 **Extraction intelligente**
- **Protection automatique** des codes Ren'Py (`{b}`, `[player_name]`, `\n`, etc.)
- **Séparation intelligente** : textes principaux, expressions `*entre astérisques*`, textes vides
- **Structure organisée** par jeu : `temporaires/[NomDuJeu]/fichiers_a_traduire/`

### 📚 **Système de glossaire permanent**
- **Traduction automatique** des termes récurrents (ex: "Sigh" → "Soupir")
- **Interface complète** : ajout, modification, recherche, validation
- **Import/Export** pour partager vos glossaires
- **Protection automatique** lors de l'extraction

### 🎯 **Modes d'entrée flexibles**
- **Drag & Drop** : Glissez vos fichiers `.rpy` directement
- **Mode Ctrl+V** : Collez du contenu Ren'Py depuis le presse-papier
- **Mode dossier** : Traitement en lot de plusieurs fichiers
- **Fallback intelligent** si Drag & Drop non disponible

### ✅ **Validation avancée**
- **Contrôle de cohérence** OLD/NEW avec rapports détaillés
- **Détection automatique** des placeholders malformés
- **Rapports d'erreurs** dans `avertissements/[NomDuJeu]/`
- **Validation désactivable** pour plus de rapidité

### 🛡️ **Sécurité et sauvegarde**
- **Sauvegardes automatiques** avant chaque traitement
- **Gestionnaire de sauvegardes** intégré avec restauration en un clic
- **Structure organisée** : `sauvegardes/[NomDuJeu]/`

### 🎨 **Interface moderne**
- **Thèmes sombre/clair** vraiment différents
- **Interface adaptative** avec messages contextuels
- **Statistiques temps réel** et compteurs de performance
- **Guide intégré** non-bloquant avec centre d'aide

---

## 📥 Installation

### 💻 **Téléchargement direct (Recommandé)**

Téléchargez la dernière version depuis les [**Releases**](https://github.com/Rory-Mercury-91/rory_tool/releases/latest) :

- **Windows** : `TraducteurRenPyPro-v2.4.4-Windows.zip`
- **Linux** : `TraducteurRenPyPro-v2.4.4-Linux.tar.gz`

### 🚀 **Installation Windows**
1. Téléchargez le fichier `.zip`
2. Extraire l'archive
3. Double-cliquez sur `TraducteurRenPyPro.exe`

### 🐧 **Installation Linux**
```bash
# Télécharger et extraire
tar -xzf TraducteurRenPyPro-v2.4.4-Linux.tar.gz

# Rendre exécutable
chmod +x TraducteurRenPyPro

# Lancer
./TraducteurRenPyPro
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
   - `"Sigh"` → `"Soupir"`
   - `"Hmm"` → `"Hmm"`
   - `"Yeah"` → `"Ouais"`

### **Utilisation automatique**
- Les termes sont **automatiquement protégés** lors de l'extraction
- Ils sont **traduits automatiquement** lors de la reconstruction
- Création d'un fichier `_glossary.txt` en lecture seule

### **Gestion avancée**
- **Import/Export** de glossaires pour partage
- **Recherche en temps réel** dans les entrées
- **Validation** pour détecter les problèmes
- **Persistance** : survit aux réinitialisations

---

## ⚙️ Configuration

### **Options disponibles**
- **📂 Auto ON/OFF** : Ouverture automatique des fichiers générés
- **✅ Valid ON/OFF** : Activation/désactivation de la validation
- **🌙/☀️** : Basculement thème sombre/clair
- **🎯 D&D ↔ 📋 Ctrl+V** : Mode d'entrée (avec fallback intelligent)

### **Raccourcis utiles**
- **Double-clic** sur la zone vide → Ouvrir un fichier
- **Glisser un dossier** → Activer le mode batch
- **🔄 Réinitialiser** → Nettoie sans perdre le fichier actuel
- **📁 Temporaire** → Ouvre le dossier du jeu en cours

---

## 🆕 Nouveautés v2.4.4

### **Architecture refactorisée**
- **Modules enhanced** pour extraction et reconstruction
- **Structure organisée** par jeu avec dossiers dédiés
- **Suppression** de la protection des points de suspension
- **Performances optimisées** pour gros fichiers

### **Nouvelles fonctionnalités**
- **Système de glossaire** permanent et intelligent
- **Validation avancée** avec rapports détaillés
- **Interface améliorée** avec thèmes vraiment différents
- **Modes d'entrée** multiples avec fallback

### **Améliorations techniques**
- **Pipeline de build** automatisé avec GitHub Actions
- **Exécutables autonomes** Windows et Linux
- **Gestion d'erreurs** renforcée
- **Documentation** complète intégrée

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

Merci à tous ceux qui utilisent et contribuent au **Traducteur Ren'Py Pro** !

Si ce projet vous aide, n'hésitez pas à lui donner une ⭐ !

---

<div align="center">

**[⬇️ Télécharger la dernière version](https://github.com/Rory-Mercury-91/rory_tool/releases/latest)**

*Fait avec ❤️ pour la communauté Ren'Py*

</div>