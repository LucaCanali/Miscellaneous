--
-- awr_latency.sql
-- this is part of the PyLatencyMap package, Luca.Canali@cern.ch
-- service script used to extract data from dba_hist_event_histogram and print it in a record format 
-- to be processes by LatencyMap.py for visualization as Frequency-Intensity HeatMap
--
-- Usage: @awr_latency.sql <event_name> <num_data_points>
-- Examples: 
--           sqlplus -S / as sysdba @awr_latency.sql "db file sequential read" 91
--           sqlplus -S / as sysdba @awr_latency.sql "log file sync" 91
--
-- Note: the script will make LatencyMap.py abort with error when an instance restart is found 
--       the reason is that histogram delta values become negative. To be fixed in future version.
--      
--

set lines 200
set pages 0
set verify off
set echo off
whenever sqlerror exit


define event_name='&1'
define NUM_DATA_POINTS=&2
define LABEL_STRING="label, &event_name histogram historical data from AWR. latest &NUM_DATA_POINTS data points"

col max_snap_id new_value MAX_SNAP_ID
select max(snap_id) max_snap_id from dba_hist_snapshot;


with ordered_data as (
     select eh.*, 'timestamp,microsec,'||to_char(1000000*(extract(day from begin_interval_time - TO_TIMESTAMP('01/01/2010 00:00:00','DD/MM/YYYY HH24:MI:SS'))*24*60*60
        + extract(hour from begin_interval_time)*60*60 + extract(minute from begin_interval_time)*60 + extract(second from begin_interval_time)))
        ||','||to_char(begin_interval_time) timestamp_string
     from dba_hist_event_histogram eh, dba_hist_snapshot sn
     where eh.snap_id=sn.snap_id and eh.instance_number=sn.instance_number and eh.dbid=sn.dbid
           and eh.event_name='&event_name'
           and sn.snap_id between &MAX_SNAP_ID-&NUM_DATA_POINTS and &MAX_SNAP_ID
     order by sn.snap_id
)
select case when lag(snap_id) over (partition by snap_id order by snap_id) is not null then '' 
            else '<begin record>'||chr(10) end ||
       wait_time_milli||', '|| wait_count||
       case when lead(snap_id) over (partition by snap_id order by snap_id) is not null then '' 
            else chr(10)||timestamp_string||chr(10)||'&LABEL_STRING'||chr(10)||'latencyunit, millisec' ||chr(10)||
                 '<end record>'||chr(10) end
from ordered_data;

exit

