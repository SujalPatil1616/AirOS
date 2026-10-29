"""Simple finger-extension heuristic for MediaPipe hand landmarks."""

def count_extended_fingers(landmarks):
    """Approximate extended-finger count from 21 MediaPipe normalized landmarks.

    Intended for a palm facing roughly toward the camera; not orientation invariant.
    """
    if landmarks is None or len(landmarks) != 21:
        return 0

    count = 0
    for tip_idx, pip_idx in ((8, 6), (12, 10), (16, 14), (20, 18)):
        if landmarks[tip_idx].y < landmarks[pip_idx].y:
            count += 1

    # Simple thumb heuristic; works best when the hand is not strongly rotated.
    if abs(landmarks[4].x - landmarks[3].x) > 0.04:
        count += 1
    return count
