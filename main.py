"""
main.py
Program utama untuk mengontrol robot humanoid
Integrasi: Serial Control + Ollama TTS + Movements
"""

import time
import sys
from serial_controller import HumanoidController
from tts_ollama import RobotSpeaker
from movements import RobotMovements

class HumanoidRobot:
    """Main class untuk robot humanoid dengan speech dan movement"""
    
    def __init__(self, ollama_model: str = "llama2"):
        print("=" * 50)
        print("🤖 HUMANOID ROBOT CONTROL SYSTEM")
        print("=" * 50)
        
        # Initialize components
        print("\n📡 Menghubungkan ke Arduino...")
        self.controller = HumanoidController()
        
        print("\n🎤 Menginisialisasi Speech System...")
        self.speaker = RobotSpeaker(model=ollama_model)
        
        print("\n🦾 Menginisialisasi Movement Library...")
        self.movements = RobotMovements(self.controller)
        
        print("\n✓ Sistem siap!\n")
    
    def speak_and_move(self, text: str, pose_name: Optional[str] = None,
                       auto_emotion: bool = True):
        """
        Berbicara dan bergerak secara bersamaan
        
        Args:
            text: Text yang akan diucapkan
            pose_name: Nama pose spesifik (None = auto detect dari emotion)
            auto_emotion: Otomatis detect emotion
        """
        print(f"\n💬 Robot akan berbicara: '{text}'")
        
        # Detect emotion dan dapatkan suggested pose
        if auto_emotion and not pose_name:
            _, suggested_pose = self.speaker.speak_with_emotion(text, auto_detect_emotion=True)
        else:
            self.speaker.tts.speak(text, use_system_tts=True)
            suggested_pose = pose_name if pose_name else 'attention'
        
        # Execute pose
        if suggested_pose:
            print(f"🦾 Executing pose: {suggested_pose}")
            time.sleep(0.5)  # Small delay before movement
            self.controller.execute_pose(suggested_pose)
    
    def interactive_mode(self):
        """Mode interaktif - user input text, robot respond"""
        print("\n" + "=" * 50)
        print("🎮 MODE INTERAKTIF")
        print("=" * 50)
        print("\nKetik text untuk robot speak + gerakan")
        print("Ketik 'quit' untuk keluar")
        print("Ketik 'commands' untuk melihat command khusus\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print("\n👋 Sampai jumpa!")
                    break
                
                if user_input.lower() == 'commands':
                    self.show_commands()
                    continue
                
                # Check untuk command khusus
                if self.handle_special_command(user_input):
                    continue
                
                # Normal speech + movement
                self.speak_and_move(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Program dihentikan")
                break
    
    def show_commands(self):
        """Tampilkan command khusus"""
        print("\n" + "=" * 50)
        print("📋 COMMAND KHUSUS:")
        print("=" * 50)
        print("\nGerakan:")
        print("  /nod          - Angguk")
        print("  /shake        - Geleng kepala")
        print("  /wave         - Lambaikan tangan")
        print("  /point_left   - Tunjuk kiri")
        print("  /point_right  - Tunjuk kanan")
        print("  /think        - Pose berpikir")
        print("  /celebrate    - Pose merayakan")
        print("  /home         - Kembali ke home position")
        print("\nPoses:")
        print("  /pose <name>  - Execute pose tertentu")
        print("  /list_poses   - Tampilkan semua poses")
        print("\nOther:")
        print("  commands      - Tampilkan menu ini")
        print("  quit          - Keluar dari program")
        print()
    
    def handle_special_command(self, command: str) -> bool:
        """
        Handle command khusus
        
        Returns:
            True jika command dihandle, False jika bukan special command
        """
        command = command.lower().strip()
        
        # Movement commands
        if command == '/nod':
            self.movements.nod_head(times=2)
            return True
        
        elif command == '/shake':
            self.movements.shake_head(times=2)
            return True
        
        elif command == '/wave':
            self.movements.wave_hand(hand="right", times=3)
            return True
        
        elif command == '/point_left':
            self.movements.point_at("left")
            return True
        
        elif command == '/point_right':
            self.movements.point_at("right")
            return True
        
        elif command == '/think':
            self.movements.thinking_gesture()
            return True
        
        elif command == '/celebrate':
            self.movements.celebrate()
            return True
        
        elif command == '/home':
            self.controller.go_home()
            return True
        
        # Pose commands
        elif command.startswith('/pose '):
            pose_name = command.split(' ', 1)[1].strip()
            success = self.controller.execute_pose(pose_name)
            if not success:
                print(f"✗ Pose '{pose_name}' tidak ditemukan")
            return True
        
        elif command == '/list_poses':
            poses = self.controller.config.list_poses()
            print("\n📋 Available Poses:")
            for pose_name in poses:
                pose_data = self.controller.config.get_pose(pose_name)
                print(f"  - {pose_name}: {pose_data['description']}")
            print()
            return True
        
        return False
    
    def demo_mode(self):
        """Mode demo - showcase berbagai kemampuan robot"""
        print("\n" + "=" * 50)
        print("🎬 MODE DEMO")
        print("=" * 50)
        
        demos = [
            {
                'name': 'Perkenalan',
                'speech': 'Halo! Nama saya Robot Humanoid. Senang bertemu dengan Anda!',
                'pose': 'greeting'
            },
            {
                'name': 'Angguk',
                'speech': 'Saya mengerti apa yang Anda maksud.',
                'action': lambda: self.movements.nod_head(times=2)
            },
            {
                'name': 'Lambaikan tangan',
                'speech': 'Sampai jumpa! Semoga hari Anda menyenangkan!',
                'action': lambda: self.movements.wave_hand(times=3)
            },
            {
                'name': 'Berpikir',
                'speech': 'Hmm, saya perlu memikirkan ini sebentar...',
                'action': lambda: self.movements.thinking_gesture()
            },
            {
                'name': 'Menunjuk',
                'speech': 'Lihat! Ada sesuatu yang menarik di sana!',
                'action': lambda: self.movements.point_at("right")
            },
            {
                'name': 'Merayakan',
                'speech': 'Horee! Kita berhasil!',
                'action': lambda: self.movements.celebrate()
            }
        ]
        
        for i, demo in enumerate(demos, 1):
            print(f"\n{i}. {demo['name']}")
            print("-" * 40)
            
            # Speak
            self.speaker.tts.speak(demo['speech'], use_system_tts=True)
            time.sleep(0.5)
            
            # Movement
            if 'pose' in demo:
                self.controller.execute_pose(demo['pose'])
            elif 'action' in demo:
                demo['action']()
            
            # Pause between demos
            if i < len(demos):
                time.sleep(2)
                print("\nKembali ke home position...")
                self.controller.go_home()
                time.sleep(2)
        
        print("\n✓ Demo selesai!")
    
    def test_mode(self):
        """Mode test - test semua fungsi dasar"""
        print("\n" + "=" * 50)
        print("🔧 MODE TEST")
        print("=" * 50)
        
        tests = [
            ("Home Position", lambda: self.controller.go_home()),
            ("Head Movement", lambda: self.movements.look_at_direction("left", 1)),
            ("Wave Hand", lambda: self.movements.wave_hand(times=1)),
            ("Simple Speech", lambda: self.speaker.tts.speak("Test speech", True)),
        ]
        
        for i, (test_name, test_func) in enumerate(tests, 1):
            print(f"\n[{i}/{len(tests)}] Testing: {test_name}")
            try:
                test_func()
                print(f"✓ {test_name} OK")
            except Exception as e:
                print(f"✗ {test_name} FAILED: {e}")
            time.sleep(1)
        
        print("\n✓ Testing complete!")
    
    def cleanup(self):
        """Cleanup - tutup semua koneksi"""
        print("\n🔄 Cleaning up...")
        self.controller.go_home()
        time.sleep(1)
        self.controller.close()
        print("✓ Cleanup complete")


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("       🤖 HUMANOID ROBOT CONTROL SYSTEM 🤖")
    print("=" * 60)
    print("\nPilih mode:")
    print("  1. Interactive Mode  - Kontrol robot dengan input text")
    print("  2. Demo Mode         - Showcase kemampuan robot")
    print("  3. Test Mode         - Test fungsi dasar")
    print("  4. Quit              - Keluar")
    print()
    
    try:
        choice = input("Pilihan (1-4): ").strip()
        
        if choice == '4':
            print("\n👋 Sampai jumpa!")
            return
        
        # Initialize robot
        robot = HumanoidRobot(ollama_model="llama2")
        
        # Go to home position first
        print("\n🏠 Moving to home position...")
        robot.controller.go_home()
        time.sleep(2)
        
        # Execute selected mode
        if choice == '1':
            robot.interactive_mode()
        elif choice == '2':
            robot.demo_mode()
        elif choice == '3':
            robot.test_mode()
        else:
            print("\n✗ Pilihan tidak valid")
        
        # Cleanup
        robot.cleanup()
        
    except KeyboardInterrupt:
        print("\n\n⚠ Program dihentikan oleh user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 60)
        print("       Program selesai. Terima kasih!")
        print("=" * 60)


if __name__ == "__main__":
    main()