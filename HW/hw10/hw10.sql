CREATE TABLE parents (parent TEXT, child TEXT);

INSERT INTO parents VALUES
  ('ace', 'bella'),
  ('ace', 'charlie'),
  ('daisy', 'hank'),
  ('finn', 'ace'),
  ('finn', 'daisy'),
  ('finn', 'ginger'),
  ('ellie', 'finn');

CREATE TABLE dogs (name TEXT, fur TEXT, height INTEGER);

INSERT INTO dogs VALUES
  ('ace',     'long',  26),
  ('bella',   'short', 52),
  ('charlie', 'long',  47),
  ('daisy',   'long',  46),
  ('ellie',   'short', 35),
  ('finn',    'curly', 32),
  ('ginger',  'short', 28),
  ('hank',    'curly', 31);

CREATE TABLE sizes (size TEXT, min INTEGER, max INTEGER);

INSERT INTO sizes VALUES
  ('toy',      24, 28),
  ('mini',     28, 35),
  ('medium',   35, 45),
  ('standard', 45, 60);


-- All dogs with parents ordered by decreasing height of their parent
CREATE TABLE by_parent_height AS
    SELECT p.child
    FROM parents AS p,dogs AS d
    WHERE p.parent = d.name
    ORDER BY d.height DESC;



-- The size of each dog
CREATE TABLE size_of_dogs AS
  SELECT d.name ,s.size
  FROM dogs AS d,sizes AS s
  WHERE d.height > s.min AND d.height <= s.max;



-- [Optional] Filling out this helper table is recommended
CREATE TABLE siblings AS
  SELECT a.child AS first,b.child AS second
  FROM parents AS a, parents AS b
  WHERE a.parent = b.parent AND a.child < b.child;

-- Sentences about siblings that are the same size
CREATE TABLE sentences AS
  SELECT "The two siblings, " || s.first || " and " || s.second || ", have the same size: " || d1.size
    FROM siblings AS s, size_of_dogs AS d1,size_of_dogs AS d2
    WHERE s.first = d1.name AND s.second = d2.name AND d1.size = d2.size;


-- Height range for each fur type where all of the heights differ by no more than 30% from the average height

CREATE TABLE low_variance AS
  SELECT fur, MAX(height) - MIN(height) AS height_range
  FROM dogs
  GROUP BY fur
  HAVING MIN(height) >= AVG(height) * 0.7
     AND MAX(height) <= AVG(height) * 1.3;
