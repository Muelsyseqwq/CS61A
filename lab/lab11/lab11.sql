CREATE table newest AS
  SELECT title,year
    FROM titles
    ORDER BY year DESC
    LIMIT 10;


CREATE table dog_movies AS 
  SELECT t.title , p.character
    FROM titles as t JOIN principals as p ON t.tconst =  p.tconst
    WHERE p.character LIKE "%dog%";



CREATE table leads AS 
  SELECT names.name, count(*) AS lead_roles
  FROM names JOIN principals ON names.nconst = principals.nconst
  WHERE principals.ordering = 1
  GROUP BY names.nconst
  HAVING count(*) > 10;


CREATE table long_movies AS 
    SELECT (titles.year /10 * 10)|| "s" AS decade, count(*) AS count
    FROM titles
    WHERE titles.runtime > 180
    GROUP BY decade;

