!define PRODUCT_NAME       "TraducteurRenPyPro"
!define PRODUCT_VERSION    "1.0"
!define PRODUCT_PUBLISHER  "Rory Mercury 91"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

OutFile "setup_${PRODUCT_NAME}_${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"

Page directory         ; choix du dossier d’installation par l’utilisateur
Page instfiles         ; page d’avancement de l’installation

Section "Installation"
  SetOutPath "$INSTDIR"

  ; Ton EXE principal généré par PyInstaller
  File "dist\TraducteurRenPyPro.exe"

  ; Si tu as d’autres fichiers dans dist (DLL, assets, etc.), décommente :
  ; File /r "dist\*.*"

  ; Raccourci sur le Bureau vers ton EXE
  CreateShortcut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\TraducteurRenPyPro.exe"

  ; Raccourci désinstallation dans le menu Démarrer
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  ; Génération du désinstalleur
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\TraducteurRenPyPro.exe"
  ; Si tu as copié d’autres fichiers, liste-les ou utilise RMDir /r
  ; Delete "$INSTDIR\autre_fichier.ext"

  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
SectionEnd
