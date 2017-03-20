def create_s1(author_id):
    tab_name = author_id + "_citations_s1"
    s = """
        create table if not exists """ + tab_name + """ (
        src_author_dc_identifier varchar(50),
        src_author_given_name varchar(200),
        src_author_indexed_name varchar(200),
        src_author_initials varchar(20),
        src_author_surname varchar(200),
        src_paper_coverDate varchar(30),
        src_paper_eid varchar(50),
        src_paper_publicationName varchar(1000),
        src_paper_title varchar(1000),
        targ_author_dc_identifier varchar(50),
        targ_author_given_name varchar(200),
        targ_author_indexed_name varchar(200),
        targ_author_initials varchar(20),
        targ_author_surname varchar(200),
        targ_paper_coverDate varchar(30),
        targ_paper_eid varchar(50),
        targ_paper_publicationName varchar(1000),
        targ_paper_title varchar(1000)
    );
    """
    return s

def check_s1(author_id):
    tab_name = author_id + "_citations_s1"
    return """select exists (select * from information_schema.tables where 
    table_name=\"""" + tab_name + """\" and table_schema=\"CiteFraud\") """

def create_s1_key(author_id):
    tab_name = author_id + "_citations_s1"
    return """ALTER TABLE """ + tab_name + """  
    ADD PRIMARY KEY (`src_author_dc_identifier`, `src_paper_eid`, `targ_author_dc_identifier`,`targ_paper_eid`); 
    """

def create_s2(author_id):
    tab_name = author_id + "_citations_s2"
    tab1_name = author_id + "_citations_s1"
    s = """drop table if exists """ + tab_name + """;
        create table """ + tab_name + """ as select
        substring(src_author_dc_identifier, 11) as src_author_id,
        src_author_given_name,
        src_author_indexed_name,
        src_author_initials,
        src_author_surname,
        DATE(src_paper_coverDate) as src_paper_coverDate,
        src_paper_eid,
        src_paper_publicationName,
        src_paper_title,
        substring(targ_author_dc_identifier, 11) as targ_author_id,
        targ_author_given_name,
        targ_author_indexed_name,
        targ_author_initials,
        targ_author_surname,
        DATE(targ_paper_coverDate) as targ_paper_coverDate,
        targ_paper_eid,
        targ_paper_publicationName,
        targ_paper_title
    from """ + tab1_name + """ 
    where src_author_dc_identifier != "" and
    targ_author_dc_identifier != "";
    ALTER TABLE """+ tab_name + """   
    ADD PRIMARY KEY (`src_author_id`, `src_paper_eid`, `targ_author_id`,`targ_paper_eid`);"""

    return s

def create_overcites(author_id):
    tab_name = author_id + "_overcites"
    tab2_name = author_id + "_citations_s2"

    s=  """drop table if exists """ + tab_name + """; 
        create table """ + tab_name + """ as
        select inter.targ_author_id, inter.src_paper_eid, inter.author_num, count(inter.targ_paper_eid) as overcites from 
        (select targ_author_id, targ_paper_eid, src_paper_eid, 
            count(src_author_id) as author_num from """ + tab2_name + """ 
            group by targ_author_id, targ_paper_eid, src_paper_eid) as inter
        group by targ_author_id, src_paper_eid, author_num
        """
    return s