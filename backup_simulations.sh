#!/usr/bin/env bash
# =============================================================================
# backup_simulations.sh
# Sauvegarde des fichiers de résultats de simulation
#
# Usage:
#   ./backup_simulations.sh [OPTIONS]
#
# Options:
#   -s, --source <dossier>      Dossier source à sauvegarder (défaut: ./simulations)
#   -d, --dest   <dossier>      Dossier de destination (défaut: ./backup)
#   -e, --ext    <extension>    Filtrer par extension (ex: csv, dat, out)
#                               Accepte plusieurs extensions: -e "csv dat out"
#   -c, --compress              Créer une archive .tar.gz (défaut: copie simple)
#   -h, --help                  Afficher cette aide
#
# Exemples:
#   ./backup_simulations.sh
#   ./backup_simulations.sh -s ~/simulations -e csv
#   ./backup_simulations.sh -s ~/simulations -e "csv dat" --compress
#   ./backup_simulations.sh -s ~/simulations -d ~/mes_backups --compress
# =============================================================================

set -euo pipefail

# ──────────────────────────────────────────────
# Couleurs pour le terminal
# ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ──────────────────────────────────────────────
# Valeurs par défaut
# ──────────────────────────────────────────────
SOURCE_DIR="./outputs"
BACKUP_BASE="./backup"
EXTENSIONS=""
COMPRESS=false

# ──────────────────────────────────────────────
# Fonctions utilitaires
# ──────────────────────────────────────────────
usage() {
    sed -n '/^# Usage:/,/^# ====/p' "$0" | sed 's/^# \?//'
    exit 0
}

log_info()    { echo -e "${BLUE}[INFO]${RESET}  $*"; }
log_ok()      { echo -e "${GREEN}[OK]${RESET}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
log_error()   { echo -e "${RED}[ERREUR]${RESET} $*"; }
log_section() { echo -e "\n${BOLD}${CYAN}── $* ──${RESET}"; }

# Écriture dans le fichier log
write_log() {
    local log_file="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$log_file"
}

# ──────────────────────────────────────────────
# Parsing des arguments
# ──────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--source)
            SOURCE_DIR="$2"; shift 2 ;;
        -d|--dest)
            BACKUP_BASE="$2"; shift 2 ;;
        -e|--ext)
            EXTENSIONS="$2"; shift 2 ;;
        -c|--compress)
            COMPRESS=true; shift ;;
        -h|--help)
            usage ;;
        *)
            log_error "Option inconnue : $1"
            echo "Utilisez -h pour afficher l'aide."
            exit 1 ;;
    esac
done

# ──────────────────────────────────────────────
# Vérifications
# ──────────────────────────────────────────────
log_section "Vérification"

# Dossier source
SOURCE_DIR="${SOURCE_DIR%/}"   # supprime le slash final si présent
if [[ ! -d "$SOURCE_DIR" ]]; then
    log_error "Le dossier source '$SOURCE_DIR' n'existe pas."
    exit 1
fi
log_ok "Dossier source : $SOURCE_DIR"

# Dossier de destination + horodatage
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
BACKUP_DIR="${BACKUP_BASE}/${TIMESTAMP}"
LOG_FILE="${BACKUP_BASE}/backup.log"

mkdir -p "$BACKUP_BASE"
log_ok "Dossier de destination : $BACKUP_DIR"

# ──────────────────────────────────────────────
# Construction de la liste des fichiers
# ──────────────────────────────────────────────
log_section "Recherche des fichiers"

# Construire la commande find selon les extensions demandées
declare -a FIND_CMD=( find "$SOURCE_DIR" -type f )

if [[ -n "$EXTENSIONS" ]]; then
    # Convertit "csv dat out" en conditions find : -name "*.csv" -o -name "*.dat" ...
    declare -a EXT_CONDS=()
    first=true
    for ext in $EXTENSIONS; do
        ext="${ext#.}"   # retire le point si l'utilisateur l'a mis
        if $first; then
            EXT_CONDS+=( -name "*.${ext}" )
            first=false
        else
            EXT_CONDS+=( -o -name "*.${ext}" )
        fi
    done
    FIND_CMD+=( \( "${EXT_CONDS[@]}" \) )
    log_info "Filtre actif : extensions [ $EXTENSIONS ]"
else
    log_info "Aucun filtre — tous les fichiers seront sauvegardés"
fi

# Collecte des fichiers dans un tableau
mapfile -t FILES < <( "${FIND_CMD[@]}" | sort )

if [[ ${#FILES[@]} -eq 0 ]]; then
    log_warn "Aucun fichier trouvé dans '$SOURCE_DIR' avec les critères donnés."
    write_log "$LOG_FILE" "WARN  | source=$SOURCE_DIR | ext=${EXTENSIONS:-*} | Aucun fichier trouvé"
    exit 0
fi

log_ok "${#FILES[@]} fichier(s) trouvé(s)"

# ──────────────────────────────────────────────
# Sauvegarde
# ──────────────────────────────────────────────
log_section "Sauvegarde ($( $COMPRESS && echo 'mode archive .tar.gz' || echo 'mode copie' ))"

SUCCESS_COUNT=0
FAIL_COUNT=0

if $COMPRESS; then
    # ── Mode archive ──────────────────────────
    ARCHIVE_PATH="${BACKUP_DIR}.tar.gz"
    TMP_DIR=$(mktemp -d)

    for file in "${FILES[@]}"; do
        rel_path="${file#"$SOURCE_DIR"/}"
        dest_file="${TMP_DIR}/${rel_path}"
        mkdir -p "$(dirname "$dest_file")"
        if cp "$file" "$dest_file"; then
            (( SUCCESS_COUNT++ )) || true
        else
            log_warn "Échec de la copie : $file"
            (( FAIL_COUNT++ )) || true
        fi
    done

    if tar -czf "$ARCHIVE_PATH" -C "$TMP_DIR" .; then
        rm -rf "$TMP_DIR"
        SIZE=$(du -sh "$ARCHIVE_PATH" | cut -f1)
        log_ok "Archive créée : ${BOLD}$ARCHIVE_PATH${RESET} (${SIZE})"
        write_log "$LOG_FILE" "OK    | archive=$ARCHIVE_PATH | fichiers=$SUCCESS_COUNT | taille=$SIZE | ext=${EXTENSIONS:-*} | echecs=$FAIL_COUNT"
    else
        rm -rf "$TMP_DIR"
        log_error "Échec lors de la création de l'archive."
        write_log "$LOG_FILE" "ERROR | archive=$ARCHIVE_PATH | Échec tar"
        exit 1
    fi

else
    # ── Mode copie simple ─────────────────────
    for file in "${FILES[@]}"; do
        rel_path="${file#"$SOURCE_DIR"/}"
        dest_file="${BACKUP_DIR}/${rel_path}"
        mkdir -p "$(dirname "$dest_file")"
        if cp "$file" "$dest_file"; then
            log_ok "Copié : $rel_path"
            (( SUCCESS_COUNT++ )) || true
        else
            log_warn "Échec : $rel_path"
            (( FAIL_COUNT++ )) || true
        fi
    done
    SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    write_log "$LOG_FILE" "OK    | dest=$BACKUP_DIR | fichiers=$SUCCESS_COUNT | taille=$SIZE | ext=${EXTENSIONS:-*} | echecs=$FAIL_COUNT"
fi

# ──────────────────────────────────────────────
# Résumé final
# ──────────────────────────────────────────────
log_section "Résumé"
echo -e "  Fichiers sauvegardés : ${GREEN}${BOLD}${SUCCESS_COUNT}${RESET}"
[[ $FAIL_COUNT -gt 0 ]] && echo -e "  Échecs               : ${RED}${BOLD}${FAIL_COUNT}${RESET}"
echo -e "  Log                  : ${CYAN}${LOG_FILE}${RESET}"
echo ""