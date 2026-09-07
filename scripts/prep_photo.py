import cv2
import numpy as np
from rembg import remove
from PIL import Image
import sys
import os

def process_image(input_path, output_path="source-prepped.png"):
    print(f"⏳ جاري معالجة الصورة: {input_path}...")

    try:
        # 1. إزالة الخلفية
        input_img = Image.open(input_path)
        no_bg = remove(input_img)
        
        # تحويل الصورة لمصفوفة لتسهيل التعديل
        no_bg_cv = np.array(no_bg)

        # فصل قنوات الألوان والشفافية
        if no_bg_cv.shape[2] == 4:
            alpha = no_bg_cv[:, :, 3]
            rgb = no_bg_cv[:, :, :3]
        else:
            print("❌ خطأ: الصورة لا تحتوي على خلفية شفافة بعد العزل.")
            return

        # تحويل الصورة لأبيض وأسود
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        # 2. زيادة التباين (Contrast) لإبراز ملامح الوجه
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)

        # 3. دمج الصورة على خلفية بيضاء نقية
        white_bg = np.ones_like(enhanced_gray) * 255
        alpha_norm = alpha / 255.0
        final_img = (enhanced_gray * alpha_norm + white_bg * (1 - alpha_norm)).astype(np.uint8)

        # حفظ النتيجة
        cv2.imwrite(output_path, final_img)
        print(f"✅ تمت العملية بنجاح! تم حفظ الصورة كـ {output_path}")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("💡 الاستخدام: python scripts/prep_photo.py <path_to_your_photo.jpg>")
        sys.exit(1)
    
    process_image(sys.argv[1])