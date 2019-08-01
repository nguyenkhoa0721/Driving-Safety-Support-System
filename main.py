import numpy as np
import cv2
import time
import os
import imutils
import serial
import ftplib
#import RPi.GPIO as GPIO
from imutils.video import VideoStream

ser = serial.Serial('COM4', 9600)
#ser = serial.Serial('/dev/ttyACM0', 9600)

cap = VideoStream(0).start()
#cap2 = VideoStream(usePiCamera=True).start()
cap2 = VideoStream(1).start()
timeL=0
lane=False

time.sleep(2)
TIME=10
tmpT=0
checkN= False
check = False
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
lefteye_cascade= cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def filter_colors(image):
  # white color mask
    lower = np.uint8([0, 190,   0])
    upper = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(image, lower, upper)
    # yellow color mask
    lower = np.uint8([ 10,   0, 100])
    upper = np.uint8([ 40, 255, 255])
    yellow_mask = cv2.inRange(image, lower, upper)
    # combine the mask
    mask = cv2.bitwise_or(white_mask, yellow_mask)
    return cv2.bitwise_and(image, image, mask = mask)
def cal(image):
    return cv2.countNonZero(image)
def process(image):
    global lane
    global timeL

    a = int(image.shape[1] * 0.42)  # 0.2
    b = int(image.shape[0] * 0.76)  # 0.7
    c = int(image.shape[1] * 0.58)  # 0.8
    d = int(image.shape[0] * 0.9)  # 0.9

    crop_image = image[b:d, a:c]

    blur_image = cv2.GaussianBlur(crop_image, (3, 3), 0)
    filter_image = filter_colors(blur_image)
    gray = cv2.cvtColor(filter_image, cv2.COLOR_RGB2GRAY)
    ret, ans = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    cv2.rectangle(image, (a, b), (c, d), (255, 0, 0), 2)

    a1 = 0  # 0.2
    b1 = int(ans.shape[0] * 0.4)  # 0.7
    c1 = int(ans.shape[1] * 0.4)  # 0.8
    d1 = int(ans.shape[0])  # 0.9
    left = ans[b1:d1, a1:c1]

    a2 = int(ans.shape[1] * 0.4)
    b2 = 0  # 0.7
    c2 = int(ans.shape[1] * 0.6)  # 0.8
    d2 = int(ans.shape[0])  # 0.9
    center=ans[b2:d2, a2:c2]

    a3 = int(ans.shape[1] * 0.6)
    b3 = int(ans.shape[0] * 0.4)  # 0.7
    c3 = int(ans.shape[1])  # 0.8
    d3 = int(ans.shape[0])  # 0.9
    right=ans[b3:d3, a3:c3]

    cv2.imshow('goc', image)
    cv2.imshow('right', right)
    cv2.imshow('left', left)
    cv2.imshow('center', center)
    r=l=c=0
    if (cal(right)>5):
        r=1;
    if (cal(left)>5):
        l=1;
    if (cal(center)>5):
        c=1;
    res=r+l+c

    if (res==0 and lane==True):
        timeL = timeL +1
        if timeL==10:
            lane=False
            timeL=0
            print("dung lan")
    else:
        timeL = 0
    if (res>1 and lane==False)or(res==1 and lane==False and c==1):
        lane = True
    if (l==1 and lane==False and res==1):
        print("left")
        lane=True
    if (r==1 and lane==False and res==1 ):
        print("right")
        lane = True


def eye(img):
    global TIME
    global checkN
    global check
    global tmpT
    lefteye = lefteye_cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=3,
                                         minSize=(30, 30), flags=cv2.CASCADE_FIND_BIGGEST_OBJECT)
    open_eye = eye_cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=0,
                                         minSize=(30, 30), flags=cv2.CASCADE_FIND_BIGGEST_OBJECT)
    minw=minh=maxw=maxh=0
    minx=miny=maxx=maxy=0
    maxdt=0
    for (x1, y1, w1, h1) in lefteye:
        if (x1>maxx):
            maxx=x1
            maxy=y1
            maxw=w1
            maxh=h1
    cv2.rectangle(img, (maxx, maxy), (maxx + maxw, maxy + maxh), (255, 0, 0), 2)
    roi_gray = img[maxy:maxy + maxh, maxx:maxx + maxw]
    canny_edges = cv2.Canny(roi_gray, 50, 150)
    eyes = eye_cascade.detectMultiScale(roi_gray)
    for (ex, ey, ew, eh) in eyes:
        if (maxdt<ew*eh):
            maxdt=minw*minh
            minx=ex
            miny=ey
            minh=eh
            minw=ew
    if ((minw*2<maxw) or (maxx*minx==0)):
        tmpT=tmpT+1
        if (tmpT>TIME) and (checkN==False):
            checkN=True
            string='N'
            ser.write(string.encode())
            update()
            print('N')
    else:
        tmpT = 0
        if (checkN==True):
            checkN=False
            string='M'
            ser.write(string.encode())
            print('M')
    cv2.rectangle(roi_gray, (minx, miny), (minx + minw, miny + minh), (0, 255, 0), 2)
    cv2.imshow('eye',img)
def update():
    session = ftplib.FTP('192.168.1.184', 'admin', '070201kt')
    str = "Thoi gian " + time.strftime("%c")
    f = open("log", "a")
    f.write(str+" ngu gat"+ "\n")
    f.close();
    file = open('log', 'rb')
    session.storbinary('STOR nguyenkhoa/log', file)
    file.close()
    print(1)
chay=True
input_state=True
while(1):
    #input_state = GPIO.input(18)
    if input_state == False:
        if (chay==True):
            chay=False
        else:
            chay=True
        time.sleep(0.5)
    if (chay==False):
        continue
    image = cap2.read()
    img = cap.read()

    if image is not None:
        image = imutils.resize(image, width=300)
        process(image)
    #========================
    if img is not None:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = img[200:400, 200:500]
        img = imutils.resize(img, width=200)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        img = eye(img)
    k = cv2.waitKey(60) & 0xff
    if k == 27:
        break
cv2.waitKey(0)
cv2.destroyAllWindows()
