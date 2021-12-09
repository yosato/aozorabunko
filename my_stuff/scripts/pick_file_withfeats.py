import os,sys,shutil,glob,zipfile,operator

def main(eConds,vConds,idsMetaData,fnc_unary):
    goodIDs=get_good_ids(eConds,vConds,idsMetaData)
    for ID in goodIDs:
        fnc_unary(ID)

def exists_layered_keys(keys,Dict):
    K1,K2=keys
    if K1 not in Dict:
        return False
    if K2 not in Dict[K1]:
        return False
    return True

def get_good_ids(existConds,valConds,idsMetaData):
    goodIDs=set()
    for (ID,meta) in idsMetaData.items():
        if not any(exists_layered_keys(keys,meta) for keys in existConds[0]): 
            continue
        if not all(exists_layered_keys(keys,meta) for keys in existConds[1]):
            continue
        if not satisfies_valconds_p(valConds,meta):
            continue
        goodIDs.add(ID)
    return goodIDs

def satisfies_valconds_p(conds,metaD):
    for (upperKey,lowerKey,op,val) in conds:
        if not exists_layered_keys((upperKey,lowerKey),metaD):
            return False
        if not op(metaD[upperKey][lowerKey],val):
            return False
    return True

def id_file_copy_to_dest(id,destDir):
    srcfps=glob.glob('../cards/*/files/'+id+'_*.zip')
    if not srcfps:
        print('file for id '+str(id)+' not found')
        return None
    elif len(srcfps)>=2:
        print('more than one file ('+str(len(srcfps))+') for id '+str(id))  
        
    srcfp=srcfps[0]
    try:
        zipObj=zipfile.ZipFile(srcfp,mode='r')
        newDest=destDir+'/'+id
        if not os.path.isdir(newDest):
            os.makedirs(newDest)
        zipObj.extractall(newDest)
    except:
        print('unzip failed for '+srcfp)

if __name__=='__main__':
    import json, argparse
    idsMeta=json.load(open('aozoraMetaData.json','rt'))
    destDir='extracted'
    id_extract=lambda id: id_file_copy_to_dest(id,destDir)
    valConds=[('作品データ','文字遣い種別',operator.eq,'新字新仮名'),('作品データ','分類',lambda cer,cnd: not cnd in cer,'K')]
    existConds=[[('作品データ','初出'),('親本データ','初版発行日')],[]]
    main(existConds,valConds,idsMeta,id_extract)           