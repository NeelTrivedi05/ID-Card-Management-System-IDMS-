# ID Card Management System (IDMS) 🪪

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/UI-Tkinter-34D399?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)

A professional, high-performance desktop application designed for educational institutions to manage, design, and issue Student ID Cards with precision and ease.

> **Commissioned for:** Shri Bhagubhai Mafatlal Polytechnic (SBMP)  
> **Department:** Computer Engineering

---

## 🌟 Key Features

### 🎨 Advanced ID Generation
- **Template System:** Fully customizable ID card layouts (JSON-driven).
- **Pro Image Processing:** Real-time photo cropping, face detection (OpenCV), and resizing (Pillow).
- **Smart Validation:** Automatic expiry date calculation and validity color-coding.
- **QR Code Branding:** Seamless integration of QR codes for digital verification.

### 📊 Comprehensive Dashboard
- **Live Analytics:** Visual data insights using Matplotlib (Student demographics, validity stats).
- **Data Mastery:** Advanced searching, column sorting, and multi-field filtering.
- **Bulk Operations:** Excel/CSV Import/Export capabilities for large-scale data handling.

### 🛡️ Enterprise-Grade Security
- **Role-Based Access (RBAC):** Admin and Staff levels with granular permissions.
- **Audit Logging:** Every critical action (Login, Delete, Modification) is recorded in a tamper-proof log.
- **Secure Authentication:** Password masking and eye-toggle features.

### 💎 Premium Experience
- **Adaptive UI:** State-of-the-art Dark and Light mode themes with a glassmorphic aesthetic.
- **Multi-language Support:** Localized interface (English/Hindi/Gujarati) for inclusive usage.
- **Offline Reliability:** Built-in automated database backup system.

---

## 🛠️ Tech Stack

- **Core:** Python 3.10+
- **GUI:** Tkinter (Custom themed with modern CSS-like styling)
- **Image Engine:** Pillow (PIL), OpenCV
- **Database:** SQLite3
- **Visualization:** Matplotlib
- **Automation:** Faker (Demo data), Openpyxl (Excel), QRcode

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher installed.
- Pip package manager.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Username/ID-Card-Management-System-IDMS-.git
   cd ID-Card-Management-System-IDMS-
   ```

2. **Set up Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or source venv/bin/activate # On Unix
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Application:**
   ```bash
   python main.py
   ```

---

## 👤 Credentials (Default)

| Role      | Username| Password   |
| :---      | :---    | :---       |
| **Admin** | `admin` | `admin123` |

---

## 📁 Project Structure

- `main.py`: Entry point and authentication logic.
- `ui_dashboard.py`: Core management interface and analytics.
- `ui_card.py`: ID card generation and preview engine.
- `database.py`: SQL abstraction and audit logging.
- `theme.py`: Design system and color tokens.
- `i18n.py`: Localization and language mapping.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

Developed with ❤️ for **SBMP Computer Engineering Department**.
