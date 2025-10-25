#!/usr/bin/env python3
"""
Simple test for BedrockClient to verify AWS Bedrock integration.
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.llm.bedrock_client import BedrockClient

def test_bedrock_client():
    """Test Bedrock client initialization and quest analysis"""
    
    print("\n" + "="*80)
    print("BEDROCK CLIENT TEST")
    print("="*80)
    
    # Test 1: Initialize client
    print("\n[TEST 1] Initializing Bedrock Client...")
    try:
        client = BedrockClient()
        print("[SUCCESS] Client initialized")
        print(f"  Region: {client.region}")
        print(f"  Model ID: {client.model_id}")
    except Exception as e:
        print(f"[FAILED] Could not initialize client: {e}")
        return False
    
    # Test 2: Simple quest analysis with a sample email
    print("\n[TEST 2] Testing Quest Analysis...")
    sample_email = {
        'sender': 'professor@university.edu',
        'subject': 'Assignment 3 Due Next Week',
        'body': 'Hi students, just a reminder that Assignment 3 is due on Friday, November 1st at 11:59 PM. Please submit your work through the course portal. This assignment covers topics from chapters 5-7.',
        'received_date': datetime.now()
    }
    
    try:
        print("  Analyzing sample email...")
        print(f"  From: {sample_email['sender']}")
        print(f"  Subject: {sample_email['subject']}")
        
        result = client.generate_quest_analysis(sample_email)
        
        print("\n[SUCCESS] Quest Analysis Result:")
        print(f"  Should Create Quest: {result.get('should_create_quest')}")
        
        if result.get('should_create_quest'):
            print(f"  Title: {result.get('title')}")
            print(f"  Description: {result.get('description', '')[:100]}...")
            print(f"  Quest Type: {result.get('quest_type')}")
            print(f"  Importance: {result.get('importance')}")
            print(f"  Urgency: {result.get('urgency')}")
            print(f"  Deadline: {result.get('deadline')}")
            print(f"  Duration: {result.get('event_duration_minutes')} minutes")
            print(f"  Reasoning: {result.get('reasoning', '')[:100]}...")
        else:
            print(f"  Reason: {result.get('reasoning', 'No reason provided')}")
        
    except Exception as e:
        print(f"[FAILED] Quest analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Test with non-actionable email (should not create quest)
    print("\n[TEST 3] Testing with Non-Actionable Email...")
    spam_email = {
        'sender': 'marketing@retailstore.com',
        'subject': '50% OFF SALE - Limited Time Only!',
        'body': 'Don\'t miss out on our biggest sale of the year! Get 50% off on all items. Shop now before it\'s too late!',
        'received_date': datetime.now()
    }
    
    try:
        print("  Analyzing marketing email...")
        print(f"  From: {spam_email['sender']}")
        print(f"  Subject: {spam_email['subject']}")
        
        result = client.generate_quest_analysis(spam_email)
        
        print("\n[SUCCESS] Analysis Result:")
        print(f"  Should Create Quest: {result.get('should_create_quest')}")
        print(f"  Reasoning: {result.get('reasoning', 'No reason provided')[:150]}...")
        
        if result.get('should_create_quest'):
            print("\n[WARNING] Expected no quest for marketing email, but one was created")
        else:
            print("\n[EXPECTED] No quest created for marketing email (correct behavior)")
        
    except Exception as e:
        print(f"[FAILED] Analysis failed: {e}")
        return False
    
    # Test 4: Test with user preferences
    print("\n[TEST 4] Testing Quest Analysis with User Goals...")
    career_email = {
        'sender': 'recruiter@techcompany.com',
        'subject': 'Software Engineer Interview Invitation',
        'body': 'We would like to invite you for an interview for the Software Engineer position. Please let us know your availability for next week, Tuesday or Wednesday.',
        'received_date': datetime.now()
    }
    
    user_prefs = {
        'long_term_goals': ['Get a software engineering job', 'Improve coding skills', 'Build portfolio']
    }
    
    try:
        print("  Analyzing career-related email with user goals...")
        print(f"  User Goals: {', '.join(user_prefs['long_term_goals'])}")
        print(f"  From: {career_email['sender']}")
        print(f"  Subject: {career_email['subject']}")
        
        result = client.generate_quest_analysis_with_goals(career_email, user_prefs)
        
        print("\n[SUCCESS] Goal-Aligned Analysis Result:")
        print(f"  Should Create Quest: {result.get('should_create_quest')}")
        
        if result.get('should_create_quest'):
            print(f"  Title: {result.get('title')}")
            print(f"  Quest Category: {result.get('quest_category')}")
            print(f"  Importance: {result.get('importance')}")
            print(f"  Urgency: {result.get('urgency')}")
            print(f"  Goal Alignment: {result.get('reasoning', '')[:150]}...")
        
    except Exception as e:
        print(f"[FAILED] Goal-aligned analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*80)
    print("[SUCCESS] All Bedrock Client tests completed!")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_bedrock_client()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

