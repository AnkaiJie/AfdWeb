from datapython.credentials import API_KEY, DBNAME, USER, PASSWORD, HOST
import pymysql
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import math
from datapython.apilib import ScopusApiLib
import csv
import os

plt.style.use('ggplot')

class Analysis:

    def __init__(self, authid, table_names, custom_name=None, version=2, show_barcounts=True):
        self.api = ScopusApiLib()

        if custom_name is None:
            self.authname = self.getAuthorName(authid)
        else:
            self.authname = custom_name

        self.authid = str(authid)
        self.table_names = table_names

        self.indices = self.getIndices(version=version)
        self.influenceIndex = str(self.indices[0])
        self.fraudIndex = str(self.indices[1])

        stackedName = self.plotOverCitesStacked(show_barcounts=show_barcounts)
        # scatterName = self.plotOvercitesScatter()
        csvName = self.overcitesCsv()


        # self.visualNames = [stackedName, scatterName, csvName]

    def createDirectory(self, path):
        if not os.path.exists(path):
            os.mkdir(path)

    def getChartNames(self):
        return self.visualNames

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
            2:'Citing Paper Title', 3:'Citing Paper Authors', 4:'Citing Paper Cited By Count', \
            5:'Citations to Target Author'}, inplace=True)
        df = df.fillna(0)
        curs.close()
        conn.close()

        return df

    def getIndices(self, version=2):
        conn = pymysql.connect(HOST, USER, PASSWORD, DBNAME, charset='utf8')
        curs = conn.cursor()
        iCmd = "select round(avg(overcites*src_paper_citedby_count), 1) from " + self.table_names['overcite']
        if version == 2:
            iCmd = """
                select round(avg(overcites.overcites*overcites.src_paper_citedby_count/cite_counts.citation_count), 2)
                    from `%s` as overcites , paper_citation_counts as cite_counts
                    where overcites.src_paper_eid = cite_counts.paper_eid
            """ % self.table_names['overcite']

        if version == 3:
            """
            select round(avg(overcites.overcites*overcites.src_paper_citedby_count), 1)
                from `%s` as overcites , paper_citation_counts as cite_counts
                where overcites.src_paper_eid = cite_counts.paper_eid and cite_counts.citation_count < 100 
            """ % self.table_names['overcite']
            
        curs.execute(iCmd)
        rows = curs.fetchone()
        influenceIndex = rows[0]

        fCmd = "select count(*) from " + self.table_names['overcite'] + " where overcites >= 5 and src_paper_citedby_count <=5;"

        curs.execute(fCmd)
        rows = curs.fetchone()
        fraudIndex = rows[0]

        curs.close()
        conn.close()

        return (influenceIndex, fraudIndex)

    def plotOvercitesScatter(self, save=True):
        df = self.getOvercites()
        fig, ax = plt.subplots(figsize=(10,10))
        fig.subplots_adjust(bottom=0.25)
        authname = self.authname


        maxCitedby = max(df['Citing Paper Cited By Count'])
        maxOvers = max(df['Citations to Target Author'])

        def roundUp(x):
            return int(math.ceil(x / 10.0)) * 10

        xtick = roundUp(maxCitedby // 10)

        citedbys = df['Citing Paper Cited By Count']
        citations = df['Citations to Target Author']

        ax.set_xlim([-1, maxCitedby + 5])
        ax.set_xticks(np.arange(0, maxCitedby, xtick))
        ax.set_ylim([0, maxOvers + 1])
        ax.set_ylabel('Number of Citations to ' + authname)
        ax.set_xlabel('Citing Paper Cited-by Count')

        ax.set_title('Influence Scatter Plot: Degree of Influence from ' + authname + \
         '\n vs Degree of Popularity of Paper out of ' + str(len(df)) + ' Citing Papers, \n \
          I=' + self.influenceIndex + ', F=' + self.fraudIndex )

        # heatmap, xedges, yedges = np.histogram2d(citedbys, citations, bins=50)

        ax.scatter(citedbys, citations, c='r')
        
        savepath = 'datapython/graphs/' + self.authid
        self.createDirectory(savepath)
        savename = savepath + '/' + 'Scatter_' + '_'.join(authname.split()) + '.png'
        if save:
            fig.savefig(savename)
        else:
            plt.show()

        return savename

    def plotOverCitesStacked(self, save=True, show_barcounts=True):
        df = self.getOvercites()
        fig, ax = plt.subplots(figsize=(10,10))
        fig.subplots_adjust(bottom=0.25)
        authname = self.authname
        citedBys = df['Citing Paper Cited By Count']
        overs = df['Citations to Target Author']
        maxOvers = max(overs)
        numRows = len(range(maxOvers)) + 1

        LOW = 5
        MID = 20
        HIGH = 50
        VERYHIGH = 200

        barDict = {}
        def mapToIndex(cb):
            if cb <= LOW:
                return 0
            elif cb <= MID:
                return 1
            elif cb <= HIGH:
                return 2
            elif cb <= VERYHIGH:
                return 3
            else:
                return 4
        for idx, over in enumerate(overs):
            # print(over)
            cb = citedBys[idx]
            cbBin = mapToIndex(cb)
            if over not in barDict:
                # 0-5, 6-20, 21-50, >50
                barDict[over] = [0,0,0,0,0]

            barDict[over][cbBin] += 1

        rows = []
        widths = []
        labels = []
        # print(barDict)
        for key, val in barDict.items():
            for freq in val:
                rows.append(key)
                widths.append(freq)
                labels.append(freq)

        colors ='cgyrm'

        patch_handles = []

        fig = plt.figure(figsize=(10,8))
        ax = fig.add_subplot(111)

        left = np.zeros(numRows,)
        row_counts = np.zeros(numRows,)

        # print(left)
        # print(row_counts)

        for (r, w, l) in zip(rows, widths, labels):
            # print (r, w, l)
            if w == 0:
                left[r] += w
                row_counts[r] += 1
                continue

            
            patch_handles.append(ax.barh(r, w, align='center', left=left[r],
                color=colors[int(row_counts[r]) % len(colors)]))
            left[r] += w
            row_counts[r] += 1
            # we know there is only one patch but could enumerate if expanded
            patch = patch_handles[-1][0] 
            bl = patch.get_xy()
            x = 0.5*patch.get_width() + bl[0]
            y = 0.5*patch.get_height() + bl[1]
            if show_barcounts:
                ax.text(x, y, "%d" % (l), ha='center',va='center')

        ax.set_yticks(np.arange(0, max(numRows, 5), 1))
        ax.set_yticklabels(range(max(numRows,10)))

        ax.set_ylabel('Number of Citations (X) to ' + authname)
        ax.set_xlabel('Number of Papers with X citation to ' + authname)

        ax.set_title('Influence Bar Plot: Frequency of Citations to ' + authname +\
         '\n Color Grouped by Number of Citations to the Citing Paper\n out of ' + str(len(df)) + \
         ' Citing Papers, I=' + self.influenceIndex + ', F=' + self.fraudIndex)


        cyan_patch = mpatches.Patch(color='c', label='n <= 5')
        green_patch = mpatches.Patch(color='g', label='5 < n <= 20')
        yellow_patch = mpatches.Patch(color='y', label='20 < n <= 50')
        red_patch = mpatches.Patch(color='r', label='50 < n <= 200')
        mag_patch = mpatches.Patch(color='m', label='n > 200')
        legend = ax.legend(title="Cited-by Count \n of Citing Paper", shadow=True,
            handles=[cyan_patch, green_patch, yellow_patch, red_patch, mag_patch])
        legend.get_frame().set_facecolor('#ffffff')

        savepath = 'datapython/graphs/' + self.authid
        self.createDirectory(savepath)
        savename = savepath + '/' + 'StackedBar_' + '_'.join(authname.split()) + '.png'

        if save:
            fig.savefig(savename)
        else:
            plt.show()

        return savename


    def overcitesCsv(self):
        df = self.getOvercites()
        name = 'datapython/graphs/' + self.authid + '/' + 'Influence_' + '_'.join(self.authname.split()) + '.csv'
        writer = csv.writer(open(name, 'w+'), lineterminator='\n')

        writer.writerow(['Target Author Id: '  + self.authid])
        writer.writerow(['Target Author Name: ' + self.authname])
        writer.writerow([])

        writer.writerow(['Citing Paper EID', 'Citing Paper Title', 'Citing Paper Authors', \
            'Citing Paper Cited By Count', 'Influence Count (Citations to Target Author)'])

        df.sort_values('Citations to Target Author', ascending=False, inplace=True)

        for idx, row in df.iterrows():
            cite, title, authors, citedby, overcites = row['Citing Paper EID'], row['Citing Paper Title'], \
                row['Citing Paper Authors'], row['Citing Paper Cited By Count'], \
                row['Citations to Target Author']

            if authors == 0:
                authors = 'No Author Info'

            writer.writerow([cite, title, authors, citedby, overcites])

        return name

