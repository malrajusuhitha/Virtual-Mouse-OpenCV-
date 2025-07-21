# Virtual-Mouse-OpenCV
VMouSE-MSR
# 🖱️ Virtual Mouse using Python & OpenCV

This project is a **gesture-controlled virtual mouse** built with **Python, OpenCV, MediaPipe, and PyAutoGUI**.  
It uses hand-tracking to allow users to perform **mouse actions** such as cursor movement, left/right click, drag and drop, zoom, scroll, and area selection – all without touching a physical mouse.

---

## 🚀 Features
- **Cursor Movement** – Control your mouse pointer with hand gestures.
- **Left and Right Click** – Single and right-click gestures with specific finger poses.
- **Drag & Drop** – Use pinch gestures for smooth dragging.
- **Scroll Up & Down** – Scroll using two-finger gestures.
- **Zoom In/Out** – Perform zoom gestures (Ctrl + +/-).
- **Area Selection** – Select an area using an index-finger double-click gesture.
- **Focus Mode** – Pauses cursor movement when an open palm is detected.
- **Smooth Cursor** – Reduced jitter with interpolation-based movement.
- **Cross-platform Support** – Works on Windows, macOS, and Linux.

---

## 🛠️ Tech Stack
- **Python 3.8+**
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/)
- NumPy
- asyncio & time libraries

---

## 📦 Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/malrajusuhitha/virtual-mouse-opencv.git
cd virtual-mouse-opencv
```
### **2.Install Dependencies**
```bash
pip install opencv-python mediapipe numpy pyautogui
```
## ▶️How to Run
1.Connect your webcam.

2.Run the script:
```bash
python virtual_mouse.py
```
3.A window named "Virtual Mouse" will open.

4.Use your hand gestures to control the cursor:
Pinch (Index + Thumb) – Drag & drop.
Thumb open (others closed) – Left click.
Pinky up – Right click.
Two fingers up/down – Scroll.
Zoom gesture – Zoom in/out (Ctrl + +/-).
Index double click – Select area.
Press q to quit.

## 📂 Project Structure
```csharp

virtual-mouse-opencv/
│-- cursor.py        # Main program file
│-- README.md               # Project documentation
```

## 📌 Notes
1.The script runs at 30 FPS and uses MediaPipe for accurate hand landmark detection.

2.Use a well-lit environment for better hand tracking.

3.Cursor smoothness and gesture sensitivity can be adjusted in the script (smooth_factor, zoom_threshold, etc.).

## 🙌 Contributing
Feel free to fork this repo, raise issues, and submit pull requests.

## 👤 Author
Malraju Suhitha Rao
