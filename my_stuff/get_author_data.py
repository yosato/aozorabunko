import sys,os,json,re

def main(jsonFP):
    IDsMetas=json.load(open(jsonFP,'rt'))
    orgLen=len(IDsMetas)
    authorsData={}
    for cntr,(ID,meta) in enumerate(IDsMetas.items()):
        if cntr%100==0:
            sys.stderr.write(str(cntr)+'\n')
        authorData=meta['作家データ']
        author=authorData['作家名']
        if '初出' in meta['作品データ']:
            publicationYearStr=meta['作品データ']['初出']
            if type(publicationYearStr).__name__=='str':
                publicationYearMatch=re.search(r'([12][098][0-9][0-9])',publicationYearStr) 
                if publicationYearMatch:
                    publicationYear=int(publicationYearMatch.groups()[0]) if publicationYearMatch else 'unknown'
                else:
                    publicationYear='unknown'
            elif type(publicationYearStr).__name__=='list' and len(publicationYearStr)==3:
                publicationYear=publicationYearStr[0]
            else:
                publicationYear='unknown'

        elif '親本データ' in meta and '初版発行日' in meta['親本データ'] and type(meta['親本データ']['初版発行日']).__name__=='list' and len(meta['親本データ']['初版発行日'])==3:
            publicationYear=meta['親本データ']['初版発行日'][0]
        else:
            publicationYearStr='unknown'
        workTitle=meta['タイトルデータ']['作品名']



        if 'fileData' not in meta:
            continue
        chrCnt=meta['fileData']['charCount']
        if author not in authorsData:
            authorsData[author]={}
            authorsData[author]['profile']=authorData
            #authorsData[author]['workDist']={}
            authorsData[author]['workDist']={publicationYear:[(ID,workTitle,chrCnt)]}
        elif publicationYear not in authorsData[author]['workDist']:
            authorsData[author]['workDist'][publicationYear]=[(ID,workTitle,chrCnt)]
        else:
            authorsData[author]['workDist'][publicationYear].append((ID,workTitle,chrCnt))
        
    return authorsData

if __name__=='__main__':
    aozoraMetaDir=os.path.join(os.getenv('myproj_loc'),'otherPeoplesProjects/aozorabunko/my_stuff')
    jsonFP=os.path.join(aozoraMetaDir,'aozoraMetaData.json')
    if not os.path.isfile(jsonFP):
        print(jsonFP+' does not exist')
        sys.exit(1)
    authorsData=main(jsonFP)
    json.dump(authorsData,open(os.path.join(aozoraMetaDir,'aozoraAuthorData.json'),'wt'),ensure_ascii=False,indent=4)