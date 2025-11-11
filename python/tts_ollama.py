"""
tts_ollama.py
Text-to-Speech dengan Ollama AI
"""

import requests
import json
import subprocess
import platform
from typing import Optional, Dict, Any

class OllamaTTS:
    def __init__(self, 
                 model: str = "llama2",
                 ollama_url: str = "http://localhost:11434"):
        """
        Initialize Ollama TTS
        
        Args:
            model: Model Ollama yang digunakan (default: llama2)
            ollama_url: URL Ollama API
        """
        self.model = model
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
        
        # Check Ollama availability
        if not self.check_ollama():
            print("⚠ Ollama tidak terdeteksi!")
            print("   Install dari: https://ollama.ai")
            print("   Atau jalankan: ollama serve")
    
    def check_ollama(self) -> bool:
        """Check apakah Ollama service berjalan"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate_speech_response(self, 
                                 text: str, 
                                 context: str = "",
                                 temperature: float = 0.7) -> Optional[str]:
        """
        Generate response dari Ollama untuk speech
        
        Args:
            text: Text yang ingin di-speak
            context: Context tambahan
            temperature: Creativity level (0.0 - 1.0)
        
        Returns:
            Generated text response
        """
        try:
            # Prompt untuk generate natural speech
            prompt = f"""You are a friendly humanoid robot speaking to a human.
            
Context: {context if context else "General conversation"}

Speak this in a natural, friendly way: "{text}"

Response (keep it natural and conversational):"""

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature
            }
            
            print(f"🤖 Generating speech with Ollama...")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                return generated_text
            else:
                print(f"✗ Ollama error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("✗ Ollama timeout")
            return None
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def speak(self, text: str, use_system_tts: bool = True) -> bool:
        """
        Speak text menggunakan system TTS
        
        Args:
            text: Text yang akan di-speak
            use_system_tts: Gunakan system TTS (Windows/Mac/Linux)
        
        Returns:
            True jika berhasil
        """
        if not text:
            return False
        
        print(f"💬 Speaking: {text}")
        
        if use_system_tts:
            return self._system_speak(text)
        
        return True
    
    def _system_speak(self, text: str) -> bool:
        """Gunakan system TTS untuk speak"""
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows PowerShell TTS
                command = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}")'
                subprocess.run(
                    ["powershell", "-Command", command],
                    check=True,
                    capture_output=True
                )
                return True
                
            elif system == "Darwin":  # macOS
                # macOS say command
                subprocess.run(
                    ["say", text],
                    check=True,
                    capture_output=True
                )
                return True
                
            elif system == "Linux":
                # Linux espeak
                subprocess.run(
                    ["espeak", text],
                    check=True,
                    capture_output=True
                )
                return True
            
            else:
                print(f"⚠ System TTS tidak didukung untuk {system}")
                return False
                
        except FileNotFoundError:
            print(f"✗ TTS tool tidak ditemukan di {system}")
            if system == "Linux":
                print("   Install dengan: sudo apt-get install espeak")
            return False
        except Exception as e:
            print(f"✗ Error TTS: {e}")
            return False
    
    def analyze_emotion(self, text: str) -> str:
        """
        Analisis emosi dari text menggunakan Ollama
        
        Returns:
            emotion: 'happy', 'sad', 'neutral', 'excited', 'thinking'
        """
        try:
            prompt = f"""Analyze the emotion in this text and respond with only ONE word: happy, sad, neutral, excited, or thinking.

Text: "{text}"

Emotion:"""

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                emotion = result.get('response', '').strip().lower()
                
                # Validasi emotion
                valid_emotions = ['happy', 'sad', 'neutral', 'excited', 'thinking']
                if any(e in emotion for e in valid_emotions):
                    for e in valid_emotions:
                        if e in emotion:
                            return e
                
                return 'neutral'
            
            return 'neutral'
            
        except Exception as e:
            print(f"⚠ Error analyzing emotion: {e}")
            return 'neutral'


class RobotSpeaker:
    """High-level interface untuk robot berbicara dengan gerakan"""
    
    def __init__(self, model: str = "llama2"):
        self.tts = OllamaTTS(model=model)
        self.emotion_to_pose = {
            'happy': 'greeting',
            'sad': 'thinking',
            'neutral': 'attention',
            'excited': 'wave_hand',
            'thinking': 'thinking'
        }
    
    def speak_with_emotion(self, text: str, 
                          auto_detect_emotion: bool = True) -> tuple[str, str]:
        """
        Speak dengan deteksi emosi otomatis
        
        Args:
            text: Text yang akan diucapkan
            auto_detect_emotion: Otomatis deteksi emosi
        
        Returns:
            (spoken_text, suggested_pose)
        """
        # Detect emotion
        if auto_detect_emotion:
            emotion = self.tts.analyze_emotion(text)
            print(f"🎭 Detected emotion: {emotion}")
        else:
            emotion = 'neutral'
        
        # Speak
        self.tts.speak(text, use_system_tts=True)
        
        # Get suggested pose
        suggested_pose = self.emotion_to_pose.get(emotion, 'attention')
        
        return (text, suggested_pose)
    
    def generate_and_speak(self, 
                          prompt: str, 
                          context: str = "") -> tuple[str, str]:
        """
        Generate response dengan Ollama dan speak
        
        Returns:
            (generated_text, suggested_pose)
        """
        # Generate dengan Ollama
        generated = self.tts.generate_speech_response(prompt, context)
        
        if not generated:
            generated = prompt  # Fallback ke original prompt
        
        # Speak dengan emotion detection
        return self.speak_with_emotion(generated)


# Test program
if __name__ == "__main__":
    print("=== Testing Ollama TTS ===\n")
    
    speaker = RobotSpeaker(model="llama2")
    
    # Test 1: Simple speak
    print("\n1. Test simple speak:")
    speaker.tts.speak("Halo, saya adalah robot humanoid!", use_system_tts=True)
    
    # Test 2: Emotion detection
    print("\n2. Test emotion detection:")
    test_texts = [
        "Selamat pagi! Senang bertemu dengan Anda!",
        "Saya sedang berpikir tentang masalah ini...",
        "Hari ini cuacanya bagus sekali!",
    ]
    
    for text in test_texts:
        text_spoken, pose = speaker.speak_with_emotion(text)
        print(f"   Text: {text}")
        print(f"   Pose: {pose}\n")
    
    # Test 3: Generate and speak
    print("\n3. Test generate and speak:")
    if speaker.tts.check_ollama():
        generated, pose = speaker.generate_and_speak(
            "Perkenalkan diri Anda sebagai robot humanoid",
            context="Meeting a new person"
        )
        print(f"   Generated: {generated}")
        print(f"   Suggested pose: {pose}")
    else:
        print("   Ollama tidak tersedia, skip test")
    
    print("\n✓ Test selesai!")