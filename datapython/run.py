import apilib

# sal = ScopusApiLib()
# k = sal.getPaperReferences('2-s2.0-79952854696', refCount=1)
# print(len(k))
# print(sal.prettifyJson(k))



apilib.storeAuthorMain(22954842600, start_index=0, pap_num=5, cite_num=1)



# from concurrent.futures import ProcessPoolExecutor
# from time import sleep
 
# def return_after_5_secs(message):
#     sleep(5)
#     return message
 
# pool = ProcessPoolExecutor(3)
 
# future = pool.submit(return_after_5_secs, 'hi')
# future2 = pool.submit(return_after_5_secs, 'hi')
# future3 = pool.submit(return_after_5_secs, 'hi')
# future4 = pool.submit(return_after_5_secs, 'hi')
# print("Result: " + future.result())
# print("Result: " + future2.result())
# print("Result: " + future3.result())
# print("Result: " + future4.result())