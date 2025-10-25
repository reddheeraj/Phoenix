#!/usr/bin/env python3
import os, json, sys
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()

def pick_model_id():
    """
    Use a known-good Anthropic Sonnet model ID that exists in us-east-1/us-west-2.
    Replace this with one you actually have access to in your region.
    """
    return os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")

def test_bedrock():
    region = os.getenv("AWS_REGION", "us-east-1")
    model_id = pick_model_id()

    print("🧪 AWS Bedrock Connection Test")
    print("="*50)
    print(f"Region: {region}")
    print(f"Model:  {model_id}")
    print()

    # Let boto3 use the default credential chain (env vars, shared config, SSO, role, etc.)
    # Do NOT hardcode or pass someone else’s keys here.
    client = boto3.client("bedrock-runtime", region_name=region)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 256,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Hi, what is the capital of India?"}
                ]
            }
        ]
    }

    try:
        resp = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            accept="application/json",
            contentType="application/json",
        )
        data = json.loads(resp["body"].read())
        # Anthropic Messages response shape on Bedrock:
        # {"content":[{"type":"text","text":"..."}], ...}
        answer = data["content"][0]["text"]
        print("✅ Success!\n")
        print(answer)
        return True

    except ClientError as e:
        print("❌ ClientError")
        print(json.dumps(e.response.get("Error", {}), indent=2))
        # Helpful hints by error type:
        code = e.response.get("Error", {}).get("Code", "")
        if code in {"UnrecognizedClientException", "InvalidSignatureException"}:
            print("\nCheck your credentials or session token (AWS_SESSION_TOKEN).")
        elif code == "AccessDeniedException":
            print("\nYour principal likely lacks bedrock:InvokeModel or model access in this region.")
        elif code == "ResourceNotFoundException":
            print("\nThat model ID isn’t available in this region or for your account.")
        elif code == "ValidationException":
            print("\nYour request payload/headers/modelId are probably malformed.")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    ok = test_bedrock()
    sys.exit(0 if ok else 1)
