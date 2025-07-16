#!/usr/bin/env python3
"""
Comprehensive Unit Test Runner for DTC API SDK

This script runs all unit tests sequentially and provides a detailed report
of test results, including pass/fail counts, timing, and error summaries.
"""

import unittest
import sys
import os
import time
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class TestResult:
    """Container for test results from a single test file"""
    def __init__(self, test_name, success=False, tests_run=0, failures=0, errors=0, 
                 skipped=0, duration=0, output="", error_output=""):
        self.test_name = test_name
        self.success = success
        self.tests_run = tests_run
        self.failures = failures
        self.errors = errors
        self.skipped = skipped
        self.duration = duration
        self.output = output
        self.error_output = error_output

class UnitTestRunner:
    """Main test runner class"""
    
    def __init__(self):
        self.test_files = [
            "unit_tests.test_version_endpoint",
            "unit_tests.test_status_endpoint", 
            "unit_tests.test_services_endpoint",
            "unit_tests.test_pipe_validate_endpoint",
            "unit_tests.test_pipe_create_endpoint",
            "unit_tests.test_pipe_delete_endpoint",
            "unit_tests.test_pipe_process_endpoint",
            "unit_tests.test_task_execute_endpoint",
            "unit_tests.test_webhook_endpoint",
            "unit_tests.test_chat_endpoint",
            "unit_tests.test_dropper_endpoint"
        ]
        
        self.results = []
        self.total_start_time = None
        self.total_end_time = None
        
    def run_single_test(self, test_module_name):
        """Run a single test module and capture results"""
        print(f"\n{'='*80}")
        print(f"Running: {test_module_name}")
        print('='*80)
        
        start_time = time.time()
        
        try:
            # Import the test module
            test_module = __import__(test_module_name, fromlist=[''])
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Capture output
            output_capture = StringIO()
            error_capture = StringIO()
            
            # Run tests with captured output
            with redirect_stdout(output_capture), redirect_stderr(error_capture):
                runner = unittest.TextTestRunner(
                    stream=output_capture,
                    verbosity=2,
                    buffer=True
                )
                result = runner.run(suite)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Create result object
            test_result = TestResult(
                test_name=test_module_name,
                success=result.wasSuccessful(),
                tests_run=result.testsRun,
                failures=len(result.failures),
                errors=len(result.errors),
                skipped=len(result.skipped),
                duration=duration,
                output=output_capture.getvalue(),
                error_output=error_capture.getvalue()
            )
            
            # Print immediate results
            status = "✅ PASSED" if result.wasSuccessful() else "❌ FAILED"
            print(f"{status} - {test_result.tests_run} tests, {test_result.failures} failures, {test_result.errors} errors, {test_result.skipped} skipped")
            print(f"Duration: {duration:.2f}s")
            
            # Show any failures or errors immediately
            if result.failures:
                print(f"\n🔴 FAILURES ({len(result.failures)}):")
                for test, traceback in result.failures:
                    print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
            
            if result.errors:
                print(f"\n🟡 ERRORS ({len(result.errors)}):")
                for test, traceback in result.errors:
                    print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
            
            if result.skipped:
                print(f"\n🟡 SKIPPED ({len(result.skipped)}):")
                for test, reason in result.skipped:
                    print(f"  - {test}: {reason}")
            
            return test_result
            
        except ImportError as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"❌ IMPORT ERROR: Could not import {test_module_name}")
            print(f"Error: {str(e)}")
            
            return TestResult(
                test_name=test_module_name,
                success=False,
                errors=1,
                duration=duration,
                error_output=str(e)
            )
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"❌ UNEXPECTED ERROR in {test_module_name}")
            print(f"Error: {str(e)}")
            
            return TestResult(
                test_name=test_module_name,
                success=False,
                errors=1,
                duration=duration,
                error_output=str(e)
            )
    
    def run_all_tests(self):
        """Run all test files sequentially"""
        print("🚀 Starting DTC API SDK Unit Test Suite")
        print(f"📋 Running {len(self.test_files)} test modules")
        
        # Check API key
        api_key = os.getenv('DTC_API_KEY')
        if not api_key:
            print("⚠️  WARNING: DTC_API_KEY not found in environment variables")
            print("   Some tests may be skipped or fail")
        else:
            print(f"✅ API Key loaded: {api_key[:10]}...")
        
        self.total_start_time = time.time()
        
        # Run each test file
        for test_module in self.test_files:
            result = self.run_single_test(test_module)
            self.results.append(result)
            
            # Small delay between tests
            time.sleep(0.5)
        
        self.total_end_time = time.time()
        
        # Print comprehensive report
        self.print_summary_report()
    
    def print_summary_report(self):
        """Print comprehensive summary report"""
        total_duration = self.total_end_time - self.total_start_time
        
        print(f"\n{'='*80}")
        print("📊 COMPREHENSIVE TEST REPORT")
        print('='*80)
        
        # Overall statistics
        total_tests = sum(r.tests_run for r in self.results)
        total_failures = sum(r.failures for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        total_skipped = sum(r.skipped for r in self.results)
        successful_modules = sum(1 for r in self.results if r.success)
        
        print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        print(f"📁 Test Modules: {len(self.results)}")
        print(f"✅ Successful Modules: {successful_modules}")
        print(f"❌ Failed Modules: {len(self.results) - successful_modules}")
        print(f"🧪 Total Tests: {total_tests}")
        print(f"✅ Passed: {total_tests - total_failures - total_errors}")
        print(f"❌ Failed: {total_failures}")
        print(f"🟡 Errors: {total_errors}")
        print(f"⏭️  Skipped: {total_skipped}")
        
        # Success rate
        if total_tests > 0:
            success_rate = ((total_tests - total_failures - total_errors) / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Detailed results by module
        print(f"\n{'='*80}")
        print("📋 DETAILED RESULTS BY MODULE")
        print('='*80)
        
        for result in self.results:
            status_icon = "✅" if result.success else "❌"
            module_name = result.test_name.replace("unit_tests.test_", "").replace("_endpoint", "")
            
            print(f"{status_icon} {module_name.upper():<20} | "
                  f"Tests: {result.tests_run:>3} | "
                  f"Failures: {result.failures:>2} | "
                  f"Errors: {result.errors:>2} | "
                  f"Skipped: {result.skipped:>2} | "
                  f"Time: {result.duration:>6.2f}s")
        
        # Failed modules details
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            print(f"\n{'='*80}")
            print("🔍 FAILED MODULES DETAILS")
            print('='*80)
            
            for result in failed_results:
                print(f"\n❌ {result.test_name}")
                print(f"   Duration: {result.duration:.2f}s")
                print(f"   Tests Run: {result.tests_run}")
                print(f"   Failures: {result.failures}")
                print(f"   Errors: {result.errors}")
                
                if result.error_output:
                    print(f"   Error Output: {result.error_output[:200]}...")
        
        # Performance summary
        print(f"\n{'='*80}")
        print("⚡ PERFORMANCE SUMMARY")
        print('='*80)
        
        # Sort by duration
        sorted_results = sorted(self.results, key=lambda r: r.duration, reverse=True)
        
        print("Slowest modules:")
        for i, result in enumerate(sorted_results[:5]):
            module_name = result.test_name.replace("unit_tests.test_", "").replace("_endpoint", "")
            print(f"  {i+1}. {module_name:<20} {result.duration:>6.2f}s")
        
        print(f"\nFastest modules:")
        for i, result in enumerate(reversed(sorted_results[-5:])):
            module_name = result.test_name.replace("unit_tests.test_", "").replace("_endpoint", "")
            print(f"  {i+1}. {module_name:<20} {result.duration:>6.2f}s")
        
        # Final summary
        print(f"\n{'='*80}")
        print("🎯 FINAL SUMMARY")
        print('='*80)
        
        if successful_modules == len(self.results):
            print("🎉 ALL TESTS PASSED! The DTC API SDK is working correctly.")
        else:
            print(f"⚠️  {len(self.results) - successful_modules} out of {len(self.results)} modules failed.")
            print("   Check the details above for specific issues.")
        
        print(f"\nTotal execution time: {total_duration:.2f} seconds")
        print(f"Average time per module: {total_duration/len(self.results):.2f} seconds")
        
        # Return overall success
        return successful_modules == len(self.results)

def main():
    """Main entry point"""
    print("🧪 DTC API SDK Unit Test Runner")
    print("=" * 50)
    
    runner = UnitTestRunner()
    
    try:
        success = runner.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test run interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n💥 Unexpected error in test runner: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 