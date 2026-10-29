from types import SimpleNamespace

from airos.gestures import count_extended_fingers


def make_landmarks():
    return [SimpleNamespace(x=0.5, y=0.8) for _ in range(21)]


def test_none_or_wrong_number_of_landmarks_returns_zero():
    assert count_extended_fingers(None) == 0
    assert count_extended_fingers([]) == 0


def test_four_fingers_extended_and_thumb_not_extended():
    points = make_landmarks()
    points[4].x = points[3].x
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        points[tip].y = 0.2
        points[pip].y = 0.5
    assert count_extended_fingers(points) == 4


def test_no_fingers_extended():
    points = make_landmarks()
    points[4].x = points[3].x
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        points[tip].y = 0.8
        points[pip].y = 0.5
    assert count_extended_fingers(points) == 0
