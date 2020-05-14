from django.shortcuts import render
from datetime import datetime,timezone
from django.contrib import auth
from django.http import HttpResponse
from fuzzywuzzy import fuzz
from fuzzywuzzy import process,utils
from pythainlp import word_tokenize, Tokenizer, sent_tokenize
from pythainlp.spell import spell, correct
from pythainlp.corpus import thai_stopwords
from difflib import SequenceMatcher
from googletrans import Translator
from keras.preprocessing import image
from keras.applications import VGG16
from keras.preprocessing.image import ImageDataGenerator
from keras.models import load_model
from PIL import Image, ImageTk
from io import StringIO
from skimage.io import imread, imshow
from skimage.transform import resize
from skimage.util import img_as_ubyte
import pyrebase
import time
import pytz
import os, random, shutil
import matplotlib.pyplot as plt
import numpy as np
import os, sys
import glob
import tkinter
import base64
import requests

import keras.backend.tensorflow_backend as tb
tb._SYMBOLIC_SCOPE.value = True


translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.co.th',
    ])

config = {
    'apiKey': "AIzaSyBPIHPOE2LWIPCDMU8STeMcm8G5CEKyjOA",
    'authDomain': "landf-d7d76.firebaseapp.com",
    'databaseURL': "https://landf-d7d76.firebaseio.com",
    'projectId': "landf-d7d76",
    'storageBucket': "landf-d7d76.appspot.com",
    'messagingSenderId': "664909858615",
    'appId': "1:664909858615:web:2959130b838ad023b0bcb2",
    'measurementId': "G-LK1FPK8MVG"
}

firebase = pyrebase.initialize_app(config)
authen = firebase.auth()
database = firebase.database()
status = 0
id = ""
model = load_model('../project_lostandfound/proj/model3.h5')


img_width, img_height = 224, 224
conv_base = VGG16(weights='imagenet',
                  include_top=False,
                  input_shape=(img_width, img_height, 3))
# img_url = ""
def signIn(request):
    return render(request,"signIn.html")

def postsignin(request):
    global status
    global id
    email = request.POST.get('email')
    passw = request.POST.get('pass')
    # database.child("users").child(uid)
    # authen
    # if(session_id):
    #     print("have user")
    #     return render(request,"welcome.html", {"e":email})
    print(email , " " , passw)
    if(status == 0):
        try:
            user = authen.sign_in_with_email_and_password(email,passw)
            status = 1
        except:
            message = "Wrong email or password."
            return render(request,"signIn.html", {"messg":message})
        # print("ID isssssss " + user['idToken'])
        # print("id " , user['localId'])
        #print(user)
        id = user['localId']
        # print(user)
        print ("id ", user['localId'])
        name = database.child('users').child(id).child("name").get().val()
        session_id = user['idToken']
        print(name)
        request.session['uid'] = str(session_id)

        return render(request,"welcome.html", {"g_email":email , "g_id":id}) #by email
    elif(status == 1):
        return render(request,"welcome.html", {"g_email":email , "g_id":id})

def logout(request):
    global status
    auth.logout(request)
    status = 0

    return render(request,'signIn.html')

def signUp(request):
    return render(request,"signUp.html")

def postsignup(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    passw = request.POST.get('pass')

    try:
        user = authen.create_user_with_email_and_password(email, passw)
    except:
        message="unable to create account,please try again"
        return render(request,"signUp.html",{"messg":message})
    uid = user['localId']
    data = {"name":name,"email":email,"password":passw}

    database.child("users").child(uid).set(data)
    return render(request,"signIn.html")

def create_lost(request):
    email = request.POST.get('email')
    return render(request,"create_lost.html", {"g_email":email})

def create_found(request):
    email = request.POST.get('email')
    return render(request,"create_found.html", {"g_email":email})

def post_create_lost(request):
    tz = pytz.timezone('Asia/Bangkok')
    time_now = datetime.now(timezone.utc).astimezone(tz)
    millis = int(time.mktime(time_now.timetuple()))
    #print("mili" + str(millis))
    email = request.POST.get('email')
    id = request.POST.get('now_id')
    name = request.POST.get('now_name')
    now_em = request.POST.get('now_email')


    work = request.POST.get('work')
    progress = request.POST.get('progress')
    url = request.POST.get('url')
    type = request.POST.get('item')
    statusPost = request.POST.get("statusPost")
    # print(type)

    if(url==""):
        url = "https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"


    idtoken = request.session['uid']
    a = authen.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    #print("info" + str(a))

    data = {
            'email':email,
            'topic':work,
            'description':progress,
            'url':url,
            'type':type,
            'statusPost':statusPost
    }
    # database.child('users').child(a).child('reports').child(millis).set(data)
    database.child('Lost').child(millis).set(data)
    # name = database.child('users').child(a).child('details').child('name').get().val()

    return render(request,"welcome.html",{'e':email , 'g_id':id , 'g_name':name , 'g_email':now_em})

def post_create_found(request):
    tz = pytz.timezone('Asia/Bangkok')
    time_now = datetime.now(timezone.utc).astimezone(tz)
    millis = int(time.mktime(time_now.timetuple()))
    #print("mili" + str(millis))
    email = request.POST.get('email')
    id = request.POST.get('now_id')
    name = request.POST.get('now_name')
    now_em = request.POST.get('now_email')

    work = request.POST.get('work')
    progress = request.POST.get('progress')
    url = request.POST.get('url')
    type = request.POST.get('item')
    statusPost = request.POST.get("statusPost")
    save = 0

    if(url==""):
        url = "https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"

    idtoken = request.session['uid']
    a = authen.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    #print("info" + str(a))

    data = {
            'email':email,
            'topic':work,
            'description':progress,
            'url':url,
            'type':type,
            'statusPost':statusPost
    }
    # database.child('users').child(a).child('reports').child(millis).set(data)
    if(save == 0):
        database.child('Found').child(millis).set(data)
        save = 1
    # name = database.child('users').child(a).child('details').child('name').get().val()

    return render(request,"welcome.html",{'e':email, 'g_id':id , 'g_name':name , 'g_email':now_em})

def check(request):
    if request.method == 'GET' and 'csrfmiddlewaretoken' in request.GET:
        search = request.GET.get('search')
        search = search.lower()
        uid = request.GET.get('uid')
        print(search)
        print(uid)

        # timestamps = database.child('Lost').child(uid).child('reports').shallow().get().val()
        timestamps = database.child('Lost').shallow().get().val()
        # print(timestamps)
        # return HttpResponse(search + ' ' + str(uid))
        work_id = []
        for i in timestamps:
            # work_list = database.child('users').child(uid).child('reports').child(i).child('work').get().val()
            work_list = database.child('users').child(i).child('email').get().val()
            work_list = str(work_list) + "$" + str(i)
            work_id.append(work_list)

        matching = [str(string) for string in work_id if search in string.lower()]

        s_work = []
        s_id = []
        for i in matching:
            work,ids = i.split("$")
            s_work.append(work)
            s_id.append(ids)

        date = []
        for i in s_id:
            date_list = datetime.fromtimestamp(float(i)).strftime('%H:%M %d-%m-%Y')
            date.append(date_list)

        comb_lis = zip(s_id,date,s_work)
        # name = database.child('users').child(uid).child('details').child('email').get().val()
        email = database.child('users').child('email').get().val()

        return render(request,'check.html', {'comb_lis':comb_lis, 'e':email, 'uid':uid})
    else:
        idtoken = request.session['uid']
        a = authen.get_account_info(idtoken)
        a = a['users']
        a = a[0]
        a = a['localId']

        timestamps = database.child('Found').shallow().get().val()

        lis_time = []
        for i in timestamps:
            lis_time.append(i)
        lis_time.sort(reverse=True)
        print(timestamps)

        work = []
        for i in lis_time:
            work_list = database.child('Found').child(i).child('email').get().val()
            work.append(work_list)
        print(work)

        date = []
        for i in lis_time:
            date_list = datetime.fromtimestamp(float(i)).strftime('%H:%M %d-%m-%Y')
            date.append(date_list)
        print(date)

        comb_lis = zip(lis_time,date,work)
        email = database.child('Found').child('email').get().val()

        return render(request,'check.html', {'comb_lis':comb_lis, 'e':email, 'uid':a})

# def post_check(request):
#     time = request.GET.get('z')
#
#     idtoken = request.session['uid']
#     a = authen.get_account_info(idtoken)
#     a = a['users']
#     a = a[0]
#     a = a['localId']
#
#     work = database.child('users').child(a).child('reports').child(time).child('work').get().val()
#     progress = database.child('users').child(a).child('reports').child(time).child('progress').get().val()
#     img_url = database.child('users').child(a).child('reports').child(time).child('url').get().val()
#
#     work = database.child('Found').child(time).child('topic').get().val()
#     progress = database.child('Found').child(time).child('progress').get().val()
#     img_url = database.child('Found').child(time).child('url').get().val()
#
#     date_list = datetime.fromtimestamp(float(time)).strftime('%H:%M %d-%m-%Y')
#     email = database.child('Found').child(a).child('details').child('email').get().val()
#
#     return render(request,'post_check.html', {'w':work, 'p':progress , 'e':email, 'i':img_url})
def topfive(inputma , listRatios):
    # print("top5")
    listRatios = [v for k, v in sorted(listRatios.items(), key=lambda item: item[1]["per"],reverse=True)]
    print("list:",listRatios)
    try:
        txt = "X#"
        for i in range(5):
            # print(i)
            txt += listRatios[i]["keyDB"] + "#"
            print("A")
            # print(inputma[0]['topic'],"\tmatching with\t",listRatios[i]['topic'] , "\t",listRatios[i]['per'])
            print(txt)
    except:
        txt = "X#"
        for i in range(len(listRatios)):
            # print(i)
            txt += listRatios[i]["keyDB"] + "#"
            print("B")
            # print(inputma[0]['topic'],"\tmatching with\t",listRatios[i]['topic'] , "\t",listRatios[i]['per'])
            print(txt)
    if(len(listRatios)==0):
        txt= "ไม่พบสิ่งที่ค้นหา"
        print(txt)
    return txt

def compare2thing(lost , found , choice):
    # print("compare")
    listRatios={}
    # print("ch " , choice)
    if(choice == 1):
        topic_lost = lost[0]["topic"]
        desc_lost = lost[0]["description"]
        key_lost = lost[0]['key']
        img_lost = lost[0]['img']
        for i in range(0, len(found) ,1):
            # print("in for 1")
            tmp = ""
            # tmp = found[i]
            topic_found = found[i]["topic"]
            desc_found = found[i]["description"]
            key_found = found[i]['key']
            img_found = found[i]['img']
            sorted1 =fuzz._process_and_sort(topic_lost, force_ascii=True, full_process=0)
            sorted2 =fuzz._process_and_sort(topic_found, force_ascii=True, full_process=0)
            sorted3 =fuzz._process_and_sort(desc_lost, force_ascii=True, full_process=0)
            sorted4 =fuzz._process_and_sort(desc_found, force_ascii=True, full_process=0)
            sorted5 =fuzz._process_and_sort(img_lost, force_ascii=True, full_process=0)
            sorted6 =fuzz._process_and_sort(img_found, force_ascii=True, full_process=0)

            s1, s2 = utils.make_type_consistent(sorted1,sorted2)
            s3, s4 = utils.make_type_consistent(sorted3,sorted4)
            s5, s6 = utils.make_type_consistent(sorted5,sorted6)

            #1 topic
            if len(s1) <= len(s2):
                shorter = s1
                longer = s2
            else:
                shorter = s2
                longer = s1

            seq1 = SequenceMatcher(None,shorter,longer)
            a = list(seq1.get_matching_blocks())

            # print(a)

            #2 description
            if len(s3) <= len(s4):
                shorter = s3
                longer = s4
            else:
                shorter = s4
                longer = s3

            seq2 = SequenceMatcher(None,shorter,longer)
            b = list(seq2.get_matching_blocks())

            # print(b)

            if len(s5) <= len(s6):
                shorter = s5
                longer = s6
            else:
                shorter = s6
                longer = s5

            seq3 = SequenceMatcher(None,shorter,longer)
            c = list(seq3.get_matching_blocks())

            # print(c)

            Ratio_topic = seq1.ratio()
            Ratios_topic = utils.intr(100 * Ratio_topic)

            Ratio_desc = seq2.ratio()
            Ratios_desc = utils.intr(100 * Ratio_desc)

            Ratio_img = seq3.ratio()
            Ratios_img = utils.intr(100 * Ratio_desc)

            # print("img per " , Ratios_img)

            Ratios_2 = utils.intr(((Ratios_topic*2) + (Ratios_desc*1) + (Ratios_img*1))/3)
            # print("key_f" , key_found)

            # print(Ratios)
            listRatios[i]={'keyDB' : key_found , "topic": topic_found,"per" : Ratios_2}
        # print("choice 1")
        top = topfive(lost , listRatios)
        return top

    elif(choice == 2):
        topic_found = found[0]["topic"]
        desc_found = found[0]["description"]
        key_found = found[0]['key']
        img_found = found[0]['img']
        for i in range(0, len(lost) ,1):
            # print("in for 2")
            tmp = ""
            # tmp = lost[i]
            topic_lost = lost[i]["topic"]
            desc_lost = lost[i]["description"]
            key_lost = lost[i]['key']
            img_lost = lost[i]['img']

            sorted1 =fuzz._process_and_sort(topic_lost, force_ascii=True, full_process=0)
            sorted2 =fuzz._process_and_sort(topic_found, force_ascii=True, full_process=0)
            sorted3 =fuzz._process_and_sort(desc_lost, force_ascii=True, full_process=0)
            sorted4 =fuzz._process_and_sort(desc_found, force_ascii=True, full_process=0)
            sorted5 =fuzz._process_and_sort(img_lost, force_ascii=True, full_process=0)
            sorted6 =fuzz._process_and_sort(img_found, force_ascii=True, full_process=0)

            s1, s2 = utils.make_type_consistent(sorted1,sorted2)
            s3, s4 = utils.make_type_consistent(sorted3,sorted4)
            s5, s6 = utils.make_type_consistent(sorted5,sorted6)

            #1 topic
            if len(s1) <= len(s2):
                shorter = s1
                longer = s2
            else:
                shorter = s2
                longer = s1

            seq1 = SequenceMatcher(None,shorter,longer)
            a = list(seq1.get_matching_blocks())

            # print(a)

            #2 description
            if len(s3) <= len(s4):
                shorter = s3
                longer = s4
            else:
                shorter = s4
                longer = s3

            seq2 = SequenceMatcher(None,shorter,longer)
            b = list(seq2.get_matching_blocks())

            # print(b)

            if len(s5) <= len(s6):
                shorter = s5
                longer = s6
            else:
                shorter = s6
                longer = s5

            seq3 = SequenceMatcher(None,shorter,longer)
            c = list(seq3.get_matching_blocks())

            # print(c)

            Ratio_topic = seq1.ratio()
            Ratios_topic = utils.intr(100 * Ratio_topic)

            Ratio_desc = seq2.ratio()
            Ratios_desc = utils.intr(100 * Ratio_desc)

            Ratio_img = seq3.ratio()
            Ratios_img = utils.intr(100 * Ratio_desc)

            # print("img per " , Ratios_img)

            Ratios_2 = utils.intr(((Ratios_topic*2) + (Ratios_desc*1) + (Ratios_img*1))/3)

            # print(Ratios)
            listRatios[i]={'keyDB' : key_lost , "topic": topic_lost,"per" : Ratios_2}
        # print("choice 2")
        top = topfive(found,listRatios)
        return top

def pdPic(dd):
    switcher = {
        0: "bag",
        1: "backpack",
        2: "iphone",
        3: "huawei",
        4: "samsung",
        5: "clashbag",
        6: "pen",
        7: "watch",
    }
    return switcher.get(dd,"?")

def visualize_predictions(classifier,img_path):

        # Get picture
    img1 = imread(img_path)
    img2 = resize(img1,(224,224))
    img3 = img_as_ubyte(img2)
    img = Image.fromarray(img3, 'RGB')

    img_tensor = image.img_to_array(img)  # Image data encoded as integers in the 0–255 range
    img_tensor /= 255.  # Normalize to [0,1] for plt.imshow application

    # Extract features
    features = conv_base.predict(img_tensor.reshape(1, 224, 224 , 3))

    # Make prediction
    try:
        prediction = classifier.predict(features)
    except:
        prediction = classifier.predict(features.reshape(1, 7*7*512))

    # Show picture
    #plt.imshow(img_tensor)
    #plt.show()
    #print(prediction[0])
    #print( (max(prediction[0])) )

    typePredic=pdPic(list(prediction[0]).index(max(prediction[0])))
    return (str(typePredic))

def match_post_L(id):
    listLost={}
    found={}
    # key = request.GET.get('key')
    # id = request.GET.get('id')
    found_topic = database.child('Found').child(id).child('topic').get().val()
    found_desc = database.child('Found').child(id).child('description').get().val()
    found_url = database.child('Found').child(id).child('url').get().val()

    # print(type(found_url))
    # print(found_url)

    found[0] = {'key' : id, 'topic' : found_topic , 'description' : found_desc , 'img' : visualize_predictions(model,found_url)}

    found_type = database.child('Found').child(id).child('type').get().val()

    # print(found)
    # print(found_type)
    # print("url_f " , found_url)

    ref = database.child('Lost').get()
    choice = 2
    # lost_arr = []
    # key_arr_l = []
    i=0
    for data in ref.each():
        lost_type = data.val()['type']
        if(found_type == lost_type):
            # print(data.key()) # Morty
            # print(data.val()['topic']) # {name": "Mortimer 'Morty' Smith"}
            topic_lost = data.val()['topic']
            desc_lost = data.val()['description']
            url_lost = data.val()['url']
            # img4 = imread(url_lost, as_gray=True)
            # img5 = resize(img4, (224, 224))
            # img6 = img_as_ubyte(img5)
            # imshow(img6)
            # picRe = url_lost

            # print("url_l " , url_lost)

            key = data.key()
            # lost_arr.append(topic_lost.strip())
            # key_arr_l.append(data.key())
            listLost[i]={'key' : key, 'topic' : topic_lost , 'description' : desc_lost , 'img' : visualize_predictions(model,url_lost)}
            i+=1
        # print(1)
    # print(lost_arr)
    comp = compare2thing(listLost, found , choice)

    # return render(request,'history.html',{"re":comp,'g_id':id,'key':key , "sta":0})
    return comp

def match_post_F(id):
    listFound={}
    lost={}
    # key = request.GET.get('key')
    # id = request.GET.get('id')
    lost_topic = database.child('Lost').child(id).child('topic').get().val()
    lost_desc = database.child('Lost').child(id).child('description').get().val()
    lost_url = database.child('Lost').child(id).child('url').get().val()

    lost[0] = {'key' : id, 'topic' : lost_topic , 'description' : lost_desc , 'img' : visualize_predictions(model,lost_url)}

    lost_type = database.child('Lost').child(id).child('type').get().val()

    # print(lost)
    # print(lost_type)
    # print("url_l " , lost_url)

    ref = database.child('Found').get()
    choice = 1
    # found_arr = []
    # key_arr_f = []
    i=0
    for data in ref.each():
        found_type = data.val()['type']
        if(lost_type == found_type):
            # print(data.key()) # Morty
            # print(data.val()['topic']) # {name": "Mortimer 'Morty' Smith"}
            topic_found = data.val()['topic']
            desc_found = data.val()['description']
            url_found =data.val()['url']
            # img4 = imread(url_found, as_gray=True)
            # img5 = resize(img4, (224, 224))
            # img6 = img_as_ubyte(img5)
            # imshow(img6)

            # print("url_f " , url_found)

            key = data.key()
            # found_arr.append(topic_found.strip())
            # key_arr_f.append(data.key())
            listFound[i]={'key' : key, 'topic' : topic_found , 'description' : desc_found , 'img' : visualize_predictions(model,url_found)}
            i+=1
        # print(2)
    # print(found_arr)
    comp = compare2thing(lost, listFound , choice)

    # return render(request,'history.html',{"re":comp,'g_id':id,'key':key, "sta":1})
    return comp

def post_check_L(request):
    id = request.GET.get('key')
    # on = request.GET.get('on')
    # print(id)
    print(1)
    # idtoken = request.session['uid']
    # a = authen.get_account_info(idtoken)
    # a = a['users']
    # a = a[0]
    # a = a['localId']
    # print(id)
    match = match_post_L(id)
    print(match)
    topic = database.child('Found').child(id).child('topic').get().val()
    desc = database.child('Found').child(id).child('description').get().val()
    img_url = database.child('Found').child(id).child('url').get().val();
    email = database.child('Found').child(id).child('email').get().val()
    # print(topic , "dasd")

    return render(request,'post_check.html', {'t':topic, 'd':desc , 'e':email, 'i':img_url, 'id':match, "sta":0})


def post_check_F(request):
    id = request.GET.get('key')
    on = request.GET.get('on')

    print(2)
    match = match_post_F(id)
    print(match)

    topic = database.child('Lost').child(id).child('topic').get().val()
    desc = database.child('Lost').child(id).child('description').get().val()
    img_url = database.child('Lost').child(id).child('url').get().val();
    email = database.child('Lost').child(id).child('email').get().val()

    return render(request,'post_check.html', {'t':topic, 'd':desc , 'e':email, 'i':img_url, 'id':match, "sta":1})

def post_check_on_L(request):
    id = request.GET.get('key')
    print("id " , id)
    print(1)

    top = database.child('Lost').child(id).child('topic').get().val()
    des = database.child('Lost').child(id).child('description').get().val()
    im_url = database.child('Lost').child(id).child('url').get().val();
    em = database.child('Lost').child(id).child('email').get().val()
    print("topic " , top)
    print("des " , des)
    print("im " , im_url)
    print("em ", em)

    # print(topic , "dasd")

    return render(request,'post_check_only.html', {'t':top, 'd':des , 'e':em, 'i':im_url, "sta":0})

def post_check_on_F(request):
    id = request.GET.get('key')
    print("id " , id)
    print(2)

    top = database.child('Found').child(id).child('topic').get().val()
    des = database.child('Found').child(id).child('description').get().val()
    im_url = database.child('Found').child(id).child('url').get().val();
    em = database.child('Found').child(id).child('email').get().val()
    print("topic " , top)
    print("des " , des)
    print("im " , im_url)
    print("em ", em)

    return render(request,'post_check_only.html', {'t':top, 'd':des , 'e':em, 'i':im_url, "sta":1})

def post_check_on_we_L(request):
    id = request.GET.get('key')
    print("id " , id)
    print(1)

    top = database.child('Found').child(id).child('topic').get().val()
    des = database.child('Found').child(id).child('description').get().val()
    im_url = database.child('Found').child(id).child('url').get().val();
    em = database.child('Found').child(id).child('email').get().val()
    print("topic " , top)
    print("des " , des)
    print("im " , im_url)
    print("em ", em)

    # print(topic , "dasd")

    return render(request,'post_check_only.html', {'t':top, 'd':des , 'e':em, 'i':im_url, "sta":0})

def post_check_on_we_F(request):
    id = request.GET.get('key')
    print("id " , id)
    print(2)

    top = database.child('Lost').child(id).child('topic').get().val()
    des = database.child('Lost').child(id).child('description').get().val()
    im_url = database.child('Lost').child(id).child('url').get().val();
    em = database.child('Lost').child(id).child('email').get().val()
    print("topic " , top)
    print("des " , des)
    print("im " , im_url)
    print("em ", em)

    return render(request,'post_check_only.html', {'t':top, 'd':des , 'e':em, 'i':im_url, "sta":1})

def history(request):
    # id = request.GET.get('g_id')
    return render(request,'history.html')
