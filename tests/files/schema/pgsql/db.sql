DROP TABLE IF EXISTS email_forwarding CASCADE;
DROP TABLE IF EXISTS email_domains CASCADE;

CREATE TABLE email_domains (
  domainid SERIAL PRIMARY KEY,
  domainname VARCHAR(70) NOT NULL,
  isactive BOOLEAN NOT NULL DEFAULT TRUE,
  createddatetime TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX ON email_domains (domainname, isactive);

CREATE TABLE email_forwarding (
  autoid SERIAL PRIMARY KEY,
  domainid INT NOT NULL REFERENCES email_domains,
  email VARCHAR(255) DEFAULT NULL,
  forwardedto VARCHAR(255) NOT NULL
);
CREATE INDEX ON email_forwarding(domainid);
CREATE UNIQUE INDEX ON email_forwarding(email);
