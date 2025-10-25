#!/usr/bin/env python3
"""
Simple script to test AWS credentials from .env file
"""

import os
import boto3
from dotenv import load_dotenv

def test_aws_credentials():
    """Test AWS credentials from .env file"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    session_token = os.getenv('AWS_SESSION_TOKEN')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    print("=== AWS Credentials Test ===")
    print(f"Access Key: {access_key[:10]}..." if access_key else "❌ Not found")
    print(f"Secret Key: {secret_key[:10]}..." if secret_key else "❌ Not found")
    print(f"Session Token: {session_token[:10]}..." if session_token else "❌ Not found")
    print(f"Region: {region}")
    print()
    
    if not all([access_key, secret_key, session_token]):
        print("❌ Missing required credentials!")
        return False
    
    try:
        # Create boto3 client with explicit credentials
        client = boto3.client(
            'bedrock',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        print("✅ Boto3 client created successfully")
        
        # Test basic connectivity
        print("Testing Bedrock connectivity...")
        response = client.list_foundation_models()
        print(f"✅ Successfully connected to Bedrock!")
        print(f"Found {len(response.get('modelSummaries', []))} foundation models")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_aws_credentials()
