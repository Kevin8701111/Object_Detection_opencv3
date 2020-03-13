import cv2
import time

save_path = '/home/kevin/kgrowth/opencv_K/img/'

camera = cv2.VideoCapture(1)

if (camera.isOpened()):
    print('OK!')
else:
    print('Error!')
 

fps = 5
pre_frame = None
 
while(1):
    start = time.time()
    ret, frame = camera.read()
    gray_lwpCV = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    if not ret:
        break
    end = time.time()

    seconds = end - start
    if seconds < 1.0 / fps:
        time.sleep(1.0 / fps - seconds)
    gray_lwpCV = cv2.resize(gray_lwpCV, (500, 500))

    gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (21, 21), 0)
 
    if pre_frame is None:
        pre_frame = gray_lwpCV
    else:

        img_delta = cv2.absdiff(pre_frame, gray_lwpCV)

        thresh = cv2.threshold(img_delta, 25, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:

            if cv2.contourArea(c) < 1000:
                continue
            else:

                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "now time: {}".format(str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) ), (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                print("#####偵測有異物#####")
                cv2.imwrite(save_path + str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) + '.jpg', frame)
                print(save_path + str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) + '.jpg')
                break
        pre_frame = gray_lwpCV
 
        cv2.imshow("capture", frame)

        cv2.imshow("Frame Delta", img_delta)
 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()