Volume/Device Management:
doevms          This enables support for IBM's pluggable EVMS, or Enterprise
                Volume Management System.  This is not safe to use with lvm2.
dolvm           This enables support for Linux's Logical Volume Management.
                This is not safe to use with evms2.
Screen reader access:
speakup.synth=synth  starts speakup using a given synthesizer.
                     supported synths are acntpc, acntsa, apollo, audptr, bns,
                     decext, dectlk, dtlk, keypc, ltlk, spkout and txprt.
                     Also, soft is supported for software speech and dummy is
                     supported for testing.
speakup.quiet=1      sets the synthesizer not to speak until a key is pressed.
speakup_SYNTH.port=n sets the port for internal synthesizers.
speakup_SYNTH.ser=n  sets the serial port for external synthesizers.
