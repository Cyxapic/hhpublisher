# Forcked Joseph Ernest, 2016/11/12
# Daemon class

import sys, os, time, atexit, logging

from signal import signal, SIGTERM


file = lambda name, command: open(name, command)

logging.basicConfig(filename="daemon.log", level=logging.CRITICAL)


class Daemon:
    """
    A generic daemon class.
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile='_.pid', stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced 
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            logging.critical(f"fork #1 failed: {e.errno} ({e.strerror})\n")
            sys.exit(1)
        # decouple from parent environment
        os.setsid()
        os.umask(0)
        # do second fork
        try:
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            logging.critical(f"fork #2 failed: {e.errno} ({e.strerror})\n")
            sys.exit(1)
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        atexit.register(self.onstop)
        signal(SIGTERM, lambda signum, stack_frame: exit())
        
        # write pidfile
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def onstop(self):
        self.quit()
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
            logging.INFO('Daemon start')
        except IOError:
            pid = None
        if pid:
            message = """pidfile {self.pidfile} already exist.
                       Daemon already running?\n"""
            logging.critical(message.format(self.pidfile))
            sys.exit(1)
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            message = """pidfile {self.pidfile} already exist.
                       Daemon already running?\n"""
            logging.critical(message.format(self.pidfile))
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                logging.critical(f"Error: {err}")
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """

    def quit(self):
        """
        You should override this method when you subclass Daemon.
        It will be called before the process is stopped.
        """
