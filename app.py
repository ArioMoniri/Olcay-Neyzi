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
age = st.number_input("Yaş (0-18)", min_value=0.0, max_value=18.0, step=0.1)
height = st.number_input("Boy (cm)", min_value=40.0, max_value=200.0, step=0.1)
weight = st.number_input("Ağırlık (kg)", min_value=2.0, max_value=100.0, step=0.1)

if st.button("Grafikte Göster"):
    img_width, img_height = img.size
    x_offset = 60
    y_offset_top = 60
    y_offset_bottom = 80
    chart_width = (img_width - 2 * x_offset) // 2
    chart_height = img_height - y_offset_top - y_offset_bottom
    
    # Yaş için piksel konumunu hesapla (düzeltilmiş)
    if age <= 6:
        age_pixel_x = map_value_to_pixel(age, 0, 6, x_offset, x_offset + chart_width // 2)
    else:
        age_pixel_x = map_value_to_pixel(age, 6, 18, x_offset + chart_width // 2, x_offset + chart_width)

    # Boy için piksel konumunu hesapla
    height_pixel_y = map_value_to_pixel(height, 55, 180, img_height - y_offset_bottom, y_offset_top)
    
    # Ağırlık için piksel konumunu hesapla
    weight_pixel_y = map_value_to_pixel(weight, 0, 80, img_height - y_offset_bottom, img_height // 2)
    
    # Cinsiyet için x pozisyonu
    gender_offset = 0 if gender == "Kız" else chart_width
    
    # Boy-yaş noktasını çiz
    img_with_point = plot_point(img.copy(), age_pixel_x + gender_offset, height_pixel_y, color="blue")
    
    # Ağırlık-yaş noktasını çiz
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
