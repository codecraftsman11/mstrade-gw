DROP TABLE IF EXISTS email_forwarding;
DROP TABLE IF EXISTS email_domains;

CREATE TABLE `email_domains` (
  `domainId` int unsigned NOT NULL AUTO_INCREMENT,
  `domainname` varchar(70) NOT NULL,
  `isActive` bool NOT NULL DEFAULT 1,
  `createdDateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`domainId`),
  UNIQUE KEY (`domainname`,`isActive`)
) ENGINE=InnoDB;

CREATE TABLE `email_forwarding` (
  `autoId` int unsigned NOT NULL AUTO_INCREMENT,
  `domainId` int unsigned NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `forwardedTo` varchar(255) NOT NULL,
  `createdDateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`autoId`),
  KEY (`domainId`),
  KEY (`email`),
  FOREIGN KEY on_domain_id (`domainId`) REFERENCES email_domains (`domainId`)
) ENGINE=InnoDB;
