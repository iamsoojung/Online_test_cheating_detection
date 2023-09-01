import tkinter.messagebox
import cv2 as cv
import dlib
import numpy as np
from datetime import datetime
from gaze_utils import getGazeRatio, notifyCheating, alert_cnt

def runExam():
    face_cascade = cv.CascadeClassifier(
        cv.data.haarcascades + 'haarcascade_frontalface_default.xml')  # 얼굴 감지를 위한 Haar 캐스케이드 분류기 (정면 얼굴 검출기)
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # 얼굴 랜드마크 predictor 객체 생성
    cap = cv.VideoCapture(0)  # 비디오 캡쳐 객체 생성 (웹캠)

    # 얼굴 랜드마크
    idx = list(range(0, 68))  # 전체 얼굴
    """
    ALL = list(range(0, 68))  # 전체 얼굴
    JAWLINE = list(range(0, 17))  # 턱선
    RIGHT_EYEBROW = list(range(17, 22))  # 오른쪽 눈썹
    LEFT_EYEBROW = list(range(22, 27))  # 왼쪽 눈썹
    NOSE = list(range(27, 36))  # 코
    RIGHT_EYE = list(range(36, 42))  # 오른쪽 눈 (36~41)
    LEFT_EYE = list(range(42, 48))  # 왼쪽 눈 (42~47)
    MOUTH_OUTLINE = list(range(48, 61))  # 입 외곽
    MOUTH_INNER = list(range(61, 68))  # 입 내부
    idx = ALL  # 사용할 얼굴 랜드마크 인덱스 (기본값 : 전체 인덱스)
    """

    alertFlag = 0

    while True:
        ret, img_frame = cap.read()  # 웹캠에서 프레임 읽기
        img_gray = cv.cvtColor(img_frame, cv.COLOR_BGR2GRAY)  # 읽은 프레임을 grayscale 변환
        faces = face_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5,
                                              minSize=(30, 30))  # 얼굴 탐지 (Face detection)

        if len(faces) > 1:
            alertFlag = 1   # Case == 1 -> 응시자가 2명 이상인 경우

        for (x, y, w, h) in faces:
            face = dlib.rectangle(x, y, x + w, y + h)  # 감지된 얼굴을 위한 dlib 사각형 그리기
            shape = predictor(img_frame, face)  # 얼굴 랜드마크 찾기 (68개 점)

            points = np.array([[s.x, s.y] for s in shape.parts()])

            # 눈, 코 points (for 고개 돌림 감지)
            left_eye = points[37:42]  # Left eye landmarks
            right_eye = points[43:48]  # Right eye landmarks
            nose = points[27]  # Nose landmark

            nose_to_eye_left = nose - left_eye.mean(axis=0)
            nose_to_eye_right = nose - right_eye.mean(axis=0)
            norm_left = np.linalg.norm(nose_to_eye_left)
            norm_right = np.linalg.norm(nose_to_eye_right)

            for pt in points[idx]:
                pt_pos = (pt[0], pt[1])
                cv.circle(img_frame, pt_pos, 2, (0, 255, 0), -1)  # 얼굴 랜드마크를 원 표시

            cv.rectangle(img_frame, (x, y), (x + w, y + h), (0, 0, 255), 3)  # 얼굴 영역을 사각형 표시

            left_eye_gazeRatio = getGazeRatio([36, 37, 38, 39, 40, 41], shape, img_frame, img_gray)
            right_eye_gazeRatio = getGazeRatio([42, 43, 44, 45, 46, 47], shape, img_frame, img_gray)
            eye_ratio = (left_eye_gazeRatio + right_eye_gazeRatio) / 2

            if eye_ratio < 0.3 or eye_ratio > 3.3:
                alertFlag = 4

        # 고개 돌림 감지
        if abs(norm_left - norm_right) >= 20:
            alertFlag = 2  # Case == 2 -> 고개를 돌린 경우

        # 입술 감지
        lip_width = points[54][0] - points[48][0]
        lip_height = points[57][1] - points[51][1]
        lip_ratio = lip_height / lip_width
        # print(lip_width, lip_height, lip_ratio)

        if lip_ratio > 0.8:
            alertFlag = 3   # Case == 3 -> 대화가 감지된 경우

        if alertFlag:  # 부정 행위 감지 시
            alertFlag = notifyCheating(alertFlag)

        key = cv.waitKey(1)  # 키 입력 대기
        cv.imshow('Taking an online exam', img_frame)  # 영상 출력

        if key == 27:  # ESC 키 -> 시험 종료
            break

    cap.release()  # 캡쳐 객체 해제

def startExam():
    msg = tkinter.messagebox.askquestion("Message", "시험을 시작할까요?")
    if msg == 'yes':
        now = datetime.now()
        print("시험 시작 : ", end="")
        print("%s년 %s월 %s일 %s시 %s분 %s초" % (now.year, now.month, now.day, now.hour, now.minute, now.second))
        runExam()
    else:
        return

alert_name = ["다수 응시자", "고개 돌림", "대화", "화면 밖 응시"]
def exitExam(window):
    msg = tkinter.messagebox.askquestion("Message", "시험을 종료할까요?")
    if msg == 'yes':
        now = datetime.now()
        window.destroy()
        print("시험 종료 : ", end="")
        print("%s년 %s월 %s일 %s시 %s분 %s초" % (now.year, now.month, now.day, now.hour, now.minute, now.second))
        print("------- 부정 행위 횟수 -------")
        for n, l in zip(alert_name, alert_cnt):
            print(n, "감지 횟수 :", l)
    else:
        return