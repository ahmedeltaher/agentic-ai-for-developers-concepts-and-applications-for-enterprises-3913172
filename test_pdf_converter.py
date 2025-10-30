#!/usr/bin/env python3
"""
Test script for HTML to PDF Converter
Quick test and usage examples
"""

import os
import sys
from pathlib import Path

# Add the current directory to path to import our converter
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from html_to_pdf_converter import HTMLToPDFConverter
except ImportError as e:
    print(f"Error importing converter: {e}")
    print("Make sure all required packages are installed:")
    print("pip install -r requirements_pdf.txt")
    sys.exit(1)


def test_single_conversion():
    """Test converting a single HTML file"""
    print("🧪 Testing single file conversion...")
    
    converter = HTMLToPDFConverter()
    
    # Test with reflection pattern file
    html_file = "explain/4.1 reflection_pattern_explained.html"
    pdf_file = "explain/pdfs/test_reflection_pattern.pdf"
    
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    # Create output directory
    Path(pdf_file).parent.mkdir(parents=True, exist_ok=True)
    
    success = converter.convert_to_pdf(html_file, pdf_file)
    
    if success:
        print(f"✅ Successfully converted {html_file} to {pdf_file}")
        print(f"📄 PDF size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
        return True
    else:
        print(f"❌ Failed to convert {html_file}")
        return False


def test_batch_conversion():
    """Test converting multiple HTML files"""
    print("\n🧪 Testing batch conversion...")
    
    converter = HTMLToPDFConverter()
    
    input_dir = "explain"
    output_dir = "explain/pdfs"
    
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return False
    
    # Convert only a few files for testing
    test_files = [
        "4.1 reflection_pattern_explained.html",
        "4.2 router_pattern_explained.html",
        "7.4 compliance_in_agentic_ai_explained.html"
    ]
    
    results = {}
    
    for filename in test_files:
        html_file = os.path.join(input_dir, filename)
        if os.path.exists(html_file):
            pdf_file = os.path.join(output_dir, f"{Path(filename).stem}.pdf")
            
            # Create output directory
            Path(pdf_file).parent.mkdir(parents=True, exist_ok=True)
            
            print(f"Converting {filename}...")
            success = converter.convert_to_pdf(html_file, pdf_file)
            results[filename] = success
            
            if success:
                size_kb = os.path.getsize(pdf_file) / 1024
                print(f"  ✅ Success - {size_kb:.1f} KB")
            else:
                print(f"  ❌ Failed")
        else:
            print(f"  ⚠️  File not found: {filename}")
            results[filename] = False
    
    print(f"\n📊 Batch conversion results:")
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    for filename, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {filename}")
    
    print(f"\n📈 Summary: {success_count}/{total_count} files converted successfully")
    return success_count > 0


def analyze_html_structure():
    """Analyze the structure of HTML files to understand card layout"""
    print("\n🔍 Analyzing HTML structure...")
    
    html_file = "explain/4.1 reflection_pattern_explained.html"
    
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return
    
    converter = HTMLToPDFConverter()
    cards = converter.extract_cards_from_html(html_file)
    
    print(f"📄 File: {html_file}")
    print(f"🃏 Cards found: {len(cards)}")
    
    for i, card in enumerate(cards[:3]):  # Show first 3 cards
        print(f"\n📋 Card {i+1}:")
        print(f"  Title: {card.title[:50]}...")
        print(f"  Content length: {len(card.content)} chars")
        print(f"  Has code: {card.has_code}")
        if card.has_code:
            print(f"  Code length: {len(card.code_content)} chars")


def main():
    """Run all tests"""
    print("🚀 HTML to PDF Converter - Test Suite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("explain"):
        print("❌ Please run this script from the project root directory")
        print("   (where the 'explain' folder is located)")
        return
    
    # Analyze HTML structure
    analyze_html_structure()
    
    # Test single conversion
    single_success = test_single_conversion()
    
    # Test batch conversion
    batch_success = test_batch_conversion()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"  Single conversion: {'✅ PASS' if single_success else '❌ FAIL'}")
    print(f"  Batch conversion: {'✅ PASS' if batch_success else '❌ FAIL'}")
    
    if single_success or batch_success:
        print("\n🎉 At least one test passed! Check the 'explain/pdfs' directory for output files.")
        print("\n💡 Usage tips:")
        print("  - Each card becomes a separate PDF page")
        print("  - Navigation links connect pages like a carousel")
        print("  - Table of contents provides overview")
        print("  - Arabic text is properly handled (RTL)")
        print("  - Code blocks are formatted separately (LTR)")
    else:
        print("\n❌ All tests failed. Check error messages above.")
        print("\n🔧 Troubleshooting:")
        print("  1. Install required packages: pip install -r requirements_pdf.txt")
        print("  2. Check if HTML files exist in 'explain' directory")
        print("  3. Ensure you have write permissions for output directory")


if __name__ == "__main__":
    main()
