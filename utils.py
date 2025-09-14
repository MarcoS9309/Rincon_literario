"""
Utility functions for Rincón Literario Static Site Generator
Author: M. Vinicio
"""

import re
import os
import json
import logging
from datetime import datetime
from config import CATEGORIES, PROCESSING_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('site_generation.log'),
        logging.StreamHandler()
    ]
)

def setup_logger(name):
    """Create a logger instance"""
    return logging.getLogger(name)

def markdown_to_html(markdown_text):
    """
    Enhanced markdown to HTML converter with better formatting
    
    Args:
        markdown_text (str): Input markdown text
        
    Returns:
        str: Converted HTML text
    """
    html = markdown_text
    
    # Headers with proper hierarchy
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Text formatting
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Process lines and create paragraphs
    lines = html.split('\n')
    result = []
    current_paragraph = []
    in_code_block = False
    
    for line in lines:
        line = line.strip()
        
        # Handle code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                if current_paragraph:
                    result.append(f'<p>{" ".join(current_paragraph)}</p>')
                    current_paragraph = []
                result.append('<pre><code>')
            else:
                result.append('</code></pre>')
            continue
            
        if in_code_block:
            result.append(line)
            continue
        
        if not line:  # Empty line
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                if not paragraph_text.startswith('<h'):
                    result.append(f'<p>{paragraph_text}</p>')
                else:
                    result.append(paragraph_text)
                current_paragraph = []
        else:
            if line.startswith('<h'):  # Header
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    result.append(f'<p>{paragraph_text}</p>')
                    current_paragraph = []
                result.append(line)
            else:
                current_paragraph.append(line)
    
    # Handle final paragraph
    if current_paragraph:
        paragraph_text = ' '.join(current_paragraph)
        if not paragraph_text.startswith('<h'):
            result.append(f'<p>{paragraph_text}</p>')
        else:
            result.append(paragraph_text)
    
    return '\n'.join(result)

def sanitize_filename(filename):
    """
    Sanitize filename for cross-platform compatibility
    
    Args:
        filename (str): Input filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace spaces and invalid characters
    filename = filename.replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = re.sub(PROCESSING_CONFIG["invalid_filename_chars"], 
                     PROCESSING_CONFIG["replacement_char"], filename)
    return filename

def get_category_info(category):
    """
    Get category configuration information
    
    Args:
        category (str): Category name
        
    Returns:
        dict: Category configuration or default values
    """
    return CATEGORIES.get(category, {
        "display_name": category,
        "description": "",
        "icon": "📄",
        "css_class": "content"
    })

def validate_file_exists(filepath):
    """
    Validate that a file exists and is readable
    
    Args:
        filepath (str): Path to file
        
    Returns:
        bool: True if file exists and is readable
    """
    try:
        return os.path.exists(filepath) and os.access(filepath, os.R_OK)
    except Exception:
        return False

def load_database(database_path='database.json'):
    """
    Load and validate the content database
    
    Args:
        database_path (str): Path to database file
        
    Returns:
        list: Database content or empty list if error
    """
    logger = setup_logger(__name__)
    
    try:
        if not validate_file_exists(database_path):
            logger.error(f"Database file not found: {database_path}")
            return []
            
        with open(database_path, 'r', encoding=PROCESSING_CONFIG["input_encoding"]) as f:
            data = json.load(f)
            
        # Validate database structure
        if not isinstance(data, list):
            logger.error("Database must be a list of items")
            return []
            
        valid_items = []
        for item in data:
            if validate_database_item(item):
                valid_items.append(item)
            else:
                logger.warning(f"Invalid database item: {item}")
                
        logger.info(f"Loaded {len(valid_items)} valid items from database")
        return valid_items
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in database: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading database: {e}")
        return []

def validate_database_item(item):
    """
    Validate a single database item
    
    Args:
        item (dict): Database item to validate
        
    Returns:
        bool: True if item is valid
    """
    required_fields = ['title', 'category', 'path']
    
    if not isinstance(item, dict):
        return False
        
    for field in required_fields:
        if field not in item or not item[field]:
            return False
            
    # Validate file exists
    if not validate_file_exists(item['path']):
        return False
        
    return True

def read_markdown_file(filepath):
    """
    Read and validate markdown file
    
    Args:
        filepath (str): Path to markdown file
        
    Returns:
        str: File content or empty string if error
    """
    logger = setup_logger(__name__)
    
    try:
        if not validate_file_exists(filepath):
            logger.error(f"Markdown file not found: {filepath}")
            return ""
            
        with open(filepath, 'r', encoding=PROCESSING_CONFIG["input_encoding"]) as f:
            content = f.read().strip()
            
        if not content:
            logger.warning(f"Empty markdown file: {filepath}")
            
        return content
        
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading {filepath}: {e}")
        return ""
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return ""

def write_html_file(filepath, content):
    """
    Write HTML content to file with error handling
    
    Args:
        filepath (str): Output file path
        content (str): HTML content to write
        
    Returns:
        bool: True if successful
    """
    logger = setup_logger(__name__)
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding=PROCESSING_CONFIG["output_encoding"]) as f:
            f.write(content)
            
        logger.debug(f"Successfully wrote: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error writing {filepath}: {e}")
        return False

def get_stats_summary(data):
    """
    Generate content statistics summary
    
    Args:
        data (list): Database items
        
    Returns:
        dict: Statistics summary
    """
    stats = {}
    total_items = len(data)
    
    # Count by category
    category_counts = {}
    for item in data:
        category = item.get('category', 'Unknown')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    stats['total'] = total_items
    stats['categories'] = category_counts
    stats['generation_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return stats

def print_generation_summary(stats, success_count, error_count):
    """
    Print a summary of the generation process
    
    Args:
        stats (dict): Content statistics
        success_count (int): Number of successful generations
        error_count (int): Number of errors
    """
    logger = setup_logger(__name__)
    
    print(f"\n{'='*50}")
    print("🎉 GENERACIÓN COMPLETADA")
    print(f"{'='*50}")
    print(f"📊 Estadísticas:")
    print(f"   • Total de elementos: {stats['total']}")
    print(f"   • Páginas generadas exitosamente: {success_count}")
    if error_count > 0:
        print(f"   • Errores encontrados: {error_count}")
    
    print(f"\n📁 Por categoría:")
    for category, count in stats['categories'].items():
        category_info = get_category_info(category)
        icon = category_info.get('icon', '📄')
        display_name = category_info.get('display_name', category)
        print(f"   {icon} {display_name}: {count}")
    
    print(f"\n⏰ Generado el: {stats['generation_time']}")
    print(f"{'='*50}")
    
    logger.info(f"Generation completed: {success_count} success, {error_count} errors")