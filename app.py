import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
from datetime import datetime, date

girl_image_url = "https://raw.githubusercontent.com/ArioMoniri/Olcay-Neyzi/bfe8b7c31670f7166370e5eafa2b6d6504258497/ca3f478a-5f03-4028-bdcb-382178bfc56b.jpeg"
boy_image_url = "https://raw.githubusercontent.com/ArioMoniri/Olcay-Neyzi/c64087ff36b6eac92d5c77af8b9fe498e59f1c76/WhatsApp%20Image%202024-10-19%20at%2021.45.55.jpeg"

def load_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def plot_point(img, x, y, color="black", size=5, label=None, font_size=12):
    draw = ImageDraw.Draw(img)
    draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
    if label:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        draw.text((x+size+2, y-size-2), label, fill=color, font=font)
    return img

def calculate_age(born, exam_date):
    age = exam_date.year - born.year - ((exam_date.month, exam_date.day) < (born.month, born.day))
    months = (exam_date.month - born.month) % 12 + (12 if exam_date.day < born.day else 0)
    return age + months / 12

# Kız grafiği için fonksiyonlar
def girl_age_to_pixel(age):
    age_left, age_right = 61, 874
    total_months = (18.75 - 0.25) * 12  # 18.5 yıl = 222 ay
    total_pixels = age_right - age_left  # 813 piksel
    months = (age - 0.25) * 12  # Girilen yaşı aya çevir
    return int(age_left + (months * total_pixels) / total_months)

def girl_height_to_pixel(height):
    height_bottom, height_top = 914, 60
    return int(height_bottom - ((height - 55) * 17) / 2.5)  # 17 piksel her 2.5 cm için

def girl_weight_to_pixel(weight):
    weight_bottom, weight_top = 1331, 740
    return int(weight_bottom - (weight * (weight_bottom - weight_top) / 50))

# Erkek grafiği için fonksiyonlar
def boy_age_to_pixel(age):
    age_left, age_right = 96, 900
    total_months = (18.75 - 0.25) * 12  # 18.5 yıl = 222 ay
    total_pixels = age_right - age_left
    months = (age - 0.25) * 12  # Girilen yaşı aya çevir
    return int(age_left + (months * total_pixels) / total_months)

def boy_height_to_pixel(height):
    height_bottom, height_top = 951, 63
    return int(height_bottom - ((height - 57.5) * 17) / 2.5)  # 17 piksel her 2.5 cm için

def boy_weight_to_pixel(weight):
    weight_bottom, weight_top = 1339, 776
    return int(weight_bottom - (weight * 6))  # Her kilo için 6 pixel

st.title("Türk Çocuklarının Persentil Büyüme Eğrileri")

gender = st.radio("Cinsiyet", ["Kız", "Erkek"])

if gender == "Kız":
    img = load_image(girl_image_url)
    age_to_pixel = girl_age_to_pixel
    height_to_pixel = girl_height_to_pixel
    weight_to_pixel = girl_weight_to_pixel
    height_min, height_max = 55.0, 180.0
    weight_min, weight_max = 2.0, 50.0
else:
    img = load_image(boy_image_url)
    age_to_pixel = boy_age_to_pixel
    height_to_pixel = boy_height_to_pixel
    weight_to_pixel = boy_weight_to_pixel
    height_min, height_max = 57.5, 185.0
    weight_min, weight_max = 2.0, 98.0

birth_date = st.date_input("Doğum Tarihi", min_value=date(2000, 1, 1), max_value=date.today())

# Muayene bilgilerini saklamak için bir liste
if 'exams' not in st.session_state:
    st.session_state.exams = []

# Yeni muayene ekleme
st.subheader("Yeni Muayene Ekle")
exam_date = st.date_input("Muayene Tarihi", min_value=birth_date, max_value=date.today())
height = st.number_input("Boy (cm)", min_value=height_min, max_value=height_max, step=2.0)
weight = st.number_input("Ağırlık (kg)", min_value=weight_min, max_value=weight_max, step=1.0)

if st.button("Muayene Ekle"):
    st.session_state.exams.append({"date": exam_date, "height": height, "weight": weight})
    st.success("Muayene başarıyla eklendi!")

# Mevcut muayeneleri göster ve düzenleme/silme seçenekleri
st.subheader("Mevcut Muayeneler")
for i, exam in enumerate(st.session_state.exams):
    col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])
    with col1:
        st.write(f"Tarih: {exam['date']}")
    with col2:
        new_height = st.number_input(f"Boy {i}", value=exam['height'], key=f"height_{i}")
    with col3:
        new_weight = st.number_input(f"Ağırlık {i}", value=exam['weight'], key=f"weight_{i}")
    with col4:
        if st.button("Güncelle", key=f"update_{i}"):
            st.session_state.exams[i]['height'] = new_height
            st.session_state.exams[i]['weight'] = new_weight
            st.success(f"Muayene {i+1} güncellendi!")
    with col5:
        if st.button("Sil", key=f"delete_{i}"):
            st.session_state.exams.pop(i)
            st.success(f"Muayene {i+1} silindi!")
            st.experimental_rerun()

# Etiketleme seçenekleri
label_option = st.radio("Nokta Etiketleme Seçeneği", 
                        ["Muayene Numarası", "Muayene Tarihi", "Özel Etiket", "Etiket Yok"])

if label_option == "Özel Etiket":
    custom_label = st.text_input("Özel Etiket Girin")

if st.button("Grafikte Göster"):
    img_with_points = img.copy()
    
    for i, exam in enumerate(st.session_state.exams):
        age = calculate_age(birth_date, exam['date'])
        age_pixel_x = age_to_pixel(age)
        height_pixel_y = height_to_pixel(exam['height'])
        weight_pixel_y = weight_to_pixel(exam['weight'])
        
        if label_option == "Muayene Numarası":
            label = str(i+1)
        elif label_option == "Muayene Tarihi":
            label = exam['date'].strftime("%d/%m/%Y")
        elif label_option == "Özel Etiket":
            label = custom_label
        else:
            label = None
        
        # Boy-yaş noktasını çiz
        img_with_points = plot_point(img_with_points, age_pixel_x, height_pixel_y, label=label)
        
        # Ağırlık-yaş noktasını çiz
        img_with_points = plot_point(img_with_points, age_pixel_x, weight_pixel_y, label=label)
    
    st.image(img_with_points, caption="Büyüme Eğrisi Üzerinde İşaretlenmiş Noktalar", use_column_width=True)
    
    buf = BytesIO()
    img_with_points.save(buf, format="JPEG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="Grafiği İndir",
        data=byte_im,
        file_name="buyume_egrisi.jpg",
        mime="image/jpeg"
    )
