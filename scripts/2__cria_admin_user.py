#!/usr/bin/python

import requests

url='http://lbgenerator.herokuapp.com/user'
params={
    "api_key": "required", 
    "id_user": "admin", 
    "name_user":"Administrador", 
    "passwd_user":"admin", 
    "email_user":"admin@lightbase.com.br"
}

response=requests.post(url, params=params)

print("Resposta do LBGenerator: ")
print(response.text)
