from PIL import Image
from pdf2image import convert_from_path
from pytesseract import image_to_string
from numpy import array
import configs

def extract_text(filePath):
    poppler = configs.poppler
    doc = convert_from_path(filePath, poppler_path= poppler) 
    txt_all= ""
    for page_number, page_data in enumerate(doc):
        img_array = array(page_data)
        #imgx = Image.fromarray(page_data)
        txt = image_to_string(img_array, lang= "ron")

        txt_all += f"\n{txt}\n"
    return txt_all
