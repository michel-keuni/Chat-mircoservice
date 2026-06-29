# Chat & Call Microservice 🚀

Un micro-service de chat & Appels(VoIP) moderne et performant construit avec **FastAPI**, offrant une communication en temps réel via WebSocket et une API REST complète.

## 🎯 Fonctionnalités

- ✅ **API REST** complète et documentée automatiquement
- 💬 **Communication WebSocket** en temps réel
- 🔐 **Authentification JWT** sécurisée
- 💾 **Base de données MongoDB** avec moteur async (Motor)
- ⚡ **Cache Redis** pour améliorer les performances
- 🧪 **Tests unitaires** avec Pytest
- 📊 **Versionning API** (v1) pour évolution future

## 🏗️ Architecture

```
chat_microservice/
├── app/
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── api/
│   │   └── v1/
│   │       ├── router.py       # Routeur API v1
│   │       └── endpoints/
│   │           ├── chat.py     # Endpoints REST du chat
│   │           └── websocket.py # Endpoints WebSocket
│   ├── core/
│   │   ├── config.py           # Configuration (env variables)
│   │   ├── database.py         # Connexion MongoDB
│   │   └── security.py         # JWT et authentification
│   ├── models/                 # Modèles MongoDB
│   ├── schemas/                # Schémas Pydantic
│   │   └── message.py          # Schéma Message
│   └── services/
│       ├── chat_service.py     # Logique métier du chat
│       ├── redis_service.py    # Service de cache Redis
│       └── websocket_manager.py # Gestion des connexions WebSocket
├── tests/
│   └── test_rest.py            # Tests de l'API REST
├── requirements.txt            # Dépendances Python
├── pytest.ini                  # Configuration Pytest
└── readme.md                   # Ce fichier
```

## 📋 Prérequis

- **Python** 3.11+
- **MongoDB** (version 4.4+)
- **Redis** (version 6.0+)
- **Git** pour le versionning

## ⚙️ Installation

### 1. Cloner le repository

```bash
git clone <your-repo-url>
cd chat_microservice
```

### 2. Créer et activer l'environnement virtuel

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Sur Linux/Mac:
source venv/bin/activate
# Sur Windows:
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
# FastAPI Configuration
PROJECT_NAME=Chat Microservice
DEBUG=True

# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=chat_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🚀 Démarrage du service

### Mode développement

```bash
# Avec rechargement automatique
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Mode production

```bash
# Avec uvloop pour meilleures performances
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Le service sera accessible à : **http://localhost:8000**

## 📚 Documentation API

La documentation interactive est accessible automatiquement :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🔌 Endpoints API

### Santé du service

```http
GET /health
```

Vérifie si le service fonctionne correctement.

**Réponse :**
```json
{
  "status": "healthy"
}
```

### Endpoints Chat (v1)

Tous les endpoints sont préfixés par `/api/v1`

#### Envoyer un message

```http
POST /api/v1/chat/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Bonjour !",
  "room_id": "alice_bob"
}
```

#### Récupérer l'historique d'un salon

```http
GET /api/v1/chat/history/{room_id}?limit=50
```

**Paramètres :**
- `room_id` (path) : Identifiant du salon
- `limit` (query, optionnel) : Nombre maximum de messages (défaut: 50)

## 🔌 WebSocket - Communication en temps réel

### Structure du `room_id`

Le `room_id` identifie un salon de conversation. Il existe deux cas d'usage :

#### 1. Discussion privée entre 2 utilisateurs (DM)

Concaténer les IDs des 2 utilisateurs **en ordre alphabétique**, séparés par un underscore :

```
// Si user1="alice" et user2="bob"
room_id = "alice_bob"  // ✅ Correct (alphabétique)
room_id = "bob_alice"  // ❌ Incorrect
```

**Avantage :** Garantit une unicité bidirectionnelle. Alice et Bob se retrouvent toujours dans le même salon.

#### 2. Discussion de groupe

Utiliser un UUID ou un identifiant unique :

```
room_id = "550e8400-e29b-41d4-a716-446655440000"  // UUID
room_id = "group_dev_team_2026"                   // Identifiant unique
```

### 1. Connexion à un salon de discussion (`/ws/{room_id}`)

Cet endpoint permet de rejoindre un salon spécifique afin d'envoyer et de recevoir des messages en temps réel.

```text
ws://localhost:8000/api/v1/ws/{room_id}?token={jwt_token}
```

### 2. Connexion globale de l'utilisateur (`/ws/user/`)

Cet endpoint établit une connexion WebSocket persistante pour un utilisateur, quel que soit le salon où il se trouve.

Son objectif principal est de recevoir des **notifications en temps réel**, notamment lorsqu'un utilisateur reçoit un **message direct (DM)** alors qu'il n'est pas connecté au salon correspondant.

Cette connexion est destinée exclusivement à la réception d'événements globaux (notifications, nouveaux messages directs, invitations, etc.). Le client ne doit pas envoyer de données via ce WebSocket.

```text
ws://localhost:8000/api/v1/ws/user/?token={jwt_token}
```

**Paramètres :**

- `room_id` (path) : Identifiant du salon (uniquement pour `/ws/{room_id}`)
- `token` (query parameter) : JWT access token obtenu auprès du service d'authentification

### Exemple avec JavaScript

```javascript
const roomId = "alice_bob";
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

// Connexion au salon
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws/${roomId}?token=${token}`
);

  ws.onopen = () => {
    console.log("Connecté au salon :", roomId);
    // Envoyer un message JSON conforme au protocole
    ws.send(JSON.stringify({ type: "chat_message", payload: { content: "Bonjour !" } }));
  };

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(`[${message.user_id}] : ${message.content}`);
};

ws.onerror = (error) => console.error("Erreur WebSocket :", error);

ws.onclose = () => console.log("Déconnecté du salon");

// Connexion globale pour les notifications
const userWs = new WebSocket(
  `ws://localhost:8000/api/v1/ws/user/?token=${token}`
);

userWs.onopen = () => {
  console.log("Connecté pour les notifications globales.");
};

userWs.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log("Nouvelle notification reçue !", notification);
};

userWs.onerror = (error) =>
  console.error("Erreur WebSocket (notifications) :", error);

userWs.onclose = () =>
  console.log("Déconnecté des notifications.");
```

### Protocole de communication

Tous les messages envoyés au serveur via les endpoints WebSocket doivent être au format JSON. Le format général attendu est :

```json
{
  "type": "<event_type>",
  "payload": { /* données dépendant du type */ }
}
```

Exemples :

- Envoi d'un message de chat (client -> serveur) :

```json
{
  "type": "chat_message",
  "payload": { "content": "Bonjour !" }
}
```

- Message de diffusion (serveur -> clients) : le serveur enrichit et renvoie un objet JSON contenant le message persisté :

```json
{
  "type": "chat_message",
  "payload": {
    "_id": "507f1f77bcf86cd799439011",
    "room_id": "alice_bob",
    "user_id": "alice",
    "content": "Bonjour !",
    "timestamp": "2026-06-25T10:30:00.000Z"
  }
}
```

- Événements d'appel / signalisation (exemples) :

```json
{
  "type": "call_request",
  "payload": { "target_user": "bob" }
}

{
  "type": "voip_offer",
  "payload": { "sdp": "v=0..." }
}

{
  "type": "ice_candidate",
  "payload": { "candidate": "candidate:..." }
}
```

Note : le serveur attend `type` et `payload` ; les messages dépourvus de ces clés seront ignorés.

## 🧪 Tests

### Exécuter tous les tests

```bash
pytest
```

### Exécuter avec rapport de couverture

```bash
pytest --cov=app --cov-report=html
```

### Tests spécifiques

```bash
# Tests REST uniquement
pytest tests/test_rest.py -v

# Avec logs détaillés
pytest -v -s
```

## 🔐 Authentification JWT

Ce service de chat utilise **JWT (JSON Web Tokens)** pour sécuriser les accès.

### ⚠️ Configuration critique : SECRET_KEY partagée

**IMPORTANT** : La `SECRET_KEY` configurée dans ce service **DOIT ÊTRE IDENTIQUE** à celle du service d'authentification qui génère les tokens JWT. Cela permet au service de chat de :

1. **Valider les tokens** reçus lors des requêtes REST (en-tête `Authorization: Bearer`)
2. **Décoder les tokens** reçus pour les connexions WebSocket (query parameter `token`)
3. **Extraire le `sub` (user_id)** du payload JWT pour identifier l'utilisateur

```env
# Cette SECRET_KEY DOIT correspondre à celle du service d'authentification
SECRET_KEY=your-same-secret-key-as-auth-service
ALGORITHM=HS256
```

### Obtenir un token (auprès du service d'auth)

Le token doit être obtenu auprès de votre service d'authentification :

```http
POST https://auth-service.example.com/auth/login
Content-Type: application/json

{
  "username": "alice",
  "password": "password123"
}
```

**Réponse :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInN1YiI6ImFsaWNlIn0...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Utiliser le token

#### Pour les requêtes REST

Ajouter l'en-tête d'autorisation :

```http
GET /api/v1/chat/history/alice_bob
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Pour les connexions WebSocket

Passer le token en query parameter :

```
ws://localhost:8000/api/v1/ws/alice_bob?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Payload JWT attendu

Le service extrait le claim `sub` pour identifier l'utilisateur. Votre service d'authentification doit générer des tokens avec cette structure minimale :

```json
{
  "sub": "alice",
  "iat": 1719323400,
  "exp": 1719325200
}
```

Où :
- `sub` : User ID (identifiant unique de l'utilisateur)
- `iat` : Issued at (timestamp de génération)
- `exp` : Expiration (timestamp d'expiration)

## 📊 Variables d'environnement

| Variable | Description | Défaut | Requis |
|----------|-------------|--------|--------|
| `SECRET_KEY` | Clé secrète JWT **[DOIT correspondre à celle du service d'auth]** | - | ✅ OUI |
| `MONGODB_URL` | URI MongoDB | mongodb://localhost:27017 | Non |
| `DATABASE_NAME` | Nom de la base MongoDB | chat_db | Non |
| `REDIS_URL` | URI Redis | redis://localhost:6379/0 | Non |
| `ALGORITHM` | Algorithme JWT | HS256 | Non |
| `PROJECT_NAME` | Nom du projet | Chat Microservice | Non |
| `DEBUG` | Mode debug | False | Non |

## 🐛 Dépannage

### MongoDB non accessible

```bash
# Vérifier que MongoDB est lancé
mongosh
# ou
mongo
```

### Redis non accessible

```bash
# Vérifier que Redis est lancé
redis-cli ping
# Devrait retourner : PONG
```

### Erreurs d'import

```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

## 📦 Dépendances principales

- **FastAPI** 0.138+ : Framework web asynchrone moderne
- **Uvicorn** 0.49+ : Serveur ASGI haute performance
- **MongoDB Motor** 3.7+ : Driver async MongoDB
- **Redis** 8.0+ : Client Redis
- **Pydantic** 2.13+ : Validation de données
- **PyJWT** 2.13+ : Implémentation JWT
- **Pytest** 9.1+ : Framework de test

## 🤝 Contribution

1. Créer une branche feature : `git checkout -b feat/my-feature`
2. Commiter les changements : `git commit -m "Add new feature"`
3. Pousser la branche : `git push origin feat/my-feature`
4. Créer une Pull Request

## 📝 Licence

MIT License - Voir LICENSE pour plus de détails

## � Notes importantes

### Redis et la diffusion en temps réel

Le service utilise Redis comme **broker de messages en temps réel** :

1. Quand un utilisateur envoie un message via WebSocket
2. Le message est sauvegardé dans MongoDB
3. Le message est publié sur le canal Redis `room:{room_id}`
4. Tous les clients connectés au même room reçoivent le message instantanément

Cette architecture permet une **scalabilité horizontale** : plusieurs instances du service peuvent être déployées derrière un load balancer.

### Gestion des connexions WebSocket

- Les connexions WebSocket écoutent les messages Redis en arrière-plan
- Lors d'une déconnexion, la connexion est supprimée du gestionnaire
- Les sessions sont sans état (stateless) pour permettre la scalabilité

## 👨‍💻 Auteur

Créé avec ❤️ par Michel Le Roi

---

**Dernière mise à jour :** 25 juin 2026
