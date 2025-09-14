#!/usr/bin/env python3
"""
Rincón Literario Static Site Generator (Refactored Version)
Author: M. Vinicio
Description: Refactored and improved version of the static site generator
             with better code organization, error handling, and modularity.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SITE_CONFIG, CATEGORIES, TEMPLATE_CONFIG
from templates import (
    get_html_head, get_page_css, get_page_template, 
    get_print_button, get_author_info
)
from utils import (
    setup_logger, markdown_to_html, sanitize_filename, 
    get_category_info, load_database, read_markdown_file, 
    write_html_file, get_stats_summary, print_generation_summary
)

class StaticSiteGenerator:
    """Main class for generating static site pages"""
    
    def __init__(self, database_path='database.json'):
        """
        Initialize the generator
        
        Args:
            database_path (str): Path to the content database
        """
        self.database_path = database_path
        self.logger = setup_logger(__name__)
        self.success_count = 0
        self.error_count = 0
        
    def generate_page_html(self, item, markdown_content):
        """
        Generate complete HTML page for a content item
        
        Args:
            item (dict): Content item from database
            markdown_content (str): Raw markdown content
            
        Returns:
            str: Complete HTML page
        """
        try:
            # Get category information
            category_info = get_category_info(item['category'])
            
            # Convert markdown to HTML
            html_content = markdown_to_html(markdown_content)
            
            # Prepare template variables
            template_vars = {
                'language': SITE_CONFIG['language'],
                'head': get_html_head(
                    title=f"{item['title']} - {SITE_CONFIG['title']}",
                    description=f"{item['title']} por {SITE_CONFIG['author']} - {category_info.get('description', '')}",
                    keywords=f"{item['title']}, {SITE_CONFIG['keywords']}"
                ),
                'css': get_page_css(),
                'category': category_info['display_name'],
                'content_class': category_info['css_class'],
                'html_content': html_content,
                'print_button': get_print_button(),
                'author_info': get_author_info(),
                'copyright': SITE_CONFIG['copyright']
            }
            
            # Generate complete page
            return get_page_template().format(**template_vars)
            
        except Exception as e:
            self.logger.error(f"Error generating HTML for {item['title']}: {e}")
            return None
    
    def process_single_item(self, item):
        """
        Process a single content item
        
        Args:
            item (dict): Content item to process
            
        Returns:
            bool: True if successful
        """
        try:
            # Read markdown content
            markdown_content = read_markdown_file(item['path'])
            if not markdown_content:
                self.logger.error(f"Could not read content for {item['title']}")
                return False
            
            # Generate HTML page
            html_content = self.generate_page_html(item, markdown_content)
            if not html_content:
                self.logger.error(f"Could not generate HTML for {item['title']}")
                return False
            
            # Generate output filename
            filename = sanitize_filename(item['title'])
            html_filename = os.path.join(SITE_CONFIG['static_dir'], f"{filename}.html")
            
            # Write HTML file
            success = write_html_file(html_filename, html_content)
            if success:
                print(f"✓ {html_filename}")
                self.logger.info(f"Generated: {html_filename}")
                return True
            else:
                print(f"✗ Failed: {html_filename}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing {item.get('title', 'unknown')}: {e}")
            print(f"✗ Error processing {item.get('title', 'unknown')}: {e}")
            return False
    
    def generate_all_pages(self):
        """
        Generate all static pages
        
        Returns:
            dict: Generation statistics
        """
        self.logger.info("Starting static site generation")
        
        # Load database
        data = load_database(self.database_path)
        if not data:
            self.logger.error("No valid data found in database")
            return None
        
        # Create static directory
        static_dir = Path(SITE_CONFIG['static_dir'])
        static_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Processing {len(data)} items")
        
        # Process each item
        self.success_count = 0
        self.error_count = 0
        
        for item in data:
            if self.process_single_item(item):
                self.success_count += 1
            else:
                self.error_count += 1
        
        # Generate statistics
        stats = get_stats_summary(data)
        
        return stats
    
    def run(self):
        """
        Main execution method
        
        Returns:
            bool: True if generation was successful
        """
        try:
            self.logger.info("=== Rincón Literario Static Site Generator ===")
            
            # Generate all pages
            stats = self.generate_all_pages()
            
            if stats is None:
                self.logger.error("Generation failed")
                return False
            
            # Print summary
            print_generation_summary(stats, self.success_count, self.error_count)
            
            # Log final status
            if self.error_count == 0:
                self.logger.info("All pages generated successfully")
                return True
            else:
                self.logger.warning(f"Generation completed with {self.error_count} errors")
                return self.success_count > 0
                
        except Exception as e:
            self.logger.error(f"Fatal error during generation: {e}")
            print(f"💥 Fatal error: {e}")
            return False

def main():
    """Main entry point"""
    try:
        # Create generator instance
        generator = StaticSiteGenerator()
        
        # Run generation
        success = generator.run()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()