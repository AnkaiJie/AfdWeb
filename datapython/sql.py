class SqlCommand:

    def __init__(self, author_id, paper_num, sampleNumber=None):
        self.paper_num = str(paper_num)
        self.suffix = self.paper_num
        self.original_prefix = author_id
        self.prefix = author_id
        self.currentSampleCount=1

        if sampleNumber:
            self.currentSampleCount = sampleNumber
            self.prefix = self.original_prefix + "_sample" + str(self.currentSampleCount)

        self.s1Name = self.prefix + "_citations_s1"
        self.s2Name = self.prefix + "_citations_s2"
        self.overciteName = self.prefix + "_overcites"

    def getSampleNumber(self):
        if self.currentSampleCount == 1:
            return None
        else:
            return self.currentSampleCount

    def incrementPrefix(self):
        self.currentSampleCount += 1
        self.prefix = self.original_prefix + "_sample" + str(self.currentSampleCount)
        self.s1Name = self.prefix + "_citations_s1"
        self.s2Name = self.prefix + "_citations_s2"
        self.overciteName = self.prefix + "_overcites"

    def create_s1(self):
        s = """
            create table if not exists """ + self.s1Name + """ (
            src_author_dc_identifier varchar(50),
            src_author_given_name varchar(200),
            src_author_indexed_name varchar(200),
            src_author_initials varchar(20),
            src_author_surname varchar(200),
            src_paper_coverDate varchar(30),
            src_paper_eid varchar(50),
            src_paper_publicationName varchar(1000),
            src_paper_title varchar(1000),
            src_paper_citedby_count varchar(50),
            targ_author_dc_identifier varchar(50),
            targ_author_given_name varchar(200),
            targ_author_indexed_name varchar(200),
            targ_author_initials varchar(20),
            targ_author_surname varchar(200),
            targ_paper_coverDate varchar(30),
            targ_paper_eid varchar(50),
            targ_paper_publicationName varchar(1000),
            targ_paper_title varchar(1000),
            targ_paper_citedby_count varchar(50)
        ) charset=utf8mb4;
        """
        s += self.create_s1_key();

        return s

    def check_s1(self):
        return """select exists (select * from information_schema.tables where 
        table_name=\"""" + self.s1Name + """\" and table_schema=\"CiteFraud\") """

    def create_s1_key(self):
        return """ALTER TABLE """ + self.s1Name + """  
        ADD PRIMARY KEY (`src_author_dc_identifier`, `src_paper_eid`,
        `targ_author_dc_identifier`,`targ_paper_eid`); 
        """

    def check_s2(self):
        return """select exists (select * from information_schema.tables where 
        table_name=\"""" + self.s2Name + """\" and table_schema=\"CiteFraud\") """

    def create_s2(self):
        s = """create table """ + self.s2Name + """ as select
            substring(src_author_dc_identifier, 11) as src_author_id,
            src_author_given_name,
            src_author_indexed_name,
            src_author_initials,
            src_author_surname,
            DATE(src_paper_coverDate) as src_paper_coverDate,
            src_paper_eid,
            src_paper_publicationName,
            src_paper_title,
            cast(src_paper_citedby_count as UNSIGNED) as src_paper_citedby_count,
            substring(targ_author_dc_identifier, 11) as targ_author_id,
            targ_author_given_name,
            targ_author_indexed_name,
            targ_author_initials,
            targ_author_surname,
            DATE(targ_paper_coverDate) as targ_paper_coverDate,
            targ_paper_eid,
            targ_paper_publicationName,
            targ_paper_title,
            cast(targ_paper_citedby_count as UNSIGNED) as targ_paper_citedby_count
        from """ + self.s1Name + """ 
        where src_author_dc_identifier != "" and
        targ_author_dc_identifier != "";
        ALTER TABLE """+ self.s2Name + """   
        ADD PRIMARY KEY (`src_author_id`, `src_paper_eid`, `targ_author_id`,
        `targ_paper_eid`);"""
        return s

    def update_s2(self):
        s = """replace into """ + self.s2Name + """
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
                `src_paper_citedby_count`,
                `targ_author_id`,
                `targ_author_given_name`,
                `targ_author_indexed_name`,
                `targ_author_initials`,
                `targ_author_surname`,
                `targ_paper_coverDate`,
                `targ_paper_eid`,
                `targ_paper_publicationName`,
                `targ_paper_title`,
                `targ_paper_citedby_count`
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
            cast(src_paper_citedby_count as UNSIGNED) as src_paper_citedby_count,
            substring(targ_author_dc_identifier, 11) as targ_author_id,
            targ_author_given_name,
            targ_author_indexed_name,
            targ_author_initials,
            targ_author_surname,
            DATE(targ_paper_coverDate) as targ_paper_coverDate,
            targ_paper_eid,
            targ_paper_publicationName,
            targ_paper_title,
            cast(targ_paper_citedby_count as UNSIGNED) as targ_paper_citedby_count
        from """ + self.s1Name + """ 
        where src_author_dc_identifier != "" and
        targ_author_dc_identifier != "";"""
        return s

    def get_s1_name(self):
        return self.s1Name

    def check_overcites(self):
        return """select exists (select * from information_schema.tables where 
        table_name=\"""" + self.overciteName + """\" and table_schema=\"CiteFraud\") """

    def update_overcites(self):
        s=  """replace into """ + self.overciteName + """ 
            (
                `targ_author_id`,
                `src_paper_eid`,
                `src_paper_title`,
                `src_paper_authors`,
                `src_paper_citedby_count`,
                `overcites`
            )
            select targ_author_id, src_paper_eid, src_paper_title, \
                GROUP_CONCAT(distinct CONCAT(src_author_given_name, ' ', src_author_surname) SEPARATOR ', ') \
                as src_paper_authors, src_paper_citedby_count, count(distinct targ_paper_eid) as overcites \
                from """ + self.s2Name + """ group by targ_author_id, \
                src_paper_eid, src_paper_title, src_paper_citedby_count;
            """
        return s


    def create_overcites(self):
        s = """create table """ + self.overciteName + """ as
            select targ_author_id, src_paper_eid, src_paper_title, \
                GROUP_CONCAT(distinct CONCAT(src_author_given_name, ' ', src_author_surname) SEPARATOR ', ') \
                as src_paper_authors, src_paper_citedby_count, count(distinct targ_paper_eid) as overcites \
                from """ + self.s2Name + """ group by targ_author_id, \
                src_paper_eid, src_paper_title, src_paper_citedby_count;
            """
        s += """ALTER TABLE """ + self.overciteName + """  
        ADD PRIMARY KEY (`targ_author_id`, `src_paper_eid`); 
        """
        return s

    def getTableNames(self):
        return {'s1': self.s1Name, 's2': self.s2Name, 'overcite': self.overciteName}
