import tkinter as tk
from tkinter import filedialog, Label, Button
from PIL import Image, ImageTk
import tensorflow as tf
import numpy as np

# Base class for AI models
class BaseModel:
    def __init__(self, model_name):
        self.model_name = model_name

    def preprocess(self, image):
        raise NotImplementedError("Subclasses should implement this method.")

    def predict(self, image):
        raise NotImplementedError("Subclasses should implement this method.")

# Derived class for Image Classification
class ImageClassificationModel(BaseModel):
    def __init__(self):
        super().__init__("MobileNetV2")
        self.model = tf.keras.applications.MobileNetV2(weights='imagenet')

    def preprocess(self, image):
        image = image.convert('RGB')
        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=0)
        return image

    def predict(self, image):
        preprocessed_image = self.preprocess(image)
        preds = self.model.predict(preprocessed_image)
        return tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=3)[0]