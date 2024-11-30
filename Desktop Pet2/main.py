import os
import sys
import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import win32api,win32con
from threading import *
import gesture_recognition

class DesktopPet(QWidget):
    def __init__(self, parent=None):
        super(DesktopPet, self).__init__(parent)
        
        # Initialize game-related flags
        self.game_begin = random.choice([1, 2, 3])  # Directly choose a random gesture
        self.flag1 = 0  # Control animation playback
        self.flag2 = 0  # Control game result determination
        self.game_state = 1  # Start the game directly
        self.result = 0  # Game result (1: victory, 2: draw, 3: defeat)
        
        # Initialize window and images
        self.init()
        self.initPetImage()
        self.petNormalAction()
        
        # Start the game directly
        Thread(target=gesture_recognition.opencv2_func).start()

    def init(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()

    def initPetImage(self):
        self.talkLabel = QLabel(self)
        self.talkLabel.setStyleSheet("font:15pt 'arial';border-width: 1px;color:blue;")
        self.talkLabel.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)  # Align text to bottom center

        self.image = QLabel(self)
        self.movie = QMovie("normal/normal1.gif")
        self.movie.setScaledSize(QSize(200, 200))
        self.image.setMovie(self.movie)
        self.movie.start()
        self.resize(1024, 1024)
        self.randomPosition()
        self.show()

        # Load game-related images
        self.process1 = []  # Rock animation
        for i in os.listdir("process1"):
            self.process1.append("process1/" + i)

        self.process2 = []  # Scissors animation 
        for i in os.listdir("process2"):
            self.process2.append("process2/" + i)

        self.process3 = []  # Paper animation
        for i in os.listdir("process3"):
            self.process3.append("process3/" + i)

    def petNormalAction(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.randomAct)
        self.timer.start(4000)

        self.talkTimer = QTimer()
        self.talkTimer.timeout.connect(self.talk)
        self.talkTimer.start(4000)

        self.talk()

    def randomAct(self):
        if gesture_recognition.result == 'none' and self.game_begin != 0:
            self.movie = QMovie("./others/ready.gif")
            self.movie.setScaledSize(QSize(200, 200))
            self.image.setMovie(self.movie)
            self.movie.start()

        # Handle the rock case
        if self.game_begin == 1 and gesture_recognition.result != 'none' and self.result == 0:
            self._handle_rock()

        # Handle the scissors case
        if self.game_begin == 2 and gesture_recognition.result != 'none' and self.result == 0:  
            self._handle_scissors()

        # Handle the paper case
        if self.game_begin == 3 and gesture_recognition.result != 'none' and self.result == 0:
            self._handle_paper()

        # Display the result animation
        if self.result > 0:
            self.movie = QMovie(f"./result/result{self.result}.gif")
            self.movie.setScaledSize(QSize(200, 200))
            self.image.setMovie(self.movie)
            self.movie.start()

    def _handle_rock(self):
        self.movie = QMovie(self.process1[self.flag1])
        self.movie.setScaledSize(QSize(200, 200))
        self.image.setMovie(self.movie)
        if self.flag1 == 1:
            self.flag2 = 1
        self.movie.start()
        self.flag1 = 1
        if self.flag2 == 1 and self.result == 0:
            self._judge_result('stone', 2, 3, 1)

    def _handle_scissors(self):
        self.movie = QMovie(self.process2[self.flag1])
        self.movie.setScaledSize(QSize(200, 200))
        self.image.setMovie(self.movie)
        if self.flag1 == 1:
            self.flag2 = 1
        self.movie.start()
        self.flag1 = 1
        if self.flag2 == 1:
            self._judge_result('scissors', 1, 2, 3)

    def _handle_paper(self):
        self.movie = QMovie(self.process3[self.flag1])
        self.movie.setScaledSize(QSize(200, 200))
        self.image.setMovie(self.movie)
        if self.flag1 == 1:
            self.flag2 = 1
        self.movie.start()
        self.flag1 = 1
        if self.flag2 == 1 and self.result == 0:
            self._judge_result('cloth', 3, 1, 2)

    def _judge_result(self, gesture, rock_result, scissors_result, paper_result):
        result_map = {
            'stone': (rock_result, "Rock"),
            'scissors': (scissors_result, "Scissors"),
            'cloth': (paper_result, "Paper")
        }

        if gesture_recognition.result in result_map:
            self.result = result_map[gesture_recognition.result][0]
            self.flag2 = 0
            user_gesture = result_map[gesture_recognition.result][1]
            pet_gesture = result_map[gesture][1]
            result_text = "You win this round" if self.result == 1 else "This round is a draw" if self.result == 2 else "You lose this round"
            win32api.MessageBox(0, f"Your gesture: {user_gesture}\nLittle Black's gesture: {pet_gesture}", result_text, win32con.MB_OK)

    def talk(self):
        if gesture_recognition.result == 'none' and self.game_state == 1 and self.result == 0:
            self._set_talk_text("Come on, let's play!")
        elif gesture_recognition.result != 'none' and self.game_state == 1 and self.result == 0:
            self._set_talk_text("Rock, paper, scissors~~")  
        elif self.result == 1:
            self._set_talk_text("55555")
        elif self.result == 2:
            self._set_talk_text("It's a draw, hehe")
        elif self.result == 3:
            self._set_talk_text("I won, woohoo!")

    def _set_talk_text(self, text):
        self.talkLabel.setText(text)
        self.talkLabel.setStyleSheet(
            "font: bold;"
            "font:25pt 'arial';"  
            "color:white;"
            "background-color: rgba(0, 0, 0, 150);"  # Semi-transparent background
            "padding: 10px;"  # Add padding around the text
        )
        self.talkLabel.adjustSize()
        self.talkLabel.move(self.width() // 2 - self.talkLabel.width() // 2, self.height() - self.talkLabel.height() - 20)  # Position text at bottom center

    def randomPosition(self):
        screen_geo = QDesktopWidget().screenGeometry()
        pet_geo = self.geometry()
        width = (screen_geo.width() - pet_geo.width()) * random.random()
        height = (screen_geo.height() - pet_geo.height()) * random.random()
        self.move(int(width), int(height))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
        event.accept()  

    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def enterEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)

    def quit_func(self):
        gesture_recognition.close2 = 1
        self.close()
        sys.exit()  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())