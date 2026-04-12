import qrcode

# 这里替换成你部署后的 Streamlit 链接
url = "https://xunyi-dashboard-m2fwgjuarcdu7pbt3ssdju.streamlit.app"

# 生成二维码
qr = qrcode.make(url)

# 保存二维码为图片
qr.save("qrcode.png")

print("二维码已生成并保存为 qrcode.png")