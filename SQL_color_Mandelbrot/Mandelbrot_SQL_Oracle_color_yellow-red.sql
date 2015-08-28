-- Mandelbrot set visualization in SQL with color for Oracle 
--
-- Ported to Oracle from the PostgreSQL version https://wiki.postgresql.org/wiki/Mandelbrot_set
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
-- Tested on Oracle (SQL*plus) 11.2.0.4 for Linux using Putty as terminal emulator
--

-- Oracle SQL*plus page setup and formatting parameters
set verify off
set lines 4000
set pages 999

-- Configuration parameters for the Mandelbrot set calculation
-- Edit to change the region displayed and/or resolution by changing the definitions here below
-- Edit your terminal screen resolution and/or modify XPOINTS and YPOINTS so that the image fits the screen
define XMIN=-2.0
define YMIN=-1.4
define XMAX=0.5
define YMAX=1.4
define XPOINTS=150
define YPOINTS=80
define XSTEP="(&XMAX - &XMIN)/(&XPOINTS - 1)"
define YSTEP="(&YMAX - &YMIN)/(&YPOINTS - 1)"

-- Visualization parameters 
define COLORMAP="012223333344445555666677770"
define MAXITER="LENGTH('&COLORMAP')"
define RED_PALETTE="0,0,1,15,2,226,3,220,4,214,5,208,6,202,7,196"
define PALETTE_NUMCOLS=8
define ESCAPE_VAL=4
define ANSICODE_PREFIX="chr(27)||'[48;5;'"
define ANSICODE_BACKTONORMAL="chr(27)||'[0m'"

WITH
   XGEN AS (                            -- X dimension values generator
        SELECT CAST(&XMIN + &XSTEP * (rownum-1) AS binary_double) AS X, rownum AS IX FROM DUAL CONNECT BY LEVEL <= &XPOINTS),
   YGEN AS (                            -- Y dimension values generator
        SELECT CAST(&YMIN + &YSTEP * (rownum-1) AS binary_double) AS Y, rownum AS IY FROM DUAL CONNECT BY LEVEL <= &YPOINTS),
   Z(IX, IY, CX, CY, X, Y, I) AS (     -- Z point iterator. Makes use of recursive common table expression 
        SELECT IX, IY, X, Y, X, Y, 0 FROM XGEN, YGEN
        UNION ALL
        SELECT IX, IY, CX, CY, X*X - Y*Y + CX, 2*X*Y + CY, I+1 FROM Z WHERE X*X + Y*Y < &ESCAPE_VAL AND I < &MAXITER),
   MANDELBROT_MAP AS (                       -- Computes an approximated map of the Mandelbrot set
        SELECT IX, IY, MAX(I) AS VAL FROM Z  -- VAL=MAX(I) represents how quickly the values reached the escape point
        GROUP BY IY, IX),
   PALETTE AS (                              -- Color palette generator using ANSI escape codes
        SELECT rownum-1 ID, &ANSICODE_PREFIX|| DECODE(rownum-1, &RED_PALETTE) || 'm ' || &ANSICODE_BACKTONORMAL COLOR 
        FROM DUAL CONNECT BY LEVEL <= &PALETTE_NUMCOLS)
SELECT LISTAGG(PALETTE.COLOR) WITHIN GROUP (ORDER BY IX) GRAPH        -- The function LISTAGG concatenates values into rows
FROM MANDELBROT_MAP, PALETTE
WHERE TO_NUMBER(SUBSTR('&COLORMAP',MANDELBROT_MAP.VAL,1))=PALETTE.ID  -- Map visualization using PALETTE and COLORMAP
GROUP BY IY
ORDER BY IY DESC;
