from tkinter import *
from exam_module import startExam, exitExam

if __name__ == '__main__':
    window = Tk()  # 루트화면 (root window) 생성
    window.title("온라인 시험 부정 행위 탐지 프로그램")
    window.geometry('400x600')
    window.config(bg='#A9CBD7')

    label = Label(window, text='온라인 시험\n부정 행위 탐지 프로그램', font='NanumGothic 32 bold')
    label.configure(fg='black', bg='#A9CBD7')
    label.pack(side=TOP, padx=20, pady=20)

    img = PhotoImage(file='Image/exam.png')
    label_img = Label(window, image=img)
    label_img.configure(bg='#A9CBD7')
    label_img.pack(side=TOP, padx=10, pady=10)

    startBtn = Button(window, bg='white', fg='black', text='Start', command=startExam,
                      font=('NanumGothic 20 bold'))  # 버튼 생성
    startBtn.configure(width=10, height=1)
    startBtn.pack(side=TOP, padx=10, pady=10)  # 배치 (배치, 좌우 여백, 상하 여백)

    exitBtn = Button(window, bg='black', fg='black', text='Quit', command=lambda: exitExam(window),
                     font=('NanumGothic 20 bold'))  # 버튼 생성
    exitBtn.configure(width=10)
    exitBtn.pack(side=TOP, padx=10, pady=10)  # 배치 (배치, 좌우 여백, 상하 여백)

    window.mainloop()  # 메인 루프 실행