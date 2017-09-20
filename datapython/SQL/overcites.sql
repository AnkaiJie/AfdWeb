
/* OLD CODE */
create table over_initial as
select targ_author_id, targ_paper_eid,
        src_paper_eid from citations_s2
        where targ_author_id !=''
        group by targ_author_id, targ_paper_eid,
        src_paper_eid

create table over_overs as
select src_author_id, src_paper_eid, targ_author_id,
        count(*) as overcites from citations_s2
        where targ_author_id!=''
        group by src_author_id, src_paper_eid, targ_author_id

drop table author_overcites;
    create table author_overcites as 
    select initial.targ_author_id, initial.targ_paper_eid, initial.src_paper_eid, 
    count(src_author_id) as author_num, overs.overcites
    from 
    over_initial as initial
    left join over_overs as overs 
    on initial.targ_author_id = overs.targ_author_id and initial.src_paper_eid = overs.src_paper_eid
    group by initial.targ_author_id, initial.src_paper_eid, initial.targ_paper_eid, overs.overcites


/* New code - remove targ_paper_eid because it just causes repeats in table columns */
drop table author_overcites;
create table author_overcites as
select inter.targ_author_id, inter.src_paper_eid, inter.author_num, count(inter.targ_paper_eid) as overcites from 
(select targ_author_id, targ_paper_eid, src_paper_eid, 
    count(src_author_id) as author_num from citations_s2
    group by targ_author_id, targ_paper_eid, src_paper_eid) as inter
group by targ_author_id, src_paper_eid, author_num


select * from author_overcites where targ_author_id='' order by overcites desc;
