import traceback
# from datapython.apilib import ScopusApiLib, DbInterface

# # # For running tests
# # dbi = DbInterface('ankaijie', 'citations_lower', 1,1)
# # print(dbi.rangeExistsOrAdd())




# sal = ScopusApiLib()
# # k = sal.getAuthorMetrics(22954842600)
# # print(sal.prettifyJson(k))
# # # k= sal.getAuthorPapers("AUTHOR_ID:22954842600", 0, 2)
# # # k = sal.getCitingPapers('2-s2.0-79956094375', num=5, sort_order="date")
# # # print(sal.prettifyJson(k))
# # # k = sal.getCitingPapers('2-s2.0-79956094375', num=5, sort_order="citations_decrease")
# # # print(sal.prettifyJson(k))
# # # k = sal.getCitingPapers('2-s2.0-79956094375', num=5, sort_order="citations_increase")
# # # print(sal.prettifyJson(k))

# # k = sal.getPaperInfo('2-s2.0-85017420948')
# # print (k)

# ref = sal.getPaperReferences('2-s2.0-26444447080')

# print(sal.prettifyJson(ref))

try:
	print ('no error')
except Exception as e:
	traceback.print_exc()




