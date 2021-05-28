# IMPORTS
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import sys
import webbrowser
import re
import itertools
from scholarly import scholarly, ProxyGenerator
from fp.fp import FreeProxy
import json
import numpy as np
from flask import jsonify, make_response, request
from pymongo import MongoClient
from pprint import pprint
from socket import timeout
import http
import urllib.request
from urllib.request import URLError, HTTPError
import random
import os
import time
import sqlite3
from sqlite3 import Error
from fake_useragent import UserAgent
from urllib.error import HTTPError, URLError
from bson import json_util


# Declaring variables
names = []
pictures = []
ids = []
idsF = []
profiles = {}
a1 = []
profile = []
email = []
emailDoPerfil = []
authorprofile = {}
listEmails = []
name = []
domain = []
ints = []
afil = []
words = []


# Building App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'


imageExt = ["jpeg", "exif", "tiff", "gif", "bmp", "png", "ppm", "pgm",
            "pbm", "pnm", "webp", "hdr", "heif", "bat", "bpg", "cgm", "svg"]
ua = UserAgent()


# Connect to MongoDB
client = MongoClient(
    "mongodb+srv://test:FpBaYfHAUJIsV@cluster0.0zcqp.mongodb.net/gs?retryWrites=true&w=majority")
db = client.admin
# Issue the serverStatus command and print the results
serverStatusResult = db.command("serverStatus")
c = client["gs"]
collection = c["Profiles"]
collection2 = c["Search"]


# Getting free Proxy
pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)

# Adding Profile to Mongo Data Base


def addProfile(id, name, domain, emailAccount, afil, ints):
    post = {"GS_Id": id, "Name": name,
            "Domain": domain, "Email": emailAccount, "Afiliation": afil,
            "Interests": ints}
    collection.insert_one(post)

# Adding Search to Mongo Data Base


def addWord(word, count):
    post = {"Word": word, "Count": count}
    collection2.insert_one(post)


# Check Data Base to find specific ID


def checkBD(id):
    results = collection.find({"GS_Id": id})
    n = results.count()
    return n

# Get all searches from Mongo Data Base


def findAllWords():
    for x in collection2.find():
        words.append(x)
    return words

# Define function to parse data


def parse_json(x):
    return json.loads(json_util.dumps(x))

# Check Data Base to find specific Search


def checkWord(word):
    results = collection2.find({"Word": word})
    p = results.count()
    return p


# Update search counter
def updateWord(word):

    query = {"Word": word}
    present_data = collection2.find_one(query)
    new_data = {'$inc': {"Count": 1}}
    collection2.update_one(present_data, new_data)

# GET Profile with given ID


def getProfileDB(id):
    name.clear()
    domain.clear()
    ints.clear()
    afil.clear()

    results = collection.find({"GS_Id": id})
    for result in results:
        print(result["Email"])
        name.append(result['Name'])
        domain.append(result['Domain'])
        ints.append(result['Interests'])
        afil.append(result['Afiliation'])
        print(result['Afiliation'])
        print(result['Name'])
        print(result['Interests'])
        for e in result["Email"]:
            listEmails.append(e)


# GET Words Counter

def getWCouhnter():

    w = []
    t = []
    for x in collection2.find():
        w.append(x)

    for wd in w:
        t.append(wd['Count'])

    counter = sum(t)
    return counter


# Function to manage searches

def dealSearch(topic):
    word = topic
    if checkWord(word) > 0:
        updateWord(word)
    else:
        count = 1
        addWord(word, count)


# Functions:

# Function that receives a search topic, and scrapes Google Scholar to get authors that have papers on that topic
def getPublishers(topic):
    profiles.clear()
    names.clear()
    idsF.clear()
    pictures.clear()
    ids.clear()
    newtopic = topic.replace(" ", "_")
    payload = {'view_op': 'search_authors',
               'mauthors': 'label:' + newtopic}
    r = requests.get(
        'https://scholar.google.com/citations?',  params=payload)
    html_content = r.text
    soup = BeautifulSoup(html_content, "html.parser")
    profile_name = soup.select('.gs_ai_name a')
    profile_picture = soup.select('.gs_ai_pho span')

    for link in profile_picture[:10]:
        pictures.append(link.img.get('src'))

    for link in profile_name[:10]:
        ids.append(link.get('href').split('='))
        names.append(link.text)

    for id in ids:
        idsF.append(id[2])

    for (a, b, c) in zip(names, idsF, pictures):

        profiles[b] = {}
        profiles[b]['name'] = a
        profiles[b]['id'] = b
        profiles[b]['img'] = c

# Funtion that receives a Google Scholar Author's ID, and asks Google Scholar API information about the author


def getProfile(id):
    authorprofile.clear()
    profile.clear()
    a1.clear()
    listEmails.clear()
    if checkBD(id) > 0:
        getProfileDB(id)
        authorprofile['author'] = {}
        authorprofile['author']['name'] = name[0]
        authorprofile['author']['email'] = listEmails
        authorprofile['author']['domain'] = domain[0]
        authorprofile['author']['interests'] = ints[0]
        authorprofile['author']['afiliation'] = afil[0]

    else:

        a1.append(scholarly.search_author_id(id))
        profile.append(a1[0]['name'])
        profile.append(a1[0]['email_domain'])
        profile.append(a1[0]['affiliation'])
        profile.append(a1[0]['interests'])

        nome = profile[0]
        mail = profile[1]
        afiliation = profile[2]
        interests = profile[3]
        pl = nome + '' + mail
        payload = {'q': pl}
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
        }
        r = requests.get(
            'https://google.com/search?',  params=payload, headers=headers)

        print(r.url)
        url = r.url
        count = 0
        listUrl = []
        listUrl.clear()
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': ua.random
            })

        try:
            conn = urllib.request.urlopen(req, timeout=10)

        except timeout:
            raise ValueError('Timeout ERROR')

        except (HTTPError, URLError):
            raise ValueError('Bad Url...')

        status = conn.getcode()
        print(status)

        if(status != 200):

            raise ValueError('Bad Url...')
        html = conn.read().decode('utf-8')

        emails = re.findall(
            r'[A-Za-z0-9.%+-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,4}', html)

        for email in emails:
            if (email not in listUrl and email[-3:] not in imageExt):
                count += 1
                print(str(count) + " - " + email)
                listUrl.append(email)
        for element in listUrl:
            listEmails.append(element)
        addProfile(id, nome, mail, listEmails, afiliation, interests)

        authorprofile['author'] = {}
        authorprofile['author']['name'] = nome
        authorprofile['author']['email'] = listEmails
        authorprofile['author']['domain'] = mail
        authorprofile['author']['afiliation'] = afiliation
        authorprofile['author']['interests'] = interests

        print(authorprofile)


# Creating routes
@app.route('/', methods=['GET', 'POST'])
def search():
    print("root")
    return render_template("search.html")


@app.route('/afterform',  methods=['POST'])
def form():
    title = "Thanks"
    topic = request.form.get("search")
    getPublishers(topic)
    return render_template("afterform.html", profiles=profiles)


#   Route to call "getProfile" function


@app.route('/searchProfile',  methods=['POST'])
def formID():
    id = request.get_json()
    print(id['AuthorID'])
    getProfile(id['AuthorID'])
    perfil = authorprofile
    print(perfil)

    return json.dumps(perfil)


#   Route to call "getPublishers" function

@app.route('/searchTopic', methods=['POST'])
def testmeco():

    # dados que recebe do servidor
    data = request.get_json()
    dealSearch(data['topico'])

    getPublishers(data['topico'])

    profilelist = profiles

    # do something with this data variable that contains the data from the node server
    return json.dumps(profilelist)


#   Route to call "findAllWords" function

@app.route('/getWord', methods=['GET', 'POST'])
def getWrd():
    a = findAllWords()

    b = parse_json(a)

    return json.dumps(b)


@app.route('/getCounter', methods=['GET', 'POST'])
def getCtr():
    a = getWCouhnter()

    b = parse_json(a)

    return json.dumps(b)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
