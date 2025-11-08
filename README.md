# Humanoid Robot Control System

## 🤖 Deskripsi Project

Sistem kontrol robot humanoid dengan 45 servo menggunakan:

- 2x Servo Controller (24 servo + 21 servo)
- 2x Arduino ATX2 (bridge ke masing-masing controller)
- Python untuk serial communication
- Ollama untuk Text-to-Speech AI

## 📁 Struktur Folder

```
humanoid_project/
├── arduino/                    # Kode Arduino untuk kedua ATX2
│   ├── controller_A/          # Arduino untuk Servo Controller A (24 servo)
│   │   └── controller_A.ino
│   └── controller_B/          # Arduino untuk Servo Controller B (21 servo)
│       └── controller_B.ino
│
├── python/                    # Program Python
│   ├── main.py               # Program utama
│   ├── serial_controller.py  # Komunikasi serial ke Arduino
│   ├── servo_config.py       # Konfigurasi servo dan poses
│   ├── tts_ollama.py         # Text-to-Speech dengan Ollama
│   └── movements.py          # Library gerakan robot
│
├── config/                    # File konfigurasi
│   ├── servo_mapping.json    # Mapping servo ke body parts
│   ├── poses.json            # Pose-pose tersimpan
│   └── serial_config.json    # Konfigurasi port serial
│
├── data/                      # Data tambahan
│   └── movements/            # JSON file untuk gerakan kompleks
│
├── requirements.txt          # Dependencies Python
└── README.md                 # File ini
```

## 🔌 Wiring Setup

### Arduino ATX2 A → Servo Controller A (24 servo)

- Arduino TX1 → Servo Controller RX
- Arduino RX1 ← Servo Controller TX
- GND ↔ GND
- 5V ↔ 5V (logic only)

### Arduino ATX2 B → Servo Controller B (21 servo)

- Arduino TX1 → Servo Controller RX
- Arduino RX1 ← Servo Controller TX
- GND ↔ GND
- 5V ↔ 5V (logic only)

### PC → Arduino (USB)

- Arduino ATX2 A: COM port pertama (cek di Device Manager)
- Arduino ATX2 B: COM port kedua (cek di Device Manager)

## 🚀 Cara Menggunakan

### 1. Upload Arduino Code

```bash
# Upload controller_A.ino ke Arduino ATX2 A
# Upload controller_B.ino ke Arduino ATX2 B
```

### 2. Install Python Dependencies

```bash
cd humanoid_project
pip install -r requirements.txt
```

### 3. Setup Ollama

```bash
# Install Ollama dari https://ollama.ai
ollama pull llama2  # atau model lain yang Anda inginkan
```

### 4. Konfigurasi Serial Ports

Edit `config/serial_config.json` sesuai COM port Arduino Anda

### 5. Jalankan Program

```bash
cd python
python main.py
```

## 📝 Cara Kerja

1. **Python mengirim command** → Arduino via USB Serial (115200 baud)
2. **Arduino menerima** → Forward ke Servo Controller via Serial1 (9600 baud)
3. **Format command**: `#<channel>P<position>T<time>D<delay>`
   - channel: 1-24 (Controller A), 1-21 (Controller B)
   - position: 500-2500 (pulsa width dalam microseconds)
   - time: durasi gerakan (ms)
   - delay: delay setelah gerakan (ms)

## 🎮 Contoh Penggunaan

```python
# Contoh di Python
from serial_controller import HumanoidController

robot = HumanoidController()

# Gerakkan servo 1 (head pan) ke tengah
robot.move_servo('A', 1, 1500, 800, 300)

# Gerakkan servo 5 (right shoulder) dan 6 (right elbow)
robot.move_multiple([
    {'controller': 'A', 'channel': 5, 'position': 2000, 'time': 1000},
    {'controller': 'A', 'channel': 6, 'position': 1800, 'time': 1000}
])

# Panggil pose tersimpan
robot.execute_pose('wave_hand')

# Text-to-Speech + Gerakan
robot.speak_and_move("Halo, nama saya Robot Humanoid!", 'greeting')
```

## 🎯 Fitur

- ✅ Kontrol 45 servo secara bersamaan
- ✅ Pose management (simpan & load poses)
- ✅ Gerakan kompleks (sequence movements)
- ✅ Text-to-Speech dengan Ollama
- ✅ Sinkronisasi gerakan dengan speech
- ✅ Error handling & timeout protection

## 🔧 Troubleshooting

### Arduino tidak terdeteksi

- Cek Device Manager untuk COM port
- Install driver CH340 jika diperlukan
- Pastikan kabel USB berfungsi

### Servo tidak bergerak

- Cek power supply servo (5-7.4V, cukup ampere)
- Cek wiring TX/RX Arduino ke Controller
- Cek channel number (1-24 atau 1-21)

### Ollama error

- Pastikan Ollama service running: `ollama serve`
- Cek model sudah di-pull: `ollama list`

## 📚 Resources

- [ATX2 Documentation](https://www.atxrobotics.com)
- [Ollama Documentation](https://ollama.ai/docs)
