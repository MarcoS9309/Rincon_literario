#!/usr/bin/env python3
import json
import os
import re

def sanitize_html_content(text):
    """Sanitiza contenido HTML para prevenir XSS"""
    import html
    # Solo escapar si no contiene etiquetas HTML válidas
    if not re.search(r'<[^>]+>', text):
        text = html.escape(text)
    return text

def markdown_to_html(markdown_text):
    """Convierte markdown básico a HTML con seguridad mejorada"""
    if not markdown_text or not isinstance(markdown_text, str):
        return ""
    
    html = markdown_text
    
    # Títulos
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Texto en cursiva y negrita
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
    
    # Separar en líneas y procesar párrafos
    lines = html.split('\n')
    result = []
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        if not line:  # Línea vacía
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                if not paragraph_text.startswith('<h'):
                    result.append(f'<p>{paragraph_text}</p>')
                else:
                    result.append(paragraph_text)
                current_paragraph = []
        else:
            if line.startswith('<h'):  # Es un encabezado
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    result.append(f'<p>{paragraph_text}</p>')
                    current_paragraph = []
                result.append(line)
            else:
                current_paragraph.append(line)
    
    # Procesar párrafo final si existe
    if current_paragraph:
        paragraph_text = ' '.join(current_paragraph)
        if not paragraph_text.startswith('<h'):
            result.append(f'<p>{paragraph_text}</p>')
        else:
            result.append(paragraph_text)
    
    return '\n'.join(result)

def create_static_page(item, markdown_content):
    """Crea una página HTML estática para un item con seguridad mejorada"""
    
    # Validar inputs
    if not item or not isinstance(item, dict):
        raise ValueError("Item inválido")
    
    if not markdown_content or not isinstance(markdown_content, str):
        raise ValueError("Contenido markdown inválido")
    
    # Convertir markdown a HTML
    html_content = markdown_to_html(markdown_content)
    
    # Determinar si es un poema
    is_poem = 'poemas' in item.get('path', '')
    content_class = 'poem-content' if is_poem else 'story-content'
    
    # Extraer título de manera segura
    title_match = re.search(r'^# (.+)$', markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else item.get('title', 'Sin título')
    title = sanitize_html_content(title)
    
    # Sanitizar categoría
    category = sanitize_html_content(item.get('category', 'Sin categoría'))
    
    # Template HTML mejorado con CSP y seguridad
    html_template = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com; script-src 'self' 'unsafe-inline'; connect-src 'self';">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <meta name="description" content="{category}: {title} por M. Vinicio">
    <title>{title} - Rincón Literario</title>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Lato', sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #2c3e50;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            min-height: 100vh;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
            position: relative;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #4a627a 100%);
            color: white;
            padding: 30px 40px;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%), 
                        radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08) 0%, transparent 50%),
                        radial-gradient(circle at 40% 80%, rgba(255,255,255,0.12) 0%, transparent 50%);
            opacity: 0.6;
        }}
        
        .navigation {{
            position: relative;
            z-index: 2;
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .nav-link {{
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 25px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
            font-weight: 300;
            backdrop-filter: blur(5px);
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .nav-link:hover {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }}
        
        .category-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 10px 25px;
            border-radius: 30px;
            font-size: 0.95rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
            position: relative;
            z-index: 2;
        }}
        
        .content {{
            padding: 50px;
            position: relative;
            z-index: 1;
            animation: fadeInUp 0.8s ease-out;
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .content h1 {{
            font-family: 'Playfair Display', serif;
            color: #2c3e50;
            font-size: 3.2rem;
            font-weight: 700;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
        }}
        
        .content h1::after {{
            content: '';
            position: absolute;
            bottom: -15px;
            left: 0;
            width: 100px;
            height: 4px;
            background: linear-gradient(135deg, #3498db, #2980b9);
            border-radius: 2px;
        }}
        
        .author-info {{
            color: #7f8c8d;
            font-style: italic;
            font-size: 1.1rem;
            margin-bottom: 40px;
            padding: 15px;
            background: rgba(52, 152, 219, 0.05);
            border-left: 4px solid #3498db;
            border-radius: 0 8px 8px 0;
        }}
        
        .story-content p {{
            font-size: 1.15rem;
            line-height: 1.9;
            margin-bottom: 2rem;
            text-align: justify;
            color: #34495e;
            text-indent: 2.5rem;
            position: relative;
        }}
        
        .story-content p:first-of-type {{
            font-size: 1.25rem;
            font-weight: 400;
            color: #2c3e50;
            text-indent: 0;
        }}
        
        .story-content p:first-of-type::first-letter {{
            font-family: 'Playfair Display', serif;
            font-size: 4.5rem;
            line-height: 0.8;
            float: left;
            margin: 0.05em 0.3em 0 0;
            color: #3498db;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        /* Estilos especiales para poemas */
        .poem-content {{
            text-align: center;
            font-family: 'Playfair Display', serif;
            max-width: 700px;
            margin: 0 auto;
        }}
        
        .poem-content h1 {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .poem-content h1::after {{
            left: 50%;
            transform: translateX(-50%);
        }}
        
        .poem-content p {{
            text-indent: 0;
            margin-bottom: 2rem;
            line-height: 2.2;
            font-size: 1.25rem;
            color: #2c3e50;
            text-align: center;
        }}
        
        .poem-content p:first-of-type::first-letter {{
            font-size: 5rem;
            line-height: 0.6;
            float: none;
            display: block;
            margin: 0 auto 20px auto;
            width: fit-content;
        }}
        
        .footer {{
            padding: 30px 40px;
            background: rgba(248, 249, 250, 0.8);
            border-top: 1px solid rgba(222, 226, 230, 0.5);
            text-align: center;
            color: #6c757d;
            font-size: 0.9rem;
            backdrop-filter: blur(10px);
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                margin: 0;
                border-radius: 0;
            }}
            
            .header, .content {{
                padding: 25px;
            }}
            
            .content h1 {{
                font-size: 2.5rem;
            }}
            
            .nav-link {{
                padding: 8px 15px;
                font-size: 0.9rem;
            }}
            
            .story-content p:first-of-type::first-letter,
            .poem-content p:first-of-type::first-letter {{
                font-size: 3.5rem;
            }}
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .header, .footer {{ 
                display: none; 
            }}
            .container {{ 
                box-shadow: none; 
                margin: 0;
                background: white;
            }}
            .content {{
                padding: 0;
                animation: none;
            }}
            .content h1::after {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <nav class="navigation">
                <a href="../index.html" class="nav-link">🏠 Inicio</a>
                <a href="javascript:history.back()" class="nav-link">← Atrás</a>
                <button onclick="window.print()" class="nav-link" style="background:none;border:none;color:rgba(255,255,255,0.9);cursor:pointer;">🖨️ Imprimir</button>
            </nav>
            <div class="category-badge">{category}</div>
        </div>
        
        <div class="content">
            <div class="{content_class}">
                {html_content}
                <div class="author-info">
                    <em>Por M. Vinicio</em>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 Rincón Literario - M. Vinicio | Obra original</p>
        </div>
    </div>
</body>
</html>'''
    
    return html_template

def safe_filename(title):
    """Genera un nombre de archivo seguro"""
    if not title or not isinstance(title, str):
        return "unknown"
    
    # Remover caracteres peligrosos y no válidos
    filename = re.sub(r'[<>:"|?*\\\/]', '_', title)
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'\s+', '_', filename.strip())
    
    # Limitar longitud
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename if filename else "unknown"

def main():
    """Función principal con manejo de errores mejorado"""
    try:
        # Cargar la base de datos
        if not os.path.exists('database.json'):
            raise FileNotFoundError("database.json no encontrado")
            
        with open('database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("database.json debe contener una lista")
        
        # Crear directorio static si no existe
        os.makedirs('static', exist_ok=True)
        
        success_count = 0
        error_count = 0
        
        for item in data:
            try:
                # Validar estructura del item
                if not isinstance(item, dict):
                    raise ValueError("Item debe ser un diccionario")
                
                required_fields = ['title', 'path']
                for field in required_fields:
                    if field not in item:
                        raise ValueError(f"Campo requerido '{field}' no encontrado")
                
                # Verificar que el archivo fuente existe
                if not os.path.exists(item['path']):
                    raise FileNotFoundError(f"Archivo fuente no encontrado: {item['path']}")
                
                # Leer el archivo markdown
                with open(item['path'], 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                # Crear la página HTML
                html_content = create_static_page(item, markdown_content)
                
                # Guardar la página con nombre seguro
                filename = safe_filename(item['title'])
                html_filename = f"static/{filename}.html"
                
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"✓ {html_filename}")
                success_count += 1
                
            except Exception as e:
                print(f"✗ Error procesando {item.get('title', 'desconocido')}: {e}")
                error_count += 1
        
        print(f"\n🎉 Generación completada:")
        print(f"   ✓ {success_count} páginas generadas exitosamente")
        if error_count > 0:
            print(f"   ✗ {error_count} errores encontrados")
            
    except Exception as e:
        print(f"Error fatal: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
