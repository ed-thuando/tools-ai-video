#!/usr/bin/env python3
"""
Test script to verify installation and setup
"""

import sys
import subprocess
import os
from pathlib import Path


class SetupTester:
    """Test installation and setup"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test(self, name: str, condition: bool, error_msg: str = ""):
        """Test a condition"""
        if condition:
            print(f"✓ {name}")
            self.passed += 1
        else:
            print(f"✗ {name}")
            if error_msg:
                print(f"  Error: {error_msg}")
            self.failed += 1
    
    def warn(self, name: str, message: str = ""):
        """Print warning"""
        print(f"⚠ {name}")
        if message:
            print(f"  {message}")
        self.warnings += 1
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("Vietnamese Story Video Generator - Setup Test")
        print("="*60 + "\n")
        
        self.test_python()
        self.test_virtual_env()
        self.test_dependencies()
        self.test_ffmpeg()
        self.test_api_key()
        self.test_directories()
        
        self.print_summary()
    
    def test_python(self):
        """Test Python installation"""
        print("Testing Python...")
        
        # Check Python version
        version_info = sys.version_info
        version_ok = version_info.major == 3 and version_info.minor >= 8
        self.test(
            f"Python {version_info.major}.{version_info.minor}",
            version_ok,
            f"Python 3.8+ required, found {version_info.major}.{version_info.minor}"
        )
        
        # Check pip
        try:
            import pip
            self.test("pip installed", True)
        except ImportError:
            self.test("pip installed", False, "pip not found")
    
    def test_virtual_env(self):
        """Test virtual environment"""
        print("\nTesting Virtual Environment...")
        
        # Check if in virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        self.test("Virtual environment active", in_venv, 
                 "Run: source venv/bin/activate")
    
    def test_dependencies(self):
        """Test required dependencies"""
        print("\nTesting Dependencies...")
        
        dependencies = {
            'google.generativeai': 'Gemini API',
            'PIL': 'Pillow (Image processing)',
            'imageio': 'imageio (Video processing)',
            'pydub': 'pydub (Audio processing)',
        }
        
        for module, name in dependencies.items():
            try:
                __import__(module)
                self.test(f"{name}", True)
            except ImportError:
                self.test(f"{name}", False, f"Install with: pip install {module.split('.')[0]}")
    
    def test_ffmpeg(self):
        """Test FFmpeg installation"""
        print("\nTesting FFmpeg...")
        
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.test("FFmpeg installed", True)
                print(f"  {version_line}")
            else:
                self.test("FFmpeg installed", False, "FFmpeg not working properly")
        except FileNotFoundError:
            self.test("FFmpeg installed", False, 
                     "Install with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
        except subprocess.TimeoutExpired:
            self.test("FFmpeg installed", False, "FFmpeg timeout")
    
    def test_api_key(self):
        """Test API key configuration"""
        print("\nTesting API Key...")
        
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            masked_key = api_key[:10] + "..." + api_key[-5:]
            self.test("GEMINI_API_KEY set", True)
            print(f"  Key: {masked_key}")
        else:
            self.warn("GEMINI_API_KEY not set",
                     "Set with: export GEMINI_API_KEY=your_key_here")
    
    def test_directories(self):
        """Test project directories"""
        print("\nTesting Directories...")
        
        # Check main files exist
        files_to_check = [
            'main.py',
            'step1_audio_analysis.py',
            'step2_image_generation.py',
            'step3_video_creation.py',
            'requirements.txt',
            'README.md',
        ]
        
        for file in files_to_check:
            exists = Path(file).exists()
            self.test(f"File: {file}", exists)
        
        # Check utils directory
        utils_dir = Path('utils')
        self.test("utils/ directory", utils_dir.exists())
        
        # Check utils files
        utils_files = ['__init__.py', 'logger.py', 'config.py']
        for file in utils_files:
            exists = (utils_dir / file).exists()
            self.test(f"File: utils/{file}", exists)
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Warnings: {self.warnings}")
        print(f"Total: {total}")
        
        if self.failed == 0:
            print("\n✓ All tests passed! Ready to use.")
            print("\nNext steps:")
            print("1. Set API key: export GEMINI_API_KEY=your_key_here")
            print("2. Run: python main.py --audio story.mp3 --project my_story")
        else:
            print(f"\n✗ {self.failed} test(s) failed. Please fix the issues above.")
            print("\nFor help, see INSTALLATION.md")
        
        print("="*60 + "\n")
        
        return self.failed == 0


def main():
    """Main entry point"""
    tester = SetupTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

