import cv2
import time
import subprocess
import pymongo
myclient = pymongo.MongoClient('mongodb://kevin87011111:<password>@cluster0-shard-00-00-b9pzv.gcp.mongodb.net:27017,cluster0-shard-00-01-b9pzv.gcp.mongodb.net:27017,cluster0-shard-00-02-b9pzv.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')
myclient = pymongo.MongoClient("mongodb://kevin87011111:asdf41207@cluster0-shard-00-00-b9pzv.gcp.mongodb.net:27017,cluster0-shard-00-01-b9pzv.gcp.mongodb.net:27017,cluster0-shard-00-02-b9pzv.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
mydb = myclient["stream_IoT"]
mycol = mydb["object_status"]
 
# datas = mycol.find()
# for data in datas:
#     print(data)

save_path = '/home/kevin/kgrowth/opencv_K/img/'
rtmp = 'rtmp://localhost:1935/mylive/test'

camera = cv2.VideoCapture(0)

size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)), int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
sizeStr = str(size[0]) + 'x' + str(size[1])

command = ['ffmpeg',
    '-y', '-an',
    '-f', 'rawvideo',
    '-vcodec','rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', sizeStr,
    '-r', '25',
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'ultrafast',
    '-f', 'flv',
    rtmp]

pipe = subprocess.Popen(command
    , shell=False
    , stdin=subprocess.PIPE
)

if (camera.isOpened()):
    print('OK!')
else:
    print('Error!')

fps = 30
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
    gray_lwpCV = cv2.resize(gray_lwpCV, (640, 480))

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

                myquery = { "stream_name": "A" }
                newvalues = { "$set": { "stream_name": "A", "stream_A_status": "safe" } }
                mycol.update_one(myquery, newvalues)
                print('status : safe')
                datas = mycol.find()
                for data in datas:
                    print(data)

                continue
            else:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "now time: {}".format(str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) ), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                print("#####偵測有異物#####")

                myquery = { "stream_name": "A" }
                newvalues = { "$set": { "stream_name": "A", "stream_A_status": "warning" } }
                mycol.update_one(myquery, newvalues)
                print('status : warning')
                datas = mycol.find()
                for data in datas:
                    print(data)

                cv2.imwrite(save_path + str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) + '.jpg', frame)
                print(save_path + str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) + '.jpg')
                break
                
        pre_frame = gray_lwpCV
        pipe.stdin.write(frame.tostring())
        cv2.imshow("capture", frame)
        cv2.imshow("Frame Delta", img_delta)
    if cv2.waitKey(40) & 0xFF == ord('q'):
        break


camera.release()
pipe.terminate()
cv2.destroyAllWindows()