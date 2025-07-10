#!/usr/bin/env python3
from dtc_api_sdk import DTCApiClient

client = DTCApiClient()

# Correct format: pipeline wrapper with components array  
config = {
    'pipeline': {
        'components': [
            {
                'id': 'parse_1',
                'provider': 'parse', 
                'config': {'profile': 'default'}
            }
        ],
        'id': 'test-parse-pipeline'
    }
}

try:
    is_valid = client.validate_pipeline(config)
    print(f'Validation: {"✅ Valid" if is_valid else "❌ Invalid"}')
    if is_valid:
        token = client.create_pipeline(config, name='correct_format_test')
        print(f'🎉 SUCCESS! Token: {token[:8]}...')
        client.delete_pipeline(token)
        print('🧹 Pipeline cleaned up')
        print('\n🎯 FOUND THE CORRECT FORMAT!')
        print('Format: {"pipeline": {"components": [...], "id": "..."}}')
except Exception as e:
    print(f'Result: {e}') 