--
-- ora_latency.sql
-- this is part of the PyLatencyMap package, by Luca.Canali@cern.ch 
-- service script used to extract data from gv$event_histogram and print it in a record format 
-- to be processes by LatencyMap.py for visualization as Frequency-Intensity HeatMap
-- Dependency: wait_and_repeat.sql provides loop-like execution
--
-- Usage: @ora_latency.sql <event_name> <wait_time_in_sec>
-- Examples: 
--           sqlplus -S / as sysdba @ora_latency.sql "db file sequential read" 3
--           sqlplus -S / as sysdba @ora_latency.sql "log file sync" 3
--

set lines 200
set pages 0
set verify off
set echo off
whenever sqlerror exit

define event_name='&1'
define time_delay=&2

select '<begin record>' latency_data from dual
union all
select 'timestamp, microsec, '||to_char(1000000*(extract(hour from systimestamp)*60*60 + extract(minute from systimestamp)*60 
        + extract(second from systimestamp))) || ',' || systimestamp from dual
union all
select 'label,&event_name latency data from gv$event_histogram' from dual
union all
select 'latencyunit, millisec' from dual
union all
select 'datasource, oracle' from dual
union all
select wait_time_milli||', '|| wait_count from gv$event_histogram where event='&event_name' and wait_time_milli<>4294967295
union all
select '<end record>' from dual;

@@wait_and_repeat.sql &time_delay

exit

