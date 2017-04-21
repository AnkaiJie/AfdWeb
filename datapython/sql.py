class SqlCommand:

    def __init__(self, author_id, citing_sort, paper_num, citing_num):
        self.paper_num = str(paper_num)
        self.citing_num = str(citing_num)
        self.suffix = self.paper_num + "_" + self.citing_num
        self.prefix = author_id + "_" + citing_sort

    def create_s1(self):
        tab_name = self.prefix + "_citations_s1"
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
            targ_paper_title varchar(1000),
            paper_index int,
            citing_index int
        ) charset=utf8mb4;
        """
        s += self.create_s1_key();

        return s

    def check_s1(self):
        tab_name = self.prefix  + "_citations_s1"
        return """select exists (select * from information_schema.tables where 
        table_name=\"""" + tab_name + """\" and table_schema=\"CiteFraud\") """

    def create_s1_key(self):
        tab_name = self.prefix  + "_citations_s1"
        return """ALTER TABLE """ + tab_name + """  
        ADD PRIMARY KEY (`src_author_dc_identifier`, `src_paper_eid`,
        `targ_author_dc_identifier`,`targ_paper_eid`, `paper_index`, `citing_index`); 
        """

    def check_s2(self):
        tab_name = self.prefix  + "_citations_s2"
        return """select exists (select * from information_schema.tables where 
        table_name=\"""" + tab_name + """\" and table_schema=\"CiteFraud\") """

    def create_s2(self):
        tab_name = self.prefix  + "_citations_s2"
        tab1_name = self.prefix  + "_citations_s1"
        s = """create table """ + tab_name + """ as select
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
            targ_paper_title,
            paper_index,
            citing_index
        from """ + tab1_name + """ 
        where src_author_dc_identifier != "" and
        targ_author_dc_identifier != "";
        ALTER TABLE """+ tab_name + """   
        ADD PRIMARY KEY (`src_author_id`, `src_paper_eid`, `targ_author_id`,
        `targ_paper_eid`, `paper_index`, `citing_index`);"""
        return s

    def update_s2(self):
        tab_name = self.prefix  + "_citations_s2"
        tab1_name = self.prefix  + "_citations_s1"
        s = """replace into """ + tab_name + """
            (
                `src_author_id`,
                `src_author_given_name`,
                `src_author_indexed_name`,
                `src_author_initials`,
                `src_author_surname`,
                `src_paper_coverDate`,
                `src_paper_eid`,
                `src_paper_publicationName`,
                `src_paper_title`,
                `targ_author_id`,
                `targ_author_given_name`,
                `targ_author_indexed_name`,
                `targ_author_initials`,
                `targ_author_surname`,
                `targ_paper_coverDate`,
                `targ_paper_eid`,
                `targ_paper_publicationName`,
                `targ_paper_title`,
                `paper_index`,
                `citing_index`
            )
            select
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
            targ_paper_title,
            paper_index,
            citing_index
        from """ + tab1_name + """ 
        where src_author_dc_identifier != "" and
        targ_author_dc_identifier != "";"""
        return s

    def get_s1_name(self):
        return self.prefix  + "_citations_s1"

    def check_overcites(self):
        tab_name = self.prefix + "_overcites_" + self.suffix
        return """select exists (select * from information_schema.tables where 
        table_name=\"""" + tab_name + """\" and table_schema=\"CiteFraud\") """

    def update_overcites(self):
        tab_name = self.prefix + "_overcites_" + self.suffix
        tab2_name = self.prefix + "_citations_s2"
        s=  """replace into """ + tab_name + """ 
            (
                `targ_author_id`,
                `src_paper_eid`,
                `author_num`,
                `overcites`
            )
            select inter.targ_author_id, inter.src_paper_eid, count(distinct inter.src_author_id) as author_num,
                count(distinct inter.targ_paper_eid) as overcites from 
            (select targ_author_id, targ_paper_eid, src_paper_eid, 
                src_author_id, min(paper_index) as paper_index, 
                min(citing_index) as citing_index from """ + tab2_name + """ group by targ_author_id, 
                targ_paper_eid, src_paper_eid, src_author_id) as inter
            where inter.paper_index<=""" + self.paper_num + """ and inter.citing_index<=""" + self.citing_num + """ 
            group by targ_author_id, src_paper_eid;
            """
        return s


    def create_overcites(self):
        tab_name = self.prefix + "_overcites_" + self.suffix
        tab2_name = self.prefix + "_citations_s2"

        s = """create table """ + tab_name + """ as
            select inter.targ_author_id, inter.src_paper_eid, count(distinct inter.src_author_id) as author_num,
                count(distinct inter.targ_paper_eid) as overcites from 
            (select targ_author_id, targ_paper_eid, src_paper_eid, 
                src_author_id, min(paper_index) as paper_index, 
                min(citing_index) as citing_index from """ + tab2_name + """ group by targ_author_id, 
                targ_paper_eid, src_paper_eid, src_author_id) as inter
            where inter.paper_index<=""" + self.paper_num + """ and inter.citing_index<=""" + self.citing_num + """ 
            group by targ_author_id, src_paper_eid;
            """
        s += """ALTER TABLE """ + tab_name + """  
        ADD PRIMARY KEY (`targ_author_id`, `src_paper_eid`); 
        """
        return s

    def getTableNames(self):
        tab1_name = self.prefix + "_citations_s1"
        overname = self.prefix + "_overcites_" + self.suffix
        tab2_name = self.prefix + "_citations_s2"
        return {'s1': tab1_name, 's2': tab2_name, 'overcite': overname}
