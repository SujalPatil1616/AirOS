
"""AirOS: Mouse control with wrist-based two-finger scrolling."""

import time

import cv2
import mediapipe as mp
import pyautogui

from .gestures import count_extended_fingers


# Click and scroll settings
CLICK_CONFIRM_FRAMES = 4

# Slightly faster scrolling
SCROLL_DEAD_ZONE = 0.004
SCROLL_DISTANCE_PER_STEP = 0.008
SCROLL_AMOUNT = 32
SCROLL_COOLDOWN = 0.015

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02


def main():
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("AirOS could not open the webcam.")
        print("Close other camera apps or try camera index 1.")
        return

    screen_width, screen_height = pyautogui.size()

    mouse_enabled = False
    little_finger_frames = 0
    click_armed = True

    scroll_anchor_y = None
    last_scroll_time = 0.0

    print("\nAirOS is running in SAFE MODE.")
    print("Index finger: move the pointer.")
    print("Index + middle fingers: wrist-based scrolling.")
    print("Little finger: left-click once.")
    print("P: pause/resume mouse control.")
    print("Q: quit AirOS.\n")

    try:
        with mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.55,
            min_tracking_confidence=0.5,
        ) as hands:

            while True:
                ok, frame = camera.read()

                if not ok:
                    print("Could not read a webcam frame.")
                    break

                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)

                status = "No hand detected"
                gesture_status = "Show your hand"
                click_status = "Mouse: PAUSED"

                if results.multi_hand_landmarks:
                    hand = results.multi_hand_landmarks[0]
                    landmarks = hand.landmark

                    mp_draw.draw_landmarks(
                        frame, hand, mp_hands.HAND_CONNECTIONS
                    )

                    count = count_extended_fingers(landmarks)
                    status = f"Hand detected | Fingers: {count}"

                    # Finger landmarks.
                    index_tip = landmarks[8]
                    index_pip = landmarks[6]
                    middle_tip = landmarks[12]
                    middle_pip = landmarks[10]
                    ring_tip = landmarks[16]
                    ring_pip = landmarks[14]
                    little_tip = landmarks[20]
                    little_pip = landmarks[18]

                    index_up = index_tip.y < index_pip.y - 0.02
                    middle_up = middle_tip.y < middle_pip.y - 0.02
                    ring_up = ring_tip.y < ring_pip.y - 0.02
                    little_up = little_tip.y < little_pip.y - 0.02

                    # Scroll gesture: index and middle raised,
                    # ring and little fingers lowered.
                    scrolling_gesture = (
                        index_up
                        and middle_up
                        and not ring_up
                        and not little_up
                    )

                    # MediaPipe landmark 0 is the wrist.
                    wrist = landmarks[0]

                    height, width = frame.shape[:2]
                    tip_x = int(little_tip.x * width)
                    tip_y = int(little_tip.y * height)

                    cv2.circle(
                        frame,
                        (tip_x, tip_y),
                        10,
                        (0, 255, 255) if little_up
                        else (255, 180, 0),
                        -1,
                    )

                    if mouse_enabled and scrolling_gesture:
                        gesture_status = "SCROLL MODE - MOVE YOUR WRIST"

                        # Record wrist position at scroll-mode entry.
                        if scroll_anchor_y is None:
                            scroll_anchor_y = wrist.y

                        wrist_movement = wrist.y - scroll_anchor_y
                        now = time.monotonic()

                        if (
                            abs(wrist_movement) >= SCROLL_DEAD_ZONE
                            and now - last_scroll_time >= SCROLL_COOLDOWN
                        ):
                            steps = int(
                                abs(wrist_movement)
                                / SCROLL_DISTANCE_PER_STEP
                            )
                            steps = max(1, min(steps, 4))

                            if wrist_movement < 0:
                                pyautogui.scroll(SCROLL_AMOUNT * steps)
                            else:
                                pyautogui.scroll(-SCROLL_AMOUNT * steps)

                            # Reset the anchor after each scroll event.
                            scroll_anchor_y = wrist.y
                            last_scroll_time = now

                    else:
                        scroll_anchor_y = None

                        # Preserve original pointer movement.
                        if mouse_enabled:
                            mouse_x = int(index_tip.x * screen_width)
                            mouse_y = int(index_tip.y * screen_height)

                            mouse_x = max(
                                0, min(screen_width - 1, mouse_x)
                            )
                            mouse_y = max(
                                0, min(screen_height - 1, mouse_y)
                            )

                            pyautogui.moveTo(
                                mouse_x, mouse_y, duration=0
                            )

                            if little_up:
                                gesture_status = "LITTLE FINGER CLICK"
                            else:
                                gesture_status = "POINTER CONTROL"
                        else:
                            gesture_status = "Mouse control PAUSED"

                    # Preserve original little-finger click behavior.
                    if little_up:
                        little_finger_frames += 1
                    else:
                        little_finger_frames = 0
                        click_armed = True

                    if (
                        mouse_enabled
                        and little_up
                        and click_armed
                        and little_finger_frames >= CLICK_CONFIRM_FRAMES
                    ):
                        pyautogui.click(button="left")
                        click_armed = False
                        click_status = "LEFT CLICK!"
                        print("Left click: little finger raised.")

                    elif not mouse_enabled:
                        click_status = "Mouse: PAUSED"
                    elif not click_armed:
                        click_status = "Lower little finger to re-arm"
                    else:
                        click_status = "Mouse: ACTIVE"

                else:
                    little_finger_frames = 0
                    click_armed = False
                    scroll_anchor_y = None

                control_status = (
                    "ACTIVE" if mouse_enabled else "PAUSED"
                )

                cv2.putText(
                    frame, status, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (0, 255, 0), 2, cv2.LINE_AA,
                )
                cv2.putText(
                    frame, gesture_status, (10, 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (0, 255, 255), 2, cv2.LINE_AA,
                )
                cv2.putText(
                    frame, click_status, (10, 82),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.43,
                    (255, 255, 0), 1, cv2.LINE_AA,
                )
                cv2.putText(
                    frame,
                    f"Mouse {control_status} | P: Toggle | Q: Quit",
                    (10, 108),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.43,
                    (255, 255, 255), 1, cv2.LINE_AA,
                )

                cv2.imshow("AirOS - Wrist Scroll", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break

                elif key == ord("p"):
                    mouse_enabled = not mouse_enabled
                    little_finger_frames = 0
                    click_armed = False
                    scroll_anchor_y = None

                    print(
                        "Mouse control:",
                        "ACTIVE" if mouse_enabled else "PAUSED",
                    )

    except pyautogui.FailSafeException:
        print("Emergency stop activated. AirOS is stopping.")

    except KeyboardInterrupt:
        print("AirOS stopped.")

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
