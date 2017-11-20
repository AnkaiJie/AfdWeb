from datapython.credentials import DBNAME, USER, PASSWORD, HOST
from datapython.ScopusApiLib import ScopusApiLib
import concurrent.futures
import pymysql
import datetime
from datapython.sql import *
import traceback
from datapython.utility import Utility
import random

# all the SQL code to insert/update is here
class DbInterface:
    def __init__(self, author_id, paper_num):
        self.paper_num = paper_num
        self.utility = Utility()
        self.scops = ScopusApiLib()
        self.author_id = author_id
        self.sqlTool = SqlCommand(author_id, paper_num)
        self.conn = pymysql.connect(HOST, USER, PASSWORD, DBNAME, charset='utf8')

    def rangeExistsOrAdd(self):
        rangeTable = 'range_table'
        cur = self.conn.cursor()
        cur.execute("select last_run_date, max_paper_num as pnum, last_run_successful \
            from %s where author_id='%s'" % (rangeTable, self.author_id))
        row = cur.fetchone()
        today = datetime.datetime.now()
        if row:
            last_date = row[0]
            pnum = row[1]
            last_run_successful = row[2]
            date_diff = today - last_date

            def rangeExists(last_run, pnum, days):
                return (last_run_successful == 1 and pnum and int(self.paper_num) <= pnum
                    and date_diff.days < 365)

            if rangeExists(last_run_successful, pnum, date_diff.days):
                return True

        toAdd = "('" + str(self.author_id) + "', '" + today.strftime('%Y-%m-%d %H:%M:%S') + "', " + \
            str(self.paper_num) + ", 0)"
        query = "insert into %s (author_id, last_run_date, max_paper_num, \
            last_run_successful) values %s on duplicate key update author_id=values(author_id), \
            last_run_date=values(last_run_date), max_paper_num=values(max_paper_num), \
            last_run_successful=values(last_run_successful)" % (rangeTable, toAdd)
        cur.execute(query)
        self.conn.commit()
        cur.close()
        return False

    def rangeUpdateFailure(self, err_msg):
        rangeTable = 'range_table'
        print(err_msg)
        cur = self.conn.cursor()
        query = "update %s set last_run_successful=0, \
            last_error_msg='%s' where author_id='%s'" % (rangeTable, err_msg, self.author_id)
        cur.execute(query)
        self.conn.commit()

    def rangeUpdateSuccess(self):
        rangeTable = 'range_table'
        cur = self.conn.cursor()
        query = "update %s set last_run_successful=1 where author_id='%s'" % (rangeTable, self.author_id)
        cur.execute(query)
        self.conn.commit()


    def pushToS1(self, srcPaperDict, targPaperDict, srcAuthor, targAuthor):

        s1_table = self.sqlTool.get_s1_name()

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


def storeRequestInfo(auth_id, auth_name, pap_num, requester_name, requester_email, req_ip, request_raw):
    conn = pymysql.connect(HOST, USER, PASSWORD, DBNAME, charset='utf8')
    cur = conn.cursor()

    today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    value_tuple = "('%s', '%s', '%s', %d, '%s', '%s', '%s', \"%s\")" % (today, auth_id, auth_name, pap_num, 
        requester_name, requester_email, req_ip, request_raw)
    query = 'insert into request_info_logs (req_date, author_id, author_name, paper_num, \
        requester_name, requester_email, requester_ip, request_raw) values %s' % value_tuple

    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

# this should be the only method that the client interacts with
def storeAuthorMain(auth_id, start_index=0, pap_num=20, workers=10, targetNum=20, test=False):
    sApi = ScopusApiLib()
    try:    
        author_profile = sApi.getAuthorMetrics(auth_id)
        author_identifier = author_profile['dc:identifier'] + '_' + author_profile['given-name'] + '_' + author_profile['surname']

        dbi = DbInterface(author_identifier, pap_num)
        dbi.createTables()

        already = dbi.rangeExistsOrAdd()

        if (already and not test):
            print("Range exists, skipping s1/s2")
        else:
            print("Range doesn't exist or there was previous failure. Beginning.")
            # Puts the main author record
            print('Beginning processing of S1 table for : ' + str(auth_id))
            
            # Puts the authors papers
            print('Getting author papers')
            papers = sApi.getAuthorPapers(auth_id, start=start_index, num=pap_num)

            def generatePickProbability(ps, goal):
                totalCbc = 0
                for paper in ps:
                    # print(paper)
                    papInfo = sApi.getPaperInfo(paper)
                    cbc = papInfo['citedby-count']
                    totalCbc += int(cbc)
                
                p = 1
                if goal <= totalCbc:
                    p = goal/totalCbc

                print("Total cited by among %d papers: %d, with probability of pick %f. Target num %d" \
                    % (len(ps), totalCbc, p, targetNum))
                return p

            pickProb = generatePickProbability(papers, targetNum)

            executor = concurrent.futures.ProcessPoolExecutor(workers)
            paper_counter = 1
            processes = []
            for paper_arr in grouper(1, papers):
                processes.append(executor.submit(processPaperMain, author_identifier, paper_arr, paper_counter, pap_num, pickProb))
                paper_counter += len(paper_arr)

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

def processPaperMain(author_id, papers, paper_counter, pap_num, pickProbability):
    sApi = ScopusApiLib()
    for eid in papers:
        print('Beginning processing for paper: ' + eid + ' of author: ' + str(author_id))

        citedbys = sApi.getAllCitingPapers(eid, sort_order="citations_upper")

        thisPaperDict = sApi.getPaperInfo(eid) #do this here to avoid duplicate api calls

        if thisPaperDict is None:
            print("NONE MAIN PAPER")
            continue

        print('Handling citing papers. Total citing papers to sample from: %d' % len(citedbys))

        ccount = 1
        for citeIdx, citing in enumerate(citedbys):

            # apply our probabilistic pick rate
            rando = random.random()
            if rando > pickProbability:
                continue

            print('Paper %d. Citing Paper %d. EIDs: %s, %s' % (paper_counter, citeIdx, eid, citing))
            citePaperDict = sApi.getPaperInfo(citing)
            if citePaperDict is None:
                print("NONE CITING PAPER")
                continue

            storeCiting(dict(citePaperDict), dict(thisPaperDict), pap_num, author_id)
            storePaperReferences(citing, dict(citePaperDict), pap_num, author_id)
            ccount += 1
        paper_counter += 1
        print('Done citing papers.')


def storePaperReferences(eid, srcPaperDict, pap_num, author_id, refCount=-1):
    dbi = DbInterface(author_id, pap_num)
    sApi = ScopusApiLib()
    references = sApi.getPaperReferences(eid, refCount=refCount)
    if references is None:
        return
    srcAuthors = [{'indexed_name': None}]
    if 'authors' in srcPaperDict and srcPaperDict['authors'] is not None:
        srcAuthors = srcPaperDict.pop('authors')

    scopus_author_id = author_id.split('_')[0]
    for targPaperDict in references:
        targAuthors = [{'indexed_name': None}]
        if 'authors' in targPaperDict and targPaperDict['authors'] is not None:
            targAuthors = targPaperDict.pop('authors')

        for targAuth in targAuthors:
            if 'dc:identifier' in targAuth and targAuth['dc:identifier'][10:] == str(scopus_author_id):
                #Scopus api doesn't give enough info, so we manually make another api call to get title, coverdate, etc
                # we only do this when we see our target author to avoid excessive API calls
                fullInfoTargPaperDict = sApi.getPaperInfo(targPaperDict['eid'])
                if 'authors' in fullInfoTargPaperDict:
                    fullInfoTargPaperDict.pop('authors')

                for srcAuth in srcAuthors:
                    dbi.pushToS1(srcPaperDict, fullInfoTargPaperDict, srcAuth, targAuth)

def storeCiting(srcPaperDict, targPaperDict, pap_num, author_id):
    dbi = DbInterface(author_id, pap_num)
    sApi = ScopusApiLib()
    srcAuthors = [{'indexed_name': None}]
    targAuthors = [{'indexed_name': None}]
    if 'authors' in srcPaperDict:
        srcAuthors = srcPaperDict.pop('authors')
    if 'authors' in targPaperDict:
        targAuthors = targPaperDict.pop('authors')

    scopus_author_id = author_id.split('_')[0]
    for targAuth in targAuthors:
        if 'dc:identifier' in targAuth and targAuth['dc:identifier'][10:] == str(scopus_author_id):
            for srcAuth in srcAuthors:
                dbi.pushToS1(srcPaperDict, targPaperDict, srcAuth, targAuth)

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
    sApi = ScopusApiLib()
    author = sApi.getAuthorMetrics(auth_id)
    return author
