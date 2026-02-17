#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_SCRIPT="$ROOT_DIR/spotify_dj_preview_downloader.py"

if [[ ! -f "$PY_SCRIPT" ]]; then
  echo "❌ Script introuvable: $PY_SCRIPT"
  exit 1
fi

usage() {
  cat <<'EOF'
Usage:
  ./bash/lancer.sh preview <playlist_url_ou_id> [output_dir] [--overwrite]
  ./bash/lancer.sh full-legal <manifest.csv> [output_dir] [--overwrite]

Exemples:
  ./bash/lancer.sh preview "https://open.spotify.com/playlist/PLAYLIST_ID"
  ./bash/lancer.sh preview "PLAYLIST_ID" mes_previews --overwrite
  ./bash/lancer.sh full-legal manifest.csv mes_full_tracks
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

MODE="$1"
INPUT="$2"
OUTPUT=""
OVERWRITE=""

if [[ $# -ge 3 ]]; then
  case "$3" in
    --overwrite)
      OVERWRITE="--overwrite"
      ;;
    *)
      OUTPUT="$3"
      ;;
  esac
fi

if [[ $# -ge 4 ]]; then
  if [[ "$4" == "--overwrite" ]]; then
    OVERWRITE="--overwrite"
  else
    echo "❌ Option inconnue: $4"
    usage
    exit 1
  fi
fi

case "$MODE" in
  preview)
    if [[ -n "$OUTPUT" ]]; then
      python3 "$PY_SCRIPT" preview "$INPUT" -o "$OUTPUT" $OVERWRITE
    else
      python3 "$PY_SCRIPT" preview "$INPUT" $OVERWRITE
    fi
    ;;
  full-legal)
    if [[ -n "$OUTPUT" ]]; then
      python3 "$PY_SCRIPT" full-legal "$INPUT" -o "$OUTPUT" $OVERWRITE
    else
      python3 "$PY_SCRIPT" full-legal "$INPUT" $OVERWRITE
    fi
    ;;
  *)
    echo "❌ Mode inconnu: $MODE"
    usage
    exit 1
    ;;
esac
