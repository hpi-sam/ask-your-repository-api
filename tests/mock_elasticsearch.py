class ElasticMock:
    def __init__(self, function, return_value):
        my_lambda = lambda **kwargs : return_value 
        setattr(self, function, my_lambda)