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
api_key = ''
service_url = 'https://www.googleapis.com/freebase/v1/search'

def bringNec(word):
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
    pprint(response)
    hay_algo = False
    if len(response['result']):
        primero = response['result'][0]
        hay_algo = True
    else:
        pprint(params)
    if hay_algo:
        # pprint.pprint(primero)
        nombre = primero['name']
        if 'id' in primero:
            topic_id = primero['id']
        else:
            topic_id = ''
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
        return propiedad

file = 'notablas.csv'
notab = {}
with open(file, 'rt') as f:
    lines = f.readlines()
    for line in lines:
        notab[line[0]] = line[1]
        
        

#trae_nec('lesa humanidad')
