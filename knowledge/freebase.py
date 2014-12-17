'''
Created on 3/11/2014

@author: aurelio
'''

import json
import urllib.request
import urllib.parse
from pprint import pprint

#info on freebase
# https://developers.google.com/freebase/v1/
api_key = 'AIzaSyCEKLXRIysevTb5RtJbv8rHFF67B5VULpM'
service_url = 'https://www.googleapis.com/freebase/v1/search'

def bringNec(word):
    word = word.replace('_', ' ')
    params = {
            'query': word,
            'key': api_key,
            # 'filter':'(any type:/people/person type:/location/citytown)',
            'lang':'es',
            'output':'(type)',
            'output':'(description:wikipedia)',
            'limit':1
    }
    # pprint.pprint(params)
    url = service_url + '?' + urllib.parse.urlencode(params)
    # print(url)
    resp = urllib.request.urlopen(url).read()
    resp = resp.decode()
    response = json.loads(resp)
    # pprint(response)
    hay_algo = False
    if len(response['result']):
        primero = response['result'][0]
        hay_algo = True
    if hay_algo:
        retorno = {}
        # pprint(primero)
        nombre = primero['name']
        if 'notable' in primero:
            propiedad = primero['notable']['name']
        else:
            propiedad = ''
        if 'output' in primero:
            if 'description:wikipedia' in primero['output']:
                if '/common/topic/description' in primero['output']['description:wikipedia']:
                    if len(primero['output']['description:wikipedia']) > 0:
                        significado = primero['output']['description:wikipedia']['/common/topic/description'][0]
                    else:
                        significado = ''
                else:
                    significado = ''
        res = [v for (k,v) in notab.items() if k == propiedad ]
        if res:
            if primero['score'] > 99:
                retorno['res'] = res[0]
                retorno['nombre'] = nombre
                retorno['propiedad'] = propiedad
                retorno['significado'] = significado
                retorno['score'] = primero['score']
                return retorno
            else:
                return None
        else:
            return None
    else:
        return None

file = 'notables.csv'
notab = {}
with open(file, 'rt') as f:
    lines = f.readlines()
    for line in lines:
        line = line[:-1].split(',')
        if line[1]:
            notab[line[0]] = line[1]
      
        

# bringNec('Iglesia')