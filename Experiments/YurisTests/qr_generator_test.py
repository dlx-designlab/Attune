import uuid
import qrcode


myRandomId = uuid.uuid4()
print('Your Random UUID: ' + str(myRandomId))
img = qrcode.make(myRandomId)
img.show()