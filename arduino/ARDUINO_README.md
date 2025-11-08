# Arduino Code untuk Humanoid Robot

## 📁 File Arduino

Ada 2 file Arduino code:

1. **controller_A.ino** - Upload ke Arduino ATX2 A (24 servo - Upper Body)
2. **controller_B.ino** - Upload ke Arduino ATX2 B (21 servo - Lower Body)

---

## 🔌 Wiring

### Arduino ATX2 A → Servo Controller A

```
Arduino TX1  →  Servo Controller RX
Arduino RX1  ←  Servo Controller TX
Arduino GND  ↔  Servo Controller GND
Arduino 5V   ↔  Servo Controller 5V (logic only, NOT servo power!)
```

### Arduino ATX2 B → Servo Controller B

```
Arduino TX1  →  Servo Controller RX
Arduino RX1  ←  Servo Controller TX
Arduino GND  ↔  Servo Controller GND
Arduino 5V   ↔  Servo Controller 5V (logic only, NOT servo power!)
```

⚠️ **PENTING:**

- Pin 5V hanya untuk logic level, BUKAN untuk power servo!
- Gunakan power supply external 5-7.4V (min 5A) untuk servo
- WAJIB share ground antara Arduino dan Servo Controller

---

## 📤 Cara Upload

### Step 1: Install Arduino IDE

Download dari: https://www.arduino.cc/en/software

### Step 2: Install Library ATX2

1. Buka Arduino IDE
2. Sketch → Include Library → Manage Libraries
3. Search "ATX2"
4. Install library ATX2

### Step 3: Upload Controller A

1. Buka file **controller_A.ino**
2. Tools → Board → Pilih board Arduino Anda
3. Tools → Port → Pilih COM port Arduino A (misal COM3)
4. Klik tombol Upload (→)
5. Tunggu sampai "Done uploading"
6. Buka Serial Monitor (Ctrl+Shift+M)
7. Set baudrate ke **115200**
8. Harus muncul:
   ```
   =================================
   Arduino ATX2 Controller A
   Servo Controller: 24 servos
   Upper body control
   =================================
   Ready to receive commands...
   ```

### Step 4: Upload Controller B

1. Buka file **controller_B.ino**
2. Tools → Board → Pilih board Arduino Anda
3. Tools → Port → Pilih COM port Arduino B (misal COM4)
4. Klik tombol Upload (→)
5. Tunggu sampai "Done uploading"
6. Buka Serial Monitor
7. Set baudrate ke **115200**
8. Harus muncul:
   ```
   =================================
   Arduino ATX2 Controller B
   Servo Controller: 21 servos
   Lower body control
   =================================
   Ready to receive commands...
   ```

### Step 5: Catat COM Ports

**PENTING!** Catat COM port untuk masing-masing Arduino:

- Arduino A: COM\_\_\_ (misal COM3)
- Arduino B: COM\_\_\_ (misal COM4)

Nanti COM port ini akan digunakan di `config/serial_config.json`

---

## 🧪 Test Arduino

### Test Manual via Serial Monitor

#### Test Controller A:

1. Buka Serial Monitor untuk Arduino A
2. Set baudrate ke 115200
3. Ketik command: `#1P1500T800D300`
4. Tekan Enter
5. Servo channel 1 harus bergerak ke posisi 1500

#### Test Controller B:

1. Buka Serial Monitor untuk Arduino B
2. Set baudrate ke 115200
3. Ketik command: `#1P1500T800D300`
4. Tekan Enter
5. Servo channel 1 harus bergerak ke posisi 1500

---

## 📝 Command Format

```
#<channel>P<position>T<time>D<delay>

<channel>  : 1-24 (Controller A) atau 1-21 (Controller B)
<position> : 500-2500 (pulse width dalam microseconds)
<time>     : 0-65535 (durasi gerakan dalam milliseconds)
<delay>    : 0-65535 (delay setelah gerakan dalam milliseconds)
```

### Contoh Commands:

```
#1P1500T800D300    - Servo 1 ke center (1500), 800ms, delay 300ms
#5P2000T1000D0     - Servo 5 ke 2000, 1 detik, no delay
#12P700T500D200    - Servo 12 ke 700, 500ms, delay 200ms
```

---

## 🔍 Perbedaan Controller A dan B

### Controller A (controller_A.ino):

- MAX_SERVOS: **24**
- Prefix debug: **[A]**
- Deskripsi: "Upper body control"
- Untuk: Head, Arms, Torso

### Controller B (controller_B.ino):

- MAX_SERVOS: **21**
- Prefix debug: **[B]**
- Deskripsi: "Lower body control"
- Untuk: Legs, Hips

---

## 🐛 Troubleshooting

### Upload Error

**Problem:** "avrdude: stk500_recv(): programmer is not responding"

**Solution:**

1. Pastikan Arduino terhubung dengan benar
2. Pilih COM port yang tepat
3. Pilih board yang tepat
4. Coba kabel USB lain
5. Restart Arduino IDE

### Serial Monitor Kosong

**Problem:** Serial Monitor tidak menampilkan apa-apa

**Solution:**

1. Cek baudrate = 115200
2. Pilih "Newline" di dropdown
3. Reset Arduino (tekan tombol reset)
4. Pastikan code sudah di-upload

### Command Tidak Bekerja

**Problem:** Ketik command tapi servo tidak bergerak

**Solution:**

1. Cek wiring TX/RX Arduino ke Controller
2. Cek ground ter-share
3. Cek power supply servo (min 5A)
4. Lihat response di Serial Monitor
5. Coba command simple: `#1P1500T800D300`

### "ERROR: Channel out of range"

**Problem:** Command ditolak dengan error channel

**Solution:**

- Controller A: gunakan channel 1-24
- Controller B: gunakan channel 1-21
- Jangan gunakan channel > MAX_SERVOS

### "ERROR: Position must be 500-2500"

**Problem:** Position di luar range

**Solution:**

- Gunakan position antara 500-2500
- 500 = full left/down
- 1500 = center
- 2500 = full right/up

---

## 📊 Serial Communication

### Arduino → PC (USB Serial)

- Baudrate: **115200**
- Protocol: ASCII text
- Terminator: CR/LF
- Port: COM3/COM4 (Windows) atau /dev/ttyUSB0 (Linux)

### Arduino → Servo Controller (Serial1)

- Baudrate: **9600**
- Protocol: ASCII text
- Terminator: LF ('\n')
- Pins: TX1, RX1

---

## 💡 Tips

### Tip 1: Test Satu-satu

Test satu servo dulu sebelum test semua:

```
#1P1500T1000D300
```

### Tip 2: Gunakan Center Position

Mulai dengan center position (1500) untuk safety:

```
#1P1500T1000D300
#2P1500T1000D300
```

### Tip 3: Monitor Serial

Selalu buka Serial Monitor untuk lihat debug messages:

- `[A] TX: #1P1500T800D300` - Command dikirim
- `[A] OK received` - Controller respond OK
- `[A] DONE` - Command selesai

### Tip 4: Slow Movement

Gunakan time yang lebih lama untuk gerakan smooth:

```
#1P1800T2000D300   // 2 detik = smooth
#1P1800T300D300    // 300ms = jerky
```

---

## 🔐 Safety Features

Code Arduino sudah include safety features:

1. **Channel Validation** - Reject channel di luar range
2. **Position Validation** - Reject position < 500 atau > 2500
3. **Timeout Protection** - Timeout jika tidak ada OK response
4. **Command Parsing** - Validasi format command
5. **Buffer Overflow Protection** - Limit input buffer 128 chars

---

## 📚 Next Steps

Setelah upload Arduino code:

1. ✅ Test manual via Serial Monitor
2. ✅ Catat COM ports
3. ✅ Edit `config/serial_config.json`
4. ✅ Install Python dependencies
5. ✅ Run Python program: `python main.py`

---
