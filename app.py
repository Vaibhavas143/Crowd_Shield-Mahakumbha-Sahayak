from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import time
import requests
import os
import threading
import logging
import random
from dotenv import load_dotenv
from ultralytics import YOLO

# --- Load Environment Variables ---
load_dotenv()

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Configuration & Constants ---
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')

# Add a check to guide the user if the API key is missing or is a placeholder
if not GOOGLE_MAPS_API_KEY or "YOUR_KEY_HERE" in GOOGLE_MAPS_API_KEY:
    logger.warning("Google Maps API Key is not configured. The map will not load.")
    logger.warning("Please create a key in Google Cloud Platform, enable 'Maps JavaScript API', and add it to your .env file.")


KUMBH_MELA_LAT = 20.0082
KUMBH_MELA_LNG = 73.7922
CROWD_DENSITY_THRESHOLD_MODERATE = 10
YOLO_INPUT_SIZE = 320
PROCESSING_INTERVAL_SECONDS = 1.0

# --- YOLOv8 Model Setup ---
model = YOLO("yolov8n.pt")

video_streams = []

def create_placeholder_video(filename="crowd_sim.mp4", num_people=20, width=640, height=480, duration_seconds=30):
    """Creates a video file with moving dots to simulate a crowd if it doesn't already exist."""
    if os.path.exists(filename):
        logger.info(f"Video file '{filename}' already exists. Skipping creation.")
        return

    logger.info(f"Generating placeholder video: '{filename}' with {num_people} simulated people...")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
    
    people = [{'pos': [random.randint(0, width), random.randint(0, height)],
               'vel': [random.randint(-2, 2), random.randint(-2, 2)]} for _ in range(num_people)]

    for _ in range(20 * duration_seconds):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        for person in people:
            person['pos'][0] += person['vel'][0]
            person['pos'][1] += person['vel'][1]
            if not 0 < person['pos'][0] < width: person['vel'][0] *= -1
            if not 0 < person['pos'][1] < height: person['vel'][1] *= -1
            cv2.circle(frame, (int(person['pos'][0]), int(person['pos'][1])), 5, (255, 255, 255), -1)
        out.write(frame)
    out.release()
    logger.info(f"Finished generating '{filename}'.")

class VideoStream:
    """Manages reading and processing a single video stream in a dedicated thread."""
    def __init__(self, stream_id, video_path):
        self.stream_id = stream_id
        self.video_path = video_path
        self.camera = cv2.VideoCapture(self.video_path)
        if not self.camera.isOpened():
            logger.error(f"Could not open video: {self.video_path}")
            return

        self.latest_frame = None
        self.latest_results = {"density_level": "Normal", "density_message": "Initializing...", "suggested_route": None, "boxes": []}
        self.lock = threading.Lock()
        self.shutdown_flag = threading.Event()
        self.thread = threading.Thread(target=self._process_stream, daemon=True)
        self.thread.start()

    def _process_stream(self):
        """Internal method to read frames and run YOLO detection at a fixed interval for performance."""
        while not self.shutdown_flag.is_set():
            try:
                success, frame = self.camera.read()
                if not success:
                    self.camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                with self.lock:
                    self.latest_frame = frame
                
                person_count, boxes = self._count_people(frame)
                density_level, density_message, suggested_route = self._get_density_info(person_count)
                
                with self.lock:
                    self.latest_results = {
                        "density_level": density_level,
                        "density_message": density_message,
                        "suggested_route": suggested_route,
                        "boxes": boxes
                    }
            except Exception as e:
                logger.error(f"Error processing stream {self.stream_id}: {e}")
            
            time.sleep(PROCESSING_INTERVAL_SECONDS)
        
        self.camera.release()

    def _count_people(self, frame):
        if frame is None: return 0, []
        
        results = model.predict(frame, classes=[0], verbose=False)
        boxes = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                boxes.append([int(x1), int(y1), int(x2 - x1), int(y2 - y1)])

        return len(boxes), boxes
        
    def _get_density_info(self, count):
        if count > CROWD_DENSITY_THRESHOLD_MODERATE:
            return "High", "Crowd is dense. Consider alternate routes.", "Consider alternate routes."
        else:
            return "Normal", "Crowd flow is normal.", None

    def get_latest_info(self):
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None, self.latest_results

    def stop(self):
        self.shutdown_flag.set()

def generate_frames_for_stream(stream_id):
    """Generator function that creates the video feed for the webpage."""
    stream = video_streams[stream_id]
    while True:
        frame, results = stream.get_latest_info()
        if frame is None:
            time.sleep(0.1)
            continue
        
        for (x, y, w, h) in results["boxes"]:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (57, 255, 20), 2)
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 50), (0, 0, 0), -1)
        alpha = 0.6
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        color = {"Normal": (0, 255, 0), "High": (0, 255, 255), "Critical": (0, 0, 255)}.get(results["density_level"], (255, 255, 255))
        cv2.putText(frame, f'Cam {stream_id + 1} | Density: {results["density_level"]}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret: continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(1/30)

# --- BUG FIX: Added the missing get_weather_data function ---
def get_weather_data():
    """Fetches weather data from OpenWeatherMap API."""
    if not OPENWEATHERMAP_API_KEY or "YOUR_KEY_HERE" in OPENWEATHERMAP_API_KEY:
        return {'description': 'Weather API Key Not Set', 'temperature': 'N/A', 'icon': '01d'}

    try:
        url = (f'https://api.openweathermap.org/data/2.5/weather?lat={KUMBH_MELA_LAT}&lon={KUMBH_MELA_LNG}&appid={OPENWEATHERMAP_API_KEY}&units=metric')
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            'temperature': data.get('main', {}).get('temp', 'N/A'),
            'description': (data.get('weather', [{}])[0].get('description', 'N/A') or '').title(),
            'icon': data.get('weather', [{}])[0].get('icon', '01d')
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather fetch error: {e}")
        return {'temperature': 'N/A', 'description': 'Connection Error', 'icon': '01d'}

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html', num_streams=len(video_streams), google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/video_feed/<int:stream_id>')
def video_feed(stream_id):
    return Response(generate_frames_for_stream(stream_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/realtime_data/<int:stream_id>')
def realtime_data(stream_id):
    if stream_id >= len(video_streams):
        return jsonify({"error": "Stream not found"}), 404
    
    _, results = video_streams[stream_id].get_latest_info()
    weather_data = get_weather_data() # This call was failing before
    
    return jsonify({
        'density_level': results["density_level"],
        'density_message': results["density_message"],
        'suggested_route': results["suggested_route"],
        'weather': weather_data,
        'kumbh_mela_lat': KUMBH_MELA_LAT + (stream_id * 0.001),
        'kumbh_mela_lng': KUMBH_MELA_LNG + (stream_id * 0.001),
        'boxes': results["boxes"],
        'person_count': len(results["boxes"])
    })

# --- Main Execution Block ---
if __name__ == '__main__':
    video_files_to_use = [
        {"name": "crowd1.mp4", "people": 10},
        {"name": "crowd2.mp4", "people": 25},
        {"name": "crowd3.mp4", "people": 40},
        {"name": "crowd4.mp4", "people": 55}
    ]

    for video_info in video_files_to_use:
        create_placeholder_video(filename=video_info["name"], num_people=video_info["people"])

    for i, video_info in enumerate(video_files_to_use):
        video_streams.append(VideoStream(stream_id=i, video_path=video_info["name"]))

    if not video_streams:
        exit("Error: No video streams were initialized.")

    app.run(host='0.0.0.0', port=5000)
