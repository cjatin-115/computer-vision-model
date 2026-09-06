"""
test_webcam.py
--------------
Run this alone first: `python test_webcam.py`
It only tests that OpenCV can open and read your webcam - nothing else.
If this fails or hangs, the problem is your camera/driver, not the AI pipeline.
Press 'q' to quit.
"""
import platform
import cv2

if platform.system() == "Windows":
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("FAILED: could not open camera index 0.")
    print("Try changing the 0 above to 1 or 2, and close any app (Zoom/Teams) using the camera.")
else:
    print("Camera opened OK. Press 'q' in the window to quit.")
    while True:
        ok, frame = cap.read()
        if not ok:
            print("FAILED: camera opened but could not read a frame.")
            break
        cv2.imshow("Webcam test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
