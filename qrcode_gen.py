import qrcode

url = "https://你的项目名.streamlit.app"

img = qrcode.make(url)
img.save("qrcode.png")