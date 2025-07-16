#!/usr/bin/env python3
"""
Simple runner script for invoice processing
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import our module
sys.path.insert(0, str(Path(__file__).parent))

from process_invoice_webhook import InvoiceProcessor

def main():
    """Simple runner for invoice processing"""
    
    print("🧾 DTC Invoice Processing Runner")
    print("=" * 40)
    
    # Set up environment
    api_key = os.getenv("DTC_API_KEY")
    if not api_key:
        print("❌ Please set DTC_API_KEY environment variable")
        print("   export DTC_API_KEY='your-api-key-here'")
        return
    
    # File to process
    invoice_file = "test_data/Invoice-E6CD52F5-0002.pdf"
    
    if not Path(invoice_file).exists():
        print(f"❌ Invoice file not found: {invoice_file}")
        print("Please ensure the PDF file is in the test_data directory")
        return
    
    try:
        # Create processor and run
        processor = InvoiceProcessor(api_key)
        results = processor.process_invoice(invoice_file)
        
        print("\n🎉 Processing completed successfully!")
        print(f"Results saved to: invoice_results_Invoice-E6CD52F5-0002.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 