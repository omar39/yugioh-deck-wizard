import cv2
import numpy as np
import os
import urllib.request

class SuperResolution:
    def __init__(self, scale_factor=2):
        self.scale_factor = scale_factor
        self.model_path = f"EDSR_x{scale_factor}.pb"
        self.model_url = self._get_model_url()
        
        # Download and load EDSR model
        self._download_model()
        self.sr = cv2.dnn_superres.DnnSuperResImpl_create()
        self.sr.readModel(self.model_path)
        self.sr.setModel("edsr", scale_factor)
        
        print(f"EDSR x{scale_factor} model loaded successfully!")
    
    def _get_model_url(self):
        """Get the download URL for EDSR model"""
        base_url = "https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/"
        return base_url + f"EDSR_x{self.scale_factor}.pb"
    
    def _download_model(self):
        """Download EDSR model if not exists"""
        if not os.path.exists(self.model_path):
            print(f"Downloading EDSR x{self.scale_factor} model...")
            try:
                urllib.request.urlretrieve(self.model_url, self.model_path)
                print("Model downloaded successfully!")
            except Exception as e:
                print(f"Error downloading model: {e}")
                raise
    
    def preprocess_image(self, img):
        """Preprocess image for better results"""
        # Apply slight denoising only
        denoised = cv2.bilateralFilter(img, 9, 75, 75)
        return denoised
    
    def postprocess_image(self, img):
        """Apply minimal post-processing without color changes"""
        # Light sharpening only
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]]) / 1.0
        
        sharpened = cv2.filter2D(img, -1, kernel)
        
        # Very light blend to avoid over-sharpening
        result = cv2.addWeighted(img, 0.8, sharpened, 0.2, 0)
        
        return result
    
    def upscale_image(self, input_path, output_path):
        """Complete EDSR super resolution pipeline"""
        print(f"Processing Yu-Gi-Oh card: {input_path}")
        
        # Load image
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not load image: {input_path}")
        
        original_shape = img.shape
        print(f"Original size: {original_shape[1]}x{original_shape[0]}")
        
        # Preprocess
        preprocessed = self.preprocess_image(img)
        
        # Apply EDSR super resolution
        print("Applying EDSR super resolution...")
        upscaled = self.sr.upsample(preprocessed)
        
        # Post-process
        enhanced = self.postprocess_image(upscaled)
        
        # Save result
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, enhanced)
        
        final_shape = enhanced.shape
        print(f"Enhanced size: {final_shape[1]}x{final_shape[0]}")
        print(f"Saved to: {output_path}")
