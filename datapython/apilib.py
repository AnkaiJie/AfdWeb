from datapython.credentials import API_KEY, DBNAME, USER, PASSWORD, HOST
import requests
import json
import time
import concurrent.futures
import pymysql
import time
from datapython.sql import *

class reqWrapper:
    def __init__(self, headers):
         self.sesh = requests.session()
         self.headers = headers

    def get(self, url):
        return self.sesh.get(url, headers=self.headers)

    def getJson(self, url):
        return self.sesh.get(url, headers=self.headers).json()

    def getJsonPretty(self, url):
        resp = self.sesh.get(url, headers=self.headers)
        return json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',', ': '))

    def prettifyJson(self, jsonObj):
        return json.dumps(jsonObj, sort_keys=True, indent=4, separators=(',', ': '))

# this class returns flattened dictionaries of api keys
# it does some filtering and flattening of returned json, but doesn ot directly modify
class ScopusApiLib:

    def __init__(self):
        headers={'Accept':'application/json', 'X-ELS-APIKey': API_KEY}
        self.reqs = reqWrapper(headers)
        self.utility = Utility()

    # returns basic info about a given author
    def getAuthorMetrics(self, auth_id):
        url = "http://api.elsevier.com/content/author?author_id=" + str(auth_id)
        resp = self.reqs.getJson(url)
        # print(resp)
        resp = resp['author-retrieval-response'][0]

        pfields = ['preferred-name', 'publication-range']
        cfields = ['citation-count', 'cited-by-count', 'dc:identifier', 'document-count', 'eid']
        profile = self.utility.filter(resp['author-profile'], pfields)
        coredata = self.utility.filter(resp['coredata'], cfields)
        profile.update(coredata)
        profile = self.utility.flattenDict(profile)
        keys = list(profile.keys())
        for k in keys:
            if 'preferred-name' in k:
                profile[k.split('_')[1]] = profile.pop(k)
        if 'given-name' in profile and profile['given-name'] is not None:
            profile['given-name'] = self.processFirstName(profile['given-name'])
        if 'dc:identifier' in profile and profile['dc:identifier']:
            profile['dc:identifier'] = profile['dc:identifier'].split(':')[1].strip()
        return profile

    #returns array of author papers eids
    def getAuthorPapers(self, auth_id, start=0, num=100):
        auth_id = str(auth_id)
        if 'AUTHOR_ID' in auth_id:
            auth_id = auth_id.split(':')[1]

        #cited by order
        url = "http://api.elsevier.com/content/search/scopus?query=AU-ID(" + auth_id + ")&field=eid&sort=citedby-count&start=" + \
            str(start) + "&count=" + str(num)
        if start is not 0:
            url += "&start=" + str(start) + "&num=" + str(num)
        results = self.reqs.getJson(url)['search-results']["entry"]
        eid_arr = []
        for pdict in results:
            eid_arr.append(pdict['eid'])
        return eid_arr

    # returns an array of papers that cite the paper with the given eid    
    def getCitingPapers(self, eid, num=100, sort_order="date"):
        #eid = '2-s2.0-79956094375'
        url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&start=0&count=' + str(num)
        if sort_order == "citations":
            url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&start=0&sort=+citedby-count&count=' + str(num)
        resp = self.reqs.getJson(url)

        resp = resp['search-results']['entry']
        if 'error' in resp[0] and resp[0]['error'] == 'Result set was empty':
            return []
        #print(resp)
        paps = [pap['eid'] for pap in resp]
        return paps

    #returns basic info about a paper with the given eid
    def getPaperInfo(self, eid):
        url = 'https://api.elsevier.com/content/abstract/eid/' + str(eid) + '?&field=authors,coverDate,eid,title,publicationName'
        resp = self.reqs.getJson(url)
        try:
            if 'service-error' in resp:
                time.sleep(3)
                resp = self.reqs.getJson(url)
                if 'service-error' in resp:
                    print("SERVICE ERROR Citing")
                    raise
            resp = resp['abstracts-retrieval-response']
        except:
            print(resp)
            print(url)
            raise
        coredata = resp['coredata']
        if resp['authors']:
            authors = resp['authors']['author']
            auinfos = self.processAuthorList(authors)
            coredata['authors'] = auinfos
        coredata = self.utility.removePrefix(coredata)
        return coredata

    def processFirstName(self, name):
        return name.split()[0].strip()

    def processAuthorList(self, arr):
        auids = []
        for a in arr:
            if '@auid' in a and a['@auid'] != '':
                res = self.utility.filter(a, ['@auid', 'ce:indexed-name', 'ce:initials', 'ce:surname', 'ce:given-name'])
                res = self.utility.removePrefix(res)
                self.utility.replaceKey(res, '@auid', 'dc:identifier')
                res['dc:identifier'] = 'AUTHOR_ID:' + res['dc:identifier']
                auids.append(res)
            else: 
                #no scopus id, just use name as id
                res = self.utility.filter(a, ['ce:indexed-name', 'ce:initials', 'ce:surname', 'ce:given-name'])
                res = self.utility.removePrefix(res)

                newid = 'AUTHOR_ID:'
                id_arr = []
                if 'initials' in res:
                    id_arr.append(res['initials'])
                if 'surname' in res:
                    id_arr.append(res['surname'])

                newid += '_'.join(id_arr)
                res['dc:identifier'] = newid

                auids.append(res)
        return auids

    # returns an array of papers that the paper with the given eid cites
    def getPaperReferences(self, eid, refCount = -1):
        url = 'https://api.elsevier.com/content/abstract/eid/' + str(eid) + '?&view=REF'
        req_url = url
        start = 1
        custom_count = False
        if refCount is not -1:
            req_url += '&refcount=' + str(refCount)
            custom_count = True
        else:
            req_url += '&start='+ str(start) + '&refcount=40'
        
        ref_arr = []
        while(True):
            time.sleep(0.2)
            resp = self.reqs.getJson(req_url)
            resp_body = {}
            try:
                resp_body = resp['abstracts-retrieval-response']
            except Exception as e:
                if 'service-error' in resp and resp['service-error']['status']['statusText'] == "'startref' or 'refcount' parameter missing or invalid":
                    break
                else:
                    time.sleep(2)
                    resp = self.reqs.getJson(url)
                    if 'service-error' in resp:
                        print("SERVICE ERROR References")
                        print(url)
                        print(resp)
                        raise
                    else:
                        resp_body = resp['abstracts-retrieval-response']

            if resp_body is None:
                return None
            else:
                resp_body = resp_body['references']['reference']

            current_refs = []
            for raw in resp_body:
                ref_dict = {}
                ref_dict['authors'] = None
                if raw['author-list'] and raw['author-list']['author']:
                    auth_list = raw['author-list']['author']
                    auids = self.processAuthorList(auth_list)
                    ref_dict['authors'] = auids

                #ref_dict['srceid'] = eid
                ref_dict['eid'] = raw['scopus-eid']
                if 'sourcetitle' in raw:
                    ref_dict['publicationName'] = raw['sourcetitle']
                current_refs.append(ref_dict)

            ref_arr += current_refs
            start += 40
            req_url = url + '&start='+ str(start) + '&refcount=40'
            if custom_count:
                break

        return ref_arr

    #makes a jsonObj pretty
    def prettifyJson(self, jsonObj):
        return self.reqs.prettifyJson(jsonObj)

class Utility:
    #returns dict with the wanted keys only, if keys empty, just flattens dict
    def flattenDict (self, d):
        def expand(key, value):
            if isinstance(value, dict):
                return [ (key + '_' + k, v) for k, v in self.flattenDict(value).items()]
            else:
                return [ (key, value) ]

        items = [ item for k, v in d.items() for item in expand(k, v) ]
        return dict(items)

    # if no keys specified, return original dictionary
    def filter(self, d, keys):
        if len(keys) is 0:
            return d
        dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
        return dictfilt(d, keys)

    def removePrefix (self, origDict, sep=':'):
        d = dict(origDict)
        rem = []
        for key, value in d.items():
            if len(key.split(sep)) > 1:
                rem.append(key)
        for k in rem:
            newkey = k.split(sep)[1]
            d[newkey] = d.pop(k)
        return d

    def addPrefixToKeys(self, dOrig, prefix):
        d = dict(dOrig)
        keys = list(d.keys())
        for key in keys:
            d[prefix+key] = d.pop(key) 
        return d

    #stack overflow code
    def merge_dicts(self, *dict_args):
        '''
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        '''
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return dict(result)

    def changeKeyString(self, d, change, toThis):
        keys = list(d.keys())
        for key in keys:
            newKey = key.replace(change, toThis)
            d[newKey] = d.pop(key)

    def changeValueString(self, d, change, toThis):
        for key, val in d.items():
            if change in val:
                d[key] = val.replace(change, toThis)

    def replaceKey(self, d, change, toThis):
        d[toThis] = d.pop(change)

    def removeNone(self, d):
        keys = list(d.keys())
        for key in keys:
            if d[key] is None:
                d.pop(key)

# all the SQL code to insert/update is here
class DbInterface:
    def __init__(self, author_id):
        self.utility = Utility()
        self.scops = ScopusApiLib()
        self.author_id = author_id

        self.conn = pymysql.connect(HOST, USER, PASSWORD, DBNAME, charset='utf8')
        self.createTables()
        

    def pushToS1(self, srcPaperDict, targPaperDict, srcAuthor, targAuthor):

        s1_table = self.author_id + "_citations_s1"

        srcPaperDict = self.utility.addPrefixToKeys(srcPaperDict, 'src_paper_')
        targPaperDict = self.utility.addPrefixToKeys(targPaperDict, 'targ_paper_')
        srcAuthor = self.utility.addPrefixToKeys(srcAuthor, 'src_author_')
        targAuthor = self.utility.addPrefixToKeys(targAuthor, 'targ_author_')

        aggDict = self.utility.merge_dicts(srcPaperDict, targPaperDict, srcAuthor, targAuthor)
        self.utility.removeNone(aggDict)
        self.utility.changeKeyString(aggDict, '-', '_')
        self.utility.changeKeyString(aggDict, '@', '')
        self.utility.changeKeyString(aggDict, ':', '_')
        self.utility.changeValueString(aggDict, '\\', '')
        self.utility.changeValueString(aggDict, '"', '\\"')

        # print(self.toString(aggDict))
        self.pushDict(s1_table, aggDict)

    def processOvercites(self):
        s2_command = create_s2(self.author_id)
        overcite_command = create_overcites(self.author_id)
        cur = self.conn.cursor()
        try:
            cur.execute(s2_command)
            cur.execute(overcite_command)
        except:
            print(s2_command)
            print(overcite_command)
            raise
        self.conn.commit()
        cur.close()
        return getTableNames(self.author_id)


    def toString(self, aggDict):
        srcp = None
        targp = None
        srca = None
        targa = None
        srce = None
        targe = None
        if 'src_paper_eid' in aggDict:
            srce = aggDict['src_paper_eid']
        if 'src_paper_title' in aggDict:
            srcp = aggDict['src_paper_title']
        if 'targ_paper_eid' in aggDict:
            targe = aggDict['targ_paper_eid']
        if 'targ_paper_title' in aggDict:
            targp = aggDict['targ_paper_title']
        if 'src_author_indexed_name' in aggDict:
            srca = aggDict['src_author_indexed_name']
        if 'targ_author_indexed_name' in aggDict:
            targa = aggDict['targ_author_indexed_name']
        return 'Source: ' + str(srca) +' / ' + str(srce) + ' / ' + str(srcp) + ' ------------- ' + 'Target: ' + str(targa) +' / ' + str(targe) + ' / ' + str(targp)

    def createTables(self):
        s1_command = create_s1(self.author_id)
        check_s1_cmd = check_s1(self.author_id)
        prim_key = create_s1_key(self.author_id)
        cur = self.conn.cursor()
        try:
            cur.execute(check_s1_cmd)
            row = cur.fetchone()
            if row[0] == 0:
                cur.execute(s1_command)
                print('create s1')
                cur.execute(prim_key)
                print('prim key s1')
        except:
            print(s1_command)
            print(check_s1_cmd)
            print(prim_key)
            raise
        self.conn.commit()
        cur.close()

    def pushDict(self, table, d):
        cur = self.conn.cursor()
        keys = d.keys()
        vals = d.values()
        vals = ['"' + v + '"' for v in vals if v is not None]
        command = "REPLACE INTO %s (%s) VALUES(%s)" % (
            table, ",".join(keys), ",".join(vals))
        try:
            cur.execute(command)
        except:
            print(command)
            raise
        self.conn.commit()
        cur.close()

    def __del__(self):
        self.conn.close()

# all the API return value parsing should be placed here
# any text/key processing is done here
# there is no sql code in this class, that should all be handled in DbInterface()

dbi = None
sApi = ScopusApiLib()

def storeAuthorTest(author_id):
    print(author_id)

# this should be the only method that the client interacts with
def storeAuthorMain(auth_id, start_index=0, pap_num=20, cite_num=20, refCount=-1, workers=5):
    author_profile = sApi.getAuthorMetrics(auth_id)
    author_identifier = author_profile['dc:identifier'] + '_' + author_profile['given-name'] + '_' + author_profile['surname']
    dbi = DbInterface(author_identifier)
    # Puts the main author record
    print('Running script on author: ' + str(auth_id))
    
    # Puts the authors papers
    print('Getting author papers')
    papers = sApi.getAuthorPapers(auth_id, start=start_index, num=pap_num)


    executor = concurrent.futures.ProcessPoolExecutor(workers)    
    processes = [executor.submit(processPaperMain, author_identifier, paper_arr, cite_num, refCount)
        for paper_arr in grouper(2, papers)]
    for p in processes:
        p.result()

    print('Beginning processing of s2 and overcite table.')
    table_names = dbi.processOvercites()
    print('Done.')
    return table_names


def grouper(lengths, arr):
    arrarr = []
    begin = 0
    arrlen = len(arr)
    while begin < arrlen:
        sub = arr[begin:begin+lengths]
        begin += lengths
        arrarr.append(sub)
    return arrarr

def processPaperMain(author_id, papers, cite_num,refCount):
    for eid in papers:
        print('Beginning processing for paper: ' + eid + ' of author: ' + str(author_id))
        #main_title = self.storePapersOnly(eid)
        # references = sApi.getPaperReferences(eid, refCount=refCount)
        # if references is None:
        #     print('No Data on References')
        #     references = []
        citedbys = sApi.getCitingPapers(eid, num=cite_num, sort_order="citations")
        thisPaperDict = sApi.getPaperInfo(eid) #do this here to avoid duplicate api calls
        if thisPaperDict is None:
            print("NONE MAIN PAPER")
            continue


        #Puts the citing papers of the authors papers, and those respective authors
        print('Handling citing papers...')

        ccount = 1
        for citing in citedbys:
            print('Citing paper index number: ' + str(ccount))
            citePaperDict = sApi.getPaperInfo(citing)
            if citePaperDict is None:
                print("NONE CITING PAPER")
                continue
            storeCiting(dict(citePaperDict), dict(thisPaperDict), author_id)
            storePaperReferences(citing, dict(citePaperDict), author_id, refCount=refCount)
            ccount += 1
        print('Done citing papers.')
        # # Puts the cited papers of the authors papers, and those respective authors
        # print('Handling references...')
        # #Repeated code from storePaperReferences for clarity
        # for ref in references:

        #     refid = ref['eid']
        #     self.storeToStage1(eid, refid)
        #     self.storePaperReferences(refid, refCount=refCount)
        # print('Done references')

def storePaperReferences(eid, srcPaperDict, author_id, refCount=-1, ):
    dbi = DbInterface(author_id)
    references = sApi.getPaperReferences(eid, refCount=refCount)
    if references is None:
        return
    srcAuthors = [{'indexed_name': None}]
    if 'authors' in srcPaperDict and srcPaperDict['authors'] is not None:
        srcAuthors = srcPaperDict.pop('authors')

    for targPaperDict in references:
        targAuthors = [{'indexed_name': None}]
        if 'authors' in targPaperDict and targPaperDict['authors'] is not None:
            targAuthors = targPaperDict.pop('authors')

        for srcAuth in srcAuthors:
            for targAuth in targAuthors:
                dbi.pushToS1(srcPaperDict, targPaperDict, srcAuth, targAuth)

def storeCiting(srcPaperDict, targPaperDict, author_id):
    dbi = DbInterface(author_id)
    srcAuthors = [{'indexed_name': None}]
    targAuthors = [{'indexed_name': None}]
    if 'authors' in srcPaperDict:
        srcAuthors = srcPaperDict.pop('authors')
    if 'authors' in targPaperDict:
        targAuthors = targPaperDict.pop('authors')

    for srcAuth in srcAuthors:
        for targAuth in targAuthors:
            dbi.pushToS1(srcPaperDict, targPaperDict, srcAuth, targAuth)


# def storeToStage1(self, srcpapid, targpapid):
#     srcPaperDict = sApi.getPaperInfo(srcpapid)
#     targPaperDict = sApi.getPaperInfo(targpapid)
#     srcAuthors = [{'indexed_name': None}]
#     targAuthors = [{'indexed_name': None}]
#     if 'authors' in srcPaperDict:
#         srcAuthors = srcPaperDict.pop('authors')
#     if 'authors' in targPaperDict:
#         targAuthors = targPaperDict.pop('authors')

#     for srcAuth in srcAuthors:
#         for targAuth in targAuthors:
#             dbi.pushToS1(srcPaperDict, targPaperDict, srcAuth, targAuth)

def getAuthorsFromPaper(origPaperDict):
    paperDict = dict(origPaperDict)

    author_arr = []
    if 'authors' in paperDict:
        for authid in paperDict['authors']:
            if isinstance(authid, dict):
                author_arr.append(authid)
            else:
                author_info = getAuthorInfo(authid)
                author_arr.append(author_info)
        origPaperDict.pop('authors')
    return author_arr

def getAuthorInfo(auth_id):
    author = sApi.getAuthorMetrics(auth_id)
    return author
