from PIL import Image, ImageFilter
import os, tkinter, tkinter.filedialog, tkinter.messagebox

fTyp = [("", "*")]
iDir = os.path.abspath(os.path.dirname(__file__))
file_name = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)

print(file_name)

Image = Image.open(file_name)
metadata = Image.info
print(metadata['data'])
print(metadata["LineJson"])