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

# Decorator for logging predictions
def log_predictions(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"Predictions: {result}")
        return result
    return wrapper

# Application class with logging decorator
class ImageClassificationApp(ImageClassificationModel):
    def __init__(self):
        super().__init__()

    @log_predictions
    def classify(self, image):
        predictions = self.predict(image)
        return {label: float(score) for (_, label, score) in predictions}

# Tkinter GUI for the app
class ImageClassificationGUI:
    def __init__(self, root, classifier_app):
        self.root = root
        self.classifier_app = classifier_app
        self.root.title("Image Classification App")
        self.root.configure(bg="#2C3E50")

        # Load Image Button with enhanced style and text
        self.load_button = Button(root, text="Select Image", command=self.load_image,
                                  font=("Arial", 16, "bold"), bg="#3498DB", fg="white",
                                  activebackground="#2980B9", activeforeground="white", padx=20, pady=10)
        self.load_button.pack(pady=20)

        # Image Display Label with padding
        self.image_label = Label(root, bg="#2C3E50")
        self.image_label.pack(pady=10)

        # Classification Result Label with better font size and padding
        self.result_label = Label(root, text="Classified Results Will Appear Here", font=("Arial", 16),
                                  bg="#2C3E50", fg="white", wraplength=300)
        self.result_label.pack(pady=20)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            self.display_image(image)
            predictions = self.classifier_app.classify(image)
            self.display_predictions(predictions)

    def display_image(self, image):
        image.thumbnail((400, 400))
        tk_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=tk_image, text="")
        self.image_label.image = tk_image

    def display_predictions(self, predictions):
        result_text = "\n".join([f"{label}: {score:.4f}" for label, score in predictions.items()])
        self.result_label.config(text=result_text)

# Initialize the Tkinter window and run the app
if __name__ == "__main__":
    classifier_app = ImageClassificationApp()
    root = tk.Tk()
    gui = ImageClassificationGUI(root, classifier_app)
    root.mainloop()
