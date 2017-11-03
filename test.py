from datapython.ScopusApiLib import ScopusApiLib
from datapython.apilib import DbInterface, storeAuthorMain
from datapython.analysis import Analysis

# # # For running tests
# # dbi = DbInterface('ankaijie', 'citations_lower', 1,1)
# # print(dbi.rangeExistsOrAdd())




sal = ScopusApiLib()
# # k = sal.getAuthorMetrics(22954842600)
# # print(sal.prettifyJson(k))
# # # k= sal.getAuthorPapers("AUTHOR_ID:22954842600", 0, 2)
# # # k = sal.getCitingPapers('2-s2.0-79956094375', num=5, sort_order="date")
# # # print(sal.prettifyJson(k))
# # # k = sal.getCitingPapers('2-s2.0-79956094375', num=5, sort_order="citations_decrease")
# # # print(sal.prettifyJson(k))

# k = sal.getAllCitingPapers('2-s2.0-33751030085', sort_order="citations_upper")
# print(sal.prettifyJson(k))
# print(len(k))

# k = sal.getPaperInfo('2-s2.0-85017420948')
# print (k)

# ref = sal.getPaperReferences('2-s2.0-26444447080')

# print(sal.prettifyJson(ref))


# Pauli Piaggi
# table_names = storeAuthorMain(35748826000, start_index=0, pap_num=5, workers=10, test=False)
# Vasilakos
# table_names = storeAuthorMain(22954842600, start_index=0, pap_num=5, workers=10, targetNum=20, test=True)
table_names = {'s2': '35748826000_Paolo_Piaggi_citations_s2', 'overcite': '35748826000_Paolo_Piaggi_overcites_5', 's1': '35748826000_Paolo_Piaggi_citations_s1'}
print(table_names)

tool = Analysis(35748826000, table_names)
tool.plotOvercitesScatter()
tool.overcitesCsv()

