    
drop table if exists citations_s2;
create table citations_s2 as select
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
from citations_s1
where src_author_dc_identifier != "" and
targ_author_dc_identifier != "";

ALTER TABLE citations_s2 
ADD PRIMARY KEY (`src_author_id`, `src_paper_eid`, `targ_author_id`,`targ_paper_eid`);

