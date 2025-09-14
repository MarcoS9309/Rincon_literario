# Configuration file for Rincón Literario Static Site Generator
# Author: M. Vinicio
# Generated: 2025

# Site configuration
SITE_CONFIG = {
    "title": "Rincón Literario - Literatura, Poesía y Meditación Espiritual",
    "author": "M. Vinicio",
    "description": "Colección personal de M. Vinicio: 44 obras literarias incluyendo historias, cuentos de ciencia ficción, poemas líricos y meditaciones espirituales. Sitio web estático con navegación intuitiva.",
    "keywords": "literatura, poesía, cuentos, historias, meditación, rosario, novena, M. Vinicio, ficción, narrativa",
    "language": "es",
    "locale": "es_ES",
    "copyright": "© 2025 Rincón Literario - M. Vinicio | Obra original",
    "base_url": "/",
    "static_dir": "static"
}

# Content categories and their display names
CATEGORIES = {
    "Historias": {
        "display_name": "Historias",
        "description": "Relatos narrativos personales y ficticios que exploran temas universales de la experiencia humana.",
        "icon": "📖",
        "css_class": "story-content"
    },
    "Cuentos": {
        "display_name": "Cuentos",
        "description": "Cuentos de ciencia ficción y fantasía que transportan al lector a mundos imaginarios.",
        "icon": "🌟",
        "css_class": "story-content"
    },
    "Poemas": {
        "display_name": "Poemas",
        "description": "Colección de poemas líricos que expresan emociones y reflexiones sobre la vida.",
        "icon": "🎭",
        "css_class": "poem-content"
    },
    "Meditaciones": {
        "display_name": "Meditaciones",
        "description": "Guías espirituales para el rezo del Santo Rosario y meditaciones religiosas.",
        "icon": "🙏",
        "css_class": "meditation-content"
    },
    "Novena y Meditación Personal": {
        "display_name": "Novena y Meditación Personal",
        "description": "Programa de meditación diaria estructurada sobre los Siete Dolores de María.",
        "icon": "✨",
        "css_class": "meditation-content"
    }
}

# Template settings
TEMPLATE_CONFIG = {
    "fonts": "https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:wght@400;700&display=swap",
    "favicon_svg": "PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiBmaWxsPSIjNGY0NmU1Ii8+CjxwYXRoIGQ9Ik04IDEwaDEydjJIOHYtMnptMCA0aDEwdjJIOHYtMnptMCA0aDE2djJIOHYtMnptMCA0aDE0djJIOHYtMnoiIGZpbGw9IndoaXRlIi8+Cjwvc3ZnPgo=",
    "enable_print": True,
    "enable_back_navigation": True
}

# File processing settings  
PROCESSING_CONFIG = {
    "input_encoding": "utf-8",
    "output_encoding": "utf-8",
    "markdown_extensions": [".md", ".markdown"],
    "invalid_filename_chars": r'[<>:"|?*]',
    "replacement_char": "_"
}

# Navigation settings
NAVIGATION_CONFIG = {
    "show_category_counts": True,
    "enable_breadcrumbs": True,
    "show_author_info": True
}