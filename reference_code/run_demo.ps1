# Invoice Processing Demo Runner
# ============================
# 
# This PowerShell script runs the complete DTC API SDK invoice processing demo
# 
# Usage:
#   .\run_demo.ps1
#   
# Prerequisites:
#   - Set DTC_API_KEY environment variable
#   - Ensure Invoice PDF is in test_data directory
#   - Python 3.8+ with DTC API SDK installed

Write-Host "🚀 DTC API SDK - Invoice Processing Demo" -ForegroundColor Green
Write-Host "=" * 50

# Check if API key is set
if (-not $env:DTC_API_KEY) {
    Write-Host "❌ DTC_API_KEY environment variable not set" -ForegroundColor Red
    Write-Host "   Please set your API key:" -ForegroundColor Yellow
    Write-Host "   `$env:DTC_API_KEY = 'your-api-key-here'" -ForegroundColor Yellow
    exit 1
}

# Check if PDF file exists
$pdfFile = "test_data\Invoice-E6CD52F5-0002.pdf"
if (-not (Test-Path $pdfFile)) {
    Write-Host "❌ PDF file not found: $pdfFile" -ForegroundColor Red
    Write-Host "   Please ensure the invoice PDF is in the test_data directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Run the demo
Write-Host "`n🎬 Starting invoice processing demo..." -ForegroundColor Cyan

try {
    python run_full_demo.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 Demo completed successfully!" -ForegroundColor Green
        
        # Show results file if it exists
        $resultsFile = "invoice_results_Invoice-E6CD52F5-0002.json"
        if (Test-Path $resultsFile) {
            Write-Host "`n📁 Results saved to: $resultsFile" -ForegroundColor Cyan
            $fileSize = (Get-Item $resultsFile).Length
            Write-Host "📊 File size: $($fileSize) bytes" -ForegroundColor Cyan
        }
    } else {
        Write-Host "`n❌ Demo failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "`n❌ Error running demo: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 