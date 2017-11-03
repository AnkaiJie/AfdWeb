from datapython.credentials import API_KEY, DBNAME, USER, PASSWORD, HOST
import operator
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from datapython.apilib import ScopusApiLib
import csv

plt.style.use('ggplot')

class Analysis:

    def __init__(self, authid, table_names):
        self.api = ScopusApiLib()
        self.authname = self.getAuthorName(authid)
        self.authid = authid
        self.table_names = table_names

    def getAuthorName(self, id):
        authname = 'Unknown'
        details = self.api.getAuthorMetrics(id)
        if 'given-name' in details and 'surname' in details:
            authname = details['given-name'] + " " + details['surname']
        elif 'indexed-name' in details:
            authname = details['indexed-name']
        return authname

    def getOvercites(self):
        conn = pymysql.connect(HOST, USER, PASSWORD, DBNAME, charset='utf8')
        curs = conn.cursor()
        cmd = "select * from " + self.table_names['overcite'] + " where \
        targ_author_id=" + "'" + self.authid + "'" + " order by src_paper_citedby_count"

        curs.execute(cmd)
        rows = curs.fetchall()
        df = pd.DataFrame([i for i in rows])
        df.rename(columns={0: 'Target Author', 1: 'Citing Paper EID', \
            2:'Citing Paper Title', 3:'Citing Paper Cited By Count', 4:'Citations to Target Author'}, inplace=True)
        return df


    def plotOvercitesScatter(self, save=True):
        df = self.getOvercites()
        fig, ax = plt.subplots(figsize=(10,10))
        fig.subplots_adjust(bottom=0.25)
        authname = self.authname

        maxCitedby = max(df['Citing Paper Cited By Count'])
        maxOvers = max(df['Citations to Target Author'])
        x_pos = np.arange(maxCitedby)

        citedbys = df['Citing Paper Cited By Count']
        citations = df['Citations to Target Author']

        ax.scatter(citedbys, citations, c='r')
        ax.set_xlim([-1, maxCitedby])
        ax.set_xticks(x_pos)
        ax.set_ylim([0, maxOvers + 1])
        ax.set_ylabel('Number of Citations to ' + authname)
        ax.set_xlabel('Number of Times Citing Paper is Cited')

        ax.set_title('Influence Scatter Plot: Degree of Influence from' + authname + ' \
            vs Degree of Popularity of Paper out of' + str(len(df)) + ' Citing Papers')

        savename = 'datapython/graphs/Scatter_' + '_'.join(authname.split()) + '_' + self.citing_sort + '.png'
        if save:
            fig.savefig(savename)
        else:
            plt.show()

        return savename


    def plotOvercitesBar(self, authid, save=True):
        df = self.getOvercites(authid)
        fig, ax = plt.subplots(figsize=(10,10))
        fig.subplots_adjust(bottom=0.25)
        authname = self.authname 
        papers = df['Citing Paper'][:25]
        x_pos = np.arange(len(papers))
        overs = df['Overcites'][:25]
        ax.bar(x_pos, overs, align='center')
        ax.set_xlim([-1, x_pos.size])
        ax.set_xticks(x_pos)
        ax.set_ylim([0, np.amax(overs) + 1])
        ax.set_xticklabels(papers, rotation="90")
        ax.set_ylabel('Number of Citations to ' + authname)
        ax.set_xlabel('Citing Paper ID')
        num = 25
        if (len(papers) < 25):
            num = len(papers)
        ax.set_title('Influence Bar Graph: Top ' + str(num) + ' influenced papers for author ' + authname + '\n from ' + str(len(df)) + ' citing papers')
        savename = 'datapython/graphs/Bar_' + '_'.join(authname.split()) + '_' + self.citing_sort + '.png'
        if save:
            fig.savefig(savename)
        else:
            plt.show()

        return savename

    def plotOvercitesHist(self, authid, save=True, threshold =10):
        authname = self.authname 
        df = self.getOvercites(authid)
        fig,ax = plt.subplots(figsize=(10,10))
        fig.subplots_adjust(bottom=0.25)

        freq = {}
        for idx, row in df.iterrows():
            overs = row['Overcites']
            if overs > threshold-1:
                f = freq.get(overs, 0)
                freq[overs] = f + 1

        sorted_freq = sorted(freq.items(), key=operator.itemgetter(0))
        x_pos = np.arange(len(sorted_freq))
        overcite_nums = [x[0] for x in sorted_freq]
        overcite_num_freqs = [x[1] for x in sorted_freq]

        ax.bar(x_pos, overcite_num_freqs, align='center')
        ax.set_xlim([-1, x_pos.size])
        ax.set_xticks(x_pos)
        ax.set_xticklabels(overcite_nums, rotation="90")
        if len(overcite_num_freqs) > 0:
            ax.set_ylim([0, np.amax(overcite_num_freqs) + 1])
        ax.set_ylabel('Number of Papers')
        ax.set_xlabel('Citation Count to ' + authname)
        ax.set_title('Influence Histogram: Number of Papers With >=' + str(threshold) + ' Influence Threshold\n from ' + str(len(df)) + ' citing papers for ' + authname)
        savename = 'datapython/graphs/Hist_' + '_'.join(authname.split()) + '_' + self.citing_sort + '.png'
        if save:
            fig.savefig(savename)
        elif save:
            fig.savefig(savename + ".png")
        else:
            plt.show()

        return savename

    def overcitesCsv(self, authid):
        authname = self.authname
        df = self.getOvercites(authid)
        name = 'datapython/graphs/Influence_' + '_'.join(authname.split()) + '_' + self.citing_sort +  '.csv'
        writer = csv.writer(open(name, 'w'), lineterminator='\n')

        writer.writerow(['Target Author Id: '  + authid])
        writer.writerow(['Target Author Name: ' + authname])
        writer.writerow([])

        writer.writerow(['Citing Paper', 'Citing Paper Title', 'Citing Paper Authors', 'Citation Count'])

        for idx, row in df.iterrows():
            src_paper_eid = row['Citing Paper']
            paper_info = self.api.getPaperInfo(src_paper_eid)
            paper_title = "Unknown"
            if 'title' in paper_info:
                paper_title = paper_info['title']

            paper_author_arr = []
            if 'authors' in paper_info:
                for auth in paper_info['authors']:
                    if 'indexed-name' in auth:
                        paper_author_arr.append(auth['indexed-name'].strip('.'))

            paper_authors = ','.join(paper_author_arr)

            cite, overcites = row['Citing Paper'],row['Overcites']
            writer.writerow([cite, paper_title, paper_authors, overcites])

        return name

