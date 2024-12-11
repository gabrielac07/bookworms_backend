from flask import Blueprint
from flask_restful import Api, Resource # used for REST API building

student_api = Blueprint('student_api', __name__,
                   url_prefix='/api')

# API docs https://flask-restful.readthedocs.io/en/latest/
api = Api(student_api)

class StudentAPI:        
    class _Maryam(Resource): 
        def get(self):
           # implement the get method 
           pass
    
    class _Katherine(Resource): 
        def get(self):
           # implement the get method 
           pass

    class _Avika(Resource): 
        def get(self):
           # implement the get method 
           pass

    class _Aditi(Resource): 
        def get(self):
           # implement the get method 
           pass

    class _Gabi(Resource): 
        def get(self):
           # implement the get method 
           pass

    class _Soumini(Resource): 
        def get(self):
           # implement the get method 
           pass
           
    # building RESTapi endpoint
    api.add_resource(_Maryam, '/student/maryam')          
    api.add_resource(_Katherine, '/student/katherine')
    api.add_resource(_Avika, '/student/avika')
    api.add_resource(_Aditi, '/student/aditi')
    api.add_resource(_Gabi, '/student/gabi')   
    api.add_resource(_Soumini, '/student/soumini')     