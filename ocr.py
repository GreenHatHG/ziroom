import re

import cv2
import easyocr

reader = easyocr.Reader(['ch_sim', 'en'])


def get_price(png_path):
    img = cv2.imread(png_path)
    x1, y1, x2, y2 = 1160, 77, 1553, 321
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    crop_img = img[y1:y2, x1:x2]

    result = reader.readtext(crop_img, detail=0)
    for item in result:
        if '/月' in item:
            pattern = r"[^/\u4e00-\u9fa5()]+"
            result = re.findall(pattern, item)
            output = "".join(result)
            price = str(output).split('+')[0]
            return price
