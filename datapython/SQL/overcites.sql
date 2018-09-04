s = """create table """ + self.overciteName + """ as
    select targ_author_id, src_paper_eid, src_paper_title, \
        GROUP_CONCAT(distinct CONCAT(src_author_given_name, ' ', src_author_surname) SEPARATOR ', ') \
        as src_paper_authors, src_paper_citedby_count, count(distinct targ_paper_eid) as overcites \
        from """ + self.s2Name + """ where targ_author_id != src_author_id \
        group by targ_author_id, src_paper_eid, src_paper_title, src_paper_citedby_count;
    """

