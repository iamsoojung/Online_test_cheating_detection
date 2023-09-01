import cv2 as cv
import numpy as np
import tkinter
import time

def getGazeRatio(eye_points, face_landmarks, frame, gray):
    left_eye_region = np.array([(face_landmarks.part(eye_points[0]).x, face_landmarks.part(eye_points[0]).y),
                                (face_landmarks.part(eye_points[1]).x, face_landmarks.part(eye_points[1]).y),
                                (face_landmarks.part(eye_points[2]).x, face_landmarks.part(eye_points[2]).y),
                                (face_landmarks.part(eye_points[3]).x, face_landmarks.part(eye_points[3]).y),
                                (face_landmarks.part(eye_points[4]).x, face_landmarks.part(eye_points[4]).y),
                                (face_landmarks.part(eye_points[5]).x, face_landmarks.part(eye_points[5]).y)],
                               np.int32)    # 왼쪽 눈 영역 좌표

    height, width, _ = frame.shape

    mask = np.zeros((height, width), np.uint8)   # 눈 영역 표시 위한 검정색 마스크
    cv.polylines(mask, [left_eye_region], True, 255, 2)
    cv.fillPoly(mask, [left_eye_region], 255)   # left_eye 기반 으로 눈 영역을 채워 넣어 흰색 만듦 -> 눈 영역 표시된 이미지 생성
    eye = cv.bitwise_and(gray, gray, mask=mask)     # gray, eye_mask 비트 연산 으로 눈 영역 내 색상 보존 이미지 생성

    min_x, max_x = np.min(left_eye_region[:, 0]), np.max(left_eye_region[:, 0])
    min_y, max_y = np.min(left_eye_region[:, 1]), np.max(left_eye_region[:, 1])

    gray_eye = eye[min_y: max_y, min_x: max_x]
    _, threshold_eye = cv.threshold(gray_eye, 70, 255, cv.THRESH_BINARY)    # eye_gray 이진화
    height, width = threshold_eye.shape

    # 왼쪽 절반과 오른쪽 절반의 임계값 이미지 추출
    left_side_threshold = threshold_eye[0:height, 0:width // 2]
    right_side_threshold = threshold_eye[0:height, width // 2:width]

    # 왼쪽 절반과 오른쪽 절반의 흰색 픽셀 개수 계산
    left_side_white = cv.countNonZero(left_side_threshold)
    right_side_white = cv.countNonZero(right_side_threshold)

    # 시선 비율 계산
    if left_side_white == 0:  # 왼쪽 절반에 흰색 X (시선이 왼쪽)
        gaze_ratio = 1
    elif right_side_white == 0:  # 오른쪽 절반에 흰색 X (시선이 오른쪽)
        gaze_ratio = 5
    else:  # 양쪽 절반 모두에 흰색 존재
        gaze_ratio = left_side_white / right_side_white  # 왼쪽 반과 오른쪽 반의 밝기 차이

    return gaze_ratio

last_alert_time = 0
alert_cnt = [0, 0, 0, 0]
def notifyCheating(alertFlag):
    global last_alert_time
    current_time = time.time()

    if current_time - last_alert_time >= 3:
        if alertFlag == 1:  # 2명 이상
            alert_cnt[0] += 1
            tkinter.messagebox.showinfo("걸렸다!!", "응시자가 2명 이상입니다 !!")
        elif alertFlag == 2:  # 고개 돌림 (턱)
            alert_cnt[1] += 1
            tkinter.messagebox.showinfo("걸렸다!!", "고개 돌림이 감지되었습니다 !!")
        elif alertFlag == 3:  # 대화 (입술)
            alert_cnt[2] += 1
            tkinter.messagebox.showinfo("걸렸다!!", "대화가 감지되었습니다 !!")
        elif alertFlag == 4:  # 화면 밖 응시 (눈의 시선 비율)
            alert_cnt[3] += 1
            tkinter.messagebox.showinfo("걸렸다!!", "화면 밖 응시가 감지되었습니다 !!")

        last_alert_time = current_time

    return 0