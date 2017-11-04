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
        # self.authname = 'kanknknka nknkna '
        self.authid = str(authid)
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
        ax.set_xlim([-1, maxCitedby + 5])
        ax.set_xticks(np.arange(0, maxCitedby, 50))
        ax.set_ylim([0, maxOvers + 1])
        ax.set_ylabel('Number of Citations to ' + authname)
        ax.set_xlabel('Number of Times Citing Paper is Cited')

        ax.set_title('Influence Scatter Plot: Degree of Influence from' + authname + ' \
            vs Degree of Popularity of Paper out of' + str(len(df)) + ' Citing Papers')

        savename = 'datapython/graphs/Scatter_' + '_'.join(authname.split()) + '.png'
        if save:
            fig.savefig(savename)
        else:
            plt.show()

        return savename


    def overcitesCsv(self):
        df = self.getOvercites()
        name = 'datapython/graphs/Influence_' + '_'.join(self.authname.split()) + '.csv'
        writer = csv.writer(open(name, 'w'), lineterminator='\n')

        writer.writerow(['Target Author Id: '  + self.authid])
        writer.writerow(['Target Author Name: ' + self.authname])
        writer.writerow([])

        writer.writerow(['Citing Paper EID', 'Citing Paper Title', 'Citing Paper Cited By Count', 'Citation Count'])

        for idx, row in df.iterrows():
            # src_paper_eid = row['Citing Paper']
            # paper_info = self.api.getPaperInfo(src_paper_eid)
            # paper_title = "Unknown"
            # if 'title' in paper_info:
            #     paper_title = paper_info['title']

            # paper_author_arr = []
            # if 'authors' in paper_info:
            #     for auth in paper_info['authors']:
            #         if 'indexed-name' in auth:
            #             paper_author_arr.append(auth['indexed-name'].strip('.'))

            # paper_authors = ','.join(paper_author_arr)

            cite, title, citedby, overcites = row['Citing Paper EID'], row['Citing Paper Title'], \
                row['Citing Paper Cited By Count'], row['Citations to Target Author']

            writer.writerow([cite, title, citedby, overcites])

        return name

