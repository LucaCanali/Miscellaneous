--
-- This script displays a simple color palette using ANSI escape codes 
-- Use with Oracle SQL, from SQL*plus
-- Requires a terminal capable of displaying ANSI escape codes, for example Putty
-- It will not work on Windows CMD.EXE
-- The palette definition come from heat map visualization as in: 
-- https://github.com/LucaCanali/OraLatencyMap
-- https://github.com/LucaCanali/PyLatencyMap
--
-- Blue-color palette
-- 

define ANSICODE_PREFIX="chr(27)||'[48;5;'"
define ANSICODE_BACKTONORMAL="chr(27)||'[0m'"

select 0 ID, &ANSICODE_PREFIX|| '0m '|| &ANSICODE_BACKTONORMAL COLOR from dual
UNION ALL  -- Black
select 1 ID, &ANSICODE_PREFIX|| '15m '|| &ANSICODE_BACKTONORMAL COLOR from dual  
UNION ALL  -- White
select 2 ID, &ANSICODE_PREFIX|| '51m '|| &ANSICODE_BACKTONORMAL COLOR from dual  
UNION ALL  -- Light blue
select 3 ID, &ANSICODE_PREFIX|| '45m '|| &ANSICODE_BACKTONORMAL COLOR from dual
UNION ALL 
select 4 ID, &ANSICODE_PREFIX|| '39m '|| &ANSICODE_BACKTONORMAL COLOR from dual  
UNION ALL 
select 5 ID, &ANSICODE_PREFIX|| '33m '|| &ANSICODE_BACKTONORMAL COLOR from dual
UNION ALL 
select 6 ID, &ANSICODE_PREFIX|| '27m '|| &ANSICODE_BACKTONORMAL COLOR from dual
UNION ALL  -- Dark blue                                                                       
select 7 ID, &ANSICODE_PREFIX|| '21m '|| &ANSICODE_BACKTONORMAL COLOR from dual; 

-- A more compact code for the same result

define BLUE_PALETTE="0,0,1,15,2,51,3,45,4,39,5,33,6,27,7,21"
define PALETTE_NUMCOLS=8

select rownum-1 ID, &ANSICODE_PREFIX|| decode(rownum-1, &BLUE_PALETTE)|| 'm '|| &ANSICODE_BACKTONORMAL COLOR 
from dual
connect by level <= &PALETTE_NUMCOLS;
