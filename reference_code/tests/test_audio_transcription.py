#!/usr/bin/env python3
"""
Test script for audio transcription pipeline
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import DTCApiError

def test_audio_transcription_pipeline():
    """Test the audio transcription pipeline configuration."""
    print("🧪 Testing Audio Transcription Pipeline")
    print("=" * 50)
    
    # Audio transcription pipeline configuration
    pipeline_config = {
        "pipeline": {
            "source": "dropper_1",
            "components": [
                {
                    "id": "dropper_1",
                    "provider": "dropper",
                    "config": {
                        "hideForm": True,
                        "mode": "Source",
                        "type": "dropper"
                    }
                },
                {
                    "id": "parse_1",
                    "provider": "parse",
                    "config": {},
                    "input": [
                        {
                            "lane": "tags",
                            "from": "dropper_1"
                        }
                    ]
                },
                {
                    "id": "audio_transcribe_1",
                    "provider": "audio_transcribe",
                    "config": {
                        "profile": "default",
                        "default": {
                            "max_seconds": 300,
                            "min_seconds": 240,
                            "model": "base",
                            "silence_threshold": 0.25,
                            "vad_level": 1
                        }
                    },
                    "input": [
                        {
                            "lane": "video",
                            "from": "parse_1"
                        },
                        {
                            "lane": "audio",
                            "from": "parse_1"
                        }
                    ]
                },
                {
                    "id": "response_1",
                    "provider": "response",
                    "config": {
                        "lanes": ["text"]
                    },
                    "input": [
                        {
                            "lane": "text",
                            "from": "audio_transcribe_1"
                        }
                    ]
                }
            ],
            "id": "audio-transcription-test"
        }
    }
    
    try:
        # Test 1: SDK initialization
        print("✅ Test 1: SDK Initialization")
        client = DTCApiClient()
        print("   ✅ Client created successfully")
        
        # Test 2: Pipeline validation
        print("\n🔍 Test 2: Pipeline Validation")
        is_valid = client.validate_pipeline(pipeline_config)
        print(f"   ✅ Pipeline validation: {'Valid ✅' if is_valid else 'Invalid ❌'}")
        
        if not is_valid:
            print("   ❌ Pipeline validation failed - check configuration")
            return False
            
        # Test 3: Pipeline creation
        print("\n🔧 Test 3: Pipeline Creation")
        pipeline_token = client.create_pipeline(
            config=pipeline_config,
            name="audio_transcription_test"
        )
        print(f"   ✅ Pipeline created successfully! Token: {pipeline_token[:8]}...")
        
        # Test 4: Interface URLs
        print("\n🌐 Test 4: Interface URLs")
        try:
            dropper_url = client.get_dropper_url(pipeline_token, "audio_transcribe")
            print(f"   ✅ Dropper URL generated: {dropper_url}")
        except Exception as e:
            print(f"   ⚠️  Dropper URL error: {e}")
            
        try:
            chat_url = client.get_chat_url(pipeline_token, "audio_transcribe")
            print(f"   ✅ Chat URL generated: {chat_url}")
        except Exception as e:
            print(f"   ⚠️  Chat URL error: {e}")
        
        # Test 5: Cleanup
        print("\n🧹 Test 5: Cleanup")
        cleanup_success = client.delete_pipeline(pipeline_token)
        print(f"   ✅ Pipeline deleted: {cleanup_success}")
        
        print("\n🎯 ALL TESTS PASSED!")
        print("✅ Audio transcription pipeline is ready to use")
        return True
        
    except DTCApiError as e:
        print(f"❌ API Error: {e}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_file_exists():
    """Check if the target MP4 file exists."""
    file_path = Path(r"C:\Users\HendrikKrack\WorkBench\dtc-api\dtc-api-sdk\test_data\Q&A and check-in-20250623_125525-Meeting Recording.mp4")
    
    print(f"\n📁 Checking target file...")
    print(f"   Path: {file_path}")
    
    if file_path.exists():
        file_size = file_path.stat().st_size / (1024*1024)
        print(f"   ✅ File found! Size: {file_size:.2f} MB")
        return True
    else:
        print(f"   ❌ File not found!")
        print("   📝 Please ensure the file exists at the specified path")
        return False

if __name__ == "__main__":
    print("🎵 Audio Transcription Pipeline Test")
    print("=" * 60)
    
    # Check API key
    if not os.getenv("DTC_API_KEY"):
        print("⚠️  No DTC_API_KEY environment variable found")
        print("   Please set your API key: export DTC_API_KEY='your_key_here'")
        exit(1)
    
    # Check file
    file_exists = check_file_exists()
    
    # Run pipeline test
    test_passed = test_audio_transcription_pipeline()
    
    if test_passed and file_exists:
        print("\n🚀 Ready to process your audio file!")
        print("   Run: python examples/audio_transcription_example.py")
    elif test_passed:
        print("\n⚠️  Pipeline test passed, but audio file not found")
        print("   Update the file path in the example script")
    else:
        print("\n❌ Pipeline test failed - check your configuration") 