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



# # Paolo_Piaggi
# table_names = storeAuthorMain(35748826000, start_index=0, pap_num=20, workers=10, targetNum=100, test=False)
# print(table_names)
# tool = Analysis(35748826000, table_names)


# # Srinivasan Keshav
# table_names = storeAuthorMain(10141917500, start_index=0, pap_num=20, workers=10, targetNum=100, test=False)
# print(table_names)
# tool = Analysis(10141917500, table_names)

# # Prabhakar Raghavan
# table_names = storeAuthorMain(7006894026, start_index=0, pap_num=20, workers=10, targetNum=100, test=False)
# print(table_names)
# tool = Analysis(7006894026, table_names)

# # Luca Beninini
# table_names = storeAuthorMain(35556997000, start_index=0, pap_num=20, workers=10, targetNum=150, test=False)
# print(table_names)
# tool = Analysis(35556997000, table_names)

# # Stephen Hawking
# table_names = storeAuthorMain(6701475619, start_index=0, pap_num=20, workers=10, targetNum=150, test=False)
# print(table_names)
# tool = Analysis(6701475619, table_names)

# # Alouini, Mohamed Slim
# table_names = storeAuthorMain(35570711700, start_index=0, pap_num=20, workers=10, targetNum=150, test=False)
# print(table_names)
# tool = Analysis(35570711700, table_names)


# Athanasios Vasilakos
table_names = storeAuthorMain(22954842600, start_index=0, pap_num=20, workers=10, targetNum=200, test=False)
print(table_names)
tool = Analysis(22954842600, table_names)

# Pinhan Ho
table_names = storeAuthorMain(7402211578, start_index=0, pap_num=20, workers=10, targetNum=200, test=False)
print(table_names)
tool = Analysis(7402211578, table_names)

# Herbert Simon
table_names = storeAuthorMain(7402135283, start_index=0, pap_num=20, workers=10, targetNum=200, test=False)
print(table_names)
tool = Analysis(7402135283, table_names)

# Helena Karsten
table_names = storeAuthorMain(6603889928, start_index=0, pap_num=20, workers=10, targetNum=200, test=False)
print(table_names)
tool = Analysis(6603889928, table_names)