
try:
    import pyblish_magenta
    pyblish_magenta.setup()

except ImportError as e:
    print "pyblish_magenta: Could not load kit: %s" % e
