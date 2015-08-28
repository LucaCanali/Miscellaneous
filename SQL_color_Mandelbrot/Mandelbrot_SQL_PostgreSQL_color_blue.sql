-- Mandelbrot set visualization in SQL for PostgreSQL
--
-- Most of the code from the PostgreSQL wiki https://wiki.postgresql.org/wiki/Mandelbrot_set
-- Added color visualization taken from the code of OraLatencyMap and PyLatencyMap
-- https://github.com/LucaCanali/
-- Author: Luca.Canali@cern.ch, August 2015
--
-- Additional references:
-- http://thedailywtf.com/articles/Stupid-Coding-Tricks-The-TSQL-Madlebrot
-- https://en.wikipedia.org/wiki/Mandelbrot_set
-- https://www.sqlite.org/lang_with.html
-- https://community.oracle.com/message/3136057
-- http://xoph.co/20130917/mandelbrot-sql/
--

-- NOTE: you will need a terminal screen with a window of at least 100 x 100 to display this
-- Changing format is needed to display ANSI escape codes in psql 
\pset format unaligned

WITH RECURSIVE
x(i)
AS (
    VALUES(0)
UNION ALL
    SELECT i + 1 FROM x WHERE i < 101
),
Z(Ix, Iy, Cx, Cy, X, Y, I)
AS (
    SELECT Ix, Iy, X::FLOAT, Y::FLOAT, X::FLOAT, Y::FLOAT, 0
    FROM
        (SELECT -2.2 + 0.031 * i, i FROM x) AS xgen(x,ix)
    CROSS JOIN
        (SELECT -1.5 + 0.031 * i, i FROM x) AS ygen(y,iy)
    UNION ALL
    SELECT Ix, Iy, Cx, Cy, X * X - Y * Y + Cx AS X, Y * X * 2 + Cy, I + 1
    FROM Z
    WHERE X * X + Y * Y < 16.0
    AND I < 27
),
Zt (Ix, Iy, I) AS (
    SELECT Ix, Iy, MAX(I) AS I
    FROM Z
    GROUP BY Iy, Ix
    ORDER BY Iy, Ix
),
Palette AS (
select 0 ID, chr(27)||'[48;5;0m '  ||chr(27)||'[0m' COLOR  -- Black
UNION ALL 
select 1 ID, chr(27)||'[48;5;15m ' ||chr(27)||'[0m' COLOR  -- White
UNION ALL 
select 2 ID, chr(27)||'[48;5;51m '||chr(27)||'[0m' COLOR   -- Light blue
UNION ALL 
select 3 ID, chr(27)||'[48;5;45m '||chr(27)||'[0m' COLOR 
UNION ALL 
select 4 ID, chr(27)||'[48;5;39m '||chr(27)||'[0m' COLOR   
UNION ALL 
select 5 ID, chr(27)||'[48;5;33m '||chr(27)||'[0m' COLOR 
UNION ALL 
select 6 ID, chr(27)||'[48;5;27m '||chr(27)||'[0m' COLOR 
UNION ALL 
select 7 ID, chr(27)||'[48;5;21m '||chr(27)||'[0m' COLOR  -- Dark blue
)
SELECT array_to_string(array_agg(COLOR),'')
FROM Zt, PALETTE
WHERE 
        cast (SUBSTRING('012223333344445555666677770',GREATEST(I,1),1) as integer) = PALETTE.ID
GROUP BY Iy
ORDER BY Iy;


