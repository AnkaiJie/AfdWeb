import requests
import json
from datapython.credentials import API_KEY
from datapython.utility import Utility
import time

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
    def getCitingPapers(self, eid, num=200, sort_order="date"):
        url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&start=0&count=' + str(num)
        if sort_order == "citations_lower":
            url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&start=0&sort=+citedby-count&count=' + str(num)
        elif sort_order == "citations_upper":
            url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&start=0&sort=-citedby-count&count=' + str(num)
        resp = self.reqs.getJson(url)

        resp = resp['search-results']['entry']
        if 'error' in resp[0] and resp[0]['error'] == 'Result set was empty':
            return []

        paps = []
        for pap in resp:
            if 'eid' in pap:
                paps.append(pap['eid'])
        return paps

    def getAllCitingPapers(self, eid, sort_order):
        MAXCOUNT = 200
        url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&count=' + str(MAXCOUNT)
        if sort_order == "citations_lower":
            url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&sort=+citedby-count&count=' + str(MAXCOUNT)
        elif sort_order == "citations_upper":
            url ='https://api.elsevier.com/content/search/scopus?query=refeid(' + str(eid) + ')&field=eid&sort=-citedby-count&count=' + str(MAXCOUNT)

        allCiting = []
        start = 0
        while(True):
            tempurl = url + '&start=' + str(start)
            resp = self.reqs.getJson(tempurl)
            #previous result gave 200 and there is no more
            try:
                if 'entry' not in resp['search-results']:
                    break
            except KeyError:
                # Usually happens when paper has > 5000 citations
                # Scopus doesn't support more than 5000 searches ...
                # So we just break 
                if resp['service-error']['status']['statusCode'] == "INVALID_INPUT":
                    print (resp)
                    print (tempurl)
                    break
            resp = resp['search-results']['entry']
            #paper has no citations to it
            if 'error' in resp[0] and resp[0]['error'] == 'Result set was empty':
                break
                
            paps = []
            for pap in resp:
                if 'eid' in pap:
                    paps.append(pap['eid'])
            allCiting += paps
            start += MAXCOUNT

        return allCiting

    #returns basic info about a paper with the given eid
    def getPaperInfo(self, eid, reference=False):
        url = 'https://api.elsevier.com/content/abstract/eid/' + str(eid) + '?&field=authors,coverDate,eid,title,publicationName,citedby-count'
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

            # Only one reference returned: it doesn't get returned as a list, so we must put it in one
            if type(resp_body) is dict:
                resp_body = [resp_body]
            for idx, raw in enumerate(resp_body):
                ref_dict = {}
                ref_dict['authors'] = None
                if raw['author-list'] and raw['author-list']['author']:
                    auth_list = raw['author-list']['author']
                    auids = self.processAuthorList(auth_list)
                    ref_dict['authors'] = auids

                ref_dict['eid'] = raw['scopus-eid']

                
                if 'sourcetitle' in raw:
                    ref_dict['publicationName'] = raw['sourcetitle']

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