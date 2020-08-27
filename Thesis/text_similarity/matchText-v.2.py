from fuzzywuzzy import fuzz
from fuzzywuzzy.process import utils
import fuzzywuzzy
from difflib import SequenceMatcher

file_lost = open("lost.txt" , 'r' , encoding="utf-8")
f_lost = file_lost.readlines()

file_found = open("found.txt" , 'r' , encoding="utf-8")
f_found = file_found.readlines()

lost_arr = []
q1=1
for m in f_lost:
    if(q1<=10):
        j=(m.strip(),1)
        lost_arr.append(j)

    elif(q1<=20):
        j=(m.strip(),2)
        lost_arr.append(j)

    elif(q1<=30):
        j=(m.strip(),3)
        lost_arr.append(j)
        
    q1+=1
found_arr = []
q2=1
for n in f_found:
    if(q2<=10):
        k=(n.strip(),1)
        found_arr.append(k)

    elif(q2<=20):
        k=(n.strip(),2)
        found_arr.append(k)

    elif(q2<=30):
        k=(n.strip(),3)
        found_arr.append(k)
        
    q2+=1

file_lost.close()
file_found.close()

def topfive(inputma , listRatios):
    # print("top5")
    listRatios = [v for k, v in sorted(listRatios.items(), key=lambda item: item[1]["per"],reverse=True)]
    #print("list:",listRatios)
    pf=0
    for i in range(0, len(listRatios),1):
        if(listRatios[i]["PD"]==1 and ((i+1)<=10) and ((i+1)>=0)):
            print("[",i+1,"]\t","ประเภทที่ ",listRatios[i]["PD"]," ",listRatios[i]["per"],"%\t",inputma," คล้ายกับ ",listRatios[i]["topic"])
            pf+=1
        elif(listRatios[i]["PD"]==2 and ((i+1)<=20) and ((i+1)>10)):
            print("[",i+1,"]\t","ประเภทที่ ",listRatios[i]["PD"]," ",listRatios[i]["per"],"%\t",inputma," คล้ายกับ ",listRatios[i]["topic"])
            pf+=1
        elif(listRatios[i]["PD"]==3 and ((i+1)<=30) and ((i+1)>20)):
            print("[",i+1,"]\t","ประเภทที่ ",listRatios[i]["PD"]," ",listRatios[i]["per"],"%\t",inputma," คล้ายกับ ",listRatios[i]["topic"])
            pf+=1
        else:
            print("[",i+1,"]\t","ประเภทที่ ",listRatios[i]["PD"]," ",listRatios[i]["per"],"%\t",inputma," คล้ายกับ ",listRatios[i]["topic"])
            pf+=0
    respf=(pf/len(listRatios))*100
    print(respf)
    
def compare2thing(lost , found , choice):
    
    listRatios={}
    
    if(choice == "1"):
        resfound=[lis[0] for lis in found]
        reslost=[lis[0] for lis in lost]
        pd=[lis[1] for lis in found]
        for i in range(0, len(resfound) ,1):
        
            sorted1 =fuzz._process_and_sort(reslost[0], force_ascii=True, full_process=0)
            sorted2 =fuzz._process_and_sort(resfound[i], force_ascii=True, full_process=0)
          

            s1, s2 = utils.make_type_consistent(sorted1,sorted2)

            #1 topic
            if len(s1) <= len(s2):
                shorter = s1
                longer = s2
            else:
                shorter = s2
                longer = s1

            seq1 = SequenceMatcher(None,shorter,longer)
            a = list(seq1.get_matching_blocks())
            #print(a)

            Ratio_topic = seq1.ratio()
            Ratios_topic = utils.intr(100 * Ratio_topic)

            # print("img per " , Ratios_img)

            # print("key_f" , key_found)

            #print(Ratio_topic)
            listRatios[i]={'keyDB' : i , "topic": resfound[i],"per" : Ratios_topic,"PD":pd[i]}
        # print("choice 1")
        top = topfive(reslost[0] , listRatios)
        
    elif(choice == "2"):
        resfound=[lis[0] for lis in found]
        reslost=[lis[0] for lis in lost]
        pd=[lis[1] for lis in lost]
        for i in range(0, len(reslost) ,1):
            
            sorted1 =fuzz._process_and_sort(resfound[0], force_ascii=True, full_process=1)
            sorted2 =fuzz._process_and_sort(reslost[i], force_ascii=True, full_process=1)
            #print("sorted1 ",sorted1)
            #print("sorted2 ",sorted2)
            #ใน partial_ratio(sorted1, sorted2)
            s1, s2 = utils.make_type_consistent(sorted1, sorted2)
            #print("s1 ",s1)
            #print("s2 ",s2)
            if len(s1) <= len(s2):
                shorter = s1
                longer = s2
            else:
                shorter = s2
                longer = s1
                
            print("shorter: ",shorter)
            print("longer: ",longer)

            m = SequenceMatcher(None, shorter, longer)
            Ratios_topic = utils.intr(100 * m.ratio())
            print("แบบเช็ดครั้งเดียว",Ratios_topic,"%")
            
            blocks = m.get_matching_blocks()
            print("blocks: ",blocks)
            print("------------")
            
            scores = []
            for block in blocks:
                print("block: ",block)

                long_start = block[1] - block[0] if (block[1] - block[0]) > 0 else 0

                po1=int(block[0]+block[2])
                po2=int(block[1]+block[2])
                print("block[0]: ",block[0],"**",shorter[block[0]:po1],"**")
                print("block[1]: ",block[1],"**",longer[block[1]:po2],"**")

                long_end = long_start + len(shorter)
                print("long_end: ",long_end)

                long_substr = longer[long_start:long_end]
                print("long_substr: ",long_substr)
                
                m2 = SequenceMatcher(None, shorter, long_substr)
                blocks2 = m2.get_matching_blocks()
                print("blocks2: ",blocks2)
                r = m2.ratio()
                print("r: ",r)
                print("------------------------")
                if r > .995:
                    return 100
                else:
                    scores.append(r)
                    
            Ratios_topic=utils.intr(100 * max(scores))
            print("Ratios_topic: ",Ratios_topic,"%")
            print("--------------------------------------------------------\n")

            listRatios[i]={'keyDB' : i , "topic": reslost[i],"per" : Ratios_topic,"PD":pd[i]}
        # print("choice 1")
        top = topfive(resfound[0] , listRatios)

choice = input("Choose your choice (1)lost , (2)found : ")
#txt = input("input Text :")
if(choice == "1"):
    #compare2thing(txt,found_arr,choice)
    compare2thing(lost_arr,found_arr,choice)
elif(choice == "2"):
    #compare2thing(lost_arr,txt,choice)
    compare2thing(lost_arr,found_arr,choice)
