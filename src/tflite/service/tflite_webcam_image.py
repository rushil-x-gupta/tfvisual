#
# tflite_webcam_image.py
#
# OpenCV - image capture and image manipulation 
# TensorFlow Lite - object classification using coco_ssd_mobilenet_v1_1.0 model
# Kafka - send inferred meta data and annotated image to event stream
#
# Sanjeev Gupta, April 2020
#

import os
import time

from package import Config
from package import Detector
from package import OpenCV
from package import VideoStream
from package import util

config = Config(resolution=(640, 480), framerate=30)
detector = Detector(config)
opencv = OpenCV()
videostream = VideoStream(config).start()

# Start mmsPoller in a different thread
config.mmsPoller()

time.sleep(1)

while True:
    # Get a frame in different states
    frame_current, frame_normalized, frame_faces, frame_gray = opencv.getFrame(config, detector, videostream)

    # Perform the actual inferencing with the initilized detector . tflite
    inference_interval = detector.infer(frame_normalized)

    # Get results
    boxes, classes, scores, num = detector.getResults()
    
    # Annotate the frame with class boundaries
    entities_dict = opencv.updateFrame(config, detector, opencv, frame_current, frame_faces, frame_gray, boxes, classes, scores, num)
    
    # Get full payload in json
    inference_data_json = detector.getInferenceDataJSON(config, inference_interval, entities_dict, frame_current)

    # Publish the result to kafka event stream
    if config.shouldPublishKafka():
        util.inference_publish(config.getPublishPayloadKafkaUrl(), inference_data_json)

    if config.shouldPublishStream():
        util.inference_publish(config.getPublishPayloadStreamUrl(), inference_data_json)

    # Update framerate
    opencv.updateFrameRate()

videostream.stop()
