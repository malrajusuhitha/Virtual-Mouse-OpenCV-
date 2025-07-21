import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
import asyncio
import platform

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize PyAutoGUI
pyautogui.FAILSAFE = False
screen_width, screen_height = pyautogui.size()

# Initialize OpenCV
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Variables for gesture recognition
prev_distance = 0
zoom_threshold = 20
last_click_time = 0
click_cooldown = 0.5
is_selecting = False
select_start = None
select_end = None
is_focused = False
last_position = None
smooth_factor = 0.05 # Reduced from 0.5 to 0.05 for faster cursor response
prev_x, prev_y = 0, 0
dragging = False
action_freeze_time = 0  # Track when to unfreeze cursor
freeze_duration = 0.3  # Freeze cursor for 0.3 seconds during actions

def get_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

async def main():
    global prev_distance, last_click_time, is_selecting, select_start, select_end
    global is_focused, last_position, prev_x, prev_y, dragging, action_freeze_time

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip and convert frame
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        # Check if cursor should be frozen
        current_time = time.time()
        cursor_frozen = current_time < action_freeze_time

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get landmark coordinates
                landmarks = hand_landmarks.landmark
                h, w, _ = frame.shape
                
                # Convert to screen coordinates
                index_tip = (int(landmarks[8].x * w), int(landmarks[8].y * h))
                thumb_tip = (int(landmarks[4].x * w), int(landmarks[4].y * h))
                middle_tip = (int(landmarks[12].x * w), int(landmarks[12].y * h))
                ring_tip = (int(landmarks[16].x * w), int(landmarks[16].y * h))
                pinky_tip = (int(landmarks[20].x * w), int(landmarks[20].y * h))

                # Smooth mouse movement (only if not frozen and not in focus mode)
                if not is_focused and not cursor_frozen:
                    screen_x = np.interp(index_tip[0], [50, w-50], [0, screen_width])
                    screen_y = np.interp(index_tip[1], [50, h-50], [0, screen_height])
                    curr_x = prev_x + (screen_x - prev_x) * smooth_factor
                    curr_y = prev_y + (screen_y - prev_y) * smooth_factor
                    pyautogui.moveTo(curr_x, curr_y)
                    prev_x, prev_y = curr_x, curr_y

                # Calculate distances for gestures
                pinch_distance = get_distance(index_tip, thumb_tip)
                middle_index_distance = get_distance(index_tip, middle_tip)
                
                # Count raised fingers
                fingers_up = sum([
                    landmarks[8].y < landmarks[6].y,  # Index
                    landmarks[12].y < landmarks[10].y,  # Middle
                    landmarks[16].y < landmarks[14].y,  # Ring
                    landmarks[20].y < landmarks[18].y,  # Pinky
                    landmarks[4].x > landmarks[3].x if landmarks[4].y < landmarks[3].y else False  # Thumb
                ])

                # Focus mode (open palm, 5 fingers)
                if fingers_up >= 4:
                    if not is_focused:
                        is_focused = True
                        last_position = (curr_x, curr_y)
                    cv2.putText(frame, "Focus Mode", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    continue
                else:
                    is_focused = False

                # --- Drag and Drop Gesture (Pinch) ---
                if fingers_up >= 2:  # Index + Thumb
                    if pinch_distance < 25:  # Pinch close
                        if not dragging:
                            pyautogui.mouseDown()
                            dragging = True
                            action_freeze_time = current_time + freeze_duration
                            cv2.putText(frame, "Dragging", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        if dragging:
                            pyautogui.mouseUp()
                            dragging = False
                            action_freeze_time = current_time + freeze_duration
                else:
                    if dragging:
                        pyautogui.mouseUp()
                        dragging = False
                        action_freeze_time = current_time + freeze_duration

                # Zoom gestures
                if fingers_up == 2 and abs(pinch_distance - prev_distance) > zoom_threshold:
                    if pinch_distance < prev_distance:  # Zoom in
                        pyautogui.hotkey('ctrl', '+')
                        action_freeze_time = current_time + freeze_duration
                        cv2.putText(frame, "Zoom In", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    elif pinch_distance > prev_distance:  # Zoom out
                        pyautogui.hotkey('ctrl', '-')
                        action_freeze_time = current_time + freeze_duration
                        cv2.putText(frame, "Zoom Out", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    prev_distance = pinch_distance
                    time.sleep(0.1)

                # Click gestures
                if current_time - last_click_time > click_cooldown:
                    # Left click: Thumb open, other fingers closed
                    if fingers_up == 1 and landmarks[4].x > landmarks[3].x and \
                       landmarks[8].y > landmarks[6].y and \
                       landmarks[12].y > landmarks[10].y and \
                       landmarks[16].y > landmarks[14].y and \
                       landmarks[20].y > landmarks[18].y:
                        pyautogui.click()
                        last_click_time = current_time
                        action_freeze_time = current_time + freeze_duration
                        cv2.putText(frame, "Left Click", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    # Right click: Pinky finger up
                    elif fingers_up == 1 and landmarks[20].y < landmarks[18].y:
                        pyautogui.rightClick()
                        last_click_time = current_time
                        action_freeze_time = current_time + freeze_duration
                        cv2.putText(frame, "Right Click", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Scroll gestures
                if fingers_up == 2 and middle_index_distance < 30:
                    if landmarks[8].y < landmarks[6].y and landmarks[12].y < landmarks[10].y:  # Both up
                        pyautogui.scroll(100) # Scroll up speed
                        action_freeze_time = current_time + freeze_duration
                        cv2.putText(frame, "Scroll Up", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    elif landmarks[8].y > landmarks[6].y and landmarks[12].y > landmarks[10].y:  # Both down
                        pyautogui.scroll(-100) # Scroll down speed
                        action_freeze_time = current_time + freeze_duration
                        cv2.putText(frame, "Scroll Down", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Area selection (using index finger double click)
                if fingers_up == 1 and landmarks[8].y < landmarks[6].y:
                    if current_time - last_click_time < 0.2:  # Double click detection speed
                        if not is_selecting:
                            is_selecting = True
                            select_start = (curr_x, curr_y)
                        else:
                            is_selecting = False
                            select_end = (curr_x, curr_y)
                            # Perform drag
                            pyautogui.mouseDown(select_start[0], select_start[1])
                            pyautogui.moveTo(select_end[0], select_end[1])
                            pyautogui.mouseUp()
                            action_freeze_time = current_time + freeze_duration
                            cv2.putText(frame, "Area Selected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        last_click_time = current_time

                # Draw selection rectangle
                if is_selecting and select_start:
                    current_pos = (int(curr_x * w / screen_width), int(curr_y * h / screen_height))
                    cv2.rectangle(frame, (int(select_start[0] * w / screen_width), int(select_start[1] * h / screen_height)),
                                current_pos, (0, 255, 255), 2)

        cv2.imshow('Virtual Mouse', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        await asyncio.sleep(1.0 / 30)  # 30 FPS

    cap.release()
    cv2.destroyAllWindows()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())