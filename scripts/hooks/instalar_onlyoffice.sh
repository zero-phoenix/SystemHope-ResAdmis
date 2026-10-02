#!/usr/bin/env bash
# Instala ONLYOFFICE Document Builder (motor de `previsualizar`; LibreOffice
# esta prohibido, regla maxima 1 de AGENTS.md). Idempotente: si ya esta, no hace
# nada. Si no hay red o permisos, avisa y sale con 0 para no romper la sesion.
set -u
DEB_URL="https://download.onlyoffice.com/install/desktop/docbuilder/linux/onlyoffice-documentbuilder_amd64.deb"

if command -v docbuilder >/dev/null 2>&1 || [ -x /opt/onlyoffice/documentbuilder/docbuilder ]; then
  echo "ONLYOFFICE Document Builder: ya instalado."
  exit 0
fi
if [ "$(uname -s)" != "Linux" ] || ! command -v apt-get >/dev/null 2>&1; then
  echo "ONLYOFFICE Document Builder: instalacion automatica solo en Linux con apt; instalalo a mano."
  exit 0
fi
SUDO=""
if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then SUDO="sudo"; fi
TMP="$(mktemp -d)"
if curl -fsSL -o "$TMP/docbuilder.deb" "$DEB_URL" \
   && $SUDO apt-get update -qq >/dev/null 2>&1 \
   && $SUDO apt-get install -y -qq --no-install-recommends "$TMP/docbuilder.deb" >/dev/null 2>&1; then
  echo "ONLYOFFICE Document Builder: instalado en /opt/onlyoffice/documentbuilder."
else
  echo "AVISO: no se pudo instalar ONLYOFFICE Document Builder (red o permisos). previsualizar no dara imagenes."
fi
rm -rf "$TMP"
exit 0
