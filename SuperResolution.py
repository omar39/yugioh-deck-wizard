import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import tensorflow_hub as hub
import cv2

class SuperResolution:
    def __init__(self, img_path):
        self.img = cv2.imread(img_path)
        self.image_plot = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        esrgn_path = "https://tfhub.dev/captain-pool/esrgan-tf2/1"
        self.model = hub.load(esrgn_path)

    def prepare_image(self):
        image_size = (tf.convert_to_tensor(self.image_plot.shape[:-1]) // 4) * 4
        cropped_image = tf.image.crop_to_bounding_box(self.img, 0, 0, image_size[0], image_size[1])
        preprocessed_image = tf.cast(cropped_image, tf.float32)
        return tf.expand_dims(preprocessed_image, 0)

        
    def srmodel(self, image_path:str):
        preprocessed_image = self.prepare_image()  # Preprocess the LR Image
        new_image = self.model(preprocessed_image)  # Runs the model
        sr_image = tf.squeeze(new_image)
        sr_image = tf.cast(sr_image, tf.uint8).numpy()
        sr_image = cv2.cvtColor(sr_image, cv2.COLOR_BGR2RGB)
        return cv2.imwrite(image_path, cv2.cvtColor(sr_image, cv2.COLOR_RGB2BGR))


# write a test from an image on local path

# img_path = 'D:\\YUGIOH Deck Wizard\\yugioh-deck-wizard\\Images Database\\anime\\27551.jpg'
# sr = SuperResolution(img_path)
# image = sr.srmodel('sr_test.jpg')
# # save the image
