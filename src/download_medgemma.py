"""
Download MedGemma 1.5 (4B Instruction-Tuned) from Hugging Face
Requires:
- A valid Hugging Face token stored in .env as HUGGINGFACE_TOKEN
- Access granted to the google/medgemma-1.5-4b-it repository
"""

import os
from dotenv import load_dotenv
from huggingface_hub import login, snapshot_download

def main():
    # Load environment variables
    load_dotenv()

    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        raise ValueError("HUGGINGFACE_TOKEN not found in .env file")

    # Authenticate with Hugging Face
    print("Logging into Hugging Face...")
    login(token=hf_token)
    print("Login successful.")

    # Model configuration
    model_name = "google/medgemma-1.5-4b-it"
    local_dir = "./models/medgemma"

    print(f"\nDownloading model: {model_name}")
    print("This may take several minutes depending on your connection.")

    try:
        snapshot_download(
            repo_id=model_name,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        print(f"\nModel successfully downloaded to: {local_dir}")

    except Exception as e:
        print(f"\nError downloading model: {e}")
        print("Verify your Hugging Face token and repository access.")

if __name__ == "__main__":
    main()