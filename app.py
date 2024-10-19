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
    
    # Grafik köşe noktaları
    left_up = (77, 75, 70)
    right_up = (87, 80, 77)
    left_down = (135, 128, 121)
    right_down = (130, 124, 120)
    
    # Yaş için piksel hesaplaması
    age_pixels_per_box = 30  # 79 - 49 = 30 piksel (bir kutu)
    months_per_box = 2.5
    pixels_per_month = age_pixels_per_box / months_per_box
    
    def age_to_pixel(age):
        months = age * 12
        x_offset = left_up[0]
        x_pixel = x_offset + (months * pixels_per_month)
        return min(x_pixel, right_up[0])
    
    # Boy için piksel hesaplaması
    height_pixels_per_box = 4  # 212 - 208 = 4 piksel (bir kutu)
    cm_per_box = 2.5
    pixels_per_cm = height_pixels_per_box / cm_per_box
    
    def height_to_pixel(height):
        y_offset = left_down[1]
        y_pixel = y_offset - ((height - 55) * pixels_per_cm)  # 55 cm grafiğin alt sınırı
        return max(y_pixel, left_up[1])
    
    # Ağırlık için piksel hesaplaması
    weight_pixels_per_box = 4  # 212 - 208 = 4 piksel (bir kutu)
    kg_per_box = 1
    pixels_per_kg = weight_pixels_per_box / kg_per_box
    
    def weight_to_pixel(weight):
        y_offset = left_down[1]
        y_pixel = y_offset - (weight * pixels_per_kg)
        return max(y_pixel, (left_down[1] + left_up[1]) / 2)
    
    age_pixel_x = age_to_pixel(age)
    height_pixel_y = height_to_pixel(height)
    weight_pixel_y = weight_to_pixel(weight)
    
    # Cinsiyet için x pozisyonu
    gender_offset = 0 if gender == "Kız" else (right_up[0] - left_up[0])
    
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
