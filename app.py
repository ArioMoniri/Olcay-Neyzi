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
    
    # Grafik sınırları (piksel olarak)
    left_border = 60
    right_border = img_width - 60
    top_border = 60
    bottom_border = img_height - 80
    middle_line = img_height // 2
    
    chart_width = (right_border - left_border) // 2
    
    # Yaş için piksel konumunu hesapla
    def age_to_pixel(age):
        if age <= 6:
            return map_value_to_pixel(age, 0, 6, left_border, left_border + chart_width // 2)
        else:
            return map_value_to_pixel(age, 6, 18, left_border + chart_width // 2, left_border + chart_width)
    
    age_pixel_x = age_to_pixel(age)

    # Boy için piksel konumunu hesapla
    def height_to_pixel(height):
        return map_value_to_pixel(height, 40, 180, middle_line - 30, top_border)

    height_pixel_y = height_to_pixel(height)
    
    # Ağırlık için piksel konumunu hesapla
    def weight_to_pixel(weight):
        return map_value_to_pixel(weight, 0, 50, bottom_border, middle_line)

    weight_pixel_y = weight_to_pixel(weight)
    
    # Cinsiyet için x pozisyonu
    gender_offset = 0 if gender == "Kız" else chart_width
    
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
