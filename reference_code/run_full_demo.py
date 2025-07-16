#!/usr/bin/env python3
"""
Complete Invoice Processing Demo
===============================

This script demonstrates the complete DTC API SDK workflow for processing
an invoice through a webhook → parse → response pipeline.

Run this script to see the full end-to-end processing flow.
"""

import os
import sys
from pathlib import Path
import subprocess

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking Prerequisites...")
    
    # Check API key
    api_key = "lCUtBHpigRHhjpPuyYNhVSLT4zX4GgeR871lDVFZspfxgPlJAuebArdDvKILLgpZ"#os.getenv("DTC_API_KEY")
    if not api_key:
        print("❌ DTC_API_KEY environment variable not set")
        print("   Please set your API key:")
        print("   export DTC_API_KEY='your-api-key-here'")
        return False
    
    # Check PDF file
    pdf_file = Path("test_data/Invoice-E6CD52F5-0002.pdf")
    if not pdf_file.exists():
        print(f"❌ PDF file not found: {pdf_file}")
        print("   Please ensure the invoice PDF is in the test_data directory")
        return False
    
    # Check SDK
    try:
        from dtc_api_sdk import DTCApiClient
        print("✅ DTC API SDK is available")
    except ImportError:
        print("❌ DTC API SDK not found")
        print("   Please install the SDK or ensure it's in your Python path")
        return False
    
    print("✅ All prerequisites met!")
    return True

def run_basic_test():
    """Run basic functionality test"""
    print("\n" + "="*60)
    print("🧪 STEP 1: Basic Functionality Test")
    print("="*60)
    
    try:
        result = subprocess.run([
            sys.executable, "test_basic_functionality.py"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running basic test: {e}")
        return False

def run_invoice_processing():
    """Run the full invoice processing"""
    print("\n" + "="*60)
    print("🧾 STEP 2: Invoice Processing")
    print("="*60)
    
    try:
        result = subprocess.run([
            sys.executable, "process_invoice_webhook.py"
        ], capture_output=False, text=True)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running invoice processing: {e}")
        return False

def show_summary():
    """Show final summary"""
    print("\n" + "="*60)
    print("📊 PROCESSING SUMMARY")
    print("="*60)
    
    # Check for results file
    results_file = Path("invoice_results_Invoice-E6CD52F5-0002.json")
    if results_file.exists():
        print(f"✅ Results file created: {results_file}")
        
        # Show file size
        file_size = results_file.stat().st_size
        print(f"📁 File size: {file_size:,} bytes")
        
        # Try to load and show summary
        try:
            import json
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            if results.get("extracted_text"):
                text_len = len(results["extracted_text"])
                print(f"📄 Extracted text: {text_len:,} characters")
            
            if results.get("metadata"):
                print(f"📋 Metadata fields: {len(results['metadata'])}")
            
            if results.get("objects"):
                print(f"📦 Processed objects: {len(results['objects'])}")
                
        except Exception as e:
            print(f"⚠️  Could not parse results file: {e}")
    else:
        print("❌ No results file found")

def main():
    """Main demo function"""
    print("🚀 DTC API SDK - Complete Invoice Processing Demo")
    print("=" * 60)
    print()
    print("This demo will:")
    print("1. 🔍 Check prerequisites")
    print("2. 🧪 Run basic functionality test")
    print("3. 🧾 Process invoice through webhook pipeline")
    print("4. 📊 Show processing summary")
    print()
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please resolve the issues above.")
        sys.exit(1)
    
    # Step 2: Run basic test
    if not run_basic_test():
        print("\n❌ Basic functionality test failed. Please check your API key and connectivity.")
        sys.exit(1)
    
    # Step 3: Run invoice processing
    print("\n🎬 Starting invoice processing...")
    if not run_invoice_processing():
        print("\n❌ Invoice processing failed. Check the output above for details.")
        sys.exit(1)
    
    # Step 4: Show summary
    show_summary()
    
    print("\n🎉 Demo completed successfully!")
    print("\nNext steps:")
    print("- Review the generated JSON results file")
    print("- Modify the pipeline configuration for your needs")
    print("- Process additional files using the same pattern")
    print("- Integrate the extracted data into your applications")

if __name__ == "__main__":
    main() 