from django.shortcuts import render
from datetime import datetime,timezone
from django.contrib import auth
from django.http import HttpResponse
from fuzzywuzzy import fuzz
from fuzzywuzzy import process,utils
from pythainlp import word_tokenize, Tokenizer, sent_tokenize
from pythainlp.spell import spell, correct
from pythainlp.corpus import thai_stopwords
from flashtext import KeywordProcessor
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
from collections import Counter
import numpy as np
import pyrebase
import time
import pytz
import os, random, shutil
import matplotlib.pyplot as plt
import os, sys
import glob
import tkinter
import base64
import requests
import json

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

keyword_processor = KeywordProcessor()
keyword_dict = {
    "โทรศัพท์": ["iphone","phone","i-phone","huawei","samsung","iphonex","โทรศัพท์","มือถือ","mobile"],
    "กระเป๋าสะพาย": ["backpack","กระเป๋าสะพาย","กระเป๋าเป้","เป้","anello","adidas","nike","kanken","herschel","troopers","longchamp","david jones","puma"],
    "กระเป๋าถือ": ["bag","กระเป๋าถือ","coach","prada","gucci","chanel","fendi","dior","louis vuitton","ysl"],
    "กระเป๋าเงิน": ["wallet","กระเป๋าเงิน","กระเป๋าตัง","jacob","guy laroach","playboy","lacoste","supreme"],
    "นาฬิกา": ["watch","นาฬิกา","g-shock","gshock","baby-g","citizen","seiko","casio","rolex","hamilton"],
    "ปากกา": ["pen","ปากกา","lamy","ม้า","quantum","parker","sailor","montblanc","horse","faber castel","pentel"]
}
keyword_processor.add_keywords_from_dict(keyword_dict)

firebase = pyrebase.initialize_app(config)
authen = firebase.auth()
database = firebase.database()
status = 0
id = ""
model = load_model('../project_lostandfound/proj/model4.h5')


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
    # type = request.POST.get('item')
    statusPost = request.POST.get("statusPost")
    statusNoti = request.POST.get("statusNoti")
    # print(type)
    if(url==""):
        url = "https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"
        type = find_keyword(work)
    listPic = (visualize_predictions(model,url))
    if(url!="https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"):
        type = pdPic(list(listPic).index(max(listPic)))

    idtoken = request.session['uid']
    a = authen.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    #print("info" + str(a))
    idP = {'id':millis}
    data = {
            'email':email,
            'topic':work,
            'description':progress,
            'url':url,
            'type':type,
            'statusPost':statusPost,
            'statusNoti':statusNoti,
    }
    dicPic = {}
    dicPic['id']=millis
    dicPic['listPic'] = listPic.tolist()
    # database.child('users').child(a).child('reports').child(millis).set(data)
    database.child('Lost').child(millis).set(data)
    database.child('CategoryL').child(type).child(millis).set(idP)
    database.child('PicCategoryL').child(type).child(millis).set(dicPic)
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
    # type = request.POST.get('item')
    statusPost = request.POST.get("statusPost")
    statusNoti = request.POST.get("statusNoti")
    save = 0

    if(url==""):
        url = "https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"
        type = find_keyword(work)
    listPic = (visualize_predictions(model,url))
    if(url!="https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"):
        type = pdPic(list(listPic).index(max(listPic)))

    idtoken = request.session['uid']
    a = authen.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    #print("info" + str(a))
    idP = {'id':millis}
    data = {
            'email':email,
            'topic':work,
            'description':progress,
            'url':url,
            'type':type,
            'statusPost':statusPost,
            'statusNoti':statusNoti,
    }
    dicPic = {}
    dicPic['id']=millis
    dicPic['listPic'] = listPic.tolist()
    # database.child('users').child(a).child('reports').child(millis).set(data)
    if(save == 0):
        database.child('Found').child(millis).set(data)
        database.child('CategoryF').child(type).child(millis).set(idP)
        database.child('PicCategoryF').child(type).child(millis).set(dicPic)
        save = 1
    # name = database.child('users').child(a).child('details').child('name').get().val()

    return render(request,"welcome.html",{'e':email, 'g_id':id , 'g_name':name , 'g_email':now_em})

def get_key(val):
    global cnt
    for key, value in cnt.items():
         if val == value:
             return key

def find_keyword(text):
    global cnt
    proc = word_tokenize(text.lower() , keep_whitespace=False)
    listToStr = ' '.join(map(str, proc))
    keywords = keyword_processor.extract_keywords(listToStr)
    cnt = Counter(keywords)
    if(cnt.get("โทรศัพท์") != None or cnt.get("กระเป๋าสะพาย") != None or cnt.get("กระเป๋าถือ") != None or cnt.get("กระเป๋าเงิน") != None or cnt.get("นาฬิกา") != None or cnt.get("ปากกา") != None):
        mylist = [cnt.get("โทรศัพท์"), cnt.get("กระเป๋าสะพาย"), cnt.get("กระเป๋าถือ"), cnt.get("กระเป๋าเงิน"), cnt.get("นาฬิกา"), cnt.get("ปากกา")]
        x = np.array(mylist, dtype=np.float64)
        mykey = get_key(int(np.nanmax(x)))
    else:
        mykey = "อื่นๆ"

    print("keyword is ", mykey)
    return mykey


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

def topTen(inputma , listRatios):
    # print("top5")
    listRatios = [v for k, v in sorted(listRatios.items(), key=lambda item: item[1]["per"],reverse=True)]
    # print("list:",listRatios)
    try:
        txt = "X#"
        for i in range(10):
            # print(i)
            txt += str(listRatios[i]["keyDB"]) + "#"
            # print("A")
            # print(inputma[0]['topic'],"\tmatching with\t",listRatios[i]['topic'] , "\t",listRatios[i]['per'])
            # print(txt)
    except:
        txt = "X#"
        for i in range(len(listRatios)):
            # print(i)
            txt += str(listRatios[i]["keyDB"]) + "#"
            # print("B")
            # print(inputma[0]['topic'],"\tmatching with\t",listRatios[i]['topic'] , "\t",listRatios[i]['per'])
            # print(txt)
    if(len(listRatios)==0):
        txt= "ไม่พบสิ่งที่ค้นหา"
        # print(txt)
    return txt

def compare2thing(lost , found , choice):
    # print("compare")
    listRatios={}
    # print("ch " , choice)
    if(choice == 1):
        topic_lost = lost[0]["topic"]
        desc_lost = lost[0]["description"]
        key_lost = lost[0]['key']
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

            s1, s2 = utils.make_type_consistent(sorted1,sorted2)
            s3, s4 = utils.make_type_consistent(sorted3,sorted4)

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
            seq3 = float(1-img_found)

            # print(c)

            Ratio_topic = seq1.ratio()
            Ratios_topic = utils.intr(100 * Ratio_topic)

            Ratio_desc = seq2.ratio()
            Ratios_desc = utils.intr(100 * Ratio_desc)


            Ratios_img = utils.intr(100 * seq3)

            # print("img per " , Ratios_img)

            Ratios_2 = utils.intr(((Ratios_topic*2) + (Ratios_desc*1) + (Ratios_img))/3)
            # print("key_f" , key_found)

            # print(Ratios)
            listRatios[i]={'keyDB' : key_found , "topic": topic_found,"per" : Ratios_2}
        # print("choice 1")
        top = topTen(lost , listRatios)
        return top

    elif(choice == 2):
        topic_found = found[0]["topic"]
        desc_found = found[0]["description"]
        key_found = found[0]['key']
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

            s1, s2 = utils.make_type_consistent(sorted1,sorted2)
            s3, s4 = utils.make_type_consistent(sorted3,sorted4)

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

            seq3 = float(1-img_lost)

            # print(c)

            Ratio_topic = seq1.ratio()
            Ratios_topic = utils.intr(100 * Ratio_topic)

            Ratio_desc = seq2.ratio()
            Ratios_desc = utils.intr(100 * Ratio_desc)

            Ratios_img = utils.intr(100 * seq3)

            # print("img per " , Ratios_img)

            Ratios_2 = utils.intr(((Ratios_topic*2) + (Ratios_desc*1) + (Ratios_img))/3)

            # print(Ratios)
            listRatios[i]={'keyDB' : key_lost , "topic": topic_lost,"per" : Ratios_2}
        # print("choice 2")
        top = topTen(found,listRatios)
        return top

def pdPic(dd):
    if(dd==2 or dd==3 or dd==4):
        tyP = "โทรศัพท์"
    else:
        switcher = {
            0: "กระเป๋าถือ",
            1: "กระเป๋าสะพาย",
            2: "iphone",
            3: "huawei",
            4: "samsung",
            5: "กระเป๋าเงิน",
            6: "ปากกา",
            7: "นาฬิกา",
            8: "อื่นๆ",
        }
        tyP=switcher.get(dd,"?")
    return tyP

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
    return (prediction[0])
    #print( (max(prediction[0])) )
    #typePredic=pdPic(list(prediction[0]).index(max(prediction[0])))
    #return (str(typePredic))

def calculate_predicPic(firstList,secondList):
    resultList=[]
    for i in range(9):
        resultList.append(float(firstList[i])/float(secondList[i]))
    result=(float(resultList[0])+float(resultList[1])+float(resultList[2])+float(resultList[3])+float(resultList[4])+float(resultList[5])+float(resultList[6])+float(resultList[7])+float(resultList[8]))/(float(9))
    Ans=abs(result-1)
    return Ans

def match_post_L(id):
    listLost={}
    found={}
    listFoundPic=[]
    listLostPic=[]
    # key = request.GET.get('key')
    # id = request.GET.get('id')
    found_topic = database.child('Found').child(id).child('topic').get().val()
    found_desc = database.child('Found').child(id).child('description').get().val()
    found_type = database.child('Found').child(id).child('type').get().val()
    # t9=time.time()
    # t6=time.time()
    found_ListPic = database.child('PicCategoryF').child(found_type).child(id).child('listPic').get().val()
    listFoundPic.append(found_ListPic[0])
    listFoundPic.append(found_ListPic[1])
    listFoundPic.append(found_ListPic[2])
    listFoundPic.append(found_ListPic[3])
    listFoundPic.append(found_ListPic[4])
    listFoundPic.append(found_ListPic[5])
    listFoundPic.append(found_ListPic[6])
    listFoundPic.append(found_ListPic[7])
    listFoundPic.append(found_ListPic[8])
    found[0] = {'key' : id, 'topic' : found_topic , 'description' : found_desc }
    # t5=time.time()
    print("List1 ",t6-t5)


    # print(found)
    # print(found_type)
    # print("url_f " , found_url)

    # database.child('Lost').child(millis).set(data)


    ref = database.child('CategoryL').child(found_type).get()
    # aaa = database.child('/Lost/..').order_by_child('type').equal_to(found_type).get()
    # print(aaa.val()['topic'])
    # l_ref = database.child('category').child('lost').child(found_type)
    # ref2 = database.child('users').order_by_key().get()
    # print("delooooooooooooooooo " , ref2.val()['type'])
    choice = 2
    # lost_arr = []
    # key_arr_l = []
    i=0
    for data in ref.each():
        idcat = data.val()['id']
        refcat = database.child('Lost').child(str(idcat)).get()
        # lost_type = data.val()['type']
        # if(found_type == lost_type):
        # print(data.key()) # Morty
        # print(data.val()['topic']) # {name": "Mortimer 'Morty' Smith"}
        # topic_lost = data.val()['topic']
        # desc_lost = data.val()['description']
        # url_lost = data.val()['url']
        topic_lost = refcat.val()['topic']
        desc_lost = refcat.val()['description']
        # url_lost = refcat.val()['url']
        # print(topic_lost, " ", desc_lost, " ", url_lost)
        # img4 = imread(url_lost, as_gray=True)
        # img5 = resize(img4, (224, 224))
        # img6 = img_as_ubyte(img5)
        # imshow(img6)
        # picRe = url_lost

        # print("url_l " , url_lost)

        # key = data.key()
        key = idcat
        # lost_arr.append(topic_lost.strip())
        # key_arr_l.append(data.key())
        # l_ref.set(key)
        # t3=time.time()
        lost_ListPic = database.child('PicCategoryL').child(found_type).child(key).child('listPic').get().val()
        listLostPic.append(lost_ListPic[0])
        listLostPic.append(lost_ListPic[1])
        listLostPic.append(lost_ListPic[2])
        listLostPic.append(lost_ListPic[3])
        listLostPic.append(lost_ListPic[4])
        listLostPic.append(lost_ListPic[5])
        listLostPic.append(lost_ListPic[6])
        listLostPic.append(lost_ListPic[7])
        listLostPic.append(lost_ListPic[8])
        # t4=time.time()
        # print("List2 ",t4-t3)
        # t1=time.time()
        PredicPic=calculate_predicPic(listFoundPic,listLostPic)
        # t2=time.time()
        # print("calculate_predicPic ",t2-t1)
        listLost[i]={'key' : key, 'topic' : topic_lost , 'description' : desc_lost , 'img' : PredicPic}
        i+=1
        # print(1)
    # print(lost_arr)
    comp = compare2thing(listLost, found , choice)
    # t10=time.time()
    # print("รวม ",t10-t9)

    # return render(request,'history.html',{"re":comp,'g_id':id,'key':key , "sta":0})
    return comp

def match_post_F(id):
    listFound={}
    lost={}
    listLostPic=[]
    listFoundPic=[]
    # key = request.GET.get('key')
    # id = request.GET.get('id')
    lost_topic = database.child('Lost').child(id).child('topic').get().val()
    lost_desc = database.child('Lost').child(id).child('description').get().val()
    lost_url = database.child('Lost').child(id).child('url').get().val()
    lost_type = database.child('Lost').child(id).child('type').get().val()


    Lost_ListPic = database.child('PicCategoryL').child(lost_type).child(id).child('listPic').get().val()
    listLostPic.append(Lost_ListPic['0'])
    listLostPic.append(Lost_ListPic['1'])
    listLostPic.append(Lost_ListPic['2'])
    listLostPic.append(Lost_ListPic['3'])
    listLostPic.append(Lost_ListPic['4'])
    listLostPic.append(Lost_ListPic['5'])
    listLostPic.append(Lost_ListPic['6'])
    listLostPic.append(Lost_ListPic['7'])
    listLostPic.append(Lost_ListPic['8'])

    lost[0] = {'key' : id, 'topic' : lost_topic , 'description' : lost_desc }


    ref = database.child('CategoryL').child(lost_type).get()
    choice = 1
    # found_arr = []
    # key_arr_f = []
    i=0
    for data in ref.each():
        idcat = data.val()['id']
        refcat = database.child('Found').child(str(idcat)).get()
        # if(lost_type == found_type):
        # print(data.key()) # Morty
        # print(data.val()['topic']) # {name": "Mortimer 'Morty' Smith"}
        topic_found = refcat.val()['topic']
        desc_found = refcat.val()['description']

        # print(topic_found, " ", desc_found, " ", url_found)
        # img4 = imread(url_found, as_gray=True)
        # img5 = resize(img4, (224, 224))
        # img6 = img_as_ubyte(img5)
        # imshow(img6)

        # print("url_f " , url_found)

        key = idcat
        # found_arr.append(topic_found.strip())
        # key_arr_f.append(data.key())

        found_ListPic = database.child('PicCategoryF').child(lost_type).child(key).child('listPic').get().val()

        listFoundPic.append(found_ListPic['0'])
        listFoundPic.append(found_ListPic['1'])
        listFoundPic.append(found_ListPic['2'])
        listFoundPic.append(found_ListPic['3'])
        listFoundPic.append(found_ListPic['4'])
        listFoundPic.append(found_ListPic['5'])
        listFoundPic.append(found_ListPic['6'])
        listFoundPic.append(found_ListPic['7'])
        listFoundPic.append(found_ListPic['8'])

        PredicPic=calculate_predicPic(listLostPic,listFoundPic)

        listFound[i]={'key' : key, 'topic' : topic_found , 'description' : desc_found , 'img' : PredicPic}
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




# def createPicFound(request):
#     firebaseRe = database.child("Found").get()
#     for childSnapshot in firebaseRe.each():
#         childKey = childSnapshot.key()
#         childData = childSnapshot.val();
#         c_type = childData['type']
#         c_topic = childData['topic']
#         c_url = childData['url'];
#
#         Ref_CategoryF=database.child('CategoryF').child(c_type).child(childKey)
#         Ref_CategoryF.remove()
#         print("remove")
#         if(c_url == "https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"):
#             type = find_keyword(c_topic)
#         listPic = (visualize_predictions(model,c_url))
#         if(c_url!="https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"):
#             type = pdPic(list(listPic).index(max(listPic)))
#         dicPic = {}
#         dicPic['id']=childKey
#         dicPic['listPic'] = listPic.tolist()
#         database.child('PicCategoryF').child(type).child(childKey).set(dicPic)
#         print("set PicCategoryF")
#         Ref_st = database.child("Found/" + childKey)
#         Ref_st.update({
#             'type': type
#         });
#         print("set type")
#         database.child('CategoryF').child(type).child(childKey).set({'id': childKey})
#         print("set CategoryF")
#     return render(request,'createPicFound.html')

# def createPicFound(request):
#     firebaseRe = database.child("Lost").get()
#     for childSnapshot in firebaseRe.each():
#         childKey = childSnapshot.key()
#         childData = childSnapshot.val();
#         c_type = childData['type']
#         c_topic = childData['topic']
#         c_url = childData['url'];
#
#         Ref_CategoryF=database.child('CategoryL').child(c_type).child(childKey)
#         Ref_CategoryF.remove()
#         print("remove")
#         if(c_url == "https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"):
#             type = find_keyword(c_topic)
#         listPic = (visualize_predictions(model,c_url))
#         if(c_url!="https://firebasestorage.googleapis.com/v0/b/landf-d7d76.appspot.com/o/nopic.png?alt=media&token=46f9cfff-5158-48c6-8c81-8b67b5a8520e"):
#             type = pdPic(list(listPic).index(max(listPic)))
#         dicPic = {}
#         dicPic['id']=childKey
#         dicPic['listPic'] = listPic.tolist()
#         database.child('PicCategoryL').child(type).child(childKey).set(dicPic)
#         print("set PicCategoryL")
#         Ref_st = database.child("Lost/" + childKey)
#         Ref_st.update({
#             'type': type
#         });
#         print("set type")
#         database.child('CategoryL').child(type).child(childKey).set({'id': childKey})
#         print("set CategoryL")
#     return render(request,'createPicFound.html')
