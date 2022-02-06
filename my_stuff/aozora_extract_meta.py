from collections import defaultdict
import os, sys, re, glob, datetime,time,json
from types import MethodWrapperType
from typing import DefaultDict
from bs4 import BeautifulSoup

def extract_all_metadata(aozoraCardDir,upTo=None):
    idsMetas={};cumKeysCnts=defaultdict(int)
    subdirs=[dir for dir in os.listdir(aozoraCardDir) if re.match(r'[0-9]+',dir) ]
    IDsFps={};HtmlFps=[]
    for mySubdir in subdirs:
        HtmlFps.extend(glob.glob(os.path.join(aozoraCardDir,mySubdir,'card*.html')))
    doneIDs=set();cumKeys=set();doneWorkAuthPairs=DefaultDict(list)
    totalFileCnt=len(HtmlFps)
    errors=defaultdict(list)
    for cntr,cardHtml in enumerate(HtmlFps):
        if upTo and cntr>upTo:
            break
        cardFN=os.path.basename(cardHtml)
        IDStr=os.path.splitext(cardFN)[0].replace('card','')
        assert(IDStr.isdigit())
        ID=int(IDStr)
        if ID in doneIDs:
            print('suspected duplicate based on ID')
            errors['idDuplicate'].append(cardHtml)
        if cntr!=0 and cntr%1000==0:
            print(str(cntr)+', '+str((cntr/totalFileCnt)*100))
        metaDict,keys=extract_meta_fromhtml(cardHtml)
        
        if metaDict is None:
            errors[keys].append(cardHtml)
            continue
        for key in keys:
            if key in cumKeysCnts:
                cumKeysCnts[key]+=1
            else:
                cumKeysCnts[key]=1

        work=metaDict['タイトルデータ']['作品名']; author=metaDict['作家データ']['作家名']
        workAuthPair=(work,author)
        if workAuthPair in doneWorkAuthPairs:
#            print('suspected duplicate based on author/work')
            errors['duplicate'].append(cardHtml)
        else:
            doneWorkAuthPairs[workAuthPair].append(ID)
        idsMetas[ID]=(metaDict,get_filedata(ID,aozoraCardDir))
    return idsMetas,cumKeysCnts,errors
    
def get_filedata(ID,Dir):
    workHtmls=glob.glob(os.path.join(Dir,'files',ID+'*.html'))
    workTexts=glob.glob(os.path.join(Dir,'files',ID+'*.txt'))
    if len(workHtmls)!=0:
        print('sth wrong')
        return None
    else:
        htmlData=(os.path.basename(workHtmls[0]),sys.getsizeof(workHtmls[0]))
    textData=None if len(workTexts)!=0 else (os.path.basename(workTexts[0]),sys.getsizeof(workTexts[0]))

    return htmlData,textData

def extract_meta_fromhtml(htmlfp):
    fn=os.path.basename(htmlfp)
    metaDict={};layeredKeys=set()
    with open(htmlfp,errors='ignore') as fsr:
        soup=BeautifulSoup(fsr,'html.parser')
    tables=soup.find_all('table')
    for table in tables:
        upperKey=  table['summary']
        internalDict={}
        for child in table.find_all('tr'):
            authorWorkPair={}
            if '：' not in child.text:
                continue
            els=child.text.strip().split('：')
            if els[0]=='人物について' or els[0]=='作品について':
                continue
            #if any(type(keyval).__name__=='str' for keyval in els):
            #    print('non string value')
            #    print(fn)
            #    continue
            if len(els)!=2:
                #print('something is wrong: '+repr(els))
                
#                time.sleep(2)
                return None,'format'
            key,val=[el.strip() for el in els]
            dateEls=extract_date(val)
            if dateEls:
                try:
                    val=datetime.date(*dateEls)
                    val=(val.year,val.month,val.day)
                except:
                    print('something wrong with date')
                    return None,'date'
            
            internalDict[key]=val
            layeredKey=(upperKey,key)
            layeredKeys.add(layeredKey)
        metaDict[upperKey]=internalDict
    if 'タイトルデータ' not in metaDict or '作品名' not in metaDict['タイトルデータ'] or '作家データ' not in metaDict or '作家名' not in metaDict['作家データ']:
        return None,'noAuthOrWork'
    return metaDict,layeredKeys

def extract_date(str):
    match=re.match(r'([0-9]+)(（.+）)?[年-]([0-9]+)[月-]([0-9]+)日?',str)
    if not match:
        return None
    else:
        Y,M,D=[int(str) for str in match.groups() if str and str.isdigit()]
#        YrCond=(Y>1600 and Y<2030)
#        MonthCond=(M in range(1,13))
#        DayCond=(D in range(1,32))
#        if any(not cond for cond in (YrCond,MonthCond,DayCond)):
#            print('something is wrong in date')
#            print(Y,M,D)
#            time.sleep(3)
#            return None
        return Y,M,D
    

if __name__=='__main__':
    aozoraCardDir=os.getenv('HOME')+'/otherPeoplesProjects/aozorabunko/cards'
    assert(os.path.isdir(aozoraCardDir))
    #htmlfps=glob.glob(aozoraCardDir+'/00*/*.html')
    #assert(os.path.isfile(htmlfps))
    IDsMetaData,cumKeys,errors=extract_all_metadata(aozoraCardDir)
    json.dump(IDsMetaData,open('aozoraMetaData.json','wt'),ensure_ascii=False,indent=4)
    print(len(IDsMetaData))