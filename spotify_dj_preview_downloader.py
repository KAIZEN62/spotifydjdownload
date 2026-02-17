#!/usr/bin/env python3
"""
Spotify DJ Downloader (legal workflows)
---------------------------------------
- Mode `preview`: télécharge les extraits MP3 (preview_url) d'une playlist Spotify.
- Mode `full-legal`: télécharge des morceaux complets depuis des URLs directes
  listées dans un CSV (sources pour lesquelles vous avez les droits/licences).

⚠️ Le script ne contourne pas les protections Spotify et ne télécharge pas les
morceaux complets depuis Spotify.
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    return re.sub(r"\s+", " ", name).strip()


def http_json_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[bytes] = None,
) -> Dict:
    req = Request(url, method=method, headers=headers or {}, data=data)
    with urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def download_binary(url: str, output_path: Path) -> None:
    req = Request(url, method="GET")
    with urlopen(req, timeout=60) as response:
        output_path.write_bytes(response.read())


def get_access_token(client_id: str, client_secret: str) -> str:
    credentials = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = base64.b64encode(credentials).decode("utf-8")
    payload = urlencode({"grant_type": "client_credentials"}).encode("utf-8")

    data = http_json_request(
        TOKEN_URL,
        method="POST",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=payload,
    )
    return data["access_token"]


def extract_playlist_id(playlist_input: str) -> str:
    match = re.search(r"playlist/([a-zA-Z0-9]+)", playlist_input)
    if match:
        return match.group(1)
    return playlist_input.strip()


def get_playlist_tracks(token: str, playlist_id: str) -> List[Dict]:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/playlists/{playlist_id}/tracks?limit=100"
    tracks: List[Dict] = []

    while url:
        payload = http_json_request(url, headers=headers)
        for item in payload.get("items", []):
            track = item.get("track")
            if track:
                tracks.append(track)
        url = payload.get("next")

    return tracks


def build_track_filename(track: Dict) -> str:
    artists = ", ".join(a["name"] for a in track.get("artists", []))
    title = track.get("name", "unknown")
    return sanitize_filename(f"{artists} - {title}.mp3")


def run_preview(playlist: str, output_dir: Path, overwrite: bool) -> None:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError(
            "Variables manquantes: SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET"
        )

    playlist_id = extract_playlist_id(playlist)
    token = get_access_token(client_id, client_secret)
    tracks = get_playlist_tracks(token, playlist_id)

    if not tracks:
        print("Aucun morceau trouvé dans la playlist.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped_no_preview = 0
    skipped_existing = 0

    for track in tracks:
        preview_url: Optional[str] = track.get("preview_url")
        if not preview_url:
            skipped_no_preview += 1
            continue

        out_file = output_dir / build_track_filename(track)
        if out_file.exists() and not overwrite:
            skipped_existing += 1
            continue

        try:
            download_binary(preview_url, out_file)
            downloaded += 1
            print(f"✅ Preview: {out_file.name}")
        except (HTTPError, URLError) as exc:
            print(f"❌ Erreur '{out_file.name}': {exc}")

    print("\n--- Résumé preview ---")
    print(f"Morceaux playlist          : {len(tracks)}")
    print(f"Previews téléchargées      : {downloaded}")
    print(f"Sans preview               : {skipped_no_preview}")
    print(f"Déjà présents (ignorés)    : {skipped_existing}")


def run_full_legal(manifest_csv: Path, output_dir: Path, overwrite: bool) -> None:
    if not manifest_csv.exists():
        raise FileNotFoundError(f"Manifest introuvable: {manifest_csv}")

    output_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped_existing = 0
    failed = 0

    with manifest_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"url", "filename"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("Le CSV doit contenir au minimum les colonnes: url, filename")

        for row in reader:
            url = (row.get("url") or "").strip()
            filename = sanitize_filename((row.get("filename") or "").strip())
            if not url or not filename:
                continue

            out_file = output_dir / filename
            if out_file.suffix == "":
                out_file = out_file.with_suffix(".mp3")

            if out_file.exists() and not overwrite:
                skipped_existing += 1
                continue

            try:
                download_binary(url, out_file)
                downloaded += 1
                print(f"✅ Full légal: {out_file.name}")
            except (HTTPError, URLError) as exc:
                failed += 1
                print(f"❌ Erreur '{out_file.name}': {exc}")

    print("\n--- Résumé full-legal ---")
    print(f"Fichiers téléchargés       : {downloaded}")
    print(f"Déjà présents (ignorés)    : {skipped_existing}")
    print(f"Échecs                     : {failed}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Outils DJ légaux: previews Spotify et téléchargements full depuis URLs autorisées."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    p_preview = subparsers.add_parser("preview", help="Télécharger les previews Spotify")
    p_preview.add_argument("playlist", help="URL/ID playlist Spotify")
    p_preview.add_argument("-o", "--output", default="downloads_previews")
    p_preview.add_argument("--overwrite", action="store_true")

    p_full = subparsers.add_parser(
        "full-legal",
        help="Télécharger des morceaux complets depuis un CSV d'URLs directes autorisées",
    )
    p_full.add_argument("manifest", help="CSV avec colonnes: url,filename")
    p_full.add_argument("-o", "--output", default="downloads_full")
    p_full.add_argument("--overwrite", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.mode == "preview":
        run_preview(args.playlist, Path(args.output), args.overwrite)
        return

    if args.mode == "full-legal":
        run_full_legal(Path(args.manifest), Path(args.output), args.overwrite)
        return

    parser.error("Mode inconnu")


if __name__ == "__main__":
    main()
