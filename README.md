# AirOS — Gesture-Controlled Desktop Prototype

AirOS is a Windows webcam prototype that detects a hand and estimates how many fingers are extended. This starter **does not move or click the mouse**; desktop control will be added only after camera tracking works reliably.

## Requirements
- Windows 10/11, 64-bit
- Python 3.11.x
- A working webcam

## Setup (PowerShell / VS Code)

Open this folder in VS Code, then run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m airos
```

Using `.venv\Scripts\python.exe` directly avoids PowerShell activation-policy issues.

On first launch, allow camera access if Windows asks. A camera window should appear. Hold one hand in view; the preview shows whether a hand is detected and the estimated number of extended fingers. Press **Q** while the camera window is focused to quit.

## Troubleshooting
- If the camera does not open, close apps that may already be using it (Teams, Zoom, Camera), then try again.
- If the wrong camera is selected, change `cv2.VideoCapture(0)` in `airos/__main__.py` to `cv2.VideoCapture(1)`.
- Keep this project's dependencies in its `.venv`. Do not install a second OpenCV package into the same environment.

## Dependency choice
This project intentionally uses **only `opencv-contrib-python`**, not both `opencv-python` and `opencv-contrib-python`. Both packages provide the same `cv2` module, and installing both can cause conflicts.
