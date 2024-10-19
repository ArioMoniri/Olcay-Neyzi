import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from io import BytesIO

# Map to the correct image based on age and gender
def get_chart_image(age, gender):
    if gender == "Male":
        if age < 3:
            return "images/male_0_3.jpeg"  # Example image for 0-3 years boys
        else:
            return "images/male_2_18.jpeg"  # Example image for 2-18 years boys
    else:
        if age < 3:
            return "images/female_0_3.jpeg"  # Example image for 0-3 years girls
        else:
            return "images/female_2_18.jpeg"  # Example image for 2-18 years girls

# Plot the point on the selected image
def plot_point_on_chart(image_path, age, weight, height, gender):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Coordinates based on specific positions from the Neyzi charts
    # These will need to be adjusted precisely based on the graph
    x_age = int((age / 18) * img.width)  # Example calculation for X-axis (age)
    y_weight = img.height - int((weight / 100) * img.height)  # Example calculation for Y-axis (weight)
    y_height = img.height - int((height / 200) * img.height)  # Example calculation for Y-axis (height)

    # Draw weight point (example position)
    draw.ellipse((x_age-5, y_weight-5, x_age+5, y_weight+5), fill="red", outline="red")

    # Draw height point (example position)
    draw.ellipse((x_age-5, y_height-5, x_age+5, y_height+5), fill="blue", outline="blue")
    
    return img

# Streamlit app interface
st.title("Neyzi Growth Charts with Plotting")

# Inputs
age = st.slider("Select the age of the child (years)", 0, 18, 5)
gender = st.selectbox("Select Gender", ["Male", "Female"])
weight = st.number_input("Enter the weight of the child (kg)", 0.0, 100.0, 20.0)
height = st.number_input("Enter the height of the child (cm)", 0.0, 200.0, 100.0)

# Select the correct chart image
chart_image = get_chart_image(age, gender)

# Plot the input data on the chart
result_image = plot_point_on_chart(chart_image, age, weight, height, gender)

# Display the final image with the plotted point
st.image(result_image, caption=f"Growth chart for {gender}, {age} years")

# Option to download the image
buf = BytesIO()
result_image.save(buf, format="JPEG")
st.download_button("Download Growth Chart", data=buf.getvalue(), file_name="growth_chart.jpg", mime="image/jpeg")
