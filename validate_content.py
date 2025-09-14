#!/usr/bin/env python3
"""
Content Validation Script for Rincón Literario
Author: M. Vinicio
Description: Validates content integrity, checks for missing files,
             and ensures all generated pages are accessible.
"""

import os
import sys
import json
from pathlib import Path
from urllib.parse import urlparse
import requests
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SITE_CONFIG, CATEGORIES
from utils import setup_logger, load_database, validate_file_exists

class ContentValidator:
    """Validates content integrity and accessibility"""
    
    def __init__(self, base_url="http://localhost:8000"):
        """
        Initialize validator
        
        Args:
            base_url (str): Base URL for testing pages
        """
        self.base_url = base_url
        self.logger = setup_logger(__name__)
        self.errors = []
        self.warnings = []
        
    def validate_database_structure(self):
        """Validate database structure and content"""
        self.logger.info("Validating database structure...")
        
        data = load_database()
        if not data:
            self.errors.append("Database could not be loaded")
            return False
            
        # Check required fields
        required_fields = ['title', 'category', 'path']
        for i, item in enumerate(data):
            for field in required_fields:
                if field not in item:
                    self.errors.append(f"Item {i}: Missing field '{field}'")
                elif not item[field]:
                    self.errors.append(f"Item {i}: Empty field '{field}'")
        
        # Check for duplicate titles
        titles = [item['title'] for item in data]
        duplicates = set([title for title in titles if titles.count(title) > 1])
        if duplicates:
            self.warnings.append(f"Duplicate titles found: {duplicates}")
        
        self.logger.info(f"Database validation complete. {len(data)} items processed.")
        return len(self.errors) == 0
    
    def validate_source_files(self):
        """Validate that all source markdown files exist"""
        self.logger.info("Validating source files...")
        
        data = load_database()
        missing_files = []
        
        for item in data:
            if not validate_file_exists(item['path']):
                missing_files.append(item['path'])
                self.errors.append(f"Missing source file: {item['path']}")
        
        if not missing_files:
            self.logger.info("All source files are present.")
        else:
            self.logger.error(f"Missing {len(missing_files)} source files.")
            
        return len(missing_files) == 0
    
    def validate_generated_files(self):
        """Validate that all HTML files were generated"""
        self.logger.info("Validating generated HTML files...")
        
        data = load_database()
        missing_html = []
        static_dir = Path(SITE_CONFIG['static_dir'])
        
        for item in data:
            # Generate expected filename (same logic as generator)
            filename = item['title'].replace(' ', '_').replace('/', '_').replace('\\', '_')
            filename = filename.replace('<', '_').replace('>', '_').replace(':', '_')
            filename = filename.replace('"', '_').replace('|', '_').replace('?', '_').replace('*', '_')
            html_path = static_dir / f"{filename}.html"
            
            if not html_path.exists():
                missing_html.append(str(html_path))
                self.errors.append(f"Missing HTML file: {html_path}")
        
        if not missing_html:
            self.logger.info("All HTML files are present.")
        else:
            self.logger.error(f"Missing {len(missing_html)} HTML files.")
            
        return len(missing_html) == 0
    
    def validate_page_accessibility(self):
        """Test that generated pages are accessible via HTTP"""
        self.logger.info("Testing page accessibility...")
        
        data = load_database()
        inaccessible_pages = []
        
        # Test main index page
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code != 200:
                self.errors.append(f"Index page not accessible: {response.status_code}")
        except Exception as e:
            self.errors.append(f"Cannot access index page: {e}")
        
        # Test individual pages
        for item in data:
            filename = item['title'].replace(' ', '_').replace('/', '_').replace('\\', '_')
            filename = filename.replace('<', '_').replace('>', '_').replace(':', '_')
            filename = filename.replace('"', '_').replace('|', '_').replace('?', '_').replace('*', '_')
            
            page_url = f"{self.base_url}/static/{filename}.html"
            
            try:
                response = requests.get(page_url, timeout=5)
                if response.status_code != 200:
                    inaccessible_pages.append(page_url)
                    self.errors.append(f"Page not accessible: {page_url} ({response.status_code})")
            except Exception as e:
                inaccessible_pages.append(page_url)
                self.errors.append(f"Cannot access page {page_url}: {e}")
        
        if not inaccessible_pages:
            self.logger.info("All pages are accessible.")
        else:
            self.logger.error(f"{len(inaccessible_pages)} pages are not accessible.")
            
        return len(inaccessible_pages) == 0
    
    def validate_content_statistics(self):
        """Validate content statistics match expected values"""
        self.logger.info("Validating content statistics...")
        
        data = load_database()
        category_counts = {}
        
        for item in data:
            category = item['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Expected counts (from README)
        expected_counts = {
            'Historias': 7,
            'Cuentos': 15,
            'Poemas': 10,
            'Meditaciones': 3,
            'Novena y Meditación Personal': 9
        }
        
        for category, expected_count in expected_counts.items():
            actual_count = category_counts.get(category, 0)
            if actual_count != expected_count:
                self.warnings.append(
                    f"Category '{category}': expected {expected_count}, got {actual_count}"
                )
        
        total_expected = 44
        total_actual = len(data)
        if total_actual != total_expected:
            self.warnings.append(
                f"Total items: expected {total_expected}, got {total_actual}"
            )
        
        self.logger.info(f"Statistics validation complete. Found {len(data)} total items.")
        
    def validate_css_and_assets(self):
        """Validate CSS and asset files are present"""
        self.logger.info("Validating CSS and assets...")
        
        # Check main CSS file
        if not validate_file_exists('style.css'):
            self.errors.append("Main CSS file 'style.css' is missing")
        
        # Check index.html
        if not validate_file_exists('index.html'):
            self.errors.append("Main index.html file is missing")
        
        self.logger.info("CSS and assets validation complete.")
        
    def generate_validation_report(self):
        """Generate a comprehensive validation report"""
        self.logger.info("Generating validation report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'errors': self.errors,
            'warnings': self.warnings,
            'status': 'PASS' if len(self.errors) == 0 else 'FAIL',
            'summary': {
                'error_count': len(self.errors),
                'warning_count': len(self.warnings)
            }
        }
        
        # Save report to file
        with open('validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def run_full_validation(self):
        """Run complete validation suite"""
        self.logger.info("=== Content Validation Suite ===")
        
        # Run all validation checks
        validations = [
            ("Database Structure", self.validate_database_structure),
            ("Source Files", self.validate_source_files),
            ("Generated Files", self.validate_generated_files),
            ("Content Statistics", self.validate_content_statistics),
            ("CSS and Assets", self.validate_css_and_assets),
        ]
        
        # Run accessible test only if base_url is reachable
        try:
            requests.get(self.base_url, timeout=2)
            validations.append(("Page Accessibility", self.validate_page_accessibility))
        except:
            self.logger.warning(f"Skipping accessibility test - server not reachable at {self.base_url}")
        
        results = {}
        for name, validation_func in validations:
            self.logger.info(f"\n--- {name} ---")
            try:
                results[name] = validation_func()
            except Exception as e:
                self.logger.error(f"Error in {name}: {e}")
                self.errors.append(f"Validation error in {name}: {e}")
                results[name] = False
        
        # Generate report
        report = self.generate_validation_report()
        
        # Print summary
        self.print_summary(results, report)
        
        return report['status'] == 'PASS'
    
    def print_summary(self, results, report):
        """Print validation summary"""
        print(f"\n{'='*60}")
        print("🔍 VALIDATION SUMMARY")
        print(f"{'='*60}")
        
        # Results by category
        for name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {name}")
        
        print(f"\n📊 Overall Status: {'✅ PASS' if report['status'] == 'PASS' else '❌ FAIL'}")
        print(f"📈 Errors: {report['summary']['error_count']}")
        print(f"⚠️  Warnings: {report['summary']['warning_count']}")
        
        if self.errors:
            print(f"\n❌ ERRORS:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print(f"\n📄 Detailed report saved to: validation_report.json")
        print(f"{'='*60}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Rincón Literario content')
    parser.add_argument('--base-url', default='http://localhost:8000',
                       help='Base URL for accessibility testing')
    parser.add_argument('--skip-http', action='store_true',
                       help='Skip HTTP accessibility tests')
    
    args = parser.parse_args()
    
    try:
        validator = ContentValidator(args.base_url)
        success = validator.run_full_validation()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()