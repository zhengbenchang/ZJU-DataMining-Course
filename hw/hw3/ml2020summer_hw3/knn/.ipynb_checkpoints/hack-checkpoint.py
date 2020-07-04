import numpy as np

import knn
import show_image
import extract_image

def hack(img_name):
    '''
    HACK Recognize a CAPTCHA image
      Inputs:
          img_name: filename of image
      Outputs:
          digits: 1x5 matrix, 5 digits in the input CAPTCHA image.
    '''
    data = np.load('hack_data.npz')

    # YOUR CODE HERE (you can delete the following code as you wish)
    x_train = data['x_train']
    y_train = data['y_train']

    # begin answer
    image = extract_image.extract_image(img_name)
    digits = knn.knn(image,x_train,y_train,5)
    show_image.show_image(image)
    # end answer
    
    return digits
