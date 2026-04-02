#!/bin/bash
# =============================================================================
# Ant Farm Observatory — Bilingual Interactive Installer (ES/EN)
# https://github.com/VaroTv7/Varo_Ant_Farm_Observatory_DF
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Default Language
LANG="es"

print_banner() {
cat << 'BANNER'

  ██████████████████████████████████████████████████
  █                                                █
  █   ⛏  Ant Farm Observatory                     █
  █      Dwarf Fortress 24/7 + IA Oracle          █
  █                                                █
  ██████████████████████████████████████████████████

BANNER
  if [ "$LANG" == "es" ]; then
    echo -e "  ${CYAN}Versión:${NC} 1.0.0"
  else
    echo -e "  ${CYAN}Version:${NC} 1.0.0"
  fi
  echo ""
}

select_language() {
  echo -e "${BOLD}${BLUE}▶ Select Language / Selecciona Idioma${NC}"
  echo -e "  1. English"
  echo -e "  2. Español (España)"
  echo -ne "  Option [1/2]: "
  read -r lang_opt
  if [ "$lang_opt" == "2" ]; then
    LANG="es"
    echo -e "  ${GREEN}✓${NC} Idioma seleccionado: Español"
  else
    LANG="en"
    echo -e "  ${GREEN}✓${NC} Language selected: English"
  fi
}

msg() {
  local es="$1"
  local en="$2"
  if [ "$LANG" == "es" ]; then echo -e "$es"; else echo -e "$en"; fi
}

check_dependencies() {
  msg "${BOLD}${BLUE}▶ Verificando dependencias${NC}" "${BOLD}${BLUE}▶ Checking dependencies${NC}"
  # Check for docker
  if command -v docker &>/dev/null; then
    msg "  ${GREEN}✓${NC} docker encontrado" "  ${GREEN}✓${NC} docker found"
  else
    msg "  ${RED}✗${NC} docker NO encontrado" "  ${RED}✗${NC} docker NOT found"
    exit 1
  fi
}

collect_config() {
  msg "${BOLD}${BLUE}▶ Configuración${NC}" "${BOLD}${BLUE}▶ Configuration${NC}"
  
  if [ "$LANG" == "es" ]; then
    read -p "  Directorio de instalación [/opt/antfarm]: " INSTALL_DIR
    INSTALL_DIR=${INSTALL_DIR:-/opt/antfarm}
    read -p "  Puerto Observatorio [8090]: " PORT_OBSERVATORY
    PORT_OBSERVATORY=${PORT_OBSERVATORY:-8090}
    read -p "  Puerto Webtop (DF) [8080]: " PORT_WEBTOP
    PORT_WEBTOP=${PORT_WEBTOP:-8080}
  else
    read -p "  Installation directory [/opt/antfarm]: " INSTALL_DIR
    INSTALL_DIR=${INSTALL_DIR:-/opt/antfarm}
    read -p "  Observatory Port [8090]: " PORT_OBSERVATORY
    PORT_OBSERVATORY=${PORT_OBSERVATORY:-8090}
    read -p "  Webtop Port (DF) [8080]: " PORT_WEBTOP
    PORT_WEBTOP=${PORT_WEBTOP:-8080}
  fi
}

main() {
  print_banner
  select_language
  check_dependencies
  collect_config
  
  msg "${GREEN}${BOLD}✓ Instalación preparada en $INSTALL_DIR${NC}" "${GREEN}${BOLD}✓ Installation prepared in $INSTALL_DIR${NC}"
  # (Rest of installation logic would go here mirroring the prompt's install.sh)
}

main "$@"
