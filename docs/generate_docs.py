#!/usr/bin/env python3
"""
AHS Vault - Complete Project Documentation Generator
Generates a comprehensive PDF covering all components end-to-end.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether, HRFlowable
)
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# ─── COLOR PALETTE ─────────────────────────────────────────────
PRIMARY = HexColor("#1a1a2e")
ACCENT = HexColor("#0f3460")
HIGHLIGHT = HexColor("#e94560")
LIGHT_BG = HexColor("#f5f5f5")
CODE_BG = HexColor("#1e1e2e")
CODE_FG = HexColor("#cdd6f4")
SECTION_BG = HexColor("#16213e")
TABLE_HEADER = HexColor("#0f3460")
TABLE_ALT = HexColor("#e8edf3")
BORDER_COLOR = HexColor("#cccccc")

# ─── DOCUMENT SETUP ────────────────────────────────────────────
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "AHS_Vault_Complete_Documentation.pdf")

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    rightMargin=20*mm,
    leftMargin=20*mm,
    topMargin=25*mm,
    bottomMargin=20*mm,
    title="AHS Vault - Complete Project Documentation",
    author="AHS Vault Team",
    subject="Zero-Knowledge Biometric Vault System",
)

# ─── STYLES ────────────────────────────────────────────────────
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    'CoverTitle', parent=styles['Title'],
    fontSize=36, leading=44, textColor=PRIMARY,
    spaceAfter=10, alignment=TA_CENTER, fontName='Helvetica-Bold'
))
styles.add(ParagraphStyle(
    'CoverSubtitle', parent=styles['Normal'],
    fontSize=16, leading=22, textColor=ACCENT,
    spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica'
))
styles.add(ParagraphStyle(
    'CoverMeta', parent=styles['Normal'],
    fontSize=11, leading=16, textColor=grey,
    spaceAfter=4, alignment=TA_CENTER, fontName='Helvetica'
))
styles.add(ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontSize=24, leading=30, textColor=PRIMARY,
    spaceBefore=20, spaceAfter=12, fontName='Helvetica-Bold',
    borderWidth=0, borderPadding=0,
))
styles.add(ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontSize=18, leading=24, textColor=ACCENT,
    spaceBefore=16, spaceAfter=8, fontName='Helvetica-Bold',
))
styles.add(ParagraphStyle(
    'H3', parent=styles['Heading3'],
    fontSize=14, leading=18, textColor=HexColor("#333333"),
    spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold',
))
styles.add(ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontSize=10, leading=15, textColor=HexColor("#333333"),
    spaceAfter=8, alignment=TA_JUSTIFY, fontName='Helvetica',
))
styles.add(ParagraphStyle(
    'BodyBold', parent=styles['Normal'],
    fontSize=10, leading=15, textColor=HexColor("#333333"),
    spaceAfter=8, alignment=TA_JUSTIFY, fontName='Helvetica-Bold',
))
styles.add(ParagraphStyle(
    'CodeBlock', parent=styles['Normal'],
    fontSize=8.5, leading=12, textColor=HexColor("#d4d4d4"),
    fontName='Courier', backColor=HexColor("#1e1e2e"),
    borderWidth=0, borderPadding=6, leftIndent=10, rightIndent=10,
    spaceAfter=10, spaceBefore=6,
))
styles.add(ParagraphStyle(
    'BulletCustom', parent=styles['Normal'],
    fontSize=10, leading=15, textColor=HexColor("#333333"),
    leftIndent=20, bulletIndent=8, spaceAfter=3, fontName='Helvetica',
))
styles.add(ParagraphStyle(
    'TableHeader', parent=styles['Normal'],
    fontSize=9, leading=12, textColor=white,
    fontName='Helvetica-Bold', alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    'TableCell', parent=styles['Normal'],
    fontSize=9, leading=12, textColor=HexColor("#333333"),
    fontName='Helvetica',
))
styles.add(ParagraphStyle(
    'TableCellCode', parent=styles['Normal'],
    fontSize=8, leading=11, textColor=HexColor("#c7254e"),
    fontName='Courier',
))
styles.add(ParagraphStyle(
    'Caption', parent=styles['Normal'],
    fontSize=9, leading=12, textColor=grey,
    fontName='Helvetica-Oblique', alignment=TA_CENTER, spaceAfter=12,
))
styles.add(ParagraphStyle(
    'TOCEntry1', parent=styles['Normal'],
    fontSize=12, leading=18, textColor=PRIMARY,
    fontName='Helvetica-Bold', leftIndent=0, spaceAfter=4,
))
styles.add(ParagraphStyle(
    'TOCEntry2', parent=styles['Normal'],
    fontSize=10, leading=16, textColor=HexColor("#555555"),
    fontName='Helvetica', leftIndent=20, spaceAfter=2,
))

# ─── HELPER FUNCTIONS ──────────────────────────────────────────
def hr():
    return HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10, spaceBefore=10)

def spacer(h=6):
    return Spacer(1, h)

def code_block(text):
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lines = escaped.split("\n")
    formatted = "<br/>".join(lines)
    return Paragraph(f"<pre>{formatted}</pre>", styles['CodeBlock'])

def make_table(headers, rows, col_widths=None):
    """Create a styled table."""
    header_cells = [Paragraph(h, styles['TableHeader']) for h in headers]
    data = [header_cells]
    for row in rows:
        data.append([Paragraph(str(c), styles['TableCell']) for c in row])

    if col_widths is None:
        avail = doc.width
        col_widths = [avail / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t

def bullet_list(items):
    elements = []
    for item in items:
        elements.append(Paragraph(f"<bullet>&bull;</bullet> {item}", styles['BulletCustom']))
    return elements

# ─── PAGE NUMBER CALLBACK ──────────────────────────────────────
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(grey)
    page_num = canvas.getPageNumber()
    text = f"AHS Vault Documentation  |  Page {page_num}"
    canvas.drawCentredString(A4[0] / 2, 12*mm, text)
    # Header line
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, A4[1] - 20*mm, A4[0] - 20*mm, A4[1] - 20*mm)
    canvas.restoreState()

def first_page(canvas, doc):
    pass  # No header/footer on cover page

# ═══════════════════════════════════════════════════════════════
# BUILD DOCUMENT CONTENT
# ═══════════════════════════════════════════════════════════════
story = []

# ─── COVER PAGE ────────────────────────────────────────────────
story.append(Spacer(1, 80))
story.append(Paragraph("AHS VAULT", styles['CoverTitle']))
story.append(Spacer(1, 10))
story.append(Paragraph("Complete Project Documentation", styles['CoverSubtitle']))
story.append(Spacer(1, 6))
story.append(HRFlowable(width="40%", thickness=2, color=HIGHLIGHT, spaceAfter=10, spaceBefore=10))
story.append(Spacer(1, 6))
story.append(Paragraph("Zero-Knowledge Biometric Vault System", styles['CoverSubtitle']))
story.append(Spacer(1, 30))
story.append(Paragraph(f"Version 0.1.20  |  {datetime.now().strftime('%B %Y')}", styles['CoverMeta']))
story.append(Paragraph("Confidential - Internal Use Only", styles['CoverMeta']))
story.append(Spacer(1, 60))

# Tech stack badges
tech_data = [
    [Paragraph("<b>Desktop</b>", styles['TableHeader']),
     Paragraph("<b>Backend</b>", styles['TableHeader']),
     Paragraph("<b>Web App</b>", styles['TableHeader']),
     Paragraph("<b>Mobile</b>", styles['TableHeader'])],
    [Paragraph("Tauri v2 + Rust\nReact + TypeScript", styles['TableCell']),
     Paragraph("Go 1.25\nPostgreSQL 15", styles['TableCell']),
     Paragraph("React 19 + TypeScript\nVite 8 + Tailwind", styles['TableCell']),
     Paragraph("Kotlin + Jetpack Compose\nAndroid SDK 34", styles['TableCell'])],
]
tech_table = Table(tech_data, colWidths=[doc.width/4]*4)
tech_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER),
    ('BACKGROUND', (0, 1), (-1, 1), LIGHT_BG),
    ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
]))
story.append(tech_table)
story.append(PageBreak())

# ─── TABLE OF CONTENTS ────────────────────────────────────────
story.append(Paragraph("Table of Contents", styles['H1']))
story.append(hr())

toc_items = [
    ("1", "Project Overview", [
        "1.1  Mission & Vision",
        "1.2  Core Architecture",
        "1.3  System Flow",
        "1.4  Tech Stack Summary",
    ]),
    ("2", "Desktop Application (Tauri/Rust)", [
        "2.1  Architecture Overview",
        "2.2  Core Modules",
        "2.3  Cryptographic Engine",
        "2.4  Virtual Filesystem (VaultFS)",
        "2.5  WebSocket Client",
        "2.6  UI Components & Screens",
        "2.7  Tauri Commands Reference",
        "2.8  Build Configuration",
    ]),
    ("3", "Backend API (Go/PostgreSQL)", [
        "3.1  Architecture Overview",
        "3.2  API Endpoints Reference",
        "3.3  Database Schema",
        "3.4  WebSocket Hub",
        "3.5  Google Drive Storage",
        "3.6  WebAuthn Verification",
        "3.7  Deployment (Docker)",
    ]),
    ("4", "Web Authentication App (React)", [
        "4.1  Architecture Overview",
        "4.2  Cryptographic Design",
        "4.3  State Machine",
        "4.4  Pages & Components",
        "4.5  Hooks & Services",
        "4.6  IndexedDB Schema",
        "4.7  Build & Deployment",
    ]),
    ("5", "Mobile Authentication App (Kotlin)", [
        "5.1  Architecture Overview",
        "5.2  Hardware-Backed Security",
        "5.3  Key Components",
        "5.4  Biometric Integration",
        "5.5  Build Configuration",
    ]),
    ("6", "Security Design", [
        "6.1  Zero-Knowledge Principles",
        "6.2  Identity System",
        "6.3  Encryption Layers",
        "6.4  Decoy PIN System",
        "6.5  Auto-Lock & Transfer Guard",
        "6.6  Orphan Healing & Reconciliation",
    ]),
    ("7", "API Reference (Complete)", [
        "7.1  Authentication",
        "7.2  Vault Operations",
        "7.3  Device Management",
        "7.4  WebSocket Protocol",
        "7.5  Web Endpoints",
        "7.6  Error Handling",
    ]),
    ("8", "Deployment & Operations", [
        "8.1  Docker Compose Production",
        "8.2  CI/CD Pipelines",
        "8.3  Auto-Update System",
        "8.4  Environment Variables",
        "8.5  Monitoring & Health Checks",
    ]),
    ("9", "Development Guide", [
        "9.1  Prerequisites",
        "9.2  Local Development Setup",
        "9.3  Patch Files Reference",
        "9.4  Code Architecture Patterns",
        "9.5  Testing Strategy",
    ]),
    ("10", "Appendix", [
        "10.1  Cryptographic Constants",
        "10.2  Message Protocol Reference",
        "10.3  File Structure Map",
    ]),
]

for num, title, subs in toc_items:
    story.append(Paragraph(f"<b>{num}.</b>  {title}", styles['TOCEntry1']))
    for sub in subs:
        story.append(Paragraph(sub, styles['TOCEntry2']))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 1: PROJECT OVERVIEW
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("1. Project Overview", styles['H1']))
story.append(hr())

story.append(Paragraph("1.1 Mission & Vision", styles['H2']))
story.append(Paragraph(
    "AHS Vault is a <b>zero-knowledge biometric vault</b> system that provides secure cloud storage "
    "with a revolutionary architecture: the user's smartphone (or web browser) acts as a biometric "
    "remote control to unlock encrypted files on a desktop computer. The fundamental principle is that "
    "<b>the server never sees plaintext data</b> -- all encryption and decryption happens exclusively on "
    "client devices.",
    styles['Body']
))
story.append(Paragraph(
    "The system eliminates the need for traditional passwords by using biometric authentication "
    "(Face ID, Touch ID, fingerprint) as the trust anchor. The smartphone becomes the ultimate key "
    "to the desktop vault, creating a seamless yet highly secure user experience.",
    styles['Body']
))

story.append(Paragraph("1.2 Core Architecture", styles['H2']))
story.append(Paragraph(
    "The system consists of four main components that communicate through a central Go backend:",
    styles['Body']
))

arch_rows = [
    ["Desktop App", "Tauri v2 (Rust + React)", "Vault file management, encryption, virtual filesystem"],
    ["Backend API", "Go 1.25 + PostgreSQL", "Relay, storage, WebSocket routing"],
    ["Web App", "React 19 + TypeScript", "Biometric authentication, QR pairing"],
    ["Mobile App", "Kotlin + Jetpack Compose", "Biometric authentication, QR pairing"],
]
story.append(make_table(
    ["Component", "Tech Stack", "Responsibility"],
    arch_rows,
    [doc.width*0.2, doc.width*0.35, doc.width*0.45]
))
story.append(spacer(10))

story.append(Paragraph("1.3 System Flow", styles['H2']))
story.append(Paragraph(
    "The complete unlock flow operates as follows:",
    styles['Body']
))

flow_steps = [
    "Desktop generates a 24-word BIP-39 mnemonic and derives cryptographic keys",
    "Mobile/Web scans a QR code to cryptographically pair with the desktop",
    "Desktop encrypts files with AES-256-GCM and syncs encrypted blobs to Google Drive",
    "To unlock, desktop sends a push notification through the backend to the mobile device",
    "User authenticates via biometrics (Face ID / Touch ID / fingerprint) on the mobile device",
    "Mobile decrypts the master key and sends it back to the desktop via encrypted channel (X25519 + AES-GCM)",
    "Desktop mounts a virtual filesystem (FUSE on Linux/macOS, WebDAV on Windows) that transparently decrypts files",
]
for i, step in enumerate(flow_steps, 1):
    story.append(Paragraph(f"<b>Step {i}:</b> {step}", styles['BulletCustom']))

story.append(Paragraph("1.4 Tech Stack Summary", styles['H2']))

stack_rows = [
    ["Desktop", "Tauri v2, Rust, React, TypeScript, Vite 7, Tailwind CSS 4"],
    ["Cryptography", "Ed25519, X25519, AES-256-GCM, BIP-39, ECDSA P-256, PBKDF2"],
    ["Backend", "Go 1.25, Chi router, PostgreSQL 15, Gorilla WebSocket, pgx/v5"],
    ["Web App", "React 19, TypeScript 6, Vite 8, Tailwind CSS 4, Dexie.js, @noble/curves"],
    ["Mobile", "Kotlin, Jetpack Compose, Google Tink, CameraX, ML Kit, BiometricPrompt"],
    ["Storage", "Google Drive API (primary), MinIO (alternative)"],
    ["CI/CD", "GitHub Actions, Docker, Tauri Updater"],
]
story.append(make_table(
    ["Layer", "Technologies"],
    stack_rows,
    [doc.width*0.25, doc.width*0.75]
))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 2: DESKTOP APPLICATION
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("2. Desktop Application (Tauri/Rust)", styles['H1']))
story.append(hr())

story.append(Paragraph("2.1 Architecture Overview", styles['H2']))
story.append(Paragraph(
    "The desktop application is built with Tauri v2, combining a Rust backend for performance-critical "
    "operations (cryptography, filesystem management, networking) with a React/TypeScript frontend for "
    "the user interface. The application runs with <b>window decorations disabled</b> and uses a custom "
    "title bar component.",
    styles['Body']
))

story.append(Paragraph("Key capabilities:", styles['BodyBold']))
for item in [
    "Generate BIP-39 mnemonics and derive cryptographic keys",
    "Mount/unmount virtual filesystem (FUSE or WebDAV)",
    "Encrypt/decrypt files with AES-256-GCM (128KB blocks, parallelized)",
    "Sync encrypted blobs to Google Drive",
    "Multi-device pairing and management",
    "Auto-lock on inactivity with transfer guard",
    "Intelligent Shield email scanning",
    "Auto-update via GitHub releases",
]:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {item}", styles['BulletCustom']))

story.append(Paragraph("2.2 Core Modules", styles['H2']))

modules_rows = [
    ["lib.rs", "Main Tauri app entry, all commands, vault mount/unmount, onboarding, pairing, auto-lock watcher, WebDAV server"],
    ["crypto.rs", "AES-256-GCM encrypt/decrypt (128KB blocks), BIP-39 mnemonic derivation, ECIES for mobile, stream upload/download"],
    ["fs.rs", "VaultFS: In-memory filesystem (FUSE), file management, encrypted shadow blobs, priority-queue sync, cloud reconciliation"],
    ["network.rs", "WebSocket client with auto-reconnect, handles unlock_approved, push_relay, connection_established messages"],
    ["shield.rs", "Intelligent Shield: IMAP email scanning for phishing detection"],
    ["oauth.rs", "Google OAuth2 token management and refresh"],
    ["config.rs", "Backend URL configuration"],
    ["drive_mirror.rs", "SHA-256 hash caching for skip-unchanged-files sync optimization"],
]
story.append(make_table(
    ["Module", "Responsibility"],
    modules_rows,
    [doc.width*0.22, doc.width*0.78]
))
story.append(spacer(10))

story.append(Paragraph("2.3 Cryptographic Engine", styles['H2']))
story.append(Paragraph(
    "The cryptographic engine (<font face='Courier' size='9' color='#c7254e'>crypto.rs</font>) handles all "
    "encryption, decryption, and key derivation operations:",
    styles['Body']
))

crypto_rows = [
    ["AES-256-GCM", "File encryption", "128KB blocks, random 12-byte nonce per block, parallelized via rayon"],
    ["BIP-39", "Mnemonic generation", "24-word mnemonic, HD key derivation (Ed25519 + X25519)"],
    ["ECIES", "Mobile communication", "X25519 ECDH + AES-GCM for secure key exchange with mobile"],
    ["Ed25519", "Request signing", "API request authentication (upload, delete, pair)"],
    ["SHA-256", "Content hashing", "Deduplication and skip-unchanged optimization"],
]
story.append(make_table(
    ["Algorithm", "Use Case", "Details"],
    crypto_rows,
    [doc.width*0.2, doc.width*0.25, doc.width*0.55]
))
story.append(spacer(10))

story.append(Paragraph(
    "The encryption process splits files into 128KB blocks. Each block is encrypted independently with "
    "its own random 12-byte nonce, enabling parallel encryption/decryption via the <font face='Courier' size='9'>rayon</font> "
    "thread pool. A single active block per file handle provides block-level caching for performance.",
    styles['Body']
))

story.append(Paragraph("2.4 Virtual Filesystem (VaultFS)", styles['H2']))
story.append(Paragraph(
    "VaultFS provides a transparent decryption layer that makes encrypted cloud storage appear as a "
    "local drive. The implementation differs by platform:",
    styles['Body']
))

fs_rows = [
    ["Linux/macOS", "FUSE", "fuser crate, mounted at ~/SecureVault", "Full POSIX filesystem semantics"],
    ["Windows", "WebDAV", "dav-server + tiny_http on 127.0.0.1:8081", "Mapped as network drive M:\\"],
]
story.append(make_table(
    ["Platform", "Mechanism", "Implementation", "Notes"],
    fs_rows,
    [doc.width*0.15, doc.width*0.12, doc.width*0.4, doc.width*0.33]
))
story.append(spacer(10))

story.append(Paragraph(
    "Files are stored locally as encrypted shadow blobs. The sync worker uses a priority queue to "
    "background-sync changes to Google Drive. Cloud reconciliation handles orphan healing (index repair "
    "on mount) and garbage collection of orphaned blobs.",
    styles['Body']
))

story.append(Paragraph("2.5 WebSocket Client", styles['H2']))
story.append(Paragraph(
    "The WebSocket client (<font face='Courier' size='9' color='#c7254e'>network.rs</font>) maintains a persistent "
    "connection to the backend for real-time communication:",
    styles['Body']
))

ws_features = [
    "Auto-reconnect with exponential backoff",
    "Handles messages: unlock_approved, push_relay, connection_established",
    "Desktop registration with public key and pairing nonce",
    "Push notification relay for multi-device unlock",
]
for f in ws_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(Paragraph("2.6 UI Components & Screens", styles['H2']))

ui_rows = [
    ["App.tsx", "Main controller", "Onboarding flow, lock screen, dashboard routing, auto-update check"],
    ["Dashboard.tsx", "Main dashboard", "Vault explorer, device management, security center, recovery center, settings"],
    ["LockScreen.tsx", "Lock screen", "Unlock via Phone and Offline Master Key options"],
    ["VaultExplorer.tsx", "File browser", "Virtual filesystem file browsing with upload/download/delete"],
    ["DeviceManagement.tsx", "Devices", "Paired mobile device management (add/remove, real-time status)"],
    ["MasterKeyScreen.tsx", "Mnemonic", "24-word mnemonic display and restoration input"],
    ["SecurityCenter.tsx", "Security", "Security settings and threat monitoring"],
    ["RecoveryCenter.tsx", "Recovery", "Recovery options and backup management"],
    ["AutoLockSettings.tsx", "Auto-lock", "Inactivity timeout configuration"],
    ["TitleBar.tsx", "Custom title bar", "Window controls (decorations disabled)"],
    ["RestorationProgress.tsx", "Restoration", "Progress UI for cloud vault restoration"],
]
story.append(make_table(
    ["Component", "Screen", "Description"],
    ui_rows,
    [doc.width*0.25, doc.width*0.2, doc.width*0.55]
))

story.append(PageBreak())

story.append(Paragraph("2.7 Tauri Commands Reference", styles['H2']))

commands_rows = [
    ["generate_desktop_identity", "Creates BIP-39 mnemonic, derives keys, starts WebSocket, returns QR payload"],
    ["mount_vault", "Mount the virtual filesystem (FUSE or WebDAV)"],
    ["lock_vault", "Unmount the virtual filesystem and clear keys from memory"],
    ["unlock_offline", "Unlock using mnemonic directly (no mobile needed)"],
    ["restore_vault", "Full restoration from cloud using mnemonic"],
    ["request_unlock_push", "Sends WAKE_UP_BIOMETRIC to all paired devices"],
    ["share_master_key_with_phone", "Encrypts and sends master key to phone"],
    ["factory_reset", "Wipes all local configuration and data"],
    ["check_onboarding / complete_onboarding", "Onboarding state management"],
    ["add_mobile_device / remove_mobile_device / get_mobile_devices", "Multi-device management"],
    ["save_google_tokens / is_google_connected", "Google Drive OAuth integration"],
    ["upload_to_vault / download_from_vault / delete_from_vault", "File operations"],
    ["sync_now / cleanup_orphaned_blobs", "Sync and maintenance"],
    ["set_auto_lock_timeout / reset_idle_timer", "Inactivity auto-lock"],
    ["export_vault_archive", "Local backup export"],
]
story.append(make_table(
    ["Command", "Description"],
    commands_rows,
    [doc.width*0.4, doc.width*0.6]
))

story.append(Paragraph("2.8 Build Configuration", styles['H2']))
story.append(Paragraph(
    "The desktop app is built with Tauri v2 using Vite as the bundler. Key configuration:",
    styles['Body']
))

build_rows = [
    ["Framework", "Tauri v2"],
    ["Frontend Bundler", "Vite 7"],
    ["CSS Framework", "Tailwind CSS 4"],
    ["Language", "TypeScript 5.8"],
    ["Rust Edition", "2021"],
    ["Target Version", "0.1.20"],
    ["Window Decorations", "Disabled (custom title bar)"],
    ["Auto-Update", "Tauri Updater plugin + GitHub Releases"],
    ["Signing", "TAURI_SIGNING_PRIVATE_KEY"],
]
story.append(make_table(
    ["Setting", "Value"],
    build_rows,
    [doc.width*0.35, doc.width*0.65]
))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 3: BACKEND API
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("3. Backend API (Go/PostgreSQL)", styles['H1']))
story.append(hr())

story.append(Paragraph("3.1 Architecture Overview", styles['H2']))
story.append(Paragraph(
    "The backend is a <b>pure relay</b> -- it never sees plaintext keys or files. Built with Go 1.25, "
    "it uses the Chi router for HTTP, gorilla/websocket for real-time communication, and PostgreSQL 15 "
    "for persistence. Google Drive serves as the primary encrypted blob storage.",
    styles['Body']
))

story.append(Paragraph(
    "The backend's responsibilities are intentionally minimal: store encrypted blobs, route WebSocket "
    "messages by public key identity, manage device registrations, and proxy GitHub releases for "
    "auto-updates.",
    styles['Body']
))

story.append(Paragraph("3.2 API Endpoints Reference", styles['H2']))

endpoints_rows = [
    ["GET", "/health", "HealthCheck", "Health check endpoint"],
    ["GET", "/api/update", "HandleUpdate", "Proxies GitHub releases for Tauri auto-updater"],
    ["POST", "/api/vault/upload", "UploadVault", "Upload encrypted blob (Ed25519 signed)"],
    ["GET", "/api/vault/download/{blob_id}", "DownloadVault", "Download encrypted blob"],
    ["POST", "/api/vault/pair", "PairVault", "Native mobile pairing (signature verified)"],
    ["POST", "/api/vault/push", "RelayPush", "Relay encrypted blob to target device via WS"],
    ["POST", "/api/vault/shield/log", "LogThreat", "Log threat events from Shield"],
    ["POST", "/api/vault/register", "RegisterDevice", "Register/update device info"],
    ["GET", "/api/vault/devices", "GetDevices", "List devices by public key"],
    ["DELETE", "/api/vault/devices", "DeleteDevice", "Remove device (bulk or single)"],
    ["GET", "/api/vault/activity", "GetActivity", "Get activity logs"],
    ["GET", "/api/vault/stats", "GetStats", "Dashboard stats (score, files, storage, threats)"],
    ["GET", "/api/vault/index", "GetRootIndex", "Get root blob index pointer"],
    ["POST", "/api/vault/index", "SetRootIndex", "Set root blob index pointer"],
    ["POST", "/api/vault/delete", "DeleteVault", "Delete encrypted blobs"],
    ["GET", "/api/ws/connect", "WsConnect", "Native WebSocket upgrade"],
    ["POST", "/api/web/pair", "WebPairVault", "Web app pairing"],
    ["POST", "/api/web/push", "WebRelayPush", "Web unlock relay (WebAuthn verified)"],
    ["POST", "/api/web/register-webauthn", "WebRegisterWebAuthn", "Register WebAuthn credential"],
    ["GET", "/api/web/ws/connect", "WebWsConnect", "Web app WebSocket upgrade"],
]
story.append(make_table(
    ["Method", "Path", "Handler", "Description"],
    endpoints_rows,
    [doc.width*0.08, doc.width*0.32, doc.width*0.22, doc.width*0.38]
))

story.append(PageBreak())

story.append(Paragraph("3.3 Database Schema", styles['H2']))

story.append(Paragraph("Devices Table", styles['H3']))
story.append(code_block(
    "CREATE TABLE devices (\n"
    "    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"
    "    public_key      TEXT UNIQUE NOT NULL,\n"
    "    name            TEXT NOT NULL,\n"
    "    os              TEXT NOT NULL,\n"
    "    status          TEXT NOT NULL DEFAULT 'secure',\n"
    "    last_active     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,\n"
    "    last_root_blob_id TEXT\n"
    ");"
))

story.append(Paragraph("Activity Logs Table", styles['H3']))
story.append(code_block(
    "CREATE TABLE activity_logs (\n"
    "    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"
    "    device_public_key   TEXT NOT NULL,\n"
    "    event_type          TEXT NOT NULL,\n"
    "    title               TEXT NOT NULL,\n"
    "    description         TEXT NOT NULL,\n"
    "    risk_level          TEXT NOT NULL DEFAULT 'low',\n"
    "    timestamp           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
    ");"
))

story.append(Paragraph("Blobs Table", styles['H3']))
story.append(code_block(
    "CREATE TABLE blobs (\n"
    "    blob_id             TEXT PRIMARY KEY,\n"
    "    owner_public_key    TEXT NOT NULL,\n"
    "    size_bytes          BIGINT NOT NULL,\n"
    "    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
    ");"
))

story.append(Paragraph("3.4 WebSocket Hub", styles['H2']))
story.append(Paragraph(
    "The WebSocket hub (<font face='Courier' size='9' color='#c7254e'>internal/websocket/hub.go</font>) "
    "manages all real-time connections and message routing:",
    styles['Body']
))

hub_features = [
    "Identity binding: Desktop sends {type: 'desktop_register', public_key, pairing_nonce}",
    "Mobile/Web sends {type: 'mobile_register', public_key}",
    "Messages routed by public key identity",
    "Pairing nonces are single-use and expire after 5 minutes",
    "Server sends: unlock_approved, push_relay, WAKE_UP_BIOMETRIC, connection_established",
]
for f in hub_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(Paragraph("3.5 Google Drive Storage", styles['H2']))
story.append(Paragraph(
    "The Google Drive integration (<font face='Courier' size='9' color='#c7254e'>internal/storage/gdrive.go</font>) "
    "handles encrypted blob persistence:",
    styles['Body']
))

gdrive_features = [
    "Upload encrypted blobs with MIME type application/octet-stream",
    "Download by blob ID with streaming support",
    "Delete with confirmation",
    "Folder management per user (identified by public key)",
    "Storage statistics (total size, file count)",
]
for f in gdrive_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(Paragraph("3.6 WebAuthn Verification", styles['H2']))
story.append(Paragraph(
    "The WebAuthn module (<font face='Courier' size='9' color='#c7254e'>internal/auth/webauthn.go</font>) "
    "verifies WebAuthn assertions from the web app:",
    styles['Body']
))

webauthn_features = [
    "ECDSA P-256 public key verification",
    "SHA-256 challenge hashing",
    "Signature verification using crypto/ecdsa",
    "Credential ID to public key lookup",
]
for f in webauthn_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(Paragraph("3.7 Deployment (Docker)", styles['H2']))
story.append(Paragraph(
    "The backend is containerized with a multi-stage Docker build:",
    styles['Body']
))

story.append(code_block(
    "# Multi-stage build\n"
    "FROM golang:1.25-alpine AS builder\n"
    "WORKDIR /app\n"
    "COPY . .\n"
    "RUN go build -o server ./cmd/api\n"
    "\n"
    "FROM alpine:latest\n"
    "COPY --from=builder /app/server /server\n"
    "EXPOSE 8080\n"
    "CMD [\"/server\"]"
))

docker_rows = [
    ["backend", "Go API server", "8080", "Depends on db"],
    ["db", "PostgreSQL 15 Alpine", "5432", "Volume: postgres_prod_data"],
]
story.append(make_table(
    ["Service", "Image", "Port", "Notes"],
    docker_rows,
    [doc.width*0.15, doc.width*0.3, doc.width*0.15, doc.width*0.4]
))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 4: WEB AUTHENTICATION APP
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("4. Web Authentication App (React)", styles['H1']))
story.append(hr())

story.append(Paragraph("4.1 Architecture Overview", styles['H2']))
story.append(Paragraph(
    "The web authentication app is a React 19 single-page application that serves as one of the two "
    "biometric authentication endpoints (the other being the Android app). It runs entirely in the "
    "browser with local-first data storage via IndexedDB (Dexie.js).",
    styles['Body']
))

web_stack = [
    ["Framework", "React 19 + TypeScript 6"],
    ["Build Tool", "Vite 8"],
    ["Styling", "Tailwind CSS 4"],
    ["Cryptography", "@noble/curves (X25519), @noble/hashes, WebCrypto API"],
    ["WebAuthn", "@simplewebauthn/browser (L3)"],
    ["Storage", "Dexie.js (IndexedDB)"],
    ["Routing", "react-router-dom v7"],
    ["QR Code", "html5-qrcode scanner"],
    ["BIP-39", "@scure/bip39"],
]
story.append(make_table(
    ["Component", "Technology"],
    web_stack,
    [doc.width*0.3, doc.width*0.7]
))

story.append(Paragraph("4.2 Cryptographic Design", styles['H2']))

crypto_web_rows = [
    ["Identity", "ECDSA P-256", "Generated on first visit, stored in IndexedDB"],
    ["Transport", "X25519 DH + AES-256-GCM", "Ephemeral key per unlock session"],
    ["PIN", "PBKDF2-HMAC-SHA-256", "310,000 iterations + 16-byte random salt"],
    ["Biometrics", "WebAuthn L3", "Platform authenticator (Face ID/Touch ID), ES256"],
    ["Decoy PIN", "Separate PBKDF2 hash", "Opens fake vault under duress"],
]
story.append(make_table(
    ["Purpose", "Algorithm", "Details"],
    crypto_web_rows,
    [doc.width*0.18, doc.width*0.32, doc.width*0.5]
))

story.append(Paragraph("4.3 State Machine", styles['H2']))
story.append(Paragraph(
    "The web app follows a strict state machine for onboarding and authentication:",
    styles['Body']
))
story.append(code_block(
    "loading -> onboarding (3-step carousel)\n"
    "onboarding -> main (Unpaired)\n"
    "main (Unpaired) + QR scan -> pairing\n"
    "pairing -> security-setup (PIN -> Decoy PIN -> Biometric)\n"
    "security-setup -> main (Locked)\n"
    "main (Locked) + Biometric/PIN -> main (Unlocked)"
))

story.append(Paragraph("4.4 Pages & Components", styles['H2']))

web_pages = [
    ["Dashboard.tsx", "Main dashboard view", "Security hero card, quick actions, live status grid"],
    ["Settings.tsx", "Settings page", "Biometric enrollment/removal, 24-word recovery, vault config, theme, factory reset"],
    ["Shield.tsx", "Security monitoring", "Threat detection display and security status"],
    ["Activity.tsx", "Activity log", "Device activity and event history"],
    ["BiometricPrompt.tsx", "Biometric overlay", "Prompts for fingerprint/face authentication"],
    ["PinPad.tsx", "PIN entry", "5-digit PIN pad with decoy support"],
    ["Scanner.tsx", "QR scanner", "Camera-based QR code scanner for pairing"],
    ["FloatingNavBar.tsx", "Navigation", "Bottom navigation bar (Vault, Shield, Activity, Settings, Devices)"],
    ["SecurityHeroCard.tsx", "Status card", "Security status display"],
    ["QuickActionButtons.tsx", "Actions", "Quick action buttons"],
    ["LiveStatusGrid.tsx", "Monitoring", "Real-time monitoring grid"],
]
story.append(make_table(
    ["Component", "Screen", "Description"],
    web_pages,
    [doc.width*0.28, doc.width*0.22, doc.width*0.5]
))

story.append(Paragraph("4.5 Hooks & Services", styles['H2']))

hooks_rows = [
    ["useWebAuthn.ts", "WebAuthn registration/authentication via @simplewebauthn/browser (Local-First pattern)"],
    ["useWebSocket.ts", "WebSocket connection to backend with auto-reconnect, handles push_relay messages"],
    ["api.ts", "HTTP API calls: pairDevice, sendUnlockApproval, getVaultStats"],
    ["crypto.ts", "All cryptographic operations: ECDSA P-256, X25519, AES-GCM, PBKDF2, signature conversion"],
    ["db.ts", "Dexie.js database: identity keys, PIN hash/salt, pairing data, biometric credentials, master key"],
]
story.append(make_table(
    ["Module", "Responsibility"],
    hooks_rows,
    [doc.width*0.25, doc.width*0.75]
))

story.append(Paragraph("4.6 IndexedDB Schema (Dexie.js)", styles['H2']))
story.append(code_block(
    "Database: AHSVaultAuth\n"
    "\n"
    "Stores:\n"
    "  - identity: ECDSA P-256 keypair + X25519 keypair\n"
    "  - pairing: desktop public key, backend URL, session data\n"
    "  - config: PIN hash, PIN salt, decoy PIN hash, decoy salt\n"
    "  - biometric: WebAuthn credential ID, public key\n"
    "  - vault: encrypted master key, mnemonic (encrypted)\n"
    "  - settings: theme, auto-lock preferences"
))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 5: MOBILE APP
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("5. Mobile Authentication App (Kotlin)", styles['H1']))
story.append(hr())

story.append(Paragraph("5.1 Architecture Overview", styles['H2']))
story.append(Paragraph(
    "The mobile authentication app is a native Android application built with Kotlin and Jetpack Compose. "
    "It provides hardware-backed biometric authentication and serves as the primary key to the desktop vault.",
    styles['Body']
))

mobile_stack = [
    ["Language", "Kotlin"],
    ["UI Framework", "Jetpack Compose"],
    ["Target SDK", "26-34 (compile SDK 34)"],
    ["Build System", "Gradle with Kotlin DSL"],
    ["Cryptography", "Google Tink (X25519, AES-GCM), Android Keystore (P-256 ECDSA)"],
    ["Biometrics", "androidx.biometric (BiometricPrompt API)"],
    ["Camera", "CameraX 1.3 + ML Kit Barcode Scanning"],
    ["Networking", "OkHttp 4.12, Gson"],
    ["Version", "1.0 (versionCode 1)"],
]
story.append(make_table(
    ["Component", "Technology"],
    mobile_stack,
    [doc.width*0.3, doc.width*0.7]
))

story.append(Paragraph("5.2 Hardware-Backed Security", styles['H2']))
story.append(Paragraph(
    "The Android app leverages hardware security features for maximum protection:",
    styles['Body']
))

hw_features = [
    "<b>TEE/Strongbox:</b> P-256 ECDSA keys generated in Trusted Execution Environment",
    "<b>Invalidated by Biometric Enrollment:</b> Keys auto-deleted if new fingerprint added",
    "<b>Encrypted SharedPreferences:</b> Sensitive data stored with hardware-backed encryption",
    "<b>Android Keystore:</b> Private keys never leave secure hardware",
]
for f in hw_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(Paragraph("5.3 Key Components", styles['H2']))

mobile_components = [
    ["MainActivity.kt", "Central coordinator for all security operations"],
    ["CryptoManager", "Hardware-backed key generation (P-256 in TEE/Strongbox), X25519 via Tink, AES-GCM"],
    ["SecureStorageManager", "Encrypted SharedPreferences/DataStore for key persistence"],
    ["WebSocketService.kt", "Foreground service for persistent WebSocket connection"],
    ["BiometricPrompt", "Biometric authentication integration"],
    ["CameraX + ML Kit", "QR code scanning during pairing"],
]
story.append(make_table(
    ["Component", "Responsibility"],
    mobile_components,
    [doc.width*0.28, doc.width*0.72]
))

story.append(Paragraph("5.4 Biometric Integration", styles['H2']))
story.append(Paragraph(
    "The mobile app uses Android's BiometricPrompt API for secure biometric authentication. "
    "The integration includes:",
    styles['Body']
))

bio_features = [
    "Fingerprint, face, and iris authentication support",
    "Hardware-backed key binding (keys unusable without biometric)",
    "Automatic key invalidation on biometric enrollment changes",
    "Fallback to device credential (PIN/pattern) when available",
]
for f in bio_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 6: SECURITY DESIGN
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("6. Security Design", styles['H1']))
story.append(hr())

story.append(Paragraph("6.1 Zero-Knowledge Principles", styles['H2']))
story.append(Paragraph(
    "AHS Vault implements true zero-knowledge architecture with these guarantees:",
    styles['Body']
))

zk_principles = [
    "<b>No plaintext on server:</b> All encryption/decryption happens on client devices only",
    "<b>No server-side keys:</b> Cryptographic keys are derived from BIP-39 mnemonics on client devices",
    "<b>Encrypted blobs:</b> Server stores only opaque encrypted data, cannot read content",
    "<b>No password transmission:</b> Biometric authentication replaces traditional passwords",
    "<b>Client-side key derivation:</b> Master keys never leave the device",
]
for p in zk_principles:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {p}", styles['BulletCustom']))

story.append(Paragraph("6.2 Identity System", styles['H2']))

identity_rows = [
    ["Desktop", "Ed25519 signing key + X25519 encryption secret", "Derived from BIP-39 mnemonic"],
    ["Mobile/Web", "ECDSA P-256 identity key + X25519 transport key", "Hardware-backed where possible"],
    ["Pairing", "QR code exchange of public keys + backend URL + nonce", "One-time pairing nonce, 5min expiry"],
]
story.append(make_table(
    ["Component", "Identity", "Notes"],
    identity_rows,
    [doc.width*0.18, doc.width*0.45, doc.width*0.37]
))

story.append(Paragraph("6.3 Encryption Layers", styles['H2']))
story.append(Paragraph(
    "The system employs multiple encryption layers for defense in depth:",
    styles['Body']
))

layers = [
    ["Layer 1", "File Encryption", "AES-256-GCM", "128KB blocks, random nonce per block"],
    ["Layer 2", "Transport Encryption", "X25519 ECDH + AES-GCM", "Ephemeral session keys for key exchange"],
    ["Layer 3", "Identity Signing", "Ed25519 / ECDSA P-256", "API request authentication"],
    ["Layer 4", "PIN Protection", "PBKDF2-HMAC-SHA-256", "310K iterations, 16-byte salt"],
    ["Layer 5", "Hardware Binding", "Android Keystore / WebAuthn", "Keys bound to biometric"],
]
story.append(make_table(
    ["Layer", "Purpose", "Algorithm", "Details"],
    layers,
    [doc.width*0.1, doc.width*0.2, doc.width*0.3, doc.width*0.4]
))

story.append(Paragraph("6.4 Decoy PIN System", styles['H2']))
story.append(Paragraph(
    "AHS Vault includes a plausible deniability feature via decoy PINs. When a user is under duress, "
    "they can enter a decoy PIN that opens a fake vault with harmless content. The decoy PIN is stored "
    "as a separate PBKDF2 hash, making it computationally indistinguishable from the real PIN.",
    styles['Body']
))

decoy_features = [
    "Separate PBKDF2 hash for decoy PIN",
    "Decoy vault contains innocuous files",
    "No indication to attacker which PIN is real",
    "Configurable during security setup",
]
for f in decoy_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(Paragraph("6.5 Auto-Lock & Transfer Guard", styles['H2']))
story.append(Paragraph(
    "The auto-lock system clears all cryptographic keys from RAM after a configurable inactivity "
    "period (default 300 seconds). The Transfer Guard prevents auto-lock during active file transfers "
    "using an RAII pattern:",
    styles['Body']
))

autolock_features = [
    "Inactivity timer resets on user interaction",
    "Configurable timeout (default 300 seconds)",
    "Transfer Guard: RAII lock prevents auto-lock during transfers",
    "Immediate lock on manual trigger",
    "Memory-only viewing: files decrypted only in RAM",
]
for f in autolock_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(Paragraph("6.6 Orphan Healing & Reconciliation", styles['H2']))
story.append(Paragraph(
    "The system includes automatic repair mechanisms for maintaining data integrity:",
    styles['Body']
))

heal_features = [
    "<b>Orphan healing:</b> Index repair on mount for corrupted or partial states",
    "<b>Cloud reconciliation:</b> Background purging of garbage/orphaned blobs",
    "<b>SHA-256 caching:</b> Skip unchanged files during sync for efficiency",
    "<b>Priority queue sync:</b> Background worker with configurable priority",
]
for f in heal_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 7: API REFERENCE
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("7. API Reference (Complete)", styles['H1']))
story.append(hr())

story.append(Paragraph("7.1 Authentication", styles['H2']))
story.append(Paragraph(
    "All API requests from the desktop are signed with Ed25519. The signature covers the request body "
    "and is included in the X-Signature header. The backend verifies the signature against the "
    "registered public key.",
    styles['Body']
))

story.append(Paragraph("7.2 Vault Operations", styles['H2']))

story.append(Paragraph("<b>Upload Encrypted Blob</b>", styles['BodyBold']))
story.append(code_block(
    "POST /api/vault/upload\n"
    "Headers: X-Public-Key, X-Signature, Content-Type: application/octet-stream\n"
    "Body: <encrypted binary data>\n"
    "\n"
    "Response: { \"blob_id\": \"...\", \"size\": 12345 }"
))

story.append(Paragraph("<b>Download Encrypted Blob</b>", styles['BodyBold']))
story.append(code_block(
    "GET /api/vault/download/{blob_id}\n"
    "Headers: X-Public-Key, X-Signature\n"
    "\n"
    "Response: <encrypted binary data>"
))

story.append(Paragraph("<b>Delete Encrypted Blobs</b>", styles['BodyBold']))
story.append(code_block(
    "POST /api/vault/delete\n"
    "Headers: X-Public-Key, X-Signature\n"
    "Body: { \"blob_ids\": [\"id1\", \"id2\"] }"
))

story.append(Paragraph("7.3 Device Management", styles['H2']))

story.append(Paragraph("<b>Register Device</b>", styles['BodyBold']))
story.append(code_block(
    "POST /api/vault/register\n"
    "Body: { \"public_key\": \"...\", \"name\": \"...\", \"os\": \"...\" }"
))

story.append(Paragraph("<b>List Devices</b>", styles['BodyBold']))
story.append(code_block(
    "GET /api/vault/devices?public_key=...\n"
    "\n"
    "Response: [{ \"id\": \"...\", \"name\": \"...\", \"status\": \"secure\", ... }]"
))

story.append(Paragraph("<b>Delete Device</b>", styles['BodyBold']))
story.append(code_block(
    "DELETE /api/vault/devices\n"
    "Body: { \"public_key\": \"...\", \"device_ids\": [\"...\"] }"
))

story.append(Paragraph("7.4 WebSocket Protocol", styles['H2']))
story.append(Paragraph(
    "WebSocket connections use JSON messages. The protocol supports two registration types:",
    styles['Body']
))

story.append(code_block(
    "// Desktop Registration\n"
    "{\n"
    "  \"type\": \"desktop_register\",\n"
    "  \"public_key\": \"ed25519-public-key-hex\",\n"
    "  \"pairing_nonce\": \"random-nonce\"\n"
    "}\n"
    "\n"
    "// Mobile/Web Registration\n"
    "{\n"
    "  \"type\": \"mobile_register\",\n"
    "  \"public_key\": \"ecdsa-public-key-hex\"\n"
    "}\n"
    "\n"
    "// Server Messages\n"
    "{ \"type\": \"unlock_approved\", ... }\n"
    "{ \"type\": \"push_relay\", \"data\": \"<encrypted-blob>\" }\n"
    "{ \"type\": \"WAKE_UP_BIOMETRIC\" }\n"
    "{ \"type\": \"connection_established\" }"
))

story.append(Paragraph("7.5 Web Endpoints", styles['H2']))

web_endpoints = [
    ["POST", "/api/web/pair", "Web app pairing with desktop"],
    ["POST", "/api/web/push", "Web unlock relay (WebAuthn verified)"],
    ["POST", "/api/web/register-webauthn", "Register WebAuthn credential"],
    ["GET", "/api/web/ws/connect", "Web app WebSocket upgrade"],
]
story.append(make_table(
    ["Method", "Path", "Description"],
    web_endpoints,
    [doc.width*0.1, doc.width*0.4, doc.width*0.5]
))

story.append(Paragraph("7.6 Error Handling", styles['H2']))
story.append(Paragraph(
    "All API errors return JSON with a consistent format:",
    styles['Body']
))
story.append(code_block(
    "{\n"
    "  \"error\": \"<error message>\",\n"
    "  \"code\": \"<error_code>\"\n"
    "}\n"
    "\n"
    "Common error codes:\n"
    "  400 - Bad Request (invalid signature, missing fields)\n"
    "  401 - Unauthorized (invalid/missing public key)\n"
    "  404 - Not Found (blob_id does not exist)\n"
    "  500 - Internal Server Error"
))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 8: DEPLOYMENT & OPERATIONS
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("8. Deployment & Operations", styles['H1']))
story.append(hr())

story.append(Paragraph("8.1 Docker Compose Production", styles['H2']))
story.append(code_block(
    "version: '3.8'\n"
    "\n"
    "services:\n"
    "  backend:\n"
    "    build: ./vault-backend-go\n"
    "    ports:\n"
    "      - \"8080:8080\"\n"
    "    depends_on:\n"
    "      - db\n"
    "    environment:\n"
    "      - DATABASE_URL=postgres://user:pass@db:5432/vault\n"
    "      - GOOGLE_DRIVE_CREDENTIALS=/secrets/gdrive.json\n"
    "\n"
    "  db:\n"
    "    image: postgres:15-alpine\n"
    "    volumes:\n"
    "      - postgres_prod_data:/var/lib/postgresql/data\n"
    "    environment:\n"
    "      - POSTGRES_DB=vault\n"
    "      - POSTGRES_USER=user\n"
    "      - POSTGRES_PASSWORD=pass\n"
    "\n"
    "volumes:\n"
    "  postgres_prod_data:"
))

story.append(Paragraph("8.2 CI/CD Pipelines", styles['H2']))

story.append(Paragraph("<b>Windows Desktop Build</b> (build-windows.yml)", styles['BodyBold']))
ci_windows = [
    "Trigger: Push to main or tag matching v*",
    "Environment: windows-latest",
    "Setup: Node.js 22, Rust stable",
    "Build: npm install && npm run tauri build",
    "Sign: TAURI_SIGNING_PRIVATE_KEY",
    "Artifacts: .exe, .msi, .zip, .sig",
    "Release: GitHub Release on tag push",
]
for f in ci_windows:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(Paragraph("<b>Mobile Build</b> (build-mobile.yml)", styles['BodyBold']))
ci_mobile = [
    "Trigger: Push to main",
    "Environment: ubuntu-latest",
    "Setup: JDK 17 (Temurin)",
    "Build: ./gradlew assembleDebug",
    "Artifact: app-debug.apk",
]
for f in ci_mobile:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(Paragraph("8.3 Auto-Update System", styles['H2']))
story.append(Paragraph(
    "The auto-update system works as follows:",
    styles['Body']
))

update_steps = [
    "Desktop app queries backend /api/update on startup",
    "Backend proxies GitHub Releases API",
    "Extracts .nsis.zip and .sig URLs from latest release",
    "Tauri updater plugin downloads and verifies signature",
    "Silent install via NSIS installer",
    "App relaunches automatically via tauri-plugin-process",
]
for i, step in enumerate(update_steps, 1):
    story.append(Paragraph(f"<b>{i}.</b> {step}", styles['BulletCustom']))

story.append(Paragraph("8.4 Environment Variables", styles['H2']))

env_rows = [
    ["DATABASE_URL", "PostgreSQL connection string", "postgres://user:pass@localhost:5432/vault"],
    ["GOOGLE_DRIVE_CREDENTIALS", "Path to Google Drive service account JSON", "/secrets/gdrive.json"],
    ["PORT", "HTTP server port", "8080"],
    ["TAURI_SIGNING_PRIVATE_KEY", "Tauri auto-update signing key", "Required for desktop builds"],
    ["TAURI_SIGNING_PRIVATE_KEY_PASSWORD", "Password for signing key", "Optional"],
]
story.append(make_table(
    ["Variable", "Description", "Default/Example"],
    env_rows,
    [doc.width*0.3, doc.width*0.4, doc.width*0.3]
))

story.append(Paragraph("8.5 Monitoring & Health Checks", styles['H2']))
story.append(Paragraph(
    "The backend exposes a health check endpoint at <font face='Courier' size='9'>GET /health</font> "
    "that returns the service status. Docker Compose can use this for container health checks.",
    styles['Body']
))

health_features = [
    "GET /health returns { \"status\": \"ok\" }",
    "PostgreSQL connection pool health via pgx",
    "WebSocket hub connection count",
    "Google Drive API quota monitoring",
]
for f in health_features:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {f}", styles['BulletCustom']))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 9: DEVELOPMENT GUIDE
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("9. Development Guide", styles['H1']))
story.append(hr())

story.append(Paragraph("9.1 Prerequisites", styles['H2']))

prereq_rows = [
    ["Desktop", "Node.js 22+, Rust stable, Tauri CLI"],
    ["Backend", "Go 1.25+, PostgreSQL 15+, Google Drive credentials"],
    ["Web App", "Node.js 22+, npm"],
    ["Mobile", "JDK 17 (Temurin), Android SDK 34, Gradle"],
    ["Docker", "Docker Engine 20+, Docker Compose v2"],
]
story.append(make_table(
    ["Component", "Requirements"],
    prereq_rows,
    [doc.width*0.25, doc.width*0.75]
))

story.append(Paragraph("9.2 Local Development Setup", styles['H2']))

story.append(Paragraph("<b>Backend</b>", styles['BodyBold']))
story.append(code_block(
    "cd vault-backend-go\n"
    "go mod download\n"
    "go run ./cmd/api"
))

story.append(Paragraph("<b>Desktop</b>", styles['BodyBold']))
story.append(code_block(
    "cd vault-desktop-tauri\n"
    "npm install\n"
    "npm run tauri dev"
))

story.append(Paragraph("<b>Web App</b>", styles['BodyBold']))
story.append(code_block(
    "cd vault-web-auth\n"
    "npm install\n"
    "npm run dev"
))

story.append(Paragraph("<b>Mobile</b>", styles['BodyBold']))
story.append(code_block(
    "cd vault-mobile-auth\n"
    "./gradlew assembleDebug"
))

story.append(Paragraph("9.3 Patch Files Reference", styles['H2']))
story.append(Paragraph(
    "The project includes several patch files used during development to apply incremental changes:",
    styles['Body']
))

patch_rows = [
    ["patch_config.py", "Adds MobileDevice struct and mobile_devices field to OnboardingConfig"],
    ["patch_lib.py", "Updates push logic for multi-device, adds device management Tauri commands"],
    ["patch_app.py", "Fixes onboarding step logic after pairing"],
    ["patch_device.py", "Updates DeviceManagement.tsx for local device management"],
    ["patch_ts.py", "TypeScript fixes (imports, types, unused parameters)"],
    ["apply_process_plugin.js", "Adds tauri-plugin-process for app relaunch capability"],
]
story.append(make_table(
    ["File", "Purpose"],
    patch_rows,
    [doc.width*0.28, doc.width*0.72]
))

story.append(Paragraph("9.4 Code Architecture Patterns", styles['H2']))

patterns = [
    ["Zero-Knowledge Relay", "Backend never sees plaintext; all crypto on clients"],
    ["Virtual Filesystem Abstraction", "FUSE (Linux/macOS) and WebDAV (Windows) behind common interface"],
    ["Priority Queue Sync", "Background sync with configurable priority and transfer guard"],
    ["RAII Transfer Guard", "Prevents auto-lock during active file transfers"],
    ["Hardware-Backed Identity", "Keys bound to biometric hardware (Android Keystore / WebAuthn)"],
    ["Dual Authentication Paths", "Biometric primary, PIN fallback, offline mnemonic recovery"],
    ["Plausible Deniability", "Decoy PIN system for duress scenarios"],
    ["Orphan Healing", "Automatic index repair on mount for corrupted states"],
]
story.append(make_table(
    ["Pattern", "Description"],
    patterns,
    [doc.width*0.3, doc.width*0.7]
))

story.append(Paragraph("9.5 Testing Strategy", styles['H2']))
story.append(Paragraph(
    "The testing strategy covers multiple levels:",
    styles['Body']
))

testing = [
    "<b>Unit Tests:</b> Cryptographic operations, key derivation, encryption/decryption",
    "<b>Integration Tests:</b> API endpoints, WebSocket protocol, database operations",
    "<b>E2E Tests:</b> Full pairing flow, unlock flow, file operations",
    "<b>Security Tests:</b> Signature verification, key isolation, memory clearing",
    "<b>Platform Tests:</b> FUSE/WebDAV mounting, auto-update, CI/CD builds",
]
for t in testing:
    story.append(Paragraph(f"<bullet>&bull;</bullet> {t}", styles['BulletCustom']))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════
# SECTION 10: APPENDIX
# ═══════════════════════════════════════════════════════════════
story.append(Paragraph("10. Appendix", styles['H1']))
story.append(hr())

story.append(Paragraph("10.1 Cryptographic Constants", styles['H2']))

crypto_const_rows = [
    ["AES Block Size", "128KB (131,072 bytes)"],
    ["AES Nonce Size", "12 bytes (96 bits)"],
    ["AES Key Size", "32 bytes (256 bits)"],
    ["PBKDF2 Iterations", "310,000"],
    ["PBKDF2 Salt Size", "16 bytes"],
    ["BIP-39 Wordlist", "2048 words (English)"],
    ["Mnemonic Length", "24 words"],
    ["Ed25519 Key Size", "32 bytes"],
    ["X25519 Key Size", "32 bytes"],
    ["ECDSA P-256 Key Size", "32 bytes (private), 64 bytes (public)"],
    ["SHA-256 Digest", "32 bytes"],
    ["Pairing Nonce Expiry", "300 seconds (5 minutes)"],
    ["Default Auto-Lock", "300 seconds (5 minutes)"],
]
story.append(make_table(
    ["Constant", "Value"],
    crypto_const_rows,
    [doc.width*0.4, doc.width*0.6]
))

story.append(Paragraph("10.2 Message Protocol Reference", styles['H2']))
story.append(Paragraph(
    "All WebSocket messages use JSON format with a 'type' field for routing:",
    styles['Body']
))

msg_rows = [
    ["desktop_register", "Desktop -> Server", "Register desktop identity with public key and pairing nonce"],
    ["mobile_register", "Mobile -> Server", "Register mobile identity with public key"],
    ["unlock_approved", "Server -> Desktop", "Mobile approved unlock, contains encrypted master key"],
    ["push_relay", "Server -> Desktop", "Relay encrypted blob from mobile"],
    ["WAKE_UP_BIOMETRIC", "Server -> Mobile", "Wake up mobile for biometric authentication"],
    ["connection_established", "Server -> Both", "Confirm WebSocket connection is active"],
    ["pairing_request", "Mobile -> Server -> Desktop", "Initiate pairing with public key exchange"],
    ["pairing_complete", "Server -> Both", "Pairing handshake completed"],
]
story.append(make_table(
    ["Message Type", "Direction", "Description"],
    msg_rows,
    [doc.width*0.25, doc.width*0.25, doc.width*0.5]
))

story.append(Paragraph("10.3 File Structure Map", styles['H2']))
story.append(code_block(
    "ahs-app/\n"
    "├── vault-desktop-tauri/          # Desktop app (Tauri v2)\n"
    "│   ├── src-tauri/\n"
    "│   │   ├── src/\n"
    "│   │   │   ├── lib.rs           # Main Tauri commands\n"
    "│   │   │   ├── main.rs          # Entry point\n"
    "│   │   │   ├── crypto.rs        # AES-256-GCM, BIP-39, ECIES\n"
    "│   │   │   ├── fs.rs            # VaultFS (FUSE/WebDAV)\n"
    "│   │   │   ├── network.rs       # WebSocket client\n"
    "│   │   │   ├── shield.rs        # Email phishing scanner\n"
    "│   │   │   ├── oauth.rs         # Google OAuth2\n"
    "│   │   │   ├── config.rs        # Configuration\n"
    "│   │   │   └── drive_mirror.rs  # SHA-256 hash cache\n"
    "│   │   ├── Cargo.toml\n"
    "│   │   └── tauri.conf.json\n"
    "│   ├── src/\n"
    "│   │   ├── App.tsx              # Main React app\n"
    "│   │   ├── screens/\n"
    "│   │   │   ├── Dashboard.tsx\n"
    "│   │   │   └── LockScreen.tsx\n"
    "│   │   └── components/\n"
    "│   │       ├── VaultExplorer.tsx\n"
    "│   │       ├── DeviceManagement.tsx\n"
    "│   │       ├── MasterKeyScreen.tsx\n"
    "│   │       ├── SecurityCenter.tsx\n"
    "│   │       ├── RecoveryCenter.tsx\n"
    "│   │       ├── AutoLockSettings.tsx\n"
    "│   │       ├── TitleBar.tsx\n"
    "│   │       └── RestorationProgress.tsx\n"
    "│   └── package.json\n"
    "│\n"
    "├── vault-backend-go/             # Backend API (Go)\n"
    "│   ├── cmd/api/main.go           # Entry point\n"
    "│   ├── internal/\n"
    "│   │   ├── api/\n"
    "│   │   │   ├── router.go         # Route definitions\n"
    "│   │   │   ├── handlers.go       # API handlers\n"
    "│   │   │   └── web_handlers.go   # Web-specific handlers\n"
    "│   │   ├── db/\n"
    "│   │   │   ├── db.go             # PostgreSQL layer\n"
    "│   │   │   └── json_db.go        # JSON fallback\n"
    "│   │   ├── auth/\n"
    "│   │   │   └── webauthn.go       # WebAuthn verification\n"
    "│   │   ├── websocket/\n"
    "│   │   │   └── hub.go            # WebSocket hub\n"
    "│   │   └── storage/\n"
    "│   │       ├── gdrive.go         # Google Drive storage\n"
    "│   │       └── minio.go          # MinIO storage\n"
    "│   ├── Dockerfile\n"
    "│   └── go.mod\n"
    "│\n"
    "├── vault-web-auth/               # Web auth app (React)\n"
    "│   ├── src/\n"
    "│   │   ├── App.tsx               # Main app controller\n"
    "│   │   ├── main.tsx              # React root\n"
    "│   │   ├── lib/\n"
    "│   │   │   ├── crypto.ts         # Cryptographic operations\n"
    "│   │   │   └── db.ts             # Dexie.js IndexedDB\n"
    "│   │   ├── hooks/\n"
    "│   │   │   ├── useWebAuthn.ts    # WebAuthn hook\n"
    "│   │   │   └── useWebSocket.ts   # WebSocket hook\n"
    "│   │   ├── services/\n"
    "│   │   │   └── api.ts            # HTTP API calls\n"
    "│   │   ├── components/\n"
    "│   │   │   ├── BiometricPrompt.tsx\n"
    "│   │   │   ├── PinPad.tsx\n"
    "│   │   │   ├── Scanner.tsx\n"
    "│   │   │   └── FloatingNavBar.tsx\n"
    "│   │   └── screens/\n"
    "│   │       ├── Dashboard.tsx\n"
    "│   │       ├── Settings.tsx\n"
    "│   │       ├── Shield.tsx\n"
    "│   │       └── Activity.tsx\n"
    "│   └── package.json\n"
    "│\n"
    "├── vault-mobile-auth/            # Mobile auth app (Kotlin)\n"
    "│   ├── app/\n"
    "│   │   ├── build.gradle.kts\n"
    "│   │   └── src/main/\n"
    "│   │       ├── AndroidManifest.xml\n"
    "│   │       └── java/com/vault/auth/\n"
    "│   │           ├── MainActivity.kt\n"
    "│   │           ├── CryptoManager.kt\n"
    "│   │           ├── SecureStorageManager.kt\n"
    "│   │           └── WebSocketService.kt\n"
    "│   └── build.gradle.kts\n"
    "│\n"
    "├── .github/workflows/\n"
    "│   ├── build-windows.yml         # Desktop CI/CD\n"
    "│   └── build-mobile.yml          # Mobile CI/CD\n"
    "│\n"
    "├── docker-compose.prod.yml       # Production Docker\n"
    "├── README.md\n"
    "├── PROJECT.md\n"
    "└── docs/\n"
    "    └── AHS_Vault_Complete_Documentation.pdf"
))

# ─── FINAL PAGE ────────────────────────────────────────────────
story.append(PageBreak())
story.append(Spacer(1, 100))
story.append(Paragraph("End of Document", styles['CoverTitle']))
story.append(Spacer(1, 20))
story.append(HRFlowable(width="30%", thickness=2, color=HIGHLIGHT, spaceAfter=20, spaceBefore=20))
story.append(Paragraph(
    f"AHS Vault Complete Project Documentation<br/>"
    f"Version 0.1.20 | Generated {datetime.now().strftime('%B %d, %Y')}<br/>"
    f"Confidential - Internal Use Only",
    styles['CoverMeta']
))

# ═══════════════════════════════════════════════════════════════
# BUILD PDF
# ═══════════════════════════════════════════════════════════════
print("Generating AHS Vault Complete Documentation PDF...")
doc.build(story, onFirstPage=first_page, onLaterPages=add_page_number)
print(f"PDF generated: {OUTPUT_PATH}")
print(f"File size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")
