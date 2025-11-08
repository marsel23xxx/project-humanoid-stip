"""
serial_controller.py
Mengelola komunikasi serial dengan kedua Arduino ATX2
"""

import serial
import time
from typing import Dict, List, Optional, Tuple
from servo_config import ServoConfig

class SerialController:
    def __init__(self, config: ServoConfig):
        self.config = config
        self.connections: Dict[str, serial.Serial] = {}
        self.connect_all()
    
    def connect_all(self):
        """Koneksi ke semua Arduino"""
        print("\n=== Menghubungkan ke Arduino ===")
        
        for controller_name in ['controller_A', 'controller_B']:
            success = self.connect_controller(controller_name)
            if success:
                print(f"✓ {controller_name} terhubung")
            else:
                print(f"✗ {controller_name} gagal terhubung")
    
    def connect_controller(self, controller_name: str) -> bool:
        """Koneksi ke satu controller"""
        cfg = self.config.get_serial_config(controller_name)
        
        if not cfg:
            print(f"✗ Config untuk {controller_name} tidak ditemukan")
            return False
        
        try:
            port = cfg['port']
            baudrate = cfg['baudrate']
            timeout = cfg['timeout']
            
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout
            )
            
            time.sleep(2)  # Tunggu Arduino reset
            
            # Bersihkan buffer
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            self.connections[controller_name] = ser
            return True
            
        except serial.SerialException as e:
            print(f"✗ Error koneksi {controller_name}: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error {controller_name}: {e}")
            return False
    
    def send_command(self, controller: str, channel: int, position: int, 
                    time_ms: int = 800, delay_ms: int = 300) -> bool:
        """
        Mengirim command ke Arduino
        
        Args:
            controller: 'A' atau 'B'
            channel: Channel servo (1-24 untuk A, 1-21 untuk B)
            position: Position servo (500-2500)
            time_ms: Waktu gerakan dalam ms
            delay_ms: Delay setelah gerakan dalam ms
        
        Returns:
            True jika sukses, False jika gagal
        """
        controller_name = f"controller_{controller}"
        
        if controller_name not in self.connections:
            print(f"✗ Controller {controller} tidak terhubung")
            return False
        
        # Validasi channel
        max_servos = self.config.serial_config[controller_name]['max_servos']
        if channel < 1 or channel > max_servos:
            print(f"✗ Channel {channel} di luar range (1-{max_servos})")
            return False
        
        # Validasi position
        if position < 500 or position > 2500:
            print(f"✗ Position {position} di luar range (500-2500)")
            return False
        
        try:
            # Format command: #<ch>P<pos>T<time>D<delay>
            command = f"#{channel}P{position}T{time_ms}D{delay_ms}\n"
            
            # Kirim command
            ser = self.connections[controller_name]
            ser.write(command.encode('utf-8'))
            
            # Tunggu response
            start_time = time.time()
            timeout = (time_ms + delay_ms) / 1000 + 2  # +2 detik safety margin
            
            response = ""
            while time.time() - start_time < timeout:
                if ser.in_waiting > 0:
                    char = ser.read(1).decode('utf-8', errors='ignore')
                    response += char
                    
                    if "DONE" in response:
                        return True
                    elif "ERROR" in response:
                        print(f"✗ Arduino error: {response.strip()}")
                        return False
            
            print(f"⚠ Timeout menunggu response dari {controller}")
            return False
            
        except Exception as e:
            print(f"✗ Error mengirim command: {e}")
            return False
    
    def send_multiple(self, commands: List[Dict]) -> bool:
        """
        Mengirim multiple commands sekaligus
        
        Args:
            commands: List of dict dengan keys: controller, channel, position, time, delay
        
        Returns:
            True jika semua sukses
        """
        all_success = True
        
        for cmd in commands:
            controller = cmd.get('controller', 'A')
            channel = cmd.get('channel')
            position = cmd.get('position')
            time_ms = cmd.get('time', 800)
            delay_ms = cmd.get('delay', 300)
            
            success = self.send_command(controller, channel, position, time_ms, delay_ms)
            
            if not success:
                all_success = False
            
            # Small delay antara commands
            time.sleep(0.05)
        
        return all_success
    
    def move_servo_by_part(self, part_path: str, position: int, 
                          time_ms: int = 800, delay_ms: int = 300) -> bool:
        """
        Gerakkan servo berdasarkan part name (contoh: "head.pan")
        
        Args:
            part_path: Path ke servo part, contoh: "head.pan"
            position: Target position
            time_ms: Waktu gerakan
            delay_ms: Delay setelah gerakan
        
        Returns:
            True jika sukses
        """
        servo_info = self.config.get_servo_info(part_path)
        
        if not servo_info:
            print(f"✗ Servo part '{part_path}' tidak ditemukan")
            return False
        
        # Validasi position dengan range yang sudah ditentukan
        if not self.config.validate_position(part_path, position):
            return False
        
        controller = servo_info['controller']
        channel = servo_info['channel']
        
        return self.send_command(controller, channel, position, time_ms, delay_ms)
    
    def close_all(self):
        """Tutup semua koneksi serial"""
        for name, ser in self.connections.items():
            try:
                ser.close()
                print(f"✓ {name} ditutup")
            except:
                pass
        
        self.connections.clear()
    
    def __del__(self):
        """Destructor - tutup koneksi saat object dihapus"""
        self.close_all()


class HumanoidController:
    """High-level controller untuk robot humanoid"""
    
    def __init__(self):
        self.config = ServoConfig()
        self.serial = SerialController(self.config)
    
    def move_servo(self, controller: str, channel: int, position: int, 
                   time_ms: int = 800, delay_ms: int = 300):
        """Gerakkan servo langsung dengan channel"""
        return self.serial.send_command(controller, channel, position, time_ms, delay_ms)
    
    def move_part(self, part_path: str, position: int, 
                  time_ms: int = 800, delay_ms: int = 300):
        """Gerakkan servo berdasarkan nama part"""
        return self.serial.move_servo_by_part(part_path, position, time_ms, delay_ms)
    
    def move_multiple(self, commands: List[Dict]):
        """Gerakkan multiple servos"""
        return self.serial.send_multiple(commands)
    
    def execute_pose(self, pose_name: str) -> bool:
        """
        Execute pose yang sudah tersimpan
        
        Args:
            pose_name: Nama pose dari poses.json
        
        Returns:
            True jika sukses
        """
        pose = self.config.get_pose(pose_name)
        
        if not pose:
            print(f"✗ Pose '{pose_name}' tidak ditemukan")
            return False
        
        print(f"\n▶ Executing pose: {pose['name']}")
        print(f"   {pose['description']}")
        
        # Check apakah pose punya sequence
        if 'sequence' in pose:
            # Pose dengan sequence (multi-step)
            for step_idx, step in enumerate(pose['sequence']):
                print(f"   Step {step_idx + 1}/{len(pose['sequence'])}")
                
                # Convert servo movements ke format command
                commands = []
                for servo_move in step['servos']:
                    servo_info = self.config.get_servo_info(servo_move['part'])
                    if servo_info:
                        commands.append({
                            'controller': servo_info['controller'],
                            'channel': servo_info['channel'],
                            'position': servo_move['position'],
                            'time': servo_move.get('time', 800),
                            'delay': 0
                        })
                
                # Execute step
                self.serial.send_multiple(commands)
                
                # Delay antar step
                if 'delay' in step:
                    time.sleep(step['delay'] / 1000.0)
        
        else:
            # Pose sederhana (single-step)
            commands = []
            for servo_move in pose['servos']:
                servo_info = self.config.get_servo_info(servo_move['part'])
                if servo_info:
                    commands.append({
                        'controller': servo_info['controller'],
                        'channel': servo_info['channel'],
                        'position': servo_move['position'],
                        'time': servo_move.get('time', 800),
                        'delay': servo_move.get('delay', 300)
                    })
            
            self.serial.send_multiple(commands)
        
        print(f"✓ Pose '{pose_name}' selesai\n")
        return True
    
    def go_home(self):
        """Kembali ke home position"""
        return self.execute_pose('home')
    
    def close(self):
        """Tutup semua koneksi"""
        self.serial.close_all()


# Test program
if __name__ == "__main__":
    print("=== Testing Humanoid Controller ===\n")
    
    try:
        robot = HumanoidController()
        
        print("\n1. Test gerakan individual servo:")
        robot.move_part("head.pan", 1800, time_ms=1000)
        time.sleep(1)
        robot.move_part("head.pan", 1500, time_ms=1000)
        
        print("\n2. Test execute pose 'greeting':")
        robot.execute_pose("greeting")
        
        time.sleep(2)
        
        print("\n3. Kembali ke home position:")
        robot.go_home()
        
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh user")
    
    finally:
        print("\nMenutup koneksi...")
        robot.close()
        print("Selesai!")