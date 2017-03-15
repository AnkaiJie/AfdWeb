import apilib


sal = apilib.ScopusApiLib()
#k = sal.getAuthorMetrics(22954842600)
# k= sal.getAuthorPapers("AUTHOR_ID:22954842600", 0, 2)
# k = sal.getCitingPapers('2-s2.0-79956094375', num=5)
# k = sal.getPaperReferences('2-s2.0-79956094375', refCount=5)
k = sal.getPaperInfo('2-s2.0-79956094375')
print(sal.prettifyJson(k))
# k = sal.getPaperInfo('2-s2.0-84992381851')
# print(sal.prettifyJson(k))

# atd = ApiToDB()
# atd.storeAuthorMain(22954842600, 0,1,5)

