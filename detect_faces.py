import sys
import cognitive_face as CF
import cv2 as cv
from pathlib import Path
import matplotlib

KEY='aead13fb5d0c42b39b3354aea3d21ad1'
BASE_URL = 'https://japaneast.api.cognitive.microsoft.com/face/v1.0'

def detect(dir_path):
    results = {}
    for file in Path(dir_path).glob('*'):
        results[str(file)] = CF.face.detect(file)
        rect = results[str(file)][0]['faceRectangle']
        box = [rect['left'], rect['top'],
            rect['left']+rect['width'],
            rect['top']+rect['height']]
        im = cv.imread(file)
        draw = ImageDraw.Draw(im)
        draw.rectangle(box)
        matplotlib.imshow(im)
        print(box)
    return results


if __name__ == '__main__':
    CF.Key.set(KEY)
    CF.BaseUrl.set(BASE_URL)
    results = detect(sys.argv[1])
    #print(results)
