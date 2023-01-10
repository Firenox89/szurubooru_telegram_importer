import requests
from requests.auth import HTTPDigestAuth
import json
import os

safety_rating_map = {"s": "safe", "q": "sketchy", "e": "unsafe"}

szuru_base_url = os.environ['SZURU_BASE_URL']
szuru_user = os.environ['SZURU_USER']
szuru_pw = os.environ['SZURU_PW']

def get_tag_type(board, tag_name):
    url = "https://"+board+"/tag.json?name=" + tag_name + "&limit=0"
    resp = requests.get(url, headers={"Content-Type": "application/json","Accept": "application/json"})

    if(resp.ok):
        jData = json.loads(resp.content)

        for jd in jData:
            if jd["name"] == tag_name:
                return jd["type"]
        return 0
    else:
        print(resp.content)
        resp.raise_for_status()

def szuruHasTag(tag):
    url = szuru_base_url + "/api/tags?query=name:"+tag

    resp = requests.get(url, auth=(szuru_user, szuru_pw), headers={"Content-Type": "application/json","Accept": "application/json"})

    if(resp.ok):
        jData = json.loads(resp.content)

        return jData["total"] > 0
    else:
        print(resp.content)
        resp.raise_for_status()

def addTags(board, tags):
    count = 0
    for tag in tags.split():
        if not szuruHasTag(tag):
            createSzuruTag(tag, get_tag_type(board ,tag))
            count = count + 1
    return count

def createSzuruPost(file_url, tags, rating, source, board_origin):
    url = szuru_base_url + "/api/posts"
    tags.append(board_origin)
    data = {"tags": tags, "contentUrl": file_url, "safety": safety_rating_map[rating], "source": source}

    resp = requests.post(url, json=data, auth=(szuru_user, szuru_pw), headers={"Content-Type": "application/json","Accept": "application/json"})

    if not resp.ok:
        print(resp.content)
        resp.raise_for_status()

def createSzuruTag(tag_name, category):
    print("create tag", tag_name, category)
    url = szuru_base_url + "/api/tags"

    data = {"names": [tag_name], "category": category}

    resp = requests.post(url, json=data, auth=(szuru_user, szuru_pw), headers={"Content-Type": "application/json","Accept": "application/json"})

    if not resp.ok:
        print(resp.content)
        resp.raise_for_status()

