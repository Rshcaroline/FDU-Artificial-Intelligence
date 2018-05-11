#!/usr/bin/env python
import qrcode
import PIL.Image
import socket
localIP = socket.gethostbyname(socket.gethostname())
port = 5000
img = qrcode.make('http://' + localIP + ':' + str(port))
img.save("temp_qrcode.png")
qr_code = PIL.Image.open("temp_qrcode.png")
qr_code.show()

from app import app
app.run('0.0.0.0', port=port, debug=False, threaded=True)
