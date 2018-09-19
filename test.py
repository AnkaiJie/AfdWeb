from datapython.ScopusApiLib import ScopusApiLib
from datapython.apilib import DbInterface, storeAuthorMain
from datapython.analysis import Analysis

# # # For running tests
# # dbi = DbInterface('ankaijie', 'citations_lower', 1,1)
# # print(dbi.rangeExistsOrAdd())

sal = ScopusApiLib()
#k = sal.getAuthorMetrics(22954842600)
#print(sal.prettifyJson(k))
# k= sal.getAuthorPapers("AUTHOR_ID:22954842600", 0, 2)
# k = sal.getCitingPapers('2-s2.0-79956094375', num=5, sort_order="date")
# print(sal.prettifyJson(k))
# k = sal.getCitingPapers('2-s2.0-79956094375', num=5, sort_order="citations_decrease")
# print(sal.prettifyJson(k))

# k = sal.getAllCitingPapers('2-s2.0-33751030085', sort_order="citations_upper")
# print(sal.prettifyJson(k))
# print(len(k))

k = sal.getPaperInfo('2-s2.0-85017420948', reference=True)
print (k)
print(k['@refcount'])


# ref = sal.getPaperReferences('2-s2.0-84877367951')

# print(sal.prettifyJson(k))



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

# Stephen Hawking
# table_names = storeAuthorMain(6701475619, start_index=0, pap_num=20, workers=10, targetNum=1, test=False, resample=True)
# print(table_names)
# tool = Analysis(6701475619, table_names)

# # Alouini, Mohamed Slim
# table_names = storeAuthorMain(35570711700, start_index=0, pap_num=20, workers=10, targetNum=150, test=False)
# print(table_names)
# tool = Analysis(35570711700, table_names)

# def getTableNames(aid, name, sample=None):
#     aid = str(aid)
#     prefix = aid +'_' + '_'.join(name.split())
#     if sample and sample is not 1:
#         prefix += "_sample" + str(sample)
#     tab1_name = prefix + "_citations_s1"
#     overname = prefix + "_overcites"
#     tab2_name = prefix + "_citations_s2"
#     return {'s1': tab1_name, 's2': tab2_name, 'overcite': overname}

# Athanasios Vasilakos
# table_names = storeAuthorMain(22954842600, start_index=0, pap_num=20, workers=10, targetNum=200, test=False, resample=True)
# print(table_names)
# tool = Analysis(22954842600, table_names)

# # Pascal Fua
# table_names = storeAuthorMain(55159125200, start_index=0, pap_num=20, workers=10, targetNum=200, test=False, resample=False, sampleNum=5)
# print(table_names)
# tool = Analysis(55159125200, table_names)

# # Anil Jain
# table_names = storeAuthorMain(36071504600, start_index=0, pap_num=20, workers=10, targetNum=200, test=False, resample=False, sampleNum=5)
# print(table_names)
# tool = Analysis(36071504600, table_names)

# # Herbert Simon
# table_names = storeAuthorMain(7402135283, start_index=0, pap_num=20, workers=10, targetNum=200, test=False, resample=True)
# print(table_names)
# tool = Analysis(6603889928, table_names)

# # Donald Knuth
# table_names = storeAuthorMain(7004138948, start_index=0, pap_num=20, workers=10, targetNum=200, test=False, resample=True)
# print(table_names)
# tool = Analysis(6603889928, table_names)

# # John Carrol
# table_names = storeAuthorMain(7402034833, start_index=0, pap_num=20, workers=10, targetNum=200, test=False, resample=True)
# print(table_names)
# tool = Analysis(7402034833, table_names)

# # Helena Karsten
# table_names = storeAuthorMain(6603889928, start_index=0, pap_num=20, workers=10, targetNum=200, test=False, resample=True)
# print(table_names)
# tool = Analysis(6603889928, table_names)


# # CUSTOM NAMES
# Stephen Hawking
# table_names = getTableNames(6701475619, "Stephen Hawking")
# print(table_names)
# tool = Analysis(6701475619, table_names, custom_name='Stephen Hawking')


# for i in range(1,6, 1):
#     # Athanasios Vasilakos
#     table_names = getTableNames(22954842600, "Athanasios Vasilakos", sample=i)
#     print(table_names)
#     tool = Analysis(22954842600, table_names, custom_name='Author E Sample ' + str(i))

#     # Herbert Simon
#     table_names = getTableNames(7402135283, 'Herbert Simon', sample=i)
#     print(table_names)
#     tool = Analysis(7402135283, table_names, custom_name='Author A Sample ' + str(i))

#     # # Helena Karsten
#     # table_names = getTableNames(6603889928, 'Helena Karsten', sample=i)
#     # print(table_names)
#     # tool = Analysis(6603889928, table_names, custom_name='Author C Sample ' + str(i))

#     # Anil Jain
#     table_names = getTableNames(36071504600, 'Anil Jain', sample=i)
#     print(table_names)
#     tool = Analysis(36071504600, table_names, custom_name='Author B Sample ' + str(i))

#     # # Pascal Fua
#     # table_names = getTableNames(55159125200, 'Pascal Fua', sample=i)
#     # print(table_names)
#     # tool = Analysis(55159125200, table_names, custom_name='Author E Sample ' + str(i))

#     # # Donald Knuth
#     # table_names = getTableNames(7004138948, 'Donald Knuth', sample=i)
#     # print(table_names)
#     # tool = Analysis(7004138948, table_names, custom_name='Author D Sample ' + str(i))

#     # Jiafu Wan
#     table_names = getTableNames(24333732700, 'Jiafu Wan', sample=i)
#     print(table_names)
#     tool = Analysis(24333732700, table_names, custom_name='Author F Sample ' + str(i))



# # 6701629145_Andrea_Schaerf_overcites
# table_names = getTableNames(6701629145, 'Andrea Schaerf', sample=1)
# print(table_names)
# tool = Analysis(6701629145, table_names, custom_name='Author C', show_barcounts=False)

# #10141917500_Srinivasan_Keshav_overcites
# table_names = getTableNames(10141917500, 'Srinivasan Keshav', sample=1)
# print(table_names)
# tool = Analysis(10141917500, table_names, custom_name='Author D', show_barcounts=False)



# # Varde Keshav
# table_names = storeAuthorMain(7004024654, start_index=0, pap_num=20, workers=10, targetNum=200, test=False, resample=False, sampleNum=None)
# print(table_names)
# tool = Analysis(7004024654, table_names)
