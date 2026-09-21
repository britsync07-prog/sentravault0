# AHS Vault

**Zero-Knowledge Biometric Vault** — Secure cloud storage where your smartphone is the key.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Rust](https://img.shields.io/badge/Rust-2021-blue.svg)](https://www.rust-lang.org/)
[![Go](https://img.shields.io/badge/Go-1.25-00ADD8.svg)](https://go.dev/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)

> The server never sees plaintext data. All encryption happens on your devices.

---

## Overview

AHS Vault is a zero-knowledge encrypted storage system where your smartphone (or web browser) acts as a biometric remote control to unlock encrypted files on your desktop. Traditional passwords are replaced with biometric authentication — Face ID, Touch ID, or fingerprint — making security both stronger and more convenient.

### How It Works

```
Desktop (Tauri/Rust) ←→ Backend (Go/PostgreSQL) ←→ Mobile (Android) / Web (React)
       │                         │                         │
  VaultFS (FUSE/WebDAV)    Google Drive API          Biometric Auth
  AES-256-GCM encryption   Encrypted blob storage    WebAuthn / AndroidKeyStore
```

1. **Desktop** generates a 24-word mnemonic and derives cryptographic keys
2. **Mobile/Web** scans a QR code to cryptographically pair with the desktop
3. **Desktop** encrypts files with AES-256-GCM and syncs encrypted blobs to Google Drive
4. To unlock, **desktop** sends a push notification through the backend to your phone
5. You authenticate via **biometrics** on your phone
6. Phone decrypts the master key and sends it back via an encrypted channel (X25519 + AES-GCM)
7. Desktop mounts a **virtual filesystem** (FUSE or WebDAV) that transparently decrypts files

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Zero-Knowledge** | Server only stores encrypted blobs — never sees plaintext keys or files |
| **Biometric Unlock** | Face ID, Touch ID, fingerprint — no passwords needed |
| **Virtual Filesystem** | FUSE (Linux/macOS) or WebDAV (Windows) — encrypted cloud storage appears as a local drive |
| **Multi-Device** | Pair multiple phones/browsers to one desktop vault |
| **Decoy PIN** | Plausible deniability — alternate PIN opens a fake vault under duress |
| **Auto-Lock** | Inactivity timer clears keys from RAM (configurable, default 5 min) |
| **Transfer Guard** | Prevents auto-lock during active file transfers |
| **Offline Recovery** | 24-word mnemonic works without any network connection |
| **Auto-Update** | Silent updates via GitHub Releases with signature verification |
| **Intelligent Shield** | Email phishing detection via IMAP scanning |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Desktop** | Tauri v2 (Rust + React), Vite 7, Tailwind CSS 4, TypeScript 5.8 |
| **Backend** | Go 1.25, Chi router, PostgreSQL 15, Gorilla WebSocket |
| **Web App** | React 19, TypeScript 6, Vite 8, Tailwind CSS 4, Dexie.js |
| **Mobile** | Kotlin, Jetpack Compose, Google Tink, CameraX, BiometricPrompt |
| **Cryptography** | Ed25519, X25519, AES-256-GCM, BIP-39, ECDSA P-256, PBKDF2 |
| **Storage** | Google Drive API (primary), MinIO (alternative) |
| **CI/CD** | GitHub Actions, Docker, Tauri Updater |

---

## Getting Started

### Prerequisites

| Component | Requirements |
|-----------|-------------|
| Desktop | Node.js 22+, Rust stable, Tauri CLI |
| Backend | Go 1.25+, PostgreSQL 15+, Google Drive service account |
| Web App | Node.js 22+, npm |
| Mobile | JDK 17 (Temurin), Android SDK 34, Gradle |
| Docker | Docker Engine 20+, Docker Compose v2 |

### Quick Start

**1. Clone the repository**

```bash
git clone https://github.com/your-org/ahs-app.git
cd ahs-app
```

**2. Start the backend**

```bash
cd vault-backend-go
go mod download

# Set up PostgreSQL (or use Docker)
docker run -d --name vault-db \
  -e POSTGRES_DB=vault \
  -e POSTGRES_USER=vault \
  -e POSTGRES_PASSWORD=vault \
  -p 5432:5432 \
  postgres:15-alpine

# Configure environment
export DATABASE_URL=postgres://vault:vault@localhost:5432/vault

# Run
go run ./cmd/api
```

**3. Start the web app**

```bash
cd vault-web-auth
npm install
npm run dev
```

**4. Start the desktop app**

```bash
cd vault-desktop-tauri
npm install
npm run tauri dev
```

**5. Build the mobile app**

```bash
cd vault-mobile-auth
./gradlew assembleDebug
# APK at app/build/outputs/apk/debug/app-debug.apk
```

### Docker Production

```bash
docker compose -f docker-compose.prod.yml up -d
```

This starts the backend on port `8080` and PostgreSQL with persistent storage.

---

## Project Structure

```
ahs-app/
├── vault-desktop-tauri/          # Desktop app (Tauri v2)
│   ├── src-tauri/
│   │   ├── src/
│   │   │   ├── lib.rs           # Main Tauri commands, vault mount/unmount
│   │   │   ├── crypto.rs        # AES-256-GCM, BIP-39, ECIES encryption
│   │   │   ├── fs.rs            # VaultFS — FUSE/WebDAV virtual filesystem
│   │   │   ├── network.rs       # WebSocket client with auto-reconnect
│   │   │   ├── shield.rs        # Email phishing scanner (IMAP)
│   │   │   ├── oauth.rs         # Google OAuth2 token management
│   │   │   └── drive_mirror.rs  # SHA-256 hash cache for sync optimization
│   │   ├── Cargo.toml
│   │   └── tauri.conf.json
│   ├── src/
│   │   ├── App.tsx              # Main React app, onboarding, lock screen
│   │   ├── screens/Dashboard.tsx
│   │   └── components/
│   │       ├── VaultExplorer.tsx      # File browser
│   │       ├── DeviceManagement.tsx   # Paired device management
│   │       ├── MasterKeyScreen.tsx    # 24-word mnemonic display
│   │       ├── SecurityCenter.tsx     # Security settings
│   │       └── TitleBar.tsx           # Custom window title bar
│   └── package.json
│
├── vault-backend-go/             # Backend API (Go)
│   ├── cmd/api/main.go           # Server entry point
│   ├── internal/
│   │   ├── api/
│   │   │   ├── router.go         # Route definitions, CORS
│   │   │   ├── handlers.go       # API handlers (upload, pair, devices)
│   │   │   └── web_handlers.go   # Web-specific handlers (WebAuthn)
│   │   ├── db/db.go              # PostgreSQL schema & queries
│   │   ├── auth/webauthn.go      # WebAuthn assertion verification
│   │   ├── websocket/hub.go      # WebSocket hub, message routing
│   │   └── storage/
│   │       ├── gdrive.go         # Google Drive blob storage
│   │       └── minio.go          # MinIO/S3 alternative
│   ├── Dockerfile
│   └── go.mod
│
├── vault-web-auth/               # Web authentication app (React)
│   ├── src/
│   │   ├── App.tsx               # State machine, biometric/PIN flows
│   │   ├── lib/
│   │   │   ├── crypto.ts         # ECDSA P-256, X25519, AES-GCM, PBKDF2
│   │   │   └── db.ts             # Dexie.js IndexedDB layer
│   │   ├── hooks/
│   │   │   ├── useWebAuthn.ts    # WebAuthn registration/authentication
│   │   │   └── useWebSocket.ts   # WebSocket with auto-reconnect
│   │   ├── services/api.ts       # HTTP API calls
│   │   ├── components/
│   │   │   ├── BiometricPrompt.tsx
│   │   │   ├── PinPad.tsx        # 5-digit PIN with decoy support
│   │   │   ├── Scanner.tsx       # QR code scanner
│   │   │   └── FloatingNavBar.tsx
│   │   └── screens/
│   │       ├── Dashboard.tsx
│   │       ├── Settings.tsx      # Biometric enrollment, recovery phrase
│   │       ├── Shield.tsx
│   │       └── Activity.tsx
│   └── package.json
│
├── vault-mobile-auth/            # Mobile auth app (Kotlin)
│   ├── app/src/main/java/com/vault/auth/
│   │   ├── MainActivity.kt       # Central coordinator
│   │   ├── CryptoManager.kt      # Hardware-backed key generation
│   │   ├── SecureStorageManager.kt
│   │   └── WebSocketService.kt   # Foreground WebSocket service
│   └── app/build.gradle.kts
│
├── .github/workflows/
│   ├── build-windows.yml         # Desktop CI/CD (Tauri build + sign)
│   └── build-mobile.yml          # Mobile CI/CD (Gradle build)
│
├── docker-compose.prod.yml       # Production Docker setup
└── docs/
    └── AHS_Vault_Complete_Documentation.pdf
```

---

## Security Architecture

### Cryptographic Primitives

| Purpose | Algorithm | Details |
|---------|-----------|---------|
| File encryption | AES-256-GCM | 128KB blocks, random 12-byte nonce per block |
| Key derivation | BIP-39 | 24-word mnemonic, HD key derivation |
| Transport encryption | X25519 ECDH + AES-GCM | Ephemeral session keys per unlock |
| Request signing | Ed25519 | API authentication (desktop) |
| Identity keys | ECDSA P-256 | Mobile/web identity (hardware-backed) |
| PIN hashing | PBKDF2-HMAC-SHA-256 | 310,000 iterations, 16-byte salt |
| Content hashing | SHA-256 | Deduplication and sync optimization |

### Identity System

| Component | Identity | Source |
|-----------|----------|--------|
| Desktop | Ed25519 signing + X25519 encryption | Derived from BIP-39 mnemonic |
| Mobile/Web | ECDSA P-256 + X25519 transport | Generated on first use, hardware-backed |
| Pairing | QR code public key exchange | One-time nonce, 5-minute expiry |

### Security Features

- **Zero-Knowledge Relay**: Backend never sees plaintext — all crypto on clients
- **Decoy PIN**: Alternate PIN opens fake vault under duress
- **Auto-Lock**: Clears keys from RAM after inactivity (default 300s)
- **Transfer Guard**: RAII pattern prevents auto-lock during file transfers
- **Hardware Binding**: Android Keystore / WebAuthn bind keys to biometrics
- **Orphan Healing**: Automatic index repair on mount for corrupted states

---

## API Reference

### Vault Operations

```http
POST /api/vault/upload          # Upload encrypted blob
GET  /api/vault/download/{id}   # Download encrypted blob
POST /api/vault/delete          # Delete encrypted blobs
GET  /api/vault/index           # Get root blob index
POST /api/vault/index           # Set root blob index
```

### Device Management

```http
POST   /api/vault/register      # Register device
GET    /api/vault/devices       # List devices
DELETE /api/vault/devices       # Remove device
```

### Authentication

```http
POST /api/vault/pair            # Mobile pairing (Ed25519 signed)
POST /api/vault/push            # Relay push to device via WebSocket
GET  /api/ws/connect            # WebSocket upgrade
```

### Web Endpoints

```http
POST /api/web/pair              # Web app pairing
POST /api/web/push              # Web unlock relay (WebAuthn verified)
POST /api/web/register-webauthn # Register WebAuthn credential
GET  /api/web/ws/connect        # Web WebSocket upgrade
```

### WebSocket Protocol

```json
// Desktop registers
{ "type": "desktop_register", "public_key": "...", "pairing_nonce": "..." }

// Mobile registers
{ "type": "mobile_register", "public_key": "..." }

// Server messages
{ "type": "unlock_approved", ... }
{ "type": "push_relay", "data": "<encrypted-blob>" }
{ "type": "WAKE_UP_BIOMETRIC" }
{ "type": "connection_established" }
```

Full API documentation: [`docs/AHS_Vault_Complete_Documentation.pdf`](docs/AHS_Vault_Complete_Documentation.pdf)

---

## Database Schema

```sql
CREATE TABLE devices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    public_key      TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    os              TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'secure',
    last_active     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_root_blob_id TEXT
);

CREATE TABLE activity_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_public_key   TEXT NOT NULL,
    event_type          TEXT NOT NULL,
    title               TEXT NOT NULL,
    description         TEXT NOT NULL,
    risk_level          TEXT NOT NULL DEFAULT 'low',
    timestamp           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blobs (
    blob_id             TEXT PRIMARY KEY,
    owner_public_key    TEXT NOT NULL,
    size_bytes          BIGINT NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## Deployment

### Docker Compose (Production)

```yaml
services:
  backend:
    build: ./vault-backend-go
    ports: ["8080:8080"]
    depends_on: [db]
    environment:
      - DATABASE_URL=postgres://vault:vault@db:5432/vault

  db:
    image: postgres:15-alpine
    volumes: [postgres_prod_data:/var/lib/postgresql/data]
    environment:
      - POSTGRES_DB=vault
      - POSTGRES_USER=vault
      - POSTGRES_PASSWORD=vault

volumes:
  postgres_prod_data:
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://vault:vault@localhost:5432/vault` |
| `GOOGLE_DRIVE_CREDENTIALS` | Path to Google Drive service account JSON | — |
| `PORT` | HTTP server port | `8080` |
| `TAURI_SIGNING_PRIVATE_KEY` | Tauri auto-update signing key | Required for desktop builds |

### CI/CD

- **Desktop**: GitHub Actions builds Windows installer on push to `main` or `v*` tags, signs with Tauri key, uploads artifacts, creates GitHub Release
- **Mobile**: GitHub Actions builds debug APK on push to `main`

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Commands

```bash
# Backend
cd vault-backend-go && go run ./cmd/api

# Desktop
cd vault-desktop-tauri && npm run tauri dev

# Web
cd vault-web-auth && npm run dev

# Mobile
cd vault-mobile-auth && ./gradlew assembleDebug
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Documentation

- [Complete Project Documentation](docs/AHS_Vault_Complete_Documentation.pdf) — Full technical reference (PDF)
- [Project Overview](PROJECT.md) — Architecture and milestones
- [Production Setup Guide](PRODUCTION_SETUP_GUIDE_V2.md) — Deployment instructions

---

*SentraVault — Zero-Knowledge Biometric Vault*
  