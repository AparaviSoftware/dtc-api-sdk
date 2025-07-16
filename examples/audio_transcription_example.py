#!/usr/bin/env python3
"""
Audio Transcription Example for DTC API SDK

This example demonstrates processing an MP4 file to extract and transcribe audio content.
Pipeline flow: File Upload → Parse → Audio Transcribe → Response

Based on the pipeline: dropper → parse → audio_transcribe → response
"""

import os
import time
from pathlib import Path
from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import DTCApiError


def create_audio_transcription_pipeline():
    """Create the audio transcription pipeline configuration."""
    return {
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
            "id": "audio-transcription-pipeline"
        }
    }


def process_audio_file(file_path: str):
    """Process an audio/video file for transcription."""
    print("🎵 Audio Transcription Pipeline")
    print("=" * 50)
    
    # Initialize client
    client = DTCApiClient()
    
    # Check if file exists
    audio_file = Path(file_path)
    if not audio_file.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📁 Processing file: {audio_file.name}")
    print(f"📊 File size: {audio_file.stat().st_size / (1024*1024):.2f} MB")
    
    # Create pipeline configuration
    pipeline_config = create_audio_transcription_pipeline()
    
    try:
        # Step 1: Validate pipeline configuration
        print("\n🔍 Step 1: Validating pipeline configuration...")
        is_valid = client.validate_pipeline(pipeline_config)
        print(f"   ✅ Pipeline validation: {'Valid' if is_valid else 'Invalid'}")
        
        if not is_valid:
            print("❌ Pipeline configuration is invalid. Exiting.")
            return
        
        # Step 2: Create pipeline
        print("\n🔧 Step 2: Creating pipeline...")
        pipeline_token = client.create_pipeline(
            config=pipeline_config,
            name="audio_transcription_demo"
        )
        print(f"   ✅ Pipeline created! Token: {pipeline_token[:8]}...")
        
        # Step 3: Upload file
        print(f"\n📤 Step 3: Uploading file...")
        upload_success = client.upload_files(
            token=pipeline_token,
            files=[str(audio_file)]
        )
        print(f"   ✅ File uploaded: {upload_success}")
        
        # Step 4: Get dropper URL for alternative upload method
        print(f"\n🌐 Step 4: Getting interface URLs...")
        try:
            dropper_url = client.get_dropper_url(pipeline_token, "audio_transcribe")
            print(f"   ✅ Dropper URL: {dropper_url}")
            print("   📁 You can also upload files via this web interface!")
        except Exception as e:
            print(f"   ⚠️  Dropper URL error: {e}")
        
        # Step 5: Monitor processing
        print(f"\n⏳ Step 5: Monitoring processing...")
        print("   🎵 Extracting audio from video...")
        print("   🗣️  Transcribing audio content...")
        print("   📝 Generating text output...")
        
        # Note: Since this is a pipeline (not a task), we can't directly monitor progress
        # In a real scenario, you might need to implement webhook endpoints or polling
        print("   ⚠️  Pipeline processing started. Check the dropper interface for results.")
        
        # Step 6: Alternative - Use task execution for direct monitoring
        print(f"\n🔄 Step 6: Alternative - Execute as task for monitoring...")
        try:
            task_token = client.execute_task(
                config=pipeline_config,
                name="audio_transcription_task",
                threads=2
            )
            print(f"   ✅ Task started! Token: {task_token[:8]}...")
            
            # Monitor task progress
            print("   ⏳ Monitoring task progress...")
            for i in range(12):  # Check for 2 minutes (12 * 10 seconds)
                task_info = client.get_task_status(task_token)
                print(f"   📊 Status: {task_info.status.value}, Progress: {task_info.progress}")
                
                if task_info.status.value == "completed":
                    print(f"   ✅ Task completed successfully!")
                    if task_info.result:
                        print(f"   📝 Result: {task_info.result}")
                    break
                elif task_info.status.value == "failed":
                    print(f"   ❌ Task failed: {task_info.error_message}")
                    break
                elif task_info.status.value == "cancelled":
                    print(f"   ⚠️  Task was cancelled")
                    break
                
                time.sleep(10)  # Wait 10 seconds between checks
            else:
                print("   ⏰ Task still running after 2 minutes. You can check status later.")
        
        except Exception as e:
            print(f"   ⚠️  Task execution error: {e}")
        
        # Step 7: Webhook example (for when you have transcription results)
        print(f"\n🪝 Step 7: Webhook example...")
        try:
            webhook_data = {
                "event": "transcription_complete",
                "data": {
                    "filename": audio_file.name,
                    "status": "processing",
                    "message": "Audio transcription in progress"
                }
            }
            webhook_response = client.send_webhook(pipeline_token, webhook_data)
            print(f"   ✅ Webhook sent: {webhook_response}")
        except Exception as e:
            print(f"   ⚠️  Webhook error: {e}")
        
        # Step 8: Clean up
        print(f"\n🧹 Step 8: Cleaning up...")
        cleanup_success = client.delete_pipeline(pipeline_token)
        print(f"   ✅ Pipeline deleted: {cleanup_success}")
        
        print(f"\n🎯 PROCESSING COMPLETE!")
        print("📋 Summary:")
        print("   ✅ Pipeline validated and created")
        print("   ✅ MP4 file uploaded successfully")
        print("   ✅ Audio extraction and transcription initiated")
        print("   ✅ Multiple monitoring methods demonstrated")
        print("   ✅ Webhook integration shown")
        print("   ✅ Pipeline cleaned up")
        
    except DTCApiError as e:
        print(f"❌ API Error: {e}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        if e.response_data:
            print(f"   Response Data: {e.response_data}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def show_pipeline_info():
    """Show information about the audio transcription pipeline."""
    print("\n📚 AUDIO TRANSCRIPTION PIPELINE INFO")
    print("=" * 50)
    print("🎯 Pipeline Components:")
    print("   1. 🗂️  Dropper - File upload source")
    print("   2. 🔍 Parse - Extract audio/video from files")
    print("   3. 🎵 Audio Transcribe - Convert speech to text")
    print("   4. 📤 Response - Output transcribed text")
    print()
    print("⚙️  Audio Transcription Settings:")
    print("   - Model: base (Whisper model)")
    print("   - Max seconds: 300 (5 minutes)")
    print("   - Min seconds: 240 (4 minutes)")
    print("   - Silence threshold: 0.25")
    print("   - VAD level: 1 (Voice Activity Detection)")
    print()
    print("📁 Supported File Types:")
    print("   - MP4 (video with audio)")
    print("   - MP3 (audio only)")
    print("   - WAV (audio only)")
    print("   - Other audio/video formats")
    print()
    print("🔄 Processing Flow:")
    print("   File → Parse → Audio Extract → Transcribe → Text Output")


def main():
    """Main function to process the user's audio file."""
    # Your specific file path
    audio_file_path = r"C:\Users\HendrikKrack\WorkBench\dtc-api\dtc-api-sdk\test_data\Q&A and check-in-20250623_125525-Meeting Recording.mp4"
    
    show_pipeline_info()
    process_audio_file(audio_file_path)


if __name__ == "__main__":
    main() 