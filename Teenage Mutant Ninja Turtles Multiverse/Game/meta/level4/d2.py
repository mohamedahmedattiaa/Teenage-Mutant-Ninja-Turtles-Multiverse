from PIL import Image
import os

# غيّر المسار هنا لمجلد الصور بتاعك
image_folder = "images"

# لف على كل الملفات في المجلد
for filename in os.listdir(image_folder):
    if filename.lower().endswith(".png"):
        filepath = os.path.join(image_folder, filename)
        try:
            img = Image.open(filepath)
            # نحفظ نسخة بدون ICC profile
            img.save(filepath, icc_profile=None)
            print(f"✔️ تم معالجة الصورة: {filename}")
        except Exception as e:
            print(f"❌ خطأ في الصورة {filename}: {e}")
