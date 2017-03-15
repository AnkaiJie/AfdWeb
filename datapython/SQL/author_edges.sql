create table author_union as select
    select * from 
    (select 
    src_author_citation_count as citation_count,
    src_author_cited_by_count as cited_by_count,
    src_author_id as id,
    src_author_document_count as document_count,
    src_author_eid as eid,
    src_author_given_name as given_name,
    src_author_indexed_name as indexed_name,
    src_author_initials as initials,
    src_author_publication_range_start as publication_range_start,
    src_author_publication_range_end as publication_range_end,
    src_author_surname as surname,
    src_paper_coverDate as coverDate,
    src_paper_eid as eid,
    src_paper_publicationName as publicationName,
    src_paper_title as title
    union
    select
    targ_author_citation_count as citation_count,
    targ_author_cited_by_count as cited_by_count,
    targ_author_id as id,
    targ_author_document_count as document_count,
    targ_author_eid as eid,
    targ_author_given_name as given_name,
    targ_author_indexed_name as indexed_name,
    targ_author_initials as initials,
    targ_author_publication_range_start as publication_range_start,
    targ_author_publication_range_end as publication_range_end,
    targ_author_surname as surname,
    targ_paper_coverDate as coverDate,
    targ_paper_eid as eid,
    targ_paper_publicationName as publicationName,
    targ_paper_title as title) as authors_union

-- create table author_name_frequencies,
--  (select id, eid, given_name,
--      indexed_name, initials, surname count(*) as name_count
--  from author_union) as step1
--  left join 
--  (select author_id, author_eid, max(name_count)
--      (select id, eid, given_name, 
--          indexed_name, initials, surname, count(*) as name_count
--      from author_union) as step1


--      )

drop table if exists author_edges;
create table author_edges as select
    src_author_id as src_author_id,
    targ_author_id as targ_author_id,
    concat_ws('_', src_author_id, targ_author_id),
    count(*) as total_cites_to_target,
    min(src_paper_coverDate) as oldest_cite_to_target,
    max(src_paper_coverDate) as newest_cite_to_target,
    src_author_eid,
    max(src_author_given_name),
    max(src_author_indexed_name),
    max(src_author_initials),
    max(src_author_surname),
    max(src_author_citation_count) as src_author_citation_count,
    max(src_author_citation_count) as src_author_cited_by_count,
    max(src_author_document_count) as src_author_paper_count,
    min(src_author_publication_range_start) as src_author_start_date,
    max(src_author_publication_range_end) as src_author_end_date,
    min(targ_paper_coverDate) as oldest_cited_by_target,
    max(targ_paper_coverDate) as newest_cited_by_target,
    targ_author_eid,
    max(targ_author_given_name),
    max(targ_author_indexed_name),
    max(targ_author_initials),
    max(targ_author_surname),
    max(targ_author_citation_count) as targ_author_citation_count,
    max(targ_author_cited_by_count) as targ_author_cited_by_count,
    max(targ_author_document_count) as targ_author_paper_count,
    min(targ_author_publication_range_start) as targ_author_start_date,
    max(targ_author_publication_range_end) as targ_author_end_date
    from citations_s2
    group by src_author_id, src_author_eid, targ_author_id, targ_author_eid;


