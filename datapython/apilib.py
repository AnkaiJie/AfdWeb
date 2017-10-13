from datapython.credentials import API_KEY, DBNAME, USER, PASSWORD, HOST
import requests
import json
import time
import concurrent.futures
import pymysql
import datetime
from datapython.sql import *
import traceback

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
        if sort_order == "citations_lower":
            url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&start=0&sort=+citedby-count&count=' + str(num)
        elif sort_order == "citations_upper":
            url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&start=0&sort=-citedby-count&count=' + str(num)
        resp = self.reqs.getJson(url)

        resp = resp['search-results']['entry']
        if 'error' in resp[0] and resp[0]['error'] == 'Result set was empty':
            return []
        # print(resp)
        paps = [pap['eid'] for pap in resp]
        return paps

    #returns basic info about a paper with the given eid
    def getPaperInfo(self, eid, reference=False):
        url = 'https://api.elsevier.com/content/abstract/eid/' + str(eid) + '?&field=authors,coverDate,eid,title,publicationName'
        if reference:
            url = url = 'https://api.elsevier.com/content/abstract/eid/' + str(eid)
        resp = self.reqs.getJson(url)
        # print(self.prettifyJsonif(resp))
        try:
            if 'service-error' in resp:
                resp = self.reqs.getJson(url)
                if 'service-error' in resp:
                    print("SERVICE ERROR Citing")
                    raise
            resp = resp['abstracts-retrieval-response']
        except:
            print(resp)
            print(url)
            raise

        if reference:
            # print(self.prettifyJson(resp))
            ref_data = resp['item']['bibrecord']['tail']['bibliography']
            return ref_data
        else:
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
            req_url += '&startref='+ str(start)
        
        ref_arr = []
        i = 0

        # For some stupid reason, Scopus API changed their reference paper title field to only give the publisher name
        # So now we have to get paper names from a separate api response
        alternate_ref_info = self.getPaperInfo(eid, reference=True)
        alt_ref_list = alternate_ref_info['reference']
        
        notMatchAmt = 0
        refIDstatement = False
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
            for idx, raw in enumerate(resp_body):

                ref_dict = {}
                current_reference_id = raw['@id']
                ref_dict['authors'] = None
                if raw['author-list'] and raw['author-list']['author']:
                    auth_list = raw['author-list']['author']
                    auids = self.processAuthorList(auth_list)
                    ref_dict['authors'] = auids

                #ref_dict['srceid'] = eid
                ref_dict['eid'] = raw['scopus-eid']

                alt_ref_idx = idx + start - 1
                altrefid = current_reference_id
                # Sometimes alt list is missing id field.
                # In that case we will assume ordering is correct at risk of getting the wrong title
                if '@id' in alt_ref_list[alt_ref_idx]:
                    altrefid = alt_ref_list[alt_ref_idx]['@id']
                if altrefid != current_reference_id:
                    notMatchAmt += 1
                    if notMatchAmt > 15 and not refIDstatement:
                        print('Double check this paper. Alt ref ID does not match ref id more than 15 times in paper %s, altref: %s, refid: %s' % (eid, altrefid, current_reference_id))
                        refIDstatement = True
                alt_ref_info_current = alt_ref_list[alt_ref_idx]['ref-info']
                if 'ref-title' in alt_ref_info_current and 'ref-titletext' in alt_ref_info_current['ref-title']:
                    title_txt = alt_ref_list[alt_ref_idx]['ref-info']['ref-title']['ref-titletext']
                    if isinstance(title_txt, list):
                        title_txt = str(title_txt[0])
                    ref_dict['publicationName'] = title_txt
                # if 'sourcetitle' in raw:
                #     ref_dict['publisherName'] = raw['sourcetitle']
                current_refs.append(ref_dict)

            ref_arr += current_refs
            start += 40
            req_url = url + '&startref='+ str(start)
            if custom_count:
                break
            i += 1
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
    def __init__(self, author_id, citing_sort, paper_num, citing_num):
        self.paper_num = paper_num
        self.citing_num = citing_num
        self.citing_sort = citing_sort
        self.utility = Utility()
        self.scops = ScopusApiLib()
        self.author_id = author_id
        self.sqlTool = SqlCommand(author_id, citing_sort, paper_num, citing_num)
        self.conn = pymysql.connect(HOST, USER, PASSWORD, DBNAME, charset='utf8')

    def rangeExistsOrAdd(self):
        rangeTable = 'range_table_' + self.citing_sort
        cur = self.conn.cursor()
        cur.execute("select last_run_date, max_paper_num as pnum, max_citing_num as cnum, last_run_successful from %s where author_id='%s'" % (rangeTable, self.author_id))
        row = cur.fetchone()
        today = datetime.datetime.now()
        if row:
            last_date = row[0]
            pnum = row[1]
            cnum = row[2]
            last_run_successful = row[3]
            date_diff = today - last_date

            def rangeExists(last_run, pnum, cnum, days):
                return (last_run_successful == 1 and pnum and cnum and int(self.paper_num) <= pnum
                    and int(self.citing_num) <= cnum and date_diff.days < 365)

            if rangeExists(last_run_successful, pnum, cnum, date_diff.days):
                return True

        toAdd = "('" + str(self.author_id) + "', '" + today.strftime('%Y-%m-%d %H:%M:%S') + "', " + \
            str(self.paper_num) + ", " + str(self.citing_num) + ", 0)"
        query = "insert into %s (author_id, last_run_date, max_paper_num, max_citing_num, \
            last_run_successful) values %s on duplicate key update author_id=values(author_id), \
            last_run_date=values(last_run_date), max_paper_num=values(max_paper_num), \
            max_citing_num=values(max_citing_num), last_run_successful=values(last_run_successful)" % (rangeTable, toAdd)
        cur.execute(query)
        self.conn.commit()
        cur.close()
        return False

    def rangeUpdateFailure(self, err_msg):
        rangeTable = 'range_table_' + self.citing_sort
        cur = self.conn.cursor()
        query = "update %s set last_run_successful=0, \
            last_error_msg='%s' where author_id='%s'" % (rangeTable, err_msg, self.author_id)
        cur.execute(query)
        self.conn.commit()

    def rangeUpdateSuccess(self):
        rangeTable = 'range_table_' + self.citing_sort
        cur = self.conn.cursor()
        query = "update %s set last_run_successful=1 where author_id='%s'" % (rangeTable, self.author_id)
        cur.execute(query)
        self.conn.commit()


    def pushToS1(self, srcPaperDict, targPaperDict, srcAuthor, targAuthor, record_dict):

        s1_table = self.sqlTool.get_s1_name()

        srcPaperDict = self.utility.addPrefixToKeys(srcPaperDict, 'src_paper_')
        targPaperDict = self.utility.addPrefixToKeys(targPaperDict, 'targ_paper_')
        srcAuthor = self.utility.addPrefixToKeys(srcAuthor, 'src_author_')
        targAuthor = self.utility.addPrefixToKeys(targAuthor, 'targ_author_')

        aggDict = self.utility.merge_dicts(srcPaperDict, targPaperDict, srcAuthor, targAuthor, record_dict)
        self.utility.removeNone(aggDict)
        self.utility.changeKeyString(aggDict, '-', '_')
        self.utility.changeKeyString(aggDict, '@', '')
        self.utility.changeKeyString(aggDict, ':', '_')
        self.utility.changeValueString(aggDict, '\\', '')
        self.utility.changeValueString(aggDict, '"', '\\"')

        # print(self.toString(aggDict))
        self.pushDict(s1_table, aggDict)

    def processOvercites(self):
        overcite_command = self.sqlTool.create_overcites()
        check_overcites_cmd = self.sqlTool.check_overcites()
        update_overcites_cmd = self.sqlTool.update_overcites()
        cur = self.conn.cursor()
        try:
            cur.execute(check_overcites_cmd)
            row = cur.fetchone()
            if row[0] == 0:
                cur.execute(overcite_command)
                print('create overcites')
            else:
                cur.execute(update_overcites_cmd)
                print('update overcites')
        except:
            print(overcite_command)
            print(check_overcites_cmd)
            print(update_overcites_cmd)
            raise
        self.conn.commit()
        cur.close()
        return self.sqlTool.getTableNames()

    def processS2(self):
        s2_command = self.sqlTool.create_s2()
        check_s2_cmd = self.sqlTool.check_s2()
        update_s2_cmd = self.sqlTool.update_s2()
        cur = self.conn.cursor()
        try:
            cur.execute(check_s2_cmd)
            row = cur.fetchone()
            if row[0] == 0:
                cur.execute(s2_command)
                print('create s2')
            else:
                cur.execute(update_s2_cmd)
                print('update s2')
        except:
            print(s2_command)
            print(check_s2_cmd)
            print(update_s2_cmd)
            raise
        self.conn.commit()
        cur.close()

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
        s1_command = self.sqlTool.create_s1()
        check_s1_cmd = self.sqlTool.check_s1()
        cur = self.conn.cursor()
        try:
            cur.execute(check_s1_cmd)
            row = cur.fetchone()
            if row[0] == 0:
                cur.execute(s1_command)
                print('create s1')
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
        try:
            vals = ['"' + v + '"' for v in vals if v is not None]
        except:
            print (vals)
            raise
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

def storeRequestInfo(auth_id, auth_name, pap_num, cite_num, requester_name, requester_email, req_ip, request_raw):
    conn = pymysql.connect(HOST, USER, PASSWORD, DBNAME, charset='utf8')
    cur = conn.cursor()

    today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    value_tuple = "('%s', '%s', '%s', %d, %d, '%s', '%s', '%s', \"%s\")" % (today, auth_id, auth_name, pap_num, 
        cite_num, requester_name, requester_email, req_ip, request_raw)
    query = 'insert into request_info_logs (req_date, author_id, author_name, paper_num, \
        cite_num, requester_name, requester_email, requester_ip, request_raw) values %s' % value_tuple

    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

# this should be the only method that the client interacts with
def storeAuthorMain(auth_id, start_index=0, pap_num=20, cite_num=20, citing_sort="citations_lower", refCount=-1, workers=10):
    try:    
        author_profile = sApi.getAuthorMetrics(auth_id)
        author_identifier = author_profile['dc:identifier'] + '_' + author_profile['given-name'] + '_' + author_profile['surname']
        dbi = DbInterface(author_identifier, citing_sort, pap_num, cite_num)
        dbi.createTables()

        already = dbi.rangeExistsOrAdd()

        if (already):
            print("Range exists, skipping s1/s2")
        else:
            print("Range doesn't exist or there was previous failure. Beginning.")
            # Puts the main author record
            print('Beginning processing of S1 table for : ' + str(auth_id))
            
            # Puts the authors papers
            print('Getting author papers')
            papers = sApi.getAuthorPapers(auth_id, start=start_index, num=pap_num)


            executor = concurrent.futures.ProcessPoolExecutor(workers)
            paper_counter = 1
            processes = []
            for paper_arr in grouper(1, papers):
                processes.append(executor.submit(processPaperMain, author_identifier, paper_arr, paper_counter, pap_num, cite_num, citing_sort, refCount))
                paper_counter += len(paper_arr)

            # processes = [executor.submit(processPaperMain, author_identifier, paper_arr, pap_num, cite_num, citing_sort, refCount)
            #     for paper_arr in grouper(1, papers)]
            for p in processes:
                p.result()

            print('Beginning processing of s2 table.')
            dbi.processS2()

        print('Beginning processing of overcite table.')
        table_names = dbi.processOvercites()
        print('Done. Updating success code..')
        dbi.rangeUpdateSuccess()
        return table_names
    except Exception:
        traceback.print_exc()
        err_msg = traceback.format_exc()
        dbi.rangeUpdateFailure(err_msg)
        return None


def grouper(lengths, arr):
    arrarr = []
    begin = 0
    arrlen = len(arr)
    while begin < arrlen:
        sub = arr[begin:begin+lengths]
        begin += lengths
        arrarr.append(sub)
    return arrarr

def processPaperMain(author_id, papers, paper_counter, pap_num, cite_num, citing_sort, refCount):
    for eid in papers:
        print('Beginning processing for paper: ' + eid + ' of author: ' + str(author_id))
        #main_title = self.storePapersOnly(eid)
        # references = sApi.getPaperReferences(eid, refCount=refCount)
        # if references is None:
        #     print('No Data on References')
        #     references = []
        citedbys = sApi.getCitingPapers(eid, num=cite_num, sort_order=citing_sort)
        thisPaperDict = sApi.getPaperInfo(eid) #do this here to avoid duplicate api calls
        if thisPaperDict is None:
            print("NONE MAIN PAPER")
            continue

        #Puts the citing papers of the authors papers, and those respective authors
        print('Handling citing papers...')

        ccount = 1
        for citeIdx, citing in enumerate(citedbys):
            print('Paper %d. Citing Paper %d. EIDs: %s, %s' % (paper_counter, citeIdx, eid, citing))
            citePaperDict = sApi.getPaperInfo(citing)
            if citePaperDict is None:
                print("NONE CITING PAPER")
                continue
            storeCiting(dict(citePaperDict), dict(thisPaperDict), pap_num, cite_num,
                paper_counter, citeIdx + 1, author_id, citing_sort)
            storePaperReferences(citing, dict(citePaperDict), pap_num, cite_num,
                paper_counter, citeIdx + 1, author_id, citing_sort, refCount=refCount)
            ccount += 1
        paper_counter += 1
        print('Done citing papers.')
        # # Puts the cited papers of the authors papers, and those respective authors
        # print('Handling references...')
        # #Repeated code from storePaperReferences for clarity
        # for ref in references:

        #     refid = ref['eid']
        #     self.storeToStage1(eid, refid)
        #     self.storePaperReferences(refid, refCount=refCount)
        # print('Done references')

def storePaperReferences(eid, srcPaperDict, pap_num, cite_num, papIdx, citeIdx, author_id, citing_sort, refCount=-1, ):
    dbi = DbInterface(author_id, citing_sort, pap_num, cite_num)
    references = sApi.getPaperReferences(eid, refCount=refCount)
    if references is None:
        return
    srcAuthors = [{'indexed_name': None}]
    if 'authors' in srcPaperDict and srcPaperDict['authors'] is not None:
        srcAuthors = srcPaperDict.pop('authors')

    #This record dict is used to keep track the paper num and citing paper num of record
    # This is useful for creating a huge master S1/S2 table, then creating overcite table
    #   from a subset, such as top 10 papers, and top 20 citing papers
    record_dict = {'paper_index': str(papIdx), 'citing_index': str(citeIdx)}

    for targPaperDict in references:
        targAuthors = [{'indexed_name': None}]
        if 'authors' in targPaperDict and targPaperDict['authors'] is not None:
            targAuthors = targPaperDict.pop('authors')

        for srcAuth in srcAuthors:
            for targAuth in targAuthors:
                dbi.pushToS1(srcPaperDict, targPaperDict, srcAuth, targAuth, record_dict)

def storeCiting(srcPaperDict, targPaperDict, pap_num, cite_num, papIdx, citeIdx, author_id, citing_sort):
    dbi = DbInterface(author_id, citing_sort, pap_num, cite_num)
    srcAuthors = [{'indexed_name': None}]
    targAuthors = [{'indexed_name': None}]
    if 'authors' in srcPaperDict:
        srcAuthors = srcPaperDict.pop('authors')
    if 'authors' in targPaperDict:
        targAuthors = targPaperDict.pop('authors')

    record_dict = {'paper_index': str(papIdx), 'citing_index': str(citeIdx)}

    for srcAuth in srcAuthors:
        for targAuth in targAuthors:
            dbi.pushToS1(srcPaperDict, targPaperDict, srcAuth, targAuth, record_dict)


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
