CREATE TABLE `request_info_logs` (
  `req_date` datetime DEFAULT NULL,
  `author_id` varchar(40) DEFAULT NULL,
  `author_name` varchar(70) DEFAULT NULL,
  `paper_num` int(11) DEFAULT NULL,
  `cite_num` int(11) DEFAULT NULL,
  `requester_name` varchar(70) DEFAULT NULL,
  `requester_email` varchar(100) DEFAULT NULL,
  `requester_ip` varchar(40) DEFAULT NULL,
  `request_raw` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1
