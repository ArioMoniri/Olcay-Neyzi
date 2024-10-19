import streamlit as st
import requests
from PIL import Image, ImageDraw
from io import BytesIO
import numpy as np

image_url = "https://raw.githubusercontent.com/ArioMoniri/Olcay-Neyzi/bfe8b7c31670f7166370e5eafa2b6d6504258497/ca3f478a-5f03-4028-bdcb-382178bfc56b.jpeg"

def load_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def map_value_to_pixel(value, min_val, max_val, min_pixel, max_pixel):
    return int(min_pixel + (value - min_val) / (max_val - min_val) * (max_pixel - min_pixel))

def plot_point(img, x, y, color="red", size=5):
    draw = ImageDraw.Draw(img)
    draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
    return img

st.title("Türk Çocuklarının Persentil Büyüme Eğrileri")

img = load_image(image_url)

gender = st.radio("Cinsiyet", ["Kız", "Erkek"])
age = st.number_input("Yaş (0-18.75)", min_value=0.0, max_value=18.75, step=0.25)
height = st.number_input("Boy (cm)", min_value=55.0, max_value=180.0, step=0.5)
weight = st.number_input("Ağırlık (kg)", min_value=2.0, max_value=100.0, step=0.1)

if st.button("Grafikte Göster"):
    img_width, img_height = img.size
    
    # Yaş grafiği sınırları
    age_left = 61
    age_right = 874
    age_bottom = 1329
    
    # Boy grafiği sınırları
    height_left = 61
    height_right = 873
    height_top = 60
    height_bottom = 914
    
    # Ağırlık grafiği sınırları
    weight_left = 61
    weight_right = 872
    weight_top = 740
    weight_bottom = 1331
    
    # Yaş için piksel konumunu hesapla
    def age_to_pixel(age):
        return int(age_left + (age * 44) / 0.75)  # 11 piksel her 3 ay için
    
    age_pixel_x = age_to_pixel(age)
    
    # Boy için piksel konumunu hesapla
    def height_to_pixel(height):
        return int(height_bottom - ((height - 55) * 17) / 2.5)  # 17 piksel her 2.5 cm için
    
    height_pixel_y = height_to_pixel(height)
    
    # Ağırlık için piksel konumunu hesapla
    def weight_to_pixel(weight):
        # Bu fonksiyonu ağırlık değerlerine göre ayarlamanız gerekebilir
        return map_value_to_pixel(weight, 0, 100, weight_bottom, weight_top)
    
    weight_pixel_y = weight_to_pixel(weight)
    
    # Cinsiyet için x pozisyonu
    gender_offset = 0 if gender == "Kız" else img_width // 2
    
    # Boy-yaş noktasını çiz (üst grafik)
    img_with_point = plot_point(img.copy(), age_pixel_x + gender_offset, height_pixel_y, color="blue")
    
    # Ağırlık-yaş noktasını çiz (alt grafik)
    img_with_point = plot_point(img_with_point, age_pixel_x + gender_offset, weight_pixel_y, color="green")
    
    st.image(img_with_point, caption="Büyüme Eğrisi Üzerinde İşaretlenmiş Noktalar", use_column_width=True)
    
    buf = BytesIO()
    img_with_point.save(buf, format="JPEG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="Grafiği İndir",
        data=byte_im,
        file_name="buyume_egrisi.jpg",
        mime="image/jpeg"
    )
