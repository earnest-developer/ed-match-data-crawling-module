CREATE TABLE match_data.football_match_data (
	id BIGINT NOT NULL AUTO_INCREMENT,
	division VARCHAR(30) NOT NULL,
	match_date DATE NOT NULL,
	home_team VARCHAR(30) NOT NULL,
	away_team VARCHAR(30) NOT NULL,
	ft_hg TINYINT NOT NULL,
	ft_ag TINYINT NOT NULL,
	ft_r VARCHAR(1) NOT NULL,
	ht_hg TINYINT NULL,
	ht_ag TINYINT NULL,
	ht_r VARCHAR(1) NULL,
	season VARCHAR(30) NOT NULL,
	created_on TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
	updated_on TIMESTAMP NULL,
 	PRIMARY KEY (id),
 	CONSTRAINT uc_match_date_home_team UNIQUE(match_date, home_team)
)
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;

