"""
i18n.py — Minimal internationalization for IDMS.
Supports English (en) and Hindi (hi).
Call i18n.set_lang("hi") to switch, then i18n.t("key") to translate.
"""

STRINGS = {
    "en": {
        # Top bar
        "app_title":    "🪪  ID Card Management System",
        "logout":       "Logout",
        "audit_log":    "📋 Audit Log",
        "toggle_theme": "🌙 Dark Mode",
        "toggle_theme_light": "☀ Light Mode",
        "backup":       "💾 Backup DB",
        "language":     "Language:",
        # Tabs
        "tab_students": "  Students  ",
        "tab_staff":    "  Staff  ",
        "tab_analytics":"  Analytics  ",
        # Toolbar
        "search":       "Search:",
        "dept":         "Dept:",
        "sort":         "Sort:",
        "asc":          "▲ ASC",
        "desc":         "▼ DESC",
        "add":          "+ Add",
        "edit":         "✏ Edit",
        "delete":       "🗑 Delete",
        "view_card":    "👁 View Card",
        "export_csv":   "⬆ Export CSV",
        "import_csv":   "⬇ Import CSV",
        "refresh":      "↻ Refresh",
        # Messages
        "no_selection": "Please select a record first.",
        "confirm_del":  "Are you sure you want to delete:\n\n{name}\n\nThis cannot be undone.",
        "deleted":      "Deleted",
        "error":        "Error",
        "records_found":"{n} record{s} found",
        "logout_confirm":"Are you sure you want to logout?",
        # Expiry
        "expiry_title": "⚠ ID Cards Expiring Soon",
        "expiry_body":  "{n} ID card(s) are due for renewal within 30 days:\n\n{items}\n\nPlease arrange renewals at your earliest convenience.",
        # Analytics
        "analytics_title": "📊  Analytics & Reports",
        "refresh_charts":  "↻ Refresh Charts",
        "no_data":         "No data to display",
        # Backup
        "backup_success":  "Backup saved to:\n{path}",
        "backup_fail":     "Backup failed:\n{err}",
        "backup_title":    "Database Backup Successful",
        # Audit
        "audit_title":     "📋  Audit Log  (last 200 actions)",
        "audit_footer":    "{n} log entr{y} shown",
    },

    "hi": {
        # Top bar
        "app_title":    "🪪  आई.डी. कार्ड प्रबंधन प्रणाली",
        "logout":       "लॉगआउट",
        "audit_log":    "📋 लेखापरीक्षा लॉग",
        "toggle_theme": "🌙 डार्क मोड",
        "toggle_theme_light": "☀ लाइट मोड",
        "backup":       "💾 बैकअप",
        "language":     "भाषा:",
        # Tabs
        "tab_students": "  छात्र  ",
        "tab_staff":    "  स्टाफ  ",
        "tab_analytics":"  विश्लेषण  ",
        # Toolbar
        "search":       "खोजें:",
        "dept":         "विभाग:",
        "sort":         "क्रम:",
        "asc":          "▲ आरोही",
        "desc":         "▼ अवरोही",
        "add":          "+ जोड़ें",
        "edit":         "✏ संपादित",
        "delete":       "🗑 हटाएं",
        "view_card":    "👁 कार्ड देखें",
        "export_csv":   "⬆ CSV निर्यात",
        "import_csv":   "⬇ CSV आयात",
        "refresh":      "↻ रीफ्रेश",
        # Messages
        "no_selection": "कृपया पहले एक रिकॉर्ड चुनें।",
        "confirm_del":  "क्या आप वाकई हटाना चाहते हैं:\n\n{name}\n\nयह पूर्ववत नहीं किया जा सकता।",
        "deleted":      "हटाया गया",
        "error":        "त्रुटि",
        "records_found":"{n} रिकॉर्ड मिले",
        "logout_confirm":"क्या आप वाकई लॉगआउट करना चाहते हैं?",
        # Expiry
        "expiry_title": "⚠ समाप्त होने वाले आई.डी. कार्ड",
        "expiry_body":  "{n} आई.डी. कार्ड 30 दिनों में नवीनीकरण के लिए हैं:\n\n{items}",
        # Analytics
        "analytics_title": "📊  विश्लेषण और रिपोर्ट",
        "refresh_charts":  "↻ चार्ट ताज़ा करें",
        "no_data":         "दिखाने के लिए कोई डेटा नहीं",
        # Backup
        "backup_success":  "बैकअप यहाँ सहेजा:\n{path}",
        "backup_fail":     "बैकअप विफल:\n{err}",
        "backup_title":    "डेटाबेस बैकअप सफल",
        # Audit
        "audit_title":     "📋  लेखापरीक्षा लॉग  (अंतिम 200)",
        "audit_footer":    "{n} प्रविष्टियाँ दिखाई",
    },
}

_lang = "en"


def set_lang(code: str):
    global _lang
    if code in STRINGS:
        _lang = code


def get_lang() -> str:
    return _lang


def t(key: str, **kwargs) -> str:
    """Translate key in the current language, with optional format args."""
    text = STRINGS.get(_lang, STRINGS["en"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


AVAILABLE_LANGS = {"English": "en", "हिन्दी": "hi"}
