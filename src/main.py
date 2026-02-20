from __future__ import print_function
import multiprocessing as mp
import logging
import argparse

import config
import tcp_egress
import connection
from logger import initialize_logging, log_server


def run_defnd(conf, packet_queue, query_pipe, kwargs):
    # Utility function to run Defnd.  (target function for the Process)
    # Get logging information from the kwargs, so we can setup logging.
    logqueue = kwargs.pop('logqueue', mp.Queue())
    loglevel = kwargs.pop('loglevel', logging.INFO)
    initialize_logging(loglevel, logqueue)

    cfg = config.defndConfig(conf)
    the_wall = cfg.create_defnd(packet_queue, query_pipe)
    the_wall.erect(**kwargs)


def run_egress(packet_queue, loglevel, logqueue):
    """Utility function to run the egress function. (target of Process)

    Given the queue to report TCP connections, as well as logging variables,
    run the egress monitor.

    """
    initialize_logging(loglevel, logqueue)
    ct = tcp_egress.DefNdEgress(packet_queue)
    ct.run()


def main(conf, loglevel, filename, **kwargs):
    """Main function of the whole program.

    Runs a Defnd given a configuration file, a loglevel, and a filename.  This
    spawns three processes (log_process, egress_process, and defnd_process).
    It then runs the connection tracker on thes process (the "master process").

    """
    # Create multiprocessing queues for IPC.
    egress_queue = mp.Queue()
    ingress_queue = mp.Queue()
    log_queue = mp.Queue()
    query_defnd, query_connection = mp.Pipe()
    kwargs['loglevel'] = loglevel
    kwargs['logqueue'] = log_queue

    # Start logging for the connection tracker.
    initialize_logging(loglevel, log_queue)

    # Initialize the connection tracker with the IPC channels.
    ct = connection.DefndTracker(ingress_queue, egress_queue, query_connection)

    # Create and start log_process.
    log_process = mp.Process(target=log_server, args=(loglevel, log_queue,
                                                      filename))
    log_process.start()

    # Create and start egress_process.
    egress_process = mp.Process(target=run_egress, args=(egress_queue,
                                                         loglevel, log_queue))
    egress_process.start()

    # Create and start Defnd process.
    defnd_process = mp.Process(target=run_defnd, args=(conf, ingress_queue, query_defnd l, kwargs))
    defnd_process.start()

    # Run the connection tracker on the "master process."
    ct.run()


if __name__ == '__main__':
    # This is run if main.py is executed. Gets arguments from the command line.
    parser = argparse.ArgumentParser(description='Build a Defnd')
    parser.add_argument('config', help='JSON configuration file')
    parser.add_argument('-l', '--log-level', choices=['DEBUG', 'INFO',
                                                      'WARNING', 'ERROR',
                                                      'CRITICAL'],
                        help='set verbosity of logging', default='INFO')
    parser.add_argument('-f', '--log-file', help='set log file', default=None)
    args = parser.parse_args()
    main(args.config, args.log_level, args.log_file)
    