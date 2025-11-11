"""
servo_config.py
Mengelola konfigurasi servo dan poses
"""

import json
import os
from typing import Dict, Any, Optional, List

class ServoConfig:
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = config_dir
        self.servo_mapping: Dict[str, Any] = {}
        self.poses: Dict[str, Any] = {}
        self.serial_config: Dict[str, Any] = {}
        
        self.load_configs()
    
    def load_configs(self):
        """Load semua file konfigurasi"""
        try:
            # Load servo mapping
            mapping_path = os.path.join(self.config_dir, "servo_mapping.json")
            with open(mapping_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.servo_mapping = data.get('servo_mapping', {})
            
            # Load poses
            poses_path = os.path.join(self.config_dir, "poses.json")
            with open(poses_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.poses = data.get('poses', {})
            
            # Load serial config
            serial_path = os.path.join(self.config_dir, "serial_config.json")
            with open(serial_path, 'r', encoding='utf-8') as f:
                self.serial_config = json.load(f)
            
            print("✓ Konfigurasi berhasil dimuat")
            
        except Exception as e:
            print(f"✗ Error loading config: {e}")
            raise
    
    def get_servo_info(self, part_path: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan info servo dari part path
        
        Args:
            part_path: Path ke servo, contoh: "head.pan" atau "right_arm.elbow"
        
        Returns:
            Dict dengan info servo (controller, channel, center, min, max)
        """
        parts = part_path.split('.')
        
        if len(parts) != 2:
            print(f"✗ Invalid part path: {part_path}")
            return None
        
        category, servo = parts
        
        if category not in self.servo_mapping:
            print(f"✗ Category not found: {category}")
            return None
        
        if servo not in self.servo_mapping[category]:
            print(f"✗ Servo not found: {servo} in {category}")
            return None
        
        return self.servo_mapping[category][servo]
    
    def get_pose(self, pose_name: str) -> Optional[Dict[str, Any]]:
        """Mendapatkan pose dari nama"""
        return self.poses.get(pose_name)
    
    def list_poses(self) -> List[str]:
        """List semua pose yang tersedia"""
        return list(self.poses.keys())
    
    def get_serial_config(self, controller: str) -> Optional[Dict[str, Any]]:
        """Mendapatkan konfigurasi serial untuk controller"""
        return self.serial_config.get(controller)
    
    def validate_position(self, part_path: str, position: int) -> bool:
        """Validasi apakah position dalam range yang aman"""
        servo_info = self.get_servo_info(part_path)
        
        if not servo_info:
            return False
        
        min_pos = servo_info.get('min', 500)
        max_pos = servo_info.get('max', 2500)
        
        if position < min_pos or position > max_pos:
            print(f"✗ Position {position} di luar range {min_pos}-{max_pos} untuk {part_path}")
            return False
        
        return True
    
    def save_pose(self, pose_name: str, pose_data: Dict[str, Any]):
        """Menyimpan pose baru ke file"""
        self.poses[pose_name] = pose_data
        
        poses_path = os.path.join(self.config_dir, "poses.json")
        
        try:
            with open(poses_path, 'w', encoding='utf-8') as f:
                json.dump({"poses": self.poses}, f, indent=2, ensure_ascii=False)
            print(f"✓ Pose '{pose_name}' berhasil disimpan")
        except Exception as e:
            print(f"✗ Error saving pose: {e}")


# Contoh penggunaan
if __name__ == "__main__":
    config = ServoConfig()
    
    print("\n=== Testing ServoConfig ===")
    
    # Test get servo info
    print("\n1. Info servo 'head.pan':")
    info = config.get_servo_info("head.pan")
    print(info)
    
    # Test get pose
    print("\n2. Info pose 'greeting':")
    pose = config.get_pose("greeting")
    print(f"Name: {pose['name']}")
    print(f"Description: {pose['description']}")
    print(f"Servos: {len(pose['servos'])} servo movements")
    
    # Test list poses
    print("\n3. Daftar poses tersedia:")
    for pose_name in config.list_poses():
        print(f"  - {pose_name}")
    
    # Test validate position
    print("\n4. Validasi position:")
    print(f"head.pan @ 1500: {config.validate_position('head.pan', 1500)}")
    print(f"head.pan @ 3000: {config.validate_position('head.pan', 3000)}")