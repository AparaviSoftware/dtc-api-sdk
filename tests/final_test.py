#!/usr/bin/env python3
from dtc_api_sdk import DTCApiClient

client = DTCApiClient()

# Try the source/transformations format inside pipeline wrapper
config = {
    'pipeline': {
        'source': 'webhook_input',
        'transformations': ['parse'],
        'destination': 'text_output',
        'settings': {'parse': {'profile': 'default'}}
    }
}

try:
    is_valid = client.validate_pipeline(config)
    print(f'Validation: {"✅ Valid" if is_valid else "❌ Invalid"}')
    if is_valid:
        token = client.create_pipeline(config, name='final_test')
        print(f'✅ SUCCESS! Token: {token[:8]}...')
        client.delete_pipeline(token)
        print('🧹 Cleaned up')
except Exception as e:
    print(f'❌ Failed: {e}') 