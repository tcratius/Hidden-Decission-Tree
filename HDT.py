########################################################################################################################
# Author: Naveenkumar Ramaraju                                                                                         #
# Hidden Decision Trees                                                                                                #
# Based article http://www.datasciencecentral.com/profiles/blogs/state-of-the-art-machine-learning-automation-with-hdt #
# Date: Feb-18-2017                                                                                                    #
# File version - 1                                                                                                     #
# Python - version: 3.6                                                                                                #
########################################################################################################################

from math import log
import time


start = time.time()


# This method updates the dictionaries based on given ID, pv and word
def update_pvs(word, pv, id, word_count_dict, word_pv_dict, min_pv_dict, max_pv_dict, ids_dict):
    if word in word_count_dict:
        word_count_dict[word] += 1
        word_pv_dict[word] += pv
        if min_pv_dict[word] > pv:
            min_pv_dict[word] = pv
        if max_pv_dict[word] < pv:
            max_pv_dict[word] = pv
        ids_dict[word].append(id)
    else:
        word_count_dict[word] = 1
        word_pv_dict[word] = pv
        min_pv_dict[word] = pv
        max_pv_dict[word] = pv
        ids_dict[word] = [id]


# dictionaries to hold count of each key words, their page views, and the ids of the article in which used.
register = dict()
registerPV = dict()
registerPVMax = dict()
registerPVMin = dict()
registerID = dict()
articleTitle = list()  # Lists to hold article id wise title name and pv
articlePV = list()
sumPV = 0
ID = 0
in_file = open("HDTdata3.txt", "r")

for line in in_file:
    if ID == 0:  # excluding first line as it is header
        ID += 1
        continue
    line = line.lower()
    # AUX is the whole row taken
    AUX = line.split('\t')  # Indexes will have: 0 - Title, 1 - URL, 2 - data and 3 - page views
    # print("This is AUX:", AUX)
    URL = AUX[1]
    # pv = page view. AUX[3] is the column for page view count
    PV = log(1 + int(AUX[3]))
    print("This is AUX[3]", AUX[3])
    if "/blogs/" in URL:
        assigningTopicType = "BLOG"
    else:
        assigningTopicType = "OTHER"
#   #--- clean article titles, remove stop words
    title = AUX[0]
    title = " " + title + " "  # adding space at the ends to treat stop words at start, mid and end alike
    title = title.replace('"', ' ')
    title = title.replace('?', ' ? ')
    title = title.replace(':', ' ')
    title = title.replace('.', ' ')
    title = title.replace('(', ' ')
    title = title.replace(')', ' ')
    title = title.replace(',', ' ')
    title = title.replace(' a ', ' ')
    title = title.replace(' the ', ' ')
    title = title.replace(' for ', ' ')
    title = title.replace(' in ', ' ')
    title = title.replace(' and ', ' ')
    title = title.replace(' or ', ' ')
    title = title.replace(' is ', ' ')
    title = title.replace(' in ', ' ')
    title = title.replace(' are ', ' ')
    title = title.replace(' of ', ' ')
    title = title.strip()
    title = ' '.join(title.split())  # replacing multiple spaces with one

    # break down article title into keyword tokens
    aux2 = title.split(' ')
    num_words = len(aux2)
    for index in range(num_words):
        word = aux2[index].strip()
        word = word + '\t' + 'N/A   ' + '\t' + assigningTopicType
        update_pvs(word, PV, ID - 1, List, registerPV, registerPVMin, registerPVMax, registerID)  # updating single word

        if (num_words - 1) > index:
            word = aux2[index] + '\t' + aux2[index+1] + '\t' + assigningTopicType
            update_pvs(word, PV, ID - 1, List, registerPV, registerPVMin, registerPVMax, registerID)  # updating bigRAM

    articleTitle.append(title)
    articlePV.append(PV)
    sumPV += PV
    ID += 1
in_file.close()

nArticles = ID - 1  # -1 as the increments were done post loop
avg_pv = sumPV / nArticles
articleFlag = ["BAD" for n in range(nArticles)]
NIDx = 0
NIDxGood = 0
OUT = open('hdt-out2.txt','w')
OUT2 = open('hdt-reasons.txt','w')
for IDx in list:
    n = list[IDx]
    print(n)
    Avg = registerPV[IDx] / n
    Min = registerPVMin[IDx]
    Max = registerPVMax[IDx]
    IDList = registerID[IDx]
    NIDx += 1
    # below values are chosen based on heuristics and experimenting
    if ((n > 3) and (n < 8) and (Min > 6.9) and (Avg > 7.6)) or \
         ((n >= 8) and (n < 16) & (Min > 6.7) and (Avg > 7.4)) or \
         ((n >= 16) and (n < 200) & (Min > 6.1) and (Avg > 7.2)):
        OUT.write(IDx + '\t' + str(n) + '\t' + str(Avg) + '\t' + str(Min) + '\t' + str(Max) + '\t' + str(IDList) + '\n')
        NIDxGood += 1
        for ID in IDList:
            title = articleTitle[ID]
            PV = articlePV[ID]
            OUT2.write(title + '\t' + str(PV) + '\t' + IDx + '\t' + str(n) + '\t' + str(Avg) + '\t' + str(Min) + '\t' + str(Max) + '\n')
            articleFlag[ID] = "GOOD"

# Computing results based on Threshold values
pv_threshold = 7.1
pv1 = 0
pv2 = 0
n1 = 0
n2 = 0
m1 = 0
m2 = 0
FalsePositive = 0
FalseNegative = 0
for ID in range(nArticles):
    PV = articlePV[ID]
    if articleFlag[ID] is "GOOD":
        n1 += 1
        pv1 += PV
        if PV < pv_threshold:
            FalsePositive += 1
    else:
        n2 += 1
        pv2 += PV
        if PV > pv_threshold:
            FalseNegative += 1
    if PV > pv_threshold:
        m1 += 1
    else:
        m2 += 1

# Printing results
avg_pv1 = pv1/n1
avg_pv2 = pv2/n2
errorRate = (FalsePositive + FalseNegative)/nArticles
aggregationFactor = (NIDx / NIDxGood) / (nArticles / n1)
print ("Average pv: " + str(avg_pv))
print ("Number of articles marked as good: ", n1, " (real number is ", m1,")", sep = "" )
print ("Number of articles marked as bad: ", n2, " (real number is ", m2,")", sep = "")
print ("Avg pv: articles marked as good:", avg_pv1)
print ("Avg pv: articles marked as bad:",avg_pv2)
print ("Number of false positive:",FalsePositive,"(bad marked as good)")
print ("Number of false negative:", FalseNegative, "(good marked as bad)")
print ("Number of articles:", nArticles)
print ("Error Rate: ", errorRate)
print ("Number of feature values: ", NIDx, " (marked as good: ", NIDxGood, ")", sep ="")
print ("Aggregation factor:", aggregationFactor)

print("Execution time: " + str(time.time() - start) +"s")
