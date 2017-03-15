from credentials import API_KEY, DBNAME, USER, PASSWORD, HOST
import operator
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from apilib import ScopusApiLib

plt.style.use('ggplot')

class Analysis:

    def __init__(self):
        self.api = ScopusApiLib()

    def getAuthorName(id):
        return

    def getOvercites(self, authid):
        conn = pymysql.connect(HOST, USER, PASSWORD, DBNAME, charset='utf8')
        curs = conn.cursor()
        cmd = "select * from author_overcites where targ_author_id=" + "'" + authid + "'" + " order by overcites desc"

        curs.execute(cmd)
        rows = curs.fetchall()
        df = pd.DataFrame([i for i in rows])
        df.rename(columns={0: 'Target Author', 1: 'Citing Paper', 2:'Author Count', 3:'Overcites'}, inplace=True)
        return df


    def plotOvercitesBar(self, authid, authname, save=False):
        df = self.getOvercites(authid)
        fig, ax = plt.subplots(figsize=(10,10))
        fig.subplots_adjust(bottom=0.25)

        papers = df['Citing Paper'][:25]
        x_pos = np.arange(len(papers))
        overs = df['Overcites'][:25]
        ax.bar(x_pos, overs, align='center')
        ax.set_xlim([-1, x_pos.size])
        ax.set_xticks(x_pos)
        ax.set_ylim([0, np.amax(overs) + 1])
        ax.set_xticklabels(papers, rotation="90")
        ax.set_ylabel('Overcites')
        ax.set_xlabel('Citing Paper ID')
        ax.set_title('Top 25 overciting papers for author ' + authname + ' from ' + str(len(df)) + ' citing papers')
        if save:
            fig.savefig('graphs/OverBar_' + '_'.join(authname.split()) + '.png')
        else:
            plt.show()

        print('Done ' + authname)

    def plotOvercitesHist(self, authid, authname, save=False, threshold =10, savename=""):

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
        ax.set_ylabel('Number of Papers with Overcite Amount')
        ax.set_xlabel('Number of Overcites')
        ax.set_title('Overcite frequency for papers with >=' + str(threshold) + ' overcites \n from ' + str(len(df)) + ' citing papers for ' + authname)
        if save and savename="":
            fig.savefig('graphs/OverHist_' + '_'.join(authname.split()) + '.png')
        elif save:
            fig.savefig(savename + ".png")
        else:
            plt.show()

        print('Done ' + authname)


# plotOvercitesBar('22954842600')
# plotOvercitesHist('22954842600')
# s = ScopusApiLib()
# print(s.getAuthorPapers('22954842600'))
# print (s.getAuthorMetrics('22954842600'))

# a = Analysis()
# a.plotOvercitesBar('22954842600', 'Athanasios Vasilakos', True)
# a.plotOvercitesBar('7004058432', 'Tarek Abdelzaher', True)
# a.plotOvercitesBar('7006637893', 'David Haussler', True)
# a.plotOvercitesBar('20734105100', 'Ian Horrocks', True)
# a.plotOvercitesBar('10141917500', 'Srinivasan Keshav', True)
# a.plotOvercitesBar('55666697100', 'Khaled Letaief', True)
# a.plotOvercitesBar('7006811415', 'Michael Lyu', True)
# a.plotOvercitesBar('55251517100', 'Burkhard Ross', True)
# a.plotOvercitesBar('7004449411', 'Thomas Henzinger', True)
# a.plotOvercitesBar('7007153024', 'Wil Vanderaalst', True)
# a.plotOvercitesBar('35618760400', 'Ronald Yager', True)

# a.plotOvercitesHist('22954842600', 'Athanasios Vasilakos', True)
# a.plotOvercitesHist('7004058432', 'Tarek Abdelzaher', True)
# a.plotOvercitesHist('7006637893', 'David Haussler', True)
# a.plotOvercitesHist('20734105100', 'Ian Horrocks', True)
# a.plotOvercitesHist('10141917500', 'Srinivasan Keshav', True)
# a.plotOvercitesHist('55666697100', 'Khaled Letaief', True)
# a.plotOvercitesHist('7006811415', 'Michael Lyu', True)
# a.plotOvercitesHist('55251517100', 'Burkhard Ross', True)
# a.plotOvercitesHist('7004449411', 'Thomas Henzinger', True)
# a.plotOvercitesHist('7007153024', 'Wil Vanderaalst', True)
# a.plotOvercitesHist('35618760400', 'Ronald Yager', True)



# a.plotOvercitesHist('22954842600')
