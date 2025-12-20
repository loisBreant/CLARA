import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import kagglehub
import os

try:
    model_path = kagglehub.model_download("sanchris/breast-cancer-detection-cnnrnn/tensorFlow2/updated") + "/cnn_rnn_model_1.h5"
    model = tf.keras.models.load_model(model_path)
    img_height, img_width = 128, 128
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def predict_single_image(image_path, model=model):
    if model is None:
        return "Error: Model not loaded."

    if not os.path.exists(image_path):
        return f"Error: File not found at {image_path}"

    try:
        # Preprocessing
        img = image.load_img(image_path, target_size=(img_height, img_width))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        
        # Prediction
        prediction_prob = model.predict(img_array, verbose=0)
        score = prediction_prob[0][0]
        
        # Interpretation
        if score > 0.5:
            label = "Malignant Mass (Cancer)"
            confidence = score
        else:
            label = "Benign Mass (Non-Cancer)"
            confidence = 1 - score
            
        return f"{label} (Confiance: {confidence:.2%})"
        
    except Exception as e:
        return f"Error during classification: {e}"

def classification_tool(image_path: str):
    if image_path.startswith("/"):
        image_path = image_path.lstrip("/")
    return predict_single_image(image_path)

