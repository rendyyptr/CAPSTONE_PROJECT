import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import io
import string
import time
import cv2
import numpy as np
import tensorflow as tf
import base64
from PIL import Image, ImageOps
from flask import Flask, jsonify, request
from tensorflow import keras
from keras import models


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get('file')
        if file is None or file.filename == "":
            return jsonify({"error": "no file"})

        try:
            model = models.load_model('{}/My_Model_4.h5'.format(os.getcwd()))
            img_bytes = file.read()

            images = np.array(Image.open(io.BytesIO(img_bytes)))
            gambar = cv2.cvtColor(images, cv2.COLOR_BGR2GRAY)
            gaussian = cv2.addWeighted(gambar,4, cv2.GaussianBlur( gambar , (0,0) , 426/10) ,-4 ,128)

            cv2.imwrite('{}/DR1_COBAGAUSSIAN.jpg'.format(os.getcwd()), gaussian)

            gmbr = tf.keras.preprocessing.image.load_img('{}/DR1_COBAGAUSSIAN.jpg'.format(os.getcwd()), target_size=(426,426))
            x = tf.keras.preprocessing.image.img_to_array(gmbr)
            x = x / 255
            x = np.expand_dims(x,axis=0)
            gambarr = np.vstack([x])
            kelas = model.predict(gambarr,batch_size=32)
            predicted = np.argmax(kelas)

            result = []
            if predicted == 0:
                result.append("Terindikasi Diabetes Ringan")
            if predicted == 1:
                result.append("Terindikasi Diabetes Sedang")
            if predicted == 2:
                result.append("Tidak Terindikasi Diabetes")
            if predicted == 3:
                result.append("Terindikasi Diabetes Parah")
            if predicted == 4:
                result.append("Terindikasi Diabetes Sangat Parah")
            img_64 = base64.b64encode(gambarr).decode('utf-8')
            hasil = {
                "predict" : result,
                "image" : img_64
            }
            os.remove('{}/DR1_COBAGAUSSIAN.jpg'.format(os.getcwd()))

            return jsonify(hasil)

        except Exception as e:
            return jsonify({"error": str(e)})

    return 'Eye Predict'


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))