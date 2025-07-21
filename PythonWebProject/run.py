from  flask import  Flask
import numpy as np

app = Flask(__name__)



if __name__ == '__main__':
    app.run(debug=True)
    print(np.random.rand(3,3))