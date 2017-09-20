# Notes and tools for measuring CPU-to-memory throughput in Linux

Many workloads in the data management/analytics space are CPU-bound and in particular depend
critically on memory access patterns, cache utilization and throughput between CPUs and memory.
These notes are about tools for memory performance investigations and troubleshooting in Linux.

- Here some links about the general picture to understand CPU measurement and pitfalls on modern systems
  - Brendan Gregg's blog post [CPU Utilization is Wrong](http://www.brendangregg.com/blog/2017-05-09/cpu-utilization-is-wrong.html)
  - For related topics in the Oracle context, see Tanel Poders's blog post ["RAM is the new disk"](https://blog.tanelpoder.com/2015/11/30/ram-is-the-new-disk-and-how-to-measure-its-performance-part-3-cpu-instructions-cycles/)
  - One of the key points is that a process on CPU can be busy executing instructions or waiting for memory  I/O. 
  - Another key point is that modern CPUs have instrumentation in the form of hardware counters. Use then to drill down beyond CPU utilization metrics.
  - Use `perf stat -a <pid>` to measure **instruction** and **cycles** (and their ratio, instructions per cycle: **IPC**).
    
- Tools to measure CPU-to-memory throughput and performance metrics
  - [Intel Processor Counter Monitor](https://github.com/opcm/pcm) 
    - Performance monitoring and benchmarking tools suite, originally by Intel.
    - Multiplatform. Default on Linux is to use perf events.
    - Suite of tools, see also docs at  [https://software.intel.com/en-us/articles/intel-performance-counter-monitor]
    - measures memory throughput, IPC, power, etc (see examples)
  - [Likwid](https://github.com/RRZE-HPC/likwid) 
    - Performance monitoring and benchmarking tools suite.
    - Works of a variety of Intel and AMD processors.
    - see doc at [https://github.com/RRZE-HPC/likwid/wiki]
    - measures memory throughput, IPC, power, etc (see examples)
  - Also of interest:
    - [pmu-tools by Andi Kleen](https://github.com/andikleen/pmu-tools)
    - [Intel pqos](https://github.com/01org/intel-cmt-cat)
    - Perfmon DB by Intel: [https://download.01.org/perfmon/] and [https://github.com/TomTheBear/perfmondb]

- How much can your system deliver? Tools for benchmarking memory throughput:
  - [Intel Memory Latency Checker](https://software.intel.com/en-us/articles/intelr-memory-latency-checker) - measure memory throughput and latency
  - John D. McCalpin's [Stream memory test](https://www.cs.virginia.edu/stream/) 
  - CPU specs at [https://ark.intel.com](https://ark.intel.com/#@Processors)

---

## Examples of [Intel Processor Counter Monitor](https://github.com/opcm/pcm)   
a suite of tools to read from PCM   

`./pcm-memory.x` -> memory throughput measurements

- examples for memory-intensive load generated with Spark reading Parquet 
- specs of CPU used at: [http://ark.intel.com/products/92981/Intel-Xeon-Processor-E5-2630-v4-25M-Cache-2_20-GHz]

```
# ./pcm-memory.x 20

 Processor Counter Monitor: Memory Bandwidth Monitoring Utility  ($Format:%ci ID=%h$)

 This utility measures memory bandwidth per channel or per DIMM rank in real-time

Number of physical cores: 20
Number of logical cores: 40
Number of online logical cores: 40
Threads (logical cores) per physical core: 2
Num sockets: 2
Physical cores per socket: 10
Core PMU (perfmon) version: 3
Number of core PMU generic (programmable) counters: 4
Width of generic (programmable) counters: 48 bits
Number of core PMU fixed counters: 3
Width of fixed counters: 48 bits
Nominal core frequency: 2200000000 Hz
Package thermal spec power: 85 Watt; Package minimum power: 42 Watt; Package maximum power: 170 Watt;
Socket 0: 2 memory controllers detected with total number of 5 channels. 2 QPI ports detected.
Socket 1: 2 memory controllers detected with total number of 5 channels. 2 QPI ports detected.

Detected Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz "Intel(r) microarchitecture codename Broadwell-EP/EX"
Update every 20 seconds
|---------------------------------------||---------------------------------------|
|--             Socket  0             --||--             Socket  1             --|
|---------------------------------------||---------------------------------------|
|--     Memory Channel Monitoring     --||--     Memory Channel Monitoring     --|
|---------------------------------------||---------------------------------------|
|-- Mem Ch  0: Reads (MB/s):  5619.41 --||-- Mem Ch  0: Reads (MB/s):  5593.16 --|
|--            Writes(MB/s):  6650.73 --||--            Writes(MB/s):  6603.49 --|
|-- Mem Ch  1: Reads (MB/s):  5600.66 --||-- Mem Ch  1: Reads (MB/s):  5595.89 --|
|--            Writes(MB/s):  6632.30 --||--            Writes(MB/s):  6604.29 --|
|-- Mem Ch  2: Reads (MB/s):  5585.95 --||-- Mem Ch  2: Reads (MB/s):  5641.05 --|
|--            Writes(MB/s):  6617.78 --||--            Writes(MB/s):  6661.20 --|
|-- Mem Ch  3: Reads (MB/s):  5587.52 --||-- Mem Ch  3: Reads (MB/s):  5597.89 --|
|--            Writes(MB/s):  6617.94 --||--            Writes(MB/s):  6609.67 --|
|-- NODE 0 Mem Read (MB/s) : 22393.54 --||-- NODE 1 Mem Read (MB/s) : 22427.99 --|
|-- NODE 0 Mem Write(MB/s) : 26518.75 --||-- NODE 1 Mem Write(MB/s) : 26478.66 --|
|-- NODE 0 P. Write (T/s):    2536161 --||-- NODE 1 P. Write (T/s):    2385163 --|
|-- NODE 0 Memory (MB/s):    48912.29 --||-- NODE 1 Memory (MB/s):    48906.65 --|
|---------------------------------------||---------------------------------------|
|---------------------------------------||---------------------------------------|
|--                 System Read Throughput(MB/s):      44821.53                --|
|--                System Write Throughput(MB/s):      52997.41                --|
|--               System Memory Throughput(MB/s):      97818.94                --|
|---------------------------------------||---------------------------------------|

```

`pcm.x` ->  memory throughput, QPI utilization, instructions and cycles (IPC), L3 misses,..

```
# ./pcm.x 20

 Processor Counter Monitor  ($Format:%ci ID=%h$)


Number of physical cores: 20
Number of logical cores: 40
Number of online logical cores: 40
Threads (logical cores) per physical core: 2
Num sockets: 2
Physical cores per socket: 10
Core PMU (perfmon) version: 3
Number of core PMU generic (programmable) counters: 4
Width of generic (programmable) counters: 48 bits
Number of core PMU fixed counters: 3
Width of fixed counters: 48 bits
Nominal core frequency: 2200000000 Hz
Package thermal spec power: 85 Watt; Package minimum power: 42 Watt; Package maximum power: 170 Watt;
Socket 0: 2 memory controllers detected with total number of 5 channels. 2 QPI ports detected.
Socket 1: 2 memory controllers detected with total number of 5 channels. 2 QPI ports detected.
Delay: 20
Trying to use Linux perf events...
Successfully programmed on-core PMU using Linux perf
Socket 0
Max QPI link 0 speed: 16.0 GBytes/second (8.0 GT/second)
Max QPI link 1 speed: 16.0 GBytes/second (8.0 GT/second)
Socket 1
Max QPI link 0 speed: 16.0 GBytes/second (8.0 GT/second)
Max QPI link 1 speed: 16.0 GBytes/second (8.0 GT/second)

Detected Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz "Intel(r) microarchitecture codename Broadwell-EP/EX" stepping 1

 EXEC  : instructions per nominal CPU cycle
 IPC   : instructions per CPU cycle
 FREQ  : relation to nominal CPU frequency='unhalted clock ticks'/'invariant timer ticks' (includes Intel Turbo Boost)
 AFREQ : relation to nominal CPU frequency while in active state (not in power-saving C state)='unhalted clock ticks'/'invariant timer ticks while in C0-state'  (includes Intel Turbo Boost)
 L3MISS: L3 cache misses
 L2MISS: L2 cache misses (including other core's L2 cache *hits*)
 L3HIT : L3 cache hit ratio (0.00-1.00)
 L2HIT : L2 cache hit ratio (0.00-1.00)
 L3MPI : number of L3 cache misses per instruction
 L2MPI : number of L2 cache misses per instruction
 READ  : bytes read from main memory controller (in GBytes)
 WRITE : bytes written to main memory controller (in GBytes)
 L3OCC : L3 occupancy (in KBytes)
 LMB   : L3 cache external bandwidth satisfied by local memory (in MBytes)
 RMB   : L3 cache external bandwidth satisfied by remote memory (in MBytes)
 TEMP  : Temperature reading in 1 degree Celsius relative to the TjMax temperature (thermal headroom): 0 corresponds to the max temperature
 energy: Energy in Joules


 Core (SKT) | EXEC | IPC  | FREQ  | AFREQ | L3MISS | L2MISS | L3HIT | L2HIT | L3MPI | L2MPI |  L3OCC |   LMB  |   RMB  | TEMP

   0    0     0.59   0.61   0.95    1.00     228 M    265 M    0.14    0.24    0.01    0.01      960    16861    16983     42
   1    0     0.60   0.61   0.99    1.00     236 M    277 M    0.15    0.24    0.01    0.01      800    17066    17675     42
   2    0     0.61   0.61   0.99    1.00     238 M    277 M    0.14    0.23    0.01    0.01     1520    17518    17872     42
   3    0     0.62   0.63   0.98    1.00     243 M    284 M    0.14    0.23    0.01    0.01     1080    17573    18472     41
   4    0     0.61   0.62   0.99    1.00     240 M    280 M    0.14    0.23    0.01    0.01     1200    17482    17849     43
   5    0     0.61   0.62   0.99    1.00     240 M    279 M    0.14    0.22    0.01    0.01     1760    17690    17790     43
   6    0     0.61   0.61   0.99    1.00     241 M    281 M    0.14    0.23    0.01    0.01      520    17964    17756     42
   7    0     0.60   0.62   0.97    1.00     240 M    280 M    0.14    0.23    0.01    0.01     1160    17779    17587     42
   8    0     0.61   0.62   0.99    1.00     244 M    284 M    0.14    0.23    0.01    0.01      280    17752    18249     43
   9    0     0.60   0.61   0.97    1.00     235 M    274 M    0.14    0.23    0.01    0.01     1200    16928    17178     43
  10    1     0.61   0.62   0.98    1.00     239 M    278 M    0.14    0.22    0.01    0.01     1280    17603    17585     48
  11    1     0.61   0.65   0.93    1.00     234 M    272 M    0.14    0.23    0.01    0.01      120    17488    17287     48
  12    1     0.61   0.64   0.96    1.00     238 M    277 M    0.14    0.23    0.01    0.01        0    17320    17634     48
  13    1     0.68   0.70   0.97    1.00     259 M    300 M    0.14    0.23    0.01    0.01     1840    19410    19120     47
  14    1     0.56   0.61   0.92    1.00     222 M    258 M    0.14    0.23    0.01    0.01     1640    16361    16174     48
  15    1     0.63   0.65   0.96    1.00     242 M    281 M    0.14    0.23    0.01    0.01     1160    17917    17819     49
  16    1     0.63   0.64   0.99    1.00     245 M    284 M    0.14    0.23    0.01    0.01      760    18479    17728     48
  17    1     0.58   0.62   0.93    1.00     226 M    265 M    0.15    0.23    0.01    0.01     2120    16979    16124     48
  18    1     0.62   0.62   0.99    1.00     243 M    282 M    0.14    0.23    0.01    0.01     1840    17988    18464     49
  19    1     0.60   0.64   0.93    1.00     233 M    272 M    0.14    0.23    0.01    0.01      720    17300    16804     48
  20    0     0.62   0.64   0.97    1.00     239 M    278 M    0.14    0.23    0.01    0.01     2280    17599    17931     42
  21    0     0.61   0.62   0.98    1.00     238 M    276 M    0.14    0.23    0.01    0.01     1000    16794    18185     42
  22    0     0.60   0.60   0.99    1.00     236 M    275 M    0.14    0.24    0.01    0.01     1920    16824    17223     42
  23    0     0.58   0.62   0.95    1.00     228 M    266 M    0.14    0.25    0.01    0.01     1160    16690    16415     41
  24    0     0.60   0.64   0.94    1.00     233 M    272 M    0.14    0.23    0.01    0.01     2120    16678    17271     43
  25    0     0.59   0.63   0.95    1.00     234 M    273 M    0.14    0.23    0.01    0.01      480    16548    17253     44
  26    0     0.61   0.62   0.97    1.00     236 M    275 M    0.14    0.23    0.01    0.01     1280    19179    19018     42
  27    0     0.60   0.66   0.92    1.00     229 M    267 M    0.14    0.24    0.01    0.01     2160    18751    18271     43
  28    0     0.60   0.64   0.94    1.00     233 M    271 M    0.14    0.23    0.01    0.01     2000    18913    19095     43
  29    0     0.60   0.65   0.92    1.00     232 M    271 M    0.14    0.23    0.01    0.01     1320    18807    18820     43
  30    1     0.61   0.62   0.99    1.00     240 M    279 M    0.14    0.22    0.01    0.01     1840    17841    17832     48
  31    1     0.58   0.67   0.87    1.00     221 M    256 M    0.14    0.23    0.01    0.01     2760    16085    16277     48
  32    1     0.60   0.65   0.92    1.00     232 M    271 M    0.14    0.23    0.01    0.01     1360    16858    16373     48
  33    1     0.48   0.65   0.74    1.00     187 M    216 M    0.13    0.23    0.01    0.01     1560    13096    13288     47
  34    1     0.65   0.66   0.98    1.00     245 M    285 M    0.14    0.24    0.01    0.01      800    18486    17712     48
  35    1     0.56   0.64   0.87    1.00     217 M    254 M    0.14    0.23    0.01    0.01     1960    16032    15274     49
  36    1     0.58   0.61   0.95    1.00     228 M    266 M    0.14    0.23    0.01    0.01     1240    18850    18938     49
  37    1     0.62   0.63   0.99    1.00     242 M    280 M    0.14    0.22    0.01    0.01     1520    19970    20085     48
  38    1     0.60   0.65   0.92    1.00     229 M    268 M    0.15    0.24    0.01    0.01     1240    18474    18766     49
  39    1     0.61   0.62   0.99    1.00     242 M    281 M    0.14    0.23    0.01    0.01     1080    20317    20219     48
---------------------------------------------------------------------------------------------------------------
 SKT    0     0.60   0.62   0.97    1.00    4733 M   5514 M    0.14    0.23    0.01    0.01    26200   351396   356893     37
 SKT    1     0.60   0.64   0.94    1.00    4674 M   5433 M    0.14    0.23    0.01    0.01    26840   352854   349503     43
---------------------------------------------------------------------------------------------------------------
 TOTAL  *     0.60   0.63   0.95    1.00    9408 M     10 G    0.14    0.23    0.01    0.01     N/A     N/A     N/A      N/A

 Instructions retired: 1059 G ; Active cycles: 1678 G ; Time (TSC):   44 Gticks ; C0 (active,non-halted) core residency: 95.33 %

 C1 core residency: 3.93 %; C3 core residency: 0.12 %; C6 core residency: 0.61 %; C7 core residency: 0.00 %;
 C2 package residency: 0.14 %; C3 package residency: 0.00 %; C6 package residency: 0.00 %; C7 package residency: 0.00 %;

 PHYSICAL CORE IPC                 : 1.26 => corresponds to 31.57 % utilization for cores in active state
 Instructions per nominal CPU cycle: 1.20 => corresponds to 30.09 % core utilization over time interval
 SMI count: 0
---------------------------------------------------------------------------------------------------------------

Intel(r) QPI traffic estimation in bytes (data and non-data traffic outgoing from CPU/socket through QPI links):

               QPI0     QPI1    |  QPI0   QPI1
---------------------------------------------------------------------------------------------------------------
 SKT    0      272 G    272 G   |   85%    85%
 SKT    1      273 G    273 G   |   85%    85%
---------------------------------------------------------------------------------------------------------------
Total QPI outgoing data and non-data traffic: 1093 G
MEM (GB)->|  READ |  WRITE | CPU energy | DIMM energy
---------------------------------------------------------------------------------------------------------------
 SKT   0    449.11    527.08     1340.82     468.02
 SKT   1    448.76    528.87     1345.09     484.43
---------------------------------------------------------------------------------------------------------------
       *    897.87    1055.95     2685.92     952.45
```

`pcm-core.x` -> info on instructions, cycles, 

```
# ./pcm-core.x 20
Number of physical cores: 20
Number of logical cores: 40
Number of online logical cores: 40
Threads (logical cores) per physical core: 2
Num sockets: 2
Physical cores per socket: 10
Core PMU (perfmon) version: 3
Number of core PMU generic (programmable) counters: 4
Width of generic (programmable) counters: 48 bits
Number of core PMU fixed counters: 3
Width of fixed counters: 48 bits
Nominal core frequency: 2200000000 Hz
Package thermal spec power: 85 Watt; Package minimum power: 42 Watt; Package maximum power: 170 Watt;
Socket 0: 2 memory controllers detected with total number of 5 channels. 2 QPI ports detected.
Socket 1: 2 memory controllers detected with total number of 5 channels. 2 QPI ports detected.

 Processor Counter Monitor: Core Monitoring Utility

Trying to use Linux perf events...
Successfully programmed on-core PMU using Linux perf
Socket 0
Max QPI link 0 speed: 16.0 GBytes/second (8.0 GT/second)
Max QPI link 1 speed: 16.0 GBytes/second (8.0 GT/second)
Socket 1
Max QPI link 0 speed: 16.0 GBytes/second (8.0 GT/second)
Max QPI link 1 speed: 16.0 GBytes/second (8.0 GT/second)

Detected Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz "Intel(r) microarchitecture codename Broadwell-EP/EX"
Update every 20.0 seconds
Time elapsed: 20233 ms
txn_rate: 1

Core | IPC | Instructions  |  Cycles  | Event0  | Event1  | Event2  | Event3
   0   0.61          26 G       43 G       0         0         0        10 G
   1   0.61          27 G       44 G       0         0         0        10 G
   2   0.63          27 G       43 G       0         0         0        10 G
   3   0.61          26 G       43 G       0         0         0        10 G
   4   0.62          26 G       43 G       0         0         0        10 G
   5   0.62          26 G       43 G       0         0         0        10 G
   6   0.61          26 G       43 G       0         0         0        10 G
   7   0.64          27 G       42 G       0         0         0        10 G
   8   0.63          27 G       43 G       0         0         0        10 G
   9   0.63          27 G       43 G       0         0         0        10 G
  10   0.67          28 G       41 G       0         0         0        10 G
  11   0.62          26 G       42 G       0         0         0        10 G
  12   0.61          26 G       43 G       0         0         0        10 G
  13   0.62          26 G       41 G       0         0         0        10 G
  14   0.64          27 G       42 G       0         0         0        10 G
  15   0.62          27 G       43 G       0         0         0        10 G
  16   0.62          27 G       43 G       0         0         0        10 G
  17   0.64          28 G       43 G       0         0         0        10 G
  18   0.62          25 G       41 G       0         0         0        10 G
  19   0.63          27 G       43 G       0         0         0        10 G
  20   0.64          26 G       41 G       0         0         0        10 G
  21   0.63          26 G       41 G       0         0         0        10 G
  22   0.61          25 G       41 G       0         0         0        10 G
  23   0.63          26 G       41 G       0         0         0        10 G
  24   0.64          26 G       41 G       0         0         0        10 G
  25   0.62          26 G       42 G       0         0         0        10 G
  26   0.64          26 G       41 G       0         0         0        10 G
  27   0.64          25 G       39 G       0         0         0        10 G
  28   0.63          26 G       41 G       0         0         0        10 G
  29   0.62          24 G       40 G       0         0         0        10 G
  30   0.63          23 G       37 G       0         0         0        10 G
  31   0.64          27 G       43 G       0         0         0        10 G
  32   0.61          26 G       43 G       0         0         0        10 G
  33   0.65          27 G       42 G       0         0         0        10 G
  34   0.63          25 G       40 G       0         0         0        10 G
  35   0.64          26 G       41 G       0         0         0        10 G
  36   0.63          26 G       42 G       0         0         0        10 G
  37   0.62          25 G       41 G       0         0         0        10 G
  38   0.66          27 G       40 G       0         0         0        10 G
  39   0.65          27 G       41 G       0         0         0        10 G
-------------------------------------------------------------------------------------------------------------------
   *   0.63        1064 G     1692 G       0         0         0       426 G
```

`./pcm-power.x` -> CPU power usage  info

``` 
# ./pcm-power.x 20

 Processor Counter Monitor  ($Format:%ci ID=%h$)

 Power Monitoring Utility
Number of physical cores: 20
Number of logical cores: 40
Number of online logical cores: 40
Threads (logical cores) per physical core: 2
Num sockets: 2
Physical cores per socket: 10
Core PMU (perfmon) version: 3
Number of core PMU generic (programmable) counters: 4
Width of generic (programmable) counters: 48 bits
Number of core PMU fixed counters: 3
Width of fixed counters: 48 bits
Nominal core frequency: 2200000000 Hz
Package thermal spec power: 85 Watt; Package minimum power: 42 Watt; Package maximum power: 170 Watt;
Socket 0: 2 memory controllers detected with total number of 5 channels. 2 QPI ports detected.
Socket 1: 2 memory controllers detected with total number of 5 channels. 2 QPI ports detected.



MC counter group: 0
PCU counter group: 0
Freq bands [0/1/2]: 1200 MHz; 2000 MHz; 4000 MHz;
----------------------------------------------------------------------------------------------
Time elapsed: 19954 ms
Called sleep function for 20000 ms
S0P0; QPIClocks: 39956674766; L0p Tx Cycles: 0.14%; L1 Cycles: 0.00%
S0P1; QPIClocks: 39956680678; L0p Tx Cycles: 0.14%; L1 Cycles: 0.00%
S0CH0; DRAMClocks: 21310233794; Rank0 CKE Off Residency: 0.12%; Rank0 CKE Off Average Cycles: 808; Rank0 Cycles per transition: 661746
S0CH0; DRAMClocks: 21310233794; Rank1 CKE Off Residency: 0.12%; Rank1 CKE Off Average Cycles: 819; Rank1 Cycles per transition: 671526
S0CH1; DRAMClocks: 21310237472; Rank0 CKE Off Residency: 0.12%; Rank0 CKE Off Average Cycles: 818; Rank0 Cycles per transition: 669081
S0CH1; DRAMClocks: 21310237472; Rank1 CKE Off Residency: 0.12%; Rank1 CKE Off Average Cycles: 840; Rank1 Cycles per transition: 683480
S0CH2; DRAMClocks: 21310240988; Rank0 CKE Off Residency: 0.12%; Rank0 CKE Off Average Cycles: 824; Rank0 Cycles per transition: 674268
S0CH2; DRAMClocks: 21310240988; Rank1 CKE Off Residency: 0.12%; Rank1 CKE Off Average Cycles: 852; Rank1 Cycles per transition: 692070
S0CH3; DRAMClocks: 21310244374; Rank0 CKE Off Residency: 0.12%; Rank0 CKE Off Average Cycles: 814; Rank0 Cycles per transition: 665009
S0CH3; DRAMClocks: 21310244374; Rank1 CKE Off Residency: 0.12%; Rank1 CKE Off Average Cycles: 842; Rank1 Cycles per transition: 684073
S0CH4; DRAMClocks: 0; Rank0 CKE Off Residency: -nan%; Rank0 CKE Off Average Cycles: -1; Rank0 Cycles per transition: -1
S0CH4; DRAMClocks: 0; Rank1 CKE Off Residency: -nan%; Rank1 CKE Off Average Cycles: -1; Rank1 Cycles per transition: -1
S0; PCUClocks: 19972702313; Freq band 0/1/2 cycles: 0.00%; 0.00%; 0.00%
S0; Consumed energy units: 21940672; Consumed Joules: 1339.15; Watts: 67.11; Thermal headroom below TjMax: 37
S0; Consumed DRAM energy units: 30697043; Consumed DRAM Joules: 469.66; DRAM Watts: 23.54
S1P0; QPIClocks: 39944957822; L0p Tx Cycles: 0.07%; L1 Cycles: 0.00%
S1P1; QPIClocks: 39944958322; L0p Tx Cycles: 0.07%; L1 Cycles: 0.00%
S1CH0; DRAMClocks: 21303979727; Rank0 CKE Off Residency: 0.05%; Rank0 CKE Off Average Cycles: 535; Rank0 Cycles per transition: 997657
S1CH0; DRAMClocks: 21303979727; Rank1 CKE Off Residency: 0.05%; Rank1 CKE Off Average Cycles: 527; Rank1 Cycles per transition: 985565
S1CH1; DRAMClocks: 21303979945; Rank0 CKE Off Residency: 0.05%; Rank0 CKE Off Average Cycles: 541; Rank0 Cycles per transition: 1007756
S1CH1; DRAMClocks: 21303979945; Rank1 CKE Off Residency: 0.05%; Rank1 CKE Off Average Cycles: 526; Rank1 Cycles per transition: 985565
S1CH2; DRAMClocks: 21303979791; Rank0 CKE Off Residency: 0.05%; Rank0 CKE Off Average Cycles: 522; Rank0 Cycles per transition: 979358
S1CH2; DRAMClocks: 21303979791; Rank1 CKE Off Residency: 0.05%; Rank1 CKE Off Average Cycles: 529; Rank1 Cycles per transition: 989180
S1CH3; DRAMClocks: 21303980198; Rank0 CKE Off Residency: 0.05%; Rank0 CKE Off Average Cycles: 538; Rank0 Cycles per transition: 1001738
S1CH3; DRAMClocks: 21303980198; Rank1 CKE Off Residency: 0.05%; Rank1 CKE Off Average Cycles: 528; Rank1 Cycles per transition: 988308
S1CH4; DRAMClocks: 0; Rank0 CKE Off Residency: -nan%; Rank0 CKE Off Average Cycles: -1; Rank0 Cycles per transition: -1
S1CH4; DRAMClocks: 0; Rank1 CKE Off Residency: -nan%; Rank1 CKE Off Average Cycles: -1; Rank1 Cycles per transition: -1
S1; PCUClocks: 19969741926; Freq band 0/1/2 cycles: 0.00%; 0.00%; 0.00%
S1; Consumed energy units: 22058738; Consumed Joules: 1346.36; Watts: 67.47; Thermal headroom below TjMax: 43
S1; Consumed DRAM energy units: 31974483; Consumed DRAM Joules: 489.21; DRAM Watts: 24.52
----------------------------------------------------------------------------------------------
```

---
## Example of usage of [likwid](https://github.com/RRZE-HPC/likwid)   
a tool to measure performance metrics 

- likwid supports multiple architectures and comes with predefined metrics groups,
see (https://github.com/RRZE-HPC/likwid/tree/master/groups)


```
/usr/local/bin/likwid-perfctr -c 0-39 -g MEM -S 10s

..selected parts of the output:

+----------------------------+---------+--------------+-------------+-------------+--------------+
|            Event           | Counter |      Sum     |     Min     |     Max     |      Avg     |
+----------------------------+---------+--------------+-------------+-------------+--------------+
|   INSTR_RETIRED_ANY STAT   |  FIXC0  | 410974008534 |  8103677612 | 12240502972 | 1.027435e+10 |
| CPU_CLK_UNHALTED_CORE STAT |  FIXC1  | 552278388932 | 11675605322 | 15588609322 | 1.380696e+10 |
|  CPU_CLK_UNHALTED_REF STAT |  FIXC2  | 552285357844 | 11675840154 | 15588821006 | 1.380713e+10 |
|      CAS_COUNT_RD STAT     | MBOX0C0 |  1694741670  |      0      |  848299793  | 4.236854e+07 |
|      CAS_COUNT_WR STAT     | MBOX0C1 |  1974785815  |      0      |  996809807  | 4.936965e+07 |
|      CAS_COUNT_RD STAT     | MBOX1C0 |  1682219881  |      0      |  841213192  | 4.205550e+07 |
|      CAS_COUNT_WR STAT     | MBOX1C1 |  1956362517  |      0      |  987873036  | 4.890906e+07 |
|      CAS_COUNT_RD STAT     | MBOX2C0 |  1679811043  |      0      |  839927316  | 4.199528e+07 |
|      CAS_COUNT_WR STAT     | MBOX2C1 |  1954309920  |      0      |  986744524  |   48857748   |
|      CAS_COUNT_RD STAT     | MBOX3C0 |  1685092073  |      0      |  844606157  | 4.212730e+07 |
|      CAS_COUNT_WR STAT     | MBOX3C1 |  1956141910  |      0      |  989925369  | 4.890355e+07 |
|      CAS_COUNT_RD STAT     | MBOX4C0 |       0      |      0      |      0      |       0      |
|      CAS_COUNT_WR STAT     | MBOX4C1 |       0      |      0      |      0      |       0      |
|      CAS_COUNT_RD STAT     | MBOX5C0 |       0      |      0      |      0      |       0      |
|      CAS_COUNT_WR STAT     | MBOX5C1 |       0      |      0      |      0      |       0      |
|      CAS_COUNT_RD STAT     | MBOX6C0 |       0      |      0      |      0      |       0      |
|      CAS_COUNT_WR STAT     | MBOX6C1 |       0      |      0      |      0      |       0      |
|      CAS_COUNT_RD STAT     | MBOX7C0 |       0      |      0      |      0      |       0      |
|      CAS_COUNT_WR STAT     | MBOX7C1 |       0      |      0      |      0      |       0      |
+----------------------------+---------+--------------+-------------+-------------+--------------+


+----------------------------------------+------------+-----------+------------+-----------+
|                 Metric                 |     Sum    |    Min    |     Max    |    Avg    |
+----------------------------------------+------------+-----------+------------+-----------+
|        Runtime (RDTSC) [s] STAT        |  400.2760  |  10.0069  |   10.0069  |  10.0069  |
|        Runtime unhalted [s] STAT       |  262.1361  |   4.6112  |   7.9159   |   6.5534  |
|            Clock [MHz] STAT            | 87748.2886 | 2193.5904 |  2193.7456 | 2193.7072 |
|                CPI STAT                |   61.8394  |   1.3462  |   1.8382   |   1.5460  |
|  Memory read bandwidth [MBytes/s] STAT | 43037.3610 |     0     | 21533.4565 | 1075.9340 |
|  Memory read data volume [GBytes] STAT |  430.6711  |     0     |  215.4834  |  10.7668  |
| Memory write bandwidth [MBytes/s] STAT | 49481.2709 |     0     | 24809.4503 | 1237.0318 |
| Memory write data volume [GBytes] STAT |  495.1547  |     0     |  248.2660  |  12.3789  |
|    Memory bandwidth [MBytes/s] STAT    | 92518.6320 |     0     | 46313.3549 | 2312.9658 |
|    Memory data volume [GBytes] STAT    |  925.8258  |     0     |  463.4537  |  23.1456  |
+----------------------------------------+------------+-----------+------------+-----------+

```

Other commands in the likwid  suiteinclude (see docs for more):

`/usr/local/bin/likwid-perfctr -c 0-39 -g ENERGY -S 10s`

`/usr/local/bin/likwid-topology`

` /usr/local/bin/likwid-powermeter`

`/usr/local/bin/likwid-features -a`

`/usr/local/bin/likwid-perfctr -c 0-39 -g L3 -S 10s `

---

## Example of [Intel Memory Latency Checker](https://software.intel.com/en-us/articles/intelr-memory-latency-checker)  
This is a tool to benchmark memory performance.  
Metrics from a dual socket system with Intel Xeon CPU E5-2630 v4:  
 
```
# mlc/Linux/mlc

Measuring idle latencies (in ns)...
        Memory node
Socket       0       1
     0   106.9   106.9
     1   107.2   107.2

Measuring Peak Injection Memory Bandwidths for the system
Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
Using all the threads from each core if Hyper-threading is enabled
Using traffic with the following read-write ratios
ALL Reads        :      93611.4
3:1 Reads-Writes :      89157.7
2:1 Reads-Writes :      86794.3
1:1 Reads-Writes :      80648.3
Stream-triad like:      81263.4

Measuring Memory Bandwidths between nodes within system
Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
Using all the threads from each core if Hyper-threading is enabled
Using Read-only traffic type
        Memory node
Socket       0       1
     0  50444.8 50349.9
     1  50487.7 50583.0

Measuring Loaded Latencies for the system
Using all the threads from each core if Hyper-threading is enabled
Using Read-only traffic type
Inject  Latency Bandwidth
Delay   (ns)    MB/sec
==========================
 00000  234.99    93581.0
 00002  234.98    93588.4
 00008  234.28    93567.0
 00015  232.72    93541.5
 00050  223.09    93153.7
 00100  159.39    88689.4
 00200  126.83    49916.2
 00300  119.27    34418.7
 00400  116.13    26341.4
 00500  114.18    21361.2
 00700  112.02    15554.4
 01000  109.97    11133.6
 01300  109.25     8728.1
 01700  108.91     6826.3
 02500  108.63     4841.3
 03500  108.50     3629.5
 05000  108.37     2719.7
 09000  108.16     1775.5
 20000  107.98     1125.7

Measuring cache-to-cache transfer latency (in ns)...
Local Socket L2->L2 HIT  latency        35.3
Local Socket L2->L2 HITM latency        39.9
Remote Socket L2->L2 HITM latency (data address homed in writer socket)
                Reader Socket
Writer Socket        0       1
            0        -   101.7
            1    102.7       -
Remote Socket L2->L2 HITM latency (data address homed in reader socket)
                Reader Socket
Writer Socket        0       1
            0        -   103.1
            1    103.3       -
```


---
## Example of stream_om
A tool for benchmarking memory.
```
gcc -O3 -fopenmp stream.c -DSTREAM_ARRAY_SIZE=100000000 -o stream_om.100M.O3
export OMP_NUM_THREADS=8

$ ./stream_om.100M.O3
-------------------------------------------------------------
STREAM version $Revision: 5.10 $
-------------------------------------------------------------
This system uses 8 bytes per array element.
-------------------------------------------------------------
Array size = 100000000 (elements), Offset = 0 (elements)
Memory per array = 762.9 MiB (= 0.7 GiB).
Total memory required = 2288.8 MiB (= 2.2 GiB).
Each kernel will be executed 10 times.
 The *best* time for each kernel (excluding the first iteration)
 will be used to compute the reported bandwidth.
-------------------------------------------------------------
Number of Threads requested = 40
Number of Threads counted = 40
-------------------------------------------------------------
Your clock granularity/precision appears to be 1 microseconds.
Each test below will take on the order of 25494 microseconds.
   (= 25494 clock ticks)
Increase the size of the arrays if this shows that
you are not getting at least 20 clock ticks per test.
-------------------------------------------------------------
WARNING -- The above is only a rough guideline.
For best results, please be sure you know the
precision of your system timer.
-------------------------------------------------------------
Function    Best Rate MB/s  Avg time     Min time     Max time
Copy:           58167.4     0.028278     0.027507     0.034045
Scale:          57820.1     0.028069     0.027672     0.030978
Add:            66598.3     0.036076     0.036037     0.036130
Triad:          66869.0     0.036157     0.035891     0.038008
-------------------------------------------------------------
Solution Validates: avg error less than 1.000000e-13 on all three arrays
-------------------------------------------------------------
```

---
## Example [pmu-tools](https://github.com/andikleen/pmu-tools)

The "ocperf" wrapper to "perf" that provides a full core performance counter event list for common Intel CPUs.

Example

./ocperf.py list

