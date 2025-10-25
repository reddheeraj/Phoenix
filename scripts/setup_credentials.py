#!/usr/bin/env python3
"""
Setup script for Google OAuth credentials.
This script helps users set up their Google OAuth credentials for Gmail and Calendar access.
"""

import os
import json
import sys
from pathlib import Path

def create_credentials_directory():
    """Create credentials directory if it doesn't exist"""
    creds_dir = Path("credentials")
    creds_dir.mkdir(exist_ok=True)
    return creds_dir

def create_client_secret_template():
    """Create a template for client_secret.json"""
    template = {
        "web": {
            "client_id": "YOUR_GOOGLE_CLIENT_ID",
            "project_id": "YOUR_PROJECT_ID",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }
    
    creds_dir = create_credentials_directory()
    template_path = creds_dir / "client_secret_template.json"
    
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    return template_path

def create_env_template():
    """Create .env template file"""
    env_template = """# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Database Configuration
DB_PATH=./solo_leveling.db

# Processing Configuration
DEFAULT_DAYS_TO_PROCESS=7
DEFAULT_EVENT_DURATION_MINUTES=60
"""
    
    with open(".env.template", 'w') as f:
        f.write(env_template)
    
    return ".env.template"

def main():
    """Main setup function"""
    print("🔧 Setting up Solo Leveling System credentials...")
    
    # Create credentials directory
    creds_dir = create_credentials_directory()
    print(f"✅ Created credentials directory: {creds_dir}")
    
    # Create client secret template
    template_path = create_client_secret_template()
    print(f"✅ Created client secret template: {template_path}")
    
    # Create .env template
    env_template_path = create_env_template()
    print(f"✅ Created .env template: {env_template_path}")
    
    print("\n📋 Next steps:")
    print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
    print("2. Create a new project or select existing one")
    print("3. Enable Gmail API and Google Calendar API")
    print("4. Create OAuth 2.0 credentials (Web application)")
    print("5. Download the credentials JSON file")
    print("6. Rename it to 'client_secret.json' and place it in the 'credentials' folder")
    print("7. Copy .env.template to .env and fill in your credentials")
    print("8. Set up your AWS credentials for Bedrock access")
    
    print("\n🔑 Required credentials:")
    print("- Google OAuth 2.0 credentials (Gmail + Calendar access)")
    print("- AWS credentials (Bedrock access)")
    
    print("\n🚀 After setup, run: python scripts/process_emails.py")

if __name__ == "__main__":
    main()

