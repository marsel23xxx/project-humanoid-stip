"""
movements.py
Library gerakan-gerakan kompleks untuk robot humanoid
"""

import time
from typing import List, Dict, Optional
from python.serial_controller import HumanoidController

class RobotMovements:
    """Collection of complex movements for humanoid robot"""
    
    def __init__(self, controller: HumanoidController):
        self.robot = controller
    
    def nod_head(self, times: int = 2, speed: int = 600):
        """
        Mengangguk (nod head)
        
        Args:
            times: Berapa kali angguk
            speed: Kecepatan gerakan (ms)
        """
        print(f"▶ Nodding head {times} times...")
        
        for i in range(times):
            # Tilt down
            self.robot.move_part("head.tilt", 1300, time_ms=speed, delay_ms=100)
            time.sleep((speed + 100) / 1000)
            
            # Tilt up
            self.robot.move_part("head.tilt", 1500, time_ms=speed, delay_ms=100)
            time.sleep((speed + 100) / 1000)
        
        print("✓ Nod complete")
    
    def shake_head(self, times: int = 2, speed: int = 600):
        """
        Menggeleng (shake head)
        
        Args:
            times: Berapa kali geleng
            speed: Kecepatan gerakan (ms)
        """
        print(f"▶ Shaking head {times} times...")
        
        for i in range(times):
            # Pan left
            self.robot.move_part("head.pan", 1800, time_ms=speed, delay_ms=100)
            time.sleep((speed + 100) / 1000)
            
            # Pan right
            self.robot.move_part("head.pan", 1200, time_ms=speed, delay_ms=100)
            time.sleep((speed + 100) / 1000)
        
        # Center
        self.robot.move_part("head.pan", 1500, time_ms=speed, delay_ms=100)
        print("✓ Shake complete")
    
    def wave_hand(self, hand: str = "right", times: int = 3, speed: int = 400):
        """
        Melambaikan tangan
        
        Args:
            hand: "right" atau "left"
            times: Berapa kali lambaian
            speed: Kecepatan gerakan
        """
        print(f"▶ Waving {hand} hand {times} times...")
        
        # Angkat tangan dulu
        if hand == "right":
            commands = [
                {'part': 'right_arm.shoulder_pitch', 'position': 800, 'time': 1000},
                {'part': 'right_arm.shoulder_roll', 'position': 1800, 'time': 1000},
                {'part': 'right_arm.elbow', 'position': 1200, 'time': 1000},
            ]
            wrist_part = "right_arm.wrist_roll"
        else:
            commands = [
                {'part': 'left_arm.shoulder_pitch', 'position': 800, 'time': 1000},
                {'part': 'left_arm.shoulder_roll', 'position': 1200, 'time': 1000},
                {'part': 'left_arm.elbow', 'position': 1800, 'time': 1000},
            ]
            wrist_part = "left_arm.wrist_roll"
        
        # Angkat tangan
        for cmd in commands:
            self.robot.move_part(cmd['part'], cmd['position'], 
                               time_ms=cmd['time'], delay_ms=100)
        
        time.sleep(1.2)
        
        # Lambaikan
        for i in range(times):
            self.robot.move_part(wrist_part, 1200, time_ms=speed, delay_ms=50)
            time.sleep((speed + 50) / 1000)
            
            self.robot.move_part(wrist_part, 1800, time_ms=speed, delay_ms=50)
            time.sleep((speed + 50) / 1000)
        
        # Center wrist
        self.robot.move_part(wrist_part, 1500, time_ms=speed, delay_ms=100)
        
        print("✓ Wave complete")
    
    def look_at_direction(self, direction: str, duration: float = 2.0):
        """
        Melihat ke arah tertentu
        
        Args:
            direction: "left", "right", "up", "down", "center"
            duration: Berapa lama melihat (detik)
        """
        print(f"▶ Looking {direction}...")
        
        positions = {
            'left': {'pan': 1800, 'tilt': 1500},
            'right': {'pan': 1200, 'tilt': 1500},
            'up': {'pan': 1500, 'tilt': 1700},
            'down': {'pan': 1500, 'tilt': 1300},
            'center': {'pan': 1500, 'tilt': 1500}
        }
        
        if direction not in positions:
            print(f"✗ Invalid direction: {direction}")
            return
        
        pos = positions[direction]
        
        # Move head
        self.robot.move_part("head.pan", pos['pan'], time_ms=800, delay_ms=100)
        self.robot.move_part("head.tilt", pos['tilt'], time_ms=800, delay_ms=100)
        
        # Hold position
        time.sleep(duration)
        
        # Return to center
        if direction != 'center':
            self.robot.move_part("head.pan", 1500, time_ms=800, delay_ms=100)
            self.robot.move_part("head.tilt", 1500, time_ms=800, delay_ms=100)
        
        print("✓ Look complete")
    
    def point_at(self, direction: str):
        """
        Menunjuk ke arah tertentu
        
        Args:
            direction: "left", "right", "forward", "up", "down"
        """
        print(f"▶ Pointing {direction}...")
        
        if direction == "right":
            self.robot.execute_pose("pointing_right")
        elif direction == "left":
            self.robot.execute_pose("pointing_left")
        elif direction == "forward":
            commands = [
                {'part': 'right_arm.shoulder_pitch', 'position': 1500, 'time': 1000},
                {'part': 'right_arm.shoulder_roll', 'position': 1800, 'time': 1000},
                {'part': 'right_arm.elbow', 'position': 1900, 'time': 1000},
            ]
            for cmd in commands:
                self.robot.move_part(cmd['part'], cmd['position'], 
                                   time_ms=cmd['time'], delay_ms=100)
        elif direction == "up":
            commands = [
                {'part': 'right_arm.shoulder_pitch', 'position': 600, 'time': 1000},
                {'part': 'right_arm.shoulder_roll', 'position': 1500, 'time': 1000},
                {'part': 'right_arm.elbow', 'position': 1900, 'time': 1000},
            ]
            for cmd in commands:
                self.robot.move_part(cmd['part'], cmd['position'], 
                                   time_ms=cmd['time'], delay_ms=100)
        
        time.sleep(2)
        print("✓ Point complete")
    
    def cross_arms(self):
        """Menyilangkan tangan di dada"""
        print("▶ Crossing arms...")
        
        commands = [
            {'part': 'right_arm.shoulder_pitch', 'position': 1200, 'time': 1200},
            {'part': 'right_arm.shoulder_roll', 'position': 1200, 'time': 1200},
            {'part': 'right_arm.elbow', 'position': 1000, 'time': 1200},
            {'part': 'left_arm.shoulder_pitch', 'position': 1200, 'time': 1200},
            {'part': 'left_arm.shoulder_roll', 'position': 1800, 'time': 1200},
            {'part': 'left_arm.elbow', 'position': 2000, 'time': 1200},
        ]
        
        for cmd in commands:
            self.robot.move_part(cmd['part'], cmd['position'], 
                               time_ms=cmd['time'], delay_ms=100)
        
        time.sleep(1.5)
        print("✓ Arms crossed")
    
    def thinking_gesture(self, duration: float = 3.0):
        """Pose berpikir dengan gerakan"""
        print("▶ Thinking gesture...")
        
        # Execute thinking pose
        self.robot.execute_pose("thinking")
        
        # Small head movements while thinking
        time.sleep(0.5)
        for _ in range(2):
            self.robot.move_part("head.tilt", 1250, time_ms=800, delay_ms=100)
            time.sleep(0.9)
            self.robot.move_part("head.tilt", 1350, time_ms=800, delay_ms=100)
            time.sleep(0.9)
        
        # Back to neutral
        self.robot.move_part("head.tilt", 1500, time_ms=800, delay_ms=100)
        
        print("✓ Thinking complete")
    
    def celebrate(self):
        """Gerakan merayakan/celebrate"""
        print("▶ Celebrating!")
        
        # Raise both arms
        commands = [
            {'part': 'right_arm.shoulder_pitch', 'position': 600, 'time': 800},
            {'part': 'right_arm.shoulder_roll', 'position': 2000, 'time': 800},
            {'part': 'left_arm.shoulder_pitch', 'position': 600, 'time': 800},
            {'part': 'left_arm.shoulder_roll', 'position': 1000, 'time': 800},
            {'part': 'head.tilt', 'position': 1600, 'time': 800},
        ]
        
        for cmd in commands:
            self.robot.move_part(cmd['part'], cmd['position'], 
                               time_ms=cmd['time'], delay_ms=50)
        
        time.sleep(1)
        
        # Wave arms
        for _ in range(2):
            self.robot.move_part("right_arm.shoulder_roll", 2200, time_ms=400, delay_ms=50)
            self.robot.move_part("left_arm.shoulder_roll", 800, time_ms=400, delay_ms=50)
            time.sleep(0.5)
            
            self.robot.move_part("right_arm.shoulder_roll", 1800, time_ms=400, delay_ms=50)
            self.robot.move_part("left_arm.shoulder_roll", 1200, time_ms=400, delay_ms=50)
            time.sleep(0.5)
        
        print("✓ Celebration complete!")


# Test program
if __name__ == "__main__":
    print("=== Testing Robot Movements ===\n")
    
    try:
        # Buat controller
        robot = HumanoidController()
        movements = RobotMovements(robot)
        
        print("\n1. Go to home position:")
        robot.go_home()
        time.sleep(2)
        
        print("\n2. Test nod head:")
        movements.nod_head(times=2)
        time.sleep(1)
        
        print("\n3. Test shake head:")
        movements.shake_head(times=2)
        time.sleep(1)
        
        print("\n4. Test wave hand:")
        movements.wave_hand(hand="right", times=3)
        time.sleep(1)
        
        print("\n5. Test look around:")
        directions = ['left', 'right', 'center']
        for direction in directions:
            movements.look_at_direction(direction, duration=1.0)
            time.sleep(0.5)
        
        print("\n6. Test point right:")
        movements.point_at("right")
        time.sleep(1)
        
        print("\n7. Back to home:")
        robot.go_home()
        
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan")
    
    finally:
        robot.close()
        print("Selesai!")