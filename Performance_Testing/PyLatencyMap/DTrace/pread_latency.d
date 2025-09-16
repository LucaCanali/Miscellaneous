#!/usr/sbin/dtrace -s

/* pread_latency.d
  this is part of the PyLatencyMap package, Luca.Canali@cern.ch Aug 2013
  Dtrace calls to pread and pread64 and output in a format to be proceed by dtrace_connector.py
  Use this to study single-block read latency
  Modify to trace different syscalls

  Usage:
         dtrace -s DTrace/pread_latency.d |python DTrace/dtrace_connector.py
*/

syscall::pread*:entry { self->s = timestamp; }

syscall::pread*:return /self->s/ { @pread["myhistogram"] = quantize(timestamp - self->s); self->s = 0; }

tick-10s {
  printf("\n<begin record>");
  printf("\ntimestamp,microsec,%d,%Y",timestamp/1000,walltimestamp);
  printf("\nlabel, pread latency measured with DTrace");
  printf("\nlatencyunit, nanosec\n");
  printf("datasource, dtrace\n");
  printa(@pread);
  printf("\n<end record>");
}

