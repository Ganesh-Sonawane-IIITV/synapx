"""
Setup verification script.
Run this to verify your environment is correctly configured.
"""
import os
import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check if required packages are installed."""
    required = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'google.generativeai',
        'PyPDF2',
        'python-dotenv'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            elif package == 'google.generativeai':
                __import__('google.generativeai')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (not installed)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Install missing packages:")
        print(f"   pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and has API key."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Create .env file with:")
        print("   GEMINI_API_KEY=your_api_key_here")
        print("\n   Get your free API key from:")
        print("   https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ .env file exists")
    
    # Check if API key is set
    with open(env_file) as f:
        content = f.read()
        if 'GEMINI_API_KEY' not in content:
            print("⚠️  GEMINI_API_KEY not found in .env")
            return False
        elif 'your_api_key_here' in content:
            print("⚠️  Please replace 'your_api_key_here' with your actual API key")
            return False
    
    print("✅ GEMINI_API_KEY configured")
    return True


def check_sample_documents():
    """Check if sample documents exist."""
    sample_dir = Path('sample_documents')
    
    if not sample_dir.exists():
        print("❌ sample_documents directory not found")
        return False
    
    samples = list(sample_dir.glob('*.txt'))
    if len(samples) < 5:
        print(f"⚠️  Expected 5 sample documents, found {len(samples)}")
        return False
    
    print(f"✅ {len(samples)} sample documents found")
    return True


def check_web_files():
    """Check if web interface files exist."""
    web_dir = Path('web')
    required_files = ['index.html', 'styles.css', 'script.js']
    
    if not web_dir.exists():
        print("❌ web directory not found")
        return False
    
    missing = []
    for file in required_files:
        if not (web_dir / file).exists():
            missing.append(file)
            print(f"❌ web/{file}")
        else:
            print(f"✅ web/{file}")
    
    return len(missing) == 0


def main():
    """Run all checks."""
    print("=" * 60)
    print("SynAPX - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Configuration", check_env_file),
        ("Sample Documents", check_sample_documents),
        ("Web Interface Files", check_web_files),
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        print("-" * 60)
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    
    if all_passed:
        print("🎉 All checks passed! You're ready to go!")
        print("\nNext steps:")
        print("1. Start the web interface: python api.py")
        print("2. Or test with CLI: python src/agent.py sample_documents/claim_001.txt")
        print("3. Or run tests: python -m pytest tests/ -v")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
