# Server URLs
BASE_URL = "i12a204.p.ssafy.io:8000"

# WebSocket URLs
WS_ROBOT_URL = f"ws://{BASE_URL}/ws/robot/"
WS_VIDEO_STREAM_URL = f"ws://{BASE_URL}/ws/video_stream/"

# RESTful API URLs
REST_DRAIN_URL = f"http://{BASE_URL}/drain/"
REST_ROBOT_INFO_URL = f"http://{BASE_URL}/robot_info/"

# Robot Configuration
ROBOT_CONFIG = {
    'robot_id': 1,
    'district_id': 1,
    'block_id': 2
}

# Camera Configuration
CAMERA_CONFIG = {
    'width': 640,
    'height': 480,
    'fps': 30
}

# Queue Configuration
QUEUE_CONFIG = {
    'frame_queue_size': 60,
    'image_queue_size': 10,
    'log_queue_size': 100
}

# Line Tracer Configuration
LINETRACER_CONFIG = {
    'speed_gain': 0.163,
    'steering_gain': 0.078,
    'steering_dgain': 0.0,
    'steering_bias': 0.05,
    'edge_value': 0,
    'mean': [0.485, 0.456, 0.406],
    'std': [0.229, 0.224, 0.225]
}


# Color Detection Configuration
GREEN_HSV_RANGE = {
    'lower': [35, 40, 30],
    'upper': [95, 255, 255]
}

# Bias Dictionary
BIAS_DICT = {
    0: 0.06,
    1: 0.03,
    2: 0.01,
    3: 0.04,
    4: 0.135
}

# Node Mapping
NODE_MAP = {
    0: 7,
    1: 8,
    2: 9,
    4: 9
}

# Other Constants
COOLDOWN_TIME = 7
CAPTURE_TIME = 1
GREEN_RATIO_THRESHOLD = 5  # percentage
