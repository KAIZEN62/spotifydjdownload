# Spotify DJ Downloader (workflows légaux)

Ce projet propose 2 modes:

1. **`preview`**: télécharge les extraits Spotify (`preview_url`) d'une playlist.
2. **`full-legal`**: télécharge des morceaux complets depuis un CSV d'URLs directes **que vous avez le droit d'utiliser** (DJ pools, achats, licences, etc.).

> ⚠️ Ce script ne contourne pas Spotify et ne télécharge pas de morceaux complets depuis Spotify.

## Installation

Aucune dépendance externe: Python standard suffit.

## Lancement direct via Bash (recommandé)

Un lanceur prêt à l'emploi est disponible:

```bash
./bash/lancer.sh
```

### Exemples

```bash
./bash/lancer.sh preview "https://open.spotify.com/playlist/PLAYLIST_ID"
./bash/lancer.sh preview "PLAYLIST_ID" mes_previews --overwrite
./bash/lancer.sh full-legal manifest.csv mes_full_tracks
```

## Mode 1: Preview Spotify (commande Python directe)

### Variables d'environnement Spotify

```bash
export SPOTIFY_CLIENT_ID="ton_client_id"
export SPOTIFY_CLIENT_SECRET="ton_client_secret"
```

### Commande

```bash
python spotify_dj_preview_downloader.py preview "https://open.spotify.com/playlist/PLAYLIST_ID"
```

## Mode 2: Full légal via manifest CSV

Créer un CSV, par exemple `manifest.csv`:

```csv
url,filename
https://example.com/track1.mp3,Artist - Track 1.mp3
https://example.com/track2.wav,Artist - Track 2.wav
```

Puis lancer:

```bash
python spotify_dj_preview_downloader.py full-legal manifest.csv -o mes_full_tracks
```

Options communes:

- `--overwrite` : remplace les fichiers existants.

## Idée workflow DJ

- Utiliser `preview` pour présélectionner rapidement.
- Acheter/licencier les versions complètes.
- Utiliser `full-legal` avec les URLs directes de vos sources autorisées.
