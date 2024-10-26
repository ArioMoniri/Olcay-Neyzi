import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
from datetime import datetime, date

girl_image_url = "https://raw.githubusercontent.com/ArioMoniri/Olcay-Neyzi/Free Image Cropper female.png"
boy_image_url = "https://raw.githubusercontent.com/ArioMoniri/Olcay-Neyzi/Free Image Cropper male.png"

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
    age_left, age_right = 294, 2088
    years_span = 19 - 1  # From 1 to 19 years
    total_pixels = age_right - age_left
    months_from_start = (age - 1) * 12  # Convert to months from 1 year start
    pixels_per_quarter = 25  # 25 pixels per 3 months
    pixels_per_month = pixels_per_quarter / 3
    return int(age_left + (months_from_start * pixels_per_month))

def girl_height_to_pixel(height):
    height_bottom, height_top = 2299, 167  # Using left side values
    height_min, height_max = 23.75, 180  # Height range in cm
    total_pixels = height_bottom - height_top
    total_height_range = height_max - height_min
    pixels_per_unit = 34 / 2.5  # 34 pixels per 2.5 cm
    return int(height_bottom - ((height - height_min) * pixels_per_unit))

def girl_weight_to_pixel(weight):
    weight_bottom, weight_top = 3036, 988  # Using right side values
    weight_min, weight_max = 0, 115  # Weight range in kg
    total_pixels = weight_bottom - weight_top
    pixels_per_unit = 45 / 2.5  # 45 pixels per 2.5 kg
    return int(weight_bottom - (weight * pixels_per_unit))

def boy_age_to_pixel(age):
    age_left, age_right = 294, 2088
    years_span = 19 - 1  # From 1 to 19 years
    total_pixels = age_right - age_left
    months_from_start = (age - 1) * 12  # Convert to months from 1 year start
    pixels_per_quarter = 25  # 25 pixels per 3 months
    pixels_per_month = pixels_per_quarter / 3
    return int(age_left + (months_from_start * pixels_per_month))

def boy_height_to_pixel(height):
    height_bottom, height_top = 2304, 167  # Using left side values
    height_min, height_max = 15.625, 195  # Height range in cm
    total_pixels = height_bottom - height_top
    pixels_per_unit = 30 / 2.5  # 30 pixels per 2.5 cm
    return int(height_bottom - ((height - height_min) * pixels_per_unit))

def boy_weight_to_pixel(weight):
    weight_bottom, weight_top = 3034, 981  # Using right side values
    weight_min, weight_max = 0, 143  # Weight range in kg
    pixels_per_unit = 36 / 2.5  # 36 pixels per 2.5 kg
    return int(weight_bottom - (weight * pixels_per_unit))

def save_and_download(img, format, dpi=None):
    buf = BytesIO()
    if format.lower() == "tiff":
        img.save(buf, format="TIFF", dpi=(dpi, dpi))
    else:
        img.save(buf, format=format.upper())
    buf.seek(0)
    return buf

st.title("Türk Çocuklarının Persentil Büyüme Eğrileri")

gender = st.radio("Cinsiyet", ["Kız", "Erkek"])

# Update the main code's input ranges
if gender == "Kız":
    img = load_image(girl_image_url)
    age_to_pixel = girl_age_to_pixel
    height_to_pixel = girl_height_to_pixel
    weight_to_pixel = girl_weight_to_pixel
    height_min, height_max = 23.75, 180.0
    weight_min, weight_max = 0.0, 115.0  # Updated weight range for girls
else:
    img = load_image(boy_image_url)
    age_to_pixel = boy_age_to_pixel
    height_to_pixel = boy_height_to_pixel
    weight_to_pixel = boy_weight_to_pixel
    height_min, height_max = 15.625, 195.0
    weight_min, weight_max = 0.0, 143.0  # Updated weight range for boys

birth_date = st.date_input("Doğum Tarihi", min_value=date(2000, 1, 1), max_value=date.today())

# Muayene bilgilerini saklamak için bir liste
if 'exams' not in st.session_state:
    st.session_state.exams = []

# Yeni muayene ekleme
st.subheader("Yeni Muayene Ekle")
exam_date = st.date_input("Muayene Tarihi", min_value=birth_date, max_value=date.today())
height = st.number_input("Boy (cm)", min_value=height_min, max_value=height_max, step=2.5)
weight = st.number_input("Ağırlık (kg)", min_value=weight_min, max_value=weight_max, step=1.0)

if st.button("Muayene Ekle"):
    st.session_state.exams.append({"date": exam_date, "height": height, "weight": weight})
    st.success("Muayene başarıyla eklendi!")

# Mevcut muayeneleri göster ve düzenleme/silme seçenekleri
st.subheader("Mevcut Muayeneler")
updated_exams = st.session_state.exams.copy()  # Mevcut muayenelerin bir kopyasını oluştur
for i, exam in enumerate(st.session_state.exams):
    col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])
    with col1:
        st.write(f"Tarih: {exam['date']}")
    with col2:
        new_height = st.number_input(f"Boy {i}", value=exam['height'], min_value=height_min, max_value=height_max, step=2.5, key=f"height_{i}")
    with col3:
        new_weight = st.number_input(f"Ağırlık {i}", value=exam['weight'], min_value=weight_min, max_value=weight_max, step=1.0, key=f"weight_{i}")
    with col4:
        if st.button("Güncelle", key=f"update_{i}"):
            updated_exams[i]['height'] = new_height
            updated_exams[i]['weight'] = new_weight
            st.success(f"Muayene {i+1} güncellendi!")
    with col5:
        if st.button("Sil", key=f"delete_{i}"):
            del updated_exams[i]
            st.success(f"Muayene {i+1} silindi!")

# Güncellenmiş muayene listesini session state'e kaydet
st.session_state.exams = updated_exams

# Etiketleme seçenekleri
label_option = st.radio("Nokta Etiketleme Seçeneği", 
                        ["Muayene Numarası", "Muayene Tarihi", "Özel Etiket", "Etiket Yok"])

if label_option == "Özel Etiket":
    custom_label = st.text_input("Özel Etiket Girin")

# Nokta rengi ve boyutu seçimi
col1, col2 = st.columns(2)
with col1:
    point_color = st.selectbox("Nokta rengi seçin", 
                               ["Siyah", "Kırmızı", "Mavi", "Yeşil", "Mor"],
                               format_func=lambda x: {"Siyah": "⚫", "Kırmızı": "🔴", "Mavi": "🔵", "Yeşil": "🟢", "Mor": "🟣"}[x])
with col2:
    point_size = st.slider("Nokta boyutu seçin", min_value=1, max_value=10, value=5)

# Renk seçimini İngilizce'ye çevir (PIL için)
color_map = {"Siyah": "black", "Kırmızı": "red", "Mavi": "blue", "Yeşil": "green", "Mor": "purple"}
selected_color = color_map[point_color]

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
        img_with_points = plot_point(img_with_points, age_pixel_x, height_pixel_y, color=selected_color, size=point_size, label=label)
        
        # Ağırlık-yaş noktasını çiz
        img_with_points = plot_point(img_with_points, age_pixel_x, weight_pixel_y, color=selected_color, size=point_size, label=label)
    
    st.session_state.img_with_points = img_with_points

# Eğer grafik oluşturulduysa, her zaman göster
if 'img_with_points' in st.session_state:
    st.image(st.session_state.img_with_points, caption="Büyüme Eğrisi Üzerinde İşaretlenmiş Noktalar", use_column_width=True)

    export_as = st.selectbox("İndirme formatını seçin", ["JPG", "PNG", "TIFF"])
    
    if export_as == "TIFF":
        dpi = st.slider("TIFF için DPI seçin", min_value=100, max_value=1200, value=600, step=50)
    
    if export_as == "JPG":
        buffer = save_and_download(st.session_state.img_with_points, "jpeg")
        st.download_button("JPG Olarak İndir", buffer, file_name='buyume_egrisi.jpg', mime='image/jpeg')
    elif export_as == "PNG":
        buffer = save_and_download(st.session_state.img_with_points, "png")
        st.download_button("PNG Olarak İndir", buffer, file_name='buyume_egrisi.png', mime='image/png')
    elif export_as == "TIFF":
        buffer = save_and_download(st.session_state.img_with_points, "tiff", dpi=dpi)
        st.download_button("TIFF Olarak İndir", buffer, file_name='buyume_egrisi.tiff', mime='image/tiff')

