#!/usr/bin/env python3
"""
HTML to PDF Converter with Card-based Carousel Navigation
Converts HTML files with card-based structure to interactive PDF with each card as a separate page
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    print("Error: WeasyPrint not installed. Install with: pip install weasyprint")
    exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: BeautifulSoup not installed. Install with: pip install beautifulsoup4")
    exit(1)

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
    from reportlab.platypus.tableofcontents import TableOfContents
except ImportError:
    print("Error: ReportLab not installed. Install with: pip install reportlab")
    exit(1)


@dataclass
class CardInfo:
    """Information about a card extracted from HTML"""
    title: str
    content: str
    html_content: str
    card_index: int
    has_code: bool = False
    code_content: str = ""


class HTMLToPDFConverter:
    """
    Converts HTML files with card structure to interactive PDF
    Each card becomes a separate page with navigation links
    """
    
    def __init__(self, 
                 page_size: tuple = A4,
                 font_size: int = 12,
                 title_font_size: int = 18,
                 margin: float = 0.75 * inch):
        """
        Initialize the converter
        
        Args:
            page_size: PDF page size (default: A4)
            font_size: Base font size
            title_font_size: Title font size
            margin: Page margins
        """
        self.page_size = page_size
        self.font_size = font_size
        self.title_font_size = title_font_size
        self.margin = margin
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup fonts for Arabic text
        self._setup_fonts()
        
        # Setup styles
        self._setup_styles()
        
    def _setup_fonts(self):
        """Setup Arabic fonts for RTL text"""
        try:
            # Try to register common Arabic fonts
            # Note: You might need to adjust font paths based on your system
            font_paths = [
                '/System/Library/Fonts/Arial.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                'C:/Windows/Fonts/arial.ttf',  # Windows
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Arabic', font_path))
                        self.logger.info(f"Registered font: {font_path}")
                        break
                    except Exception as e:
                        self.logger.warning(f"Could not register font {font_path}: {e}")
                        
        except Exception as e:
            self.logger.warning(f"Font setup failed: {e}")
    
    def _setup_styles(self):
        """Setup paragraph styles for different content types"""
        self.styles = getSampleStyleSheet()
        
        # Arabic title style
        self.styles.add(ParagraphStyle(
            name='ArabicTitle',
            parent=self.styles['Heading1'],
            fontName='Arabic',
            fontSize=self.title_font_size,
            alignment=TA_RIGHT,
            spaceAfter=20,
            textColor='#2c3e50'
        ))
        
        # Arabic content style
        self.styles.add(ParagraphStyle(
            name='ArabicContent',
            parent=self.styles['Normal'],
            fontName='Arabic',
            fontSize=self.font_size,
            alignment=TA_RIGHT,
            spaceAfter=12,
            leading=18
        ))
        
        # Code style (LTR)
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Code'],
            fontName='Courier',
            fontSize=10,
            alignment=TA_LEFT,
            leftIndent=20,
            rightIndent=20,
            backColor='#f8f9fa',
            borderColor='#dee2e6',
            borderWidth=1,
            borderPadding=10
        ))
        
        # Navigation style
        self.styles.add(ParagraphStyle(
            name='Navigation',
            parent=self.styles['Normal'],
            fontName='Arabic',
            fontSize=10,
            alignment=TA_CENTER,
            textColor='#007bff'
        ))

    def extract_cards_from_html(self, html_file_path: str) -> List[CardInfo]:
        """
        Extract card information from HTML file
        
        Args:
            html_file_path: Path to HTML file
            
        Returns:
            List of CardInfo objects
        """
        cards = []
        
        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
                
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract main title
            title_element = soup.find('h1')
            main_title = title_element.get_text(strip=True) if title_element else "Untitled"
            
            # Find all cards
            card_elements = soup.find_all('div', class_='card')
            
            for idx, card in enumerate(card_elements):
                # Extract card title
                title_elem = card.find(['h2', 'h3', '.card-title', '.card h2', '.card h3'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    # Remove icons/emojis if present
                    title = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', '', title).strip()
                else:
                    title = f"Card {idx + 1}"
                
                # Extract content (excluding title and code blocks)
                content_elements = card.find_all(['p', 'ul', 'ol', 'div'], 
                                               class_=lambda x: x not in ['code-card', 'code'] if x else True)
                
                content_text = ""
                for elem in content_elements:
                    if not any(cls in (elem.get('class', []) if elem.get('class') else []) 
                             for cls in ['code-card', 'code']):
                        content_text += elem.get_text(strip=True) + "\n\n"
                
                # Extract code if present
                code_elements = card.find_all(['div', 'pre'], class_=['code-card', 'code'])
                code_content = ""
                has_code = len(code_elements) > 0
                
                for code_elem in code_elements:
                    code_content += code_elem.get_text(strip=True) + "\n\n"
                
                card_info = CardInfo(
                    title=title or f"Card {idx + 1}",
                    content=content_text.strip(),
                    html_content=str(card),
                    card_index=idx,
                    has_code=has_code,
                    code_content=code_content.strip()
                )
                
                cards.append(card_info)
                
            self.logger.info(f"Extracted {len(cards)} cards from {html_file_path}")
            return cards
            
        except Exception as e:
            self.logger.error(f"Error extracting cards from {html_file_path}: {e}")
            return []

    def create_navigation_links(self, current_page: int, total_pages: int) -> List[Paragraph]:
        """
        Create navigation links for carousel functionality
        
        Args:
            current_page: Current page number (0-based)
            total_pages: Total number of pages
            
        Returns:
            List of navigation paragraphs
        """
        nav_elements = []
        
        # Previous button
        if current_page > 0:
            prev_text = f"← الصفحة السابقة ({current_page})"
            nav_elements.append(Paragraph(prev_text, self.styles['Navigation']))
        
        # Page indicator
        page_indicator = f"الصفحة {current_page + 1} من {total_pages}"
        nav_elements.append(Paragraph(page_indicator, self.styles['Navigation']))
        
        # Next button
        if current_page < total_pages - 1:
            next_text = f"الصفحة التالية ({current_page + 2}) →"
            nav_elements.append(Paragraph(next_text, self.styles['Navigation']))
        
        # Table of contents link
        toc_text = "العودة للفهرس"
        nav_elements.append(Paragraph(toc_text, self.styles['Navigation']))
        
        return nav_elements

    def create_table_of_contents(self, cards: List[CardInfo], main_title: str) -> List:
        """
        Create table of contents page
        
        Args:
            cards: List of cards
            main_title: Main document title
            
        Returns:
            List of content elements
        """
        content = []
        
        # Title
        content.append(Paragraph(main_title, self.styles['ArabicTitle']))
        content.append(Spacer(1, 20))
        
        # TOC Header
        toc_header = "فهرس المحتويات"
        content.append(Paragraph(toc_header, self.styles['ArabicTitle']))
        content.append(Spacer(1, 30))
        
        # TOC entries
        for idx, card in enumerate(cards):
            toc_entry = f"{idx + 1}. {card.title}"
            content.append(Paragraph(toc_entry, self.styles['ArabicContent']))
            content.append(Spacer(1, 10))
        
        content.append(PageBreak())
        return content

    def create_card_page(self, card: CardInfo, page_num: int, total_pages: int) -> List:
        """
        Create a single card page
        
        Args:
            card: Card information
            page_num: Current page number
            total_pages: Total number of pages
            
        Returns:
            List of content elements
        """
        content = []
        
        # Card title
        content.append(Paragraph(card.title, self.styles['ArabicTitle']))
        content.append(Spacer(1, 20))
        
        # Card content
        if card.content:
            # Split content into paragraphs
            paragraphs = card.content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    content.append(Paragraph(para.strip(), self.styles['ArabicContent']))
                    content.append(Spacer(1, 12))
        
        # Code content if present
        if card.has_code and card.code_content:
            content.append(Spacer(1, 20))
            code_title = "الكود:"
            content.append(Paragraph(code_title, self.styles['ArabicContent']))
            content.append(Spacer(1, 10))
            
            # Format code (preserve formatting)
            code_lines = card.code_content.split('\n')
            for line in code_lines:
                if line.strip():
                    content.append(Paragraph(line, self.styles['CodeStyle']))
        
        # Navigation
        content.append(Spacer(1, 40))
        nav_elements = self.create_navigation_links(page_num, total_pages)
        for nav_elem in nav_elements:
            content.append(nav_elem)
            content.append(Spacer(1, 5))
        
        # Page break (except for last page)
        if page_num < total_pages - 1:
            content.append(PageBreak())
            
        return content

    def convert_to_pdf(self, html_file_path: str, output_pdf_path: str) -> bool:
        """
        Convert HTML file to PDF with carousel navigation
        
        Args:
            html_file_path: Path to input HTML file
            output_pdf_path: Path to output PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract cards
            cards = self.extract_cards_from_html(html_file_path)
            if not cards:
                self.logger.error("No cards found in HTML file")
                return False
            
            # Get main title
            with open(html_file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                title_elem = soup.find('h1')
                main_title = title_elem.get_text(strip=True) if title_elem else Path(html_file_path).stem
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_pdf_path,
                pagesize=self.page_size,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Build content
            content = []
            
            # Table of contents
            content.extend(self.create_table_of_contents(cards, main_title))
            
            # Card pages
            for idx, card in enumerate(cards):
                card_content = self.create_card_page(card, idx, len(cards))
                content.extend(card_content)
            
            # Build PDF
            doc.build(content)
            
            self.logger.info(f"Successfully created PDF: {output_pdf_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting to PDF: {e}")
            return False

    def convert_multiple_files(self, input_dir: str, output_dir: str, 
                             file_pattern: str = "*.html") -> Dict[str, bool]:
        """
        Convert multiple HTML files to PDF
        
        Args:
            input_dir: Directory containing HTML files
            output_dir: Directory for output PDF files
            file_pattern: File pattern to match
            
        Returns:
            Dictionary with filename: success status
        """
        results = {}
        
        try:
            input_path = Path(input_dir)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            html_files = list(input_path.glob(file_pattern))
            
            for html_file in html_files:
                pdf_file = output_path / f"{html_file.stem}.pdf"
                self.logger.info(f"Converting {html_file.name} to {pdf_file.name}")
                
                success = self.convert_to_pdf(str(html_file), str(pdf_file))
                results[html_file.name] = success
                
        except Exception as e:
            self.logger.error(f"Error in batch conversion: {e}")
            
        return results


def main():
    """Example usage of the HTML to PDF converter"""
    
    # Initialize converter
    converter = HTMLToPDFConverter()
    
    # Example: Convert single file
    html_file = "/Users/I550080/ML study/agentic-ai-for-developers-concepts-and-applications-for-enterprises-3913172/explain/4.1 reflection_pattern_explained.html"
    pdf_file = "/Users/I550080/ML study/agentic-ai-for-developers-concepts-and-applications-for-enterprises-3913172/explain/pdfs/reflection_pattern.pdf"
    
    # Create output directory
    Path(pdf_file).parent.mkdir(parents=True, exist_ok=True)
    
    success = converter.convert_to_pdf(html_file, pdf_file)
    
    if success:
        print(f"✅ Successfully converted {html_file} to {pdf_file}")
    else:
        print(f"❌ Failed to convert {html_file}")
    
    # Example: Convert all HTML files in directory
    input_dir = "/Users/I550080/ML study/agentic-ai-for-developers-concepts-and-applications-for-enterprises-3913172/explain"
    output_dir = "/Users/I550080/ML study/agentic-ai-for-developers-concepts-and-applications-for-enterprises-3913172/explain/pdfs"
    
    results = converter.convert_multiple_files(input_dir, output_dir)
    
    print("\n📊 Batch Conversion Results:")
    for filename, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {filename}")


if __name__ == "__main__":
    main()
