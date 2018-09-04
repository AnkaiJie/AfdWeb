from datapython.ScopusApiLib import ScopusApiLib
from datapython.apilib import DbInterface, storeAuthorMain
from datapython.analysis import Analysis


def getTableNames(aid, name, sample=None):
    aid = str(aid)
    prefix = aid +'_' + '_'.join(name.split())
    if sample is not None:
        prefix += "_sample" + str(sample)
    tab1_name = prefix + "_citations_s1"
    overname = prefix + "_overcites"
    tab2_name = prefix + "_citations_s2"
    return {'s1': tab1_name, 's2': tab2_name, 'overcite': overname}


# table_names = storeAuthorMain(14036725000, start_index=0, pap_num=160, workers=10, targetNum=1500, test=False, resample=False)
# print(table_names)
# tool = Analysis(14036725000, table_names)


# table_names = storeAuthorMain(7004138948, start_index=0, pap_num=120, workers=10, targetNum=1500, test=False, resample=False)
# print(table_names)
# tool = Analysis(7004138948, table_names)



# table_names = storeAuthorMain(6701629145, start_index=0, pap_num=25, workers=10, targetNum=1500, test=False, resample=False)
# print(table_names)
# tool = Analysis(6701629145, table_names)


for i in range(1,6, 1):

    # Keshav
    table_names = storeAuthorMain(10141917500, start_index=0, pap_num=20, workers=20, targetNum=200, test=False, resample=False, sampleNum=i)
    table_names = getTableNames(10141917500, "Srinivasan Keshav", sample=i)
    print(table_names)
    tool = Analysis(10141917500, table_names, custom_name='Author D Sample ' + str(i))


    # Andrea Schaerf
    table_names = storeAuthorMain(6701629145, start_index=0, pap_num=20, workers=20, targetNum=200, test=False, resample=False, sampleNum=i)
    table_names = getTableNames(6701629145, "Andrea Schaerf", sample=i)
    print(table_names)
    tool = Analysis(6701629145, table_names, custom_name='Author C Sample ' + str(i))

    # Athanasios Vasilakos
    table_names = getTableNames(22954842600, "Athanasios Vasilakos", sample=i)
    print(table_names)
    tool = Analysis(22954842600, table_names, custom_name='Author E Sample ' + str(i))

    # Herbert Simon
    table_names = getTableNames(7402135283, 'Herbert Simon', sample=i)
    print(table_names)
    tool = Analysis(7402135283, table_names, custom_name='Author A Sample ' + str(i))

    # Anil Jain
    table_names = getTableNames(36071504600, 'Anil Jain', sample=i)
    print(table_names)
    tool = Analysis(36071504600, table_names, custom_name='Author B Sample ' + str(i))


    # Jiafu Wan
    table_names = getTableNames(24333732700, 'Jiafu Wan', sample=i)
    print(table_names)
    tool = Analysis(24333732700, table_names, custom_name='Author F Sample ' + str(i))



# table_names = storeAuthorMain(10141917500, start_index=0, pap_num=200, workers=25, targetNum=None, test=False, resample=False, sampleNum=None)
# print(table_names)
# tool = Analysis(10141917500, table_names, custom_name='Author D')


# table_names = storeAuthorMain(6701629145, start_index=0, pap_num=100, workers=1, targetNum=None, test=False, resample=False, sampleNum=None)
# print(table_names)
# tool = Analysis(6701629145, table_names, custom_name='Author C')