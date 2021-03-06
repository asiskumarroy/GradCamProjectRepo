from flask import Flask, render_template, redirect
from flask.globals import request

from utils import predict

from PIL import Image
import io
import os

from torchvision import models
import torch

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

prediction_content = [{
    'name': 'Melanocytic nevi',
    'desc': 'Melanocytic nevi are benign neoplasms of melanocytes and appear in a myriad of variants, which all are included in our series. The variants may differ significantly from a dermatoscopic point of view.'
}, {
    'name': 'Benign keratosis',
    'desc': 'It is a generic class that includes seborrheic ker- atoses ("senile wart"), solar lentigo - which can be regarded a flat variant of seborrheic keratosis - and lichen-planus like keratoses (LPLK), which corresponds to a seborrheic keratosis or a solar lentigo with inflammation and regression. The three subgroups may look different dermatoscop- ically, but we grouped them together because they are similar biologically and often reported under the same generic term histopathologically. From a dermatoscopic view, lichen planus-like keratoses are especially challeng- ing because they can show morphologic features mimicking melanoma and are often biopsied or excised for diagnostic reasons.'
}, {
    'name': 'Melanoma',
    'desc': 'Melanoma is a malignant neoplasm derived from melanocytes that may appear in different variants. If excised in an early stage it can be cured by simple surgical excision. Melanomas can be invasive or non-invasive (in situ). We included all variants of melanoma including melanoma in situ, but did exclude non-pigmented, subungual, ocular or mucosal melanoma.'
}]

# Load Model
model_ft = models.vgg19_bn()
num_ftrs = model_ft.classifier[6].in_features
model_ft.classifier[6] = torch.nn.Linear(num_ftrs, 3)
model_ft.load_state_dict(torch.load(
    './best_model_vgg19.pt', map_location=torch.device('cpu')))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/result', methods=['GET', 'POST'])
def result():
    print('request recieved')
    if 'photo' in request.files and allowed_file(request.files['photo'].filename):
        # Get The File into bytes and convert into PIL Image
        file = request.files['photo']
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        pred, pngImageB64String = predict(img, model_ft)
        return render_template('result.html', image=pngImageB64String, content=prediction_content[pred])

    else:
        return redirect('/')


@app.route('/demo/<number>', methods=['GET'])
def demo(number):
    filename = f'./static/demo/{number}.jpg'
    if os.path.exists(filename):
        img = Image.open(filename).convert('RGB')
        pred, pngImageB64String = predict(img, model_ft)
        return render_template('result.html', image=pngImageB64String, content=prediction_content[pred])
    else:
        return 'no such file'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
