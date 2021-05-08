import cv2

vcap = cv2.VideoCapture("rtsp://localhost:8888/live")
print("Connected")
while(1):
    ret, frame = vcap.read()
    cv2.imshow('VIDEO', frame)
    cv2.waitKey(1)