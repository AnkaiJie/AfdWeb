    
create table citations_s1 (
    src_author_citation_count varchar(15),
    src_author_cited_by_count varchar(15),
    src_author_dc_identifier varchar(50),
    src_author_document_count varchar(15),
    src_author_eid varchar(50),
    src_author_given_name varchar(200),
    src_author_indexed_name varchar(200),
    src_author_initials varchar(20),
    src_author_publication_range_end varchar(10),
    src_author_publication_range_start varchar(10),
    src_author_surname varchar(200),
    src_paper_coverDate varchar(30),
    src_paper_eid varchar(50),
    src_paper_publicationName varchar(1000),
    src_paper_title varchar(1000),
    targ_author_citation_count varchar(15),
    targ_author_cited_by_count varchar(15),
    targ_author_dc_identifier varchar(50),
    targ_author_document_count varchar(15),
    targ_author_eid varchar(50),
    targ_author_given_name varchar(200),
    targ_author_indexed_name varchar(200),
    targ_author_initials varchar(20),
    targ_author_publication_range_end varchar(10),
    targ_author_publication_range_start varchar(10),
    targ_author_surname varchar(200),
    targ_paper_coverDate varchar(30),
    targ_paper_eid varchar(50),
    targ_paper_publicationName varchar(1000),
    targ_paper_title varchar(1000)
);
ALTER TABLE citations_s1 
ADD PRIMARY KEY (`src_author_dc_identifier`, `src_paper_eid`, `targ_author_dc_identifier`,`targ_paper_eid`); 


create table citations_s1 (
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
ALTER TABLE citations_s1 
ADD PRIMARY KEY (`src_author_dc_identifier`, `src_paper_eid`, `targ_author_dc_identifier`,`targ_paper_eid`); 

