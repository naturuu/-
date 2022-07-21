#센서 제어 라이브러리
import RPi.GPIO as gpio
import time
from time import sleep

#카메라 라이브러리
import picamera

#Timestamp를 위한 datetime 라이브러리
from datetime import datetime

#GUI 관련 라이브러리
from tkinter import *

#메일시스템 라이브러리

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

#문자시스템 라이브러리
from twilio.rest import Client	


#Twilio의 내 계정 정보
account_sid =''	#사이트의 계정
auth_token=''	#사이트의 토큰
client = Client (account_sid, auth_token)

#카메라 모듈로 찍은 파일 저장명
file = "objectvideo.h264"

#초음파 핀 번호 설정
trig = 23
echo = 24

#피에조 핀 번호 설정
buzzer=18

#센서 GPIO 설정
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)
gpio.setup(buzzer, gpio.OUT)


startTime = time.time()

#Tkinter GUI 
root = Tk()
root.title("Secure System")
root.geometry("1280x600+100+300")

def OnMode():
    now = datetime.now()
    label1 = Label(root, text =now.strftime('%Y-%m-%d %H:%M:%S'),fg='blue',font=('koberwatch',10))
    label1.pack()

    try:
        while True:
            gpio.output(buzzer, gpio.LOW)
            gpio.output(trig, False)
            time.sleep(1)
            gpio.output(trig, True)
            time.sleep(0.00001)
            gpio.output(trig, False)
            while gpio.input(echo)==0:
                pulse_start = time.time()
            while gpio.input(echo)==1:
                pulse_end = time.time()
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17000
            distance = round(distance,2)
            
            print("DISTANCE : ",distance, "cm")
            if (distance > 25 ):
            
                gpio.output(buzzer,gpio.HIGH)
                print("beep")
                sleep(0.5)
                gpio.output(buzzer, gpio.LOW)

             
                with picamera.PiCamera() as camera:
                    camera.resolution = (640,480)
                    camera.start_preview()
                    camera.start_recording(file)
                    camera.wait_recording(3)
                    camera.stop_recording()
                    camera.stop_preview()

                #메세지 설정

                message = client.messages.create(	#메세지 주내용과 발신자 수신자
                    body="", #보내고싶은 문자 내용
                    from_= '',  #발급받은 trial number
                    to ='+821011112222' #내 번호
                )
            

                #메일 설정
                smtp = smtplib.SMTP('smtp.gmail.com',587)
                smtp.starttls()
                smtp.login('','')	#발신자 로그인과 앱비밀번호
                msg=MIMEMultipart()
                #메일 주내용과 수신자

                msg['Subject']='Object detected'    #메일 제목
                msg['To']=''   #수신자 메일
                text =MIMEText('raspberry send mail')  #메일 내용
                msg.attach(text)    

                #메일에 보내려는 파일 첨부

                with open(file,'rb') as file_FD:
                    etcPart = MIMEApplication(file_FD.read())
                    etcPart.add_header('Content-Disposition','attachment', filename=file)
                    msg.attach(etcPart)

                    smtp.sendmail('','',msg.as_string()) #SMTP 설정 메일과 수신자 메일
                    print("send mail! ")

                smtp.quit()
            
                break
    except KeyboardInterrupt:
        print("System Finish")
        
            



btn1 = Button(root,text="외출모드 ON",fg='red',bg='lightgrey',font=('koberwatch',60),command = OnMode)
btn1.pack(fill=BOTH)

label2 = Label(root, text="Time stamp",fg='black',font=('koberwatch'))
label2.pack()

root.mainloop()
