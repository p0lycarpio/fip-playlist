# fip-playlist

Synchronisation des morceaux mis en favoris sur Radio France avec Spotify.
Originallement conçu pour Fip, l'appli fonctionne avec toutes les radios du groupe qui diffusent les titres.

## Prérequis

- Un compte Radio France (créé sur l'appli mobile ou site web)
- Un compte Spotify
  - Créer une [app développeur](https://developer.spotify.com/documentation/web-api/concepts/apps). Récupérer le `client_id`, `client_secret` et définir l'URL de redirection à `http://127.0.0.1:8080` par exemple. [Documentation](https://developer.spotify.com/documentation/web-api)

### Architectures

| Architecture | Available | Dockerfile |
| :----: | :----: | ---- |
| x86-64 | ✅ | Dockerfile |
| arm64 | ✅ | Dockerfile.aarch64 |
| armhf | ❌ | |

## Installation

Construire l'image Docker avec `docker build -t fip-playlist -f Dockerfile .`

Définir les variables d'environnement dans un fichier ou via les arguments `-e`. Lancer l'application (remplacer le port par celui défini sur Spotify) :

```bash
docker run -d \
    --env-file .env \
    --port 8080:8080
    --name fiplaylist fip-playlist
```

### Utilisation

Enregistrez des "titres favoris" directement sur l'application ou le site Radio France grâce à l'icône « 🤍 ». Retrouvez-les ensuite dans vos favoris ou une playlist Spotify après la synchronisation périodique. 

## Variables d'environnement

- **RADIO_FRANCE_EMAIL**: adresse e-mail du compte
- **RADIO_FRANCE_PASSWORD**: mot de passe Radio France
- **SPOTIFY_CLIENT_ID**: Spotify app client id
- **SPOTIFY_CLIENT_SECRET**: Spotify app secret
- **SPOTIFY_REDIRECT_URL**: lien de redirection de l'app et port
- *SPOTIFY_PLAYLIST*: ID de la playlist, optionnel. Si non définie, enregistre les morceaux dans les favoris
- *CRON*: lancement programmé de la synchronisation. Format CRON, par défaut : `*/10 * * * *`
- *TZ* : timezone. Défaut: `UTC`
