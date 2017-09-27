CREATE TABLE `range_table_citations_upper` (
  `author_id` varchar(40) NOT NULL,
  `last_run_date` datetime NOT NULL,
  `max_paper_num` int(11) NOT NULL,
  `max_citing_num` int(11) NOT NULL,
  `last_run_successful` int(10) unsigned NOT NULL DEFAULT '0',
  `last_error_msg` text,
  PRIMARY KEY (`author_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
