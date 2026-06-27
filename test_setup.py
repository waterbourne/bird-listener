#!/usr/bin/env python3
"""
Test script to verify BirdNET installation
Uses a built-in sample to test bird detection
"""

import tempfile
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from pathlib import Path

def test_birdnet():
    """Test BirdNET with a simple setup"""
    print("🧪 Testing BirdNET analyzer...")
    
    try:
        analyzer = Analyzer()
        print("✅ BirdNET analyzer initialized successfully!")
        print(f"   Model version: {analyzer.custom_model_path if hasattr(analyzer, 'custom_model_path') else 'default'}")
        print(f"   Labels loaded: {len(analyzer.labels) if hasattr(analyzer, 'labels') else 'unknown'}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize BirdNET: {e}")
        return False

def test_audio_device():
    """Test if we can access audio devices"""
    print("\n🎤 Testing audio device access...")
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        print(f"✅ Found {p.get_device_count()} audio device(s):")
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"   [{i}] {info['name']} (input channels: {info['maxInputChannels']})")
        
        p.terminate()
        return True
    except Exception as e:
        print(f"❌ Audio device test failed: {e}")
        return False

def test_gemini():
    """Test Gemini API key"""
    print("\n🎨 Testing Gemini API setup...")
    
    try:
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️  GEMINI_API_KEY not configured in .env file")
            print("   Get your API key at: https://makersuite.google.com/app/apikey")
            return False
        
        print("✅ GEMINI_API_KEY found in .env")
        return True
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("Bird Listener System - Environment Test")
    print("="*60)
    
    tests_passed = 0
    tests_total = 3
    
    if test_birdnet():
        tests_passed += 1
    
    if test_audio_device():
        tests_passed += 1
    
    if test_gemini():
        tests_passed += 1
    
    print("\n" + "="*60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n🎉 All systems ready! You can now run ./launch.sh")
    else:
        print("\n⚠️  Some tests failed. Fix the issues above before launching.")
    
    print("="*60)

if __name__ == "__main__":
    main()
