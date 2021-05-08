from flask import Flask, render_template, Response, request
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from queue import Queue, Empty

app = Flask(
    __name__, 
    static_url_path="/static", 
    static_folder="server/static",
    template_folder="server/templates")

# Init data stream
origin_capture = cv2.VideoCapture(0)
result_frame = Queue(0)
error_frame = cv2.imread("server/static/image-service/error.jpg")
DIR_SAVE_IMAGE = "server/static/image-service"

def handle_frame(frame):
    '''
        Handle your task here then return the frame
            + frame: opencv image
    '''
    result = cv2.putText(
        frame, 
        'After processing', 
        (50, 50), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        1, 
        (255, 0, 0), 
        2, cv2.LINE_AA)
    return result

def get_origin():  # generate frame by frame from camer
    # get global variable
    global origin_capture
    global result_frame
    global error_frame
    # clear all previos frame
    with result_frame.mutex:
        result_frame.queue.clear()
    # loop all frame
    while True:
        # Capture frame-by-frame
        success, frame = origin_capture.read()  
        # Show error frame
        if not success:
            frame = error_frame
        else:
            result = handle_frame(frame.copy())
        # Convert origin to base64
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        # Convert and Send result if success
        if success: 
            ret, buffer = cv2.imencode('.jpg', result)
            result = buffer.tobytes()
            result_frame.put(result)
        # Send to client
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def get_result():
    # get global variable
    global result_frame
    global error_frame
    # clear all previos frame
    with result_frame.mutex:
        result_frame.queue.clear()
    while True:
        try:
            frame = result_frame.get(block=True, timeout=1.5)
        except Empty as e:
            ret, buffer = cv2.imencode('.jpg', error_frame)
            frame = buffer.tobytes()
            
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video-result')
def video_result():
    return Response(get_result(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video-origin')
def video_origin():
    return Response(get_origin(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload-image', methods=["POST"])
def upload_image():
    try:
        #read image file string data
        f = request.files['file']
        filename = secure_filename(f.filename)
        frame = cv2.imdecode(np.fromfile(f, np.uint8), cv2.IMREAD_ANYCOLOR)
        result = handle_frame(frame)
        cv2.imwrite("server/static/image-service/" + filename, result)
        return {"success": True, "image_url": "/static/image-service/" + filename}
    except Exception as e:
        print(e)
        return {"success": False}

@app.route('/update-stream', methods=["POST"])
def update_stream():
    global origin_capture
    url = request.json["url"]
    if url.isdigit():
        url = int(url)
    origin_capture = cv2.VideoCapture(url)
    return {"success": True}

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)