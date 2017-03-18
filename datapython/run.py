from apilib import *

# sal = ScopusApiLib()
# k = sal.getPaperReferences('2-s2.0-79952854696', refCount=1)
# print(len(k))
# print(sal.prettifyJson(k))



atd = ApiToDB()
atd.storeAuthorMain(22954842600, start_index=0, pap_num=1, cite_num=1)