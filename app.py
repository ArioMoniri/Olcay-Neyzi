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

def interpolate(x, x1, x2, y1, y2):
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

st.title("Türk Çocuklarının Persentil Büyüme Eğrileri")

img = load_image(image_url)

gender = st.radio("Cinsiyet", ["Kız", "Erkek"])
age = st.number_input("Yaş (0-18)", min_value=0.0, max_value=18.0, step=0.1)
height = st.number_input("Boy (cm)", min_value=40.0, max_value=200.0, step=0.1)
weight = st.number_input("Ağırlık (kg)", min_value=0.0, max_value=100.0, step=0.1)

if st.button("Grafikte Göster"):
    # Calibrated Age -> X pixel calculation
    age_points = [
        (0, 125), (1, 128), (6, 188), (18, 99), (19, 130)  # Calibrated based on new data
    ]
    
    def age_to_pixel(age):
        for i in range(len(age_points) - 1):
            if age_points[i][0] <= age <= age_points[i+1][0]:
                return interpolate(age, age_points[i][0], age_points[i+1][0], 
                                   age_points[i][1], age_points[i+1][1])
        return age_points[-1][1]  # 18 yaş üstü için son nokta
    
    # Calibrated Height -> Y pixel calculation
    height_points = [
        (55, 209), (80, 111), (140, 166), (180, 64)  # Based on the new calibrated data
    ]
    
    def height_to_pixel(height):
        for i in range(len(height_points) - 1):
            if height_points[i][0] <= height <= height_points[i+1][0]:
                return interpolate(height, height_points[i][0], height_points[i+1][0], 
                                   height_points[i][1], height_points[i+1][1])
        return height_points[-1][1] if height > 180 else height_points[0][1]
    
    # Calibrated Weight -> Y pixel calculation (for the lower part)
    weight_points = [
        (0, 125), (5, 162), (50, 188), (77.5, 174)  # Based on the updated calibration
    ]
    
    def weight_to_pixel(weight):
        for i in range(len(weight_points) - 1):
            if weight_points[i][0] <= weight <= weight_points[i+1][0]:
                return interpolate(weight, weight_points[i][0], weight_points[i+1][0], 
                                   weight_points[i][1], weight_points[i+1][1])
        return weight_points[-1][1] if weight > 77.5 else weight_points[0][1]
    
    # Compute the corresponding pixel values for age, height, and weight
    age_pixel_x = age_to_pixel(age)
    height_pixel_y = height_to_pixel(height)
    weight_pixel_y = weight_to_pixel(weight)
    
    # Offset for gender-specific graphs
    gender_offset = 0 if gender == "Kız" else 320  # Roughly half the graph width
    
    # Plot the height-age point (upper graph for height)
    img_with_point = plot_point(img.copy(), age_pixel_x + gender_offset, height_pixel_y, color="blue")
    
    # Plot the weight-age point (lower graph for weight, offset by 210 pixels for the lower section)
    img_with_point = plot_point(img_with_point, age_pixel_x + gender_offset, weight_pixel_y + 210, color="green")
    
    st.image(img_with_point, caption="Büyüme Eğrisi Üzerinde İşaretlenmiş Noktalar", use_column_width=True)
    
    # Enable download of the marked image
    buf = BytesIO()
    img_with_point.save(buf, format="JPEG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="Grafiği İndir",
        data=byte_im,
        file_name="buyume_egrisi.jpg",
        mime="image/jpeg"
    )
