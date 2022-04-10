from fastapi import FastAPI,Path
import uvicorn
from typing import Optional
from pydantic import BaseModel
import re
import os
from bs4 import BeautifulSoup
import unicodedata
import json


app = FastAPI()


path = os.path.dirname(os.path.abspath(__file__))
abbreviations_path = os.path.join(path, 'data','abbreviations_wordlist.json')

def cont_exp(x):
    abbreviations = json.load(open(abbreviations_path))
    #print(abbreviations)
    if type(x) is str:
	    for key in abbreviations:
		    value = abbreviations[key]
		    raw_text = r'\b' + key + r'\b'
		    x = re.sub(raw_text, value, x)
			# print(raw_text,value, x)
	    return x
    else:
	    return x

def remove_emails(x):
	return re.sub(r'([a-z0-9+._-]+@[a-z0-9+._-]+\.[a-z0-9+_-]+)',"", x)       


def remove_urls(x):
	return re.sub(r'(http|https|ftp|ssh)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', '' , x)

def remove_rt(x):
	return re.sub(r'\brt\b', '', x).strip()


def remove_special_chars(x):
	x = re.sub(r'[^\w ]+', "", x)
	x = ' '.join(x.split())
	return x

def remove_html_tags(x):
	return BeautifulSoup(x, 'lxml').get_text().strip()

def remove_accented_chars(x):
	x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode('utf-8', 'ignore')
	return x    

def get_clean(x):
    x = str(x).lower().replace('\\', '').replace('_', ' ')
    x = cont_exp(x)
    x = remove_emails(x)
    x = remove_urls(x)
    x = remove_html_tags(x)
    x = remove_rt(x)
    x = remove_accented_chars(x)
    x = remove_special_chars(x)
    x = re.sub("(.)\\1{2,}", "\\1", x)
    return x


class Preprocess(BaseModel):
	X : str

@app.get("/")
def index():
	return {'message' : f'Hello Stranger'}  

@app.post("/preprocess")
def preProcessData(data:Preprocess):
	data = data.dict()
	X= data['X']
	preprocessed = get_clean(X)
	return {
		'preprocessed' : preprocessed
	}	

