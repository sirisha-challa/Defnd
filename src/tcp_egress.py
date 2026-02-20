from __future__ import print_function
import os
import logging
import subprocess
import netfilterqueue as nfq
from packets import IPPacket, TCPPacket,to_tuple

class DefNdEgress(object):
    #Egress Monitoring Process
    def __init__(self, mp_queue,queue_num=2):
        #Create the Egress Process
        self.queue_num = queue_num
        self.mp_queue = mp_queue
        self._nfq_init = 'iptables -I OUTPUT -j NFQUEUE --queue-num %d'
        self._nfq_close = 'iptables -D OUTPUT -j NFQUEUE --queue-num %d'
    
    def run(self):
        setup = self._nfq_init % self.queue_num
        teardown = self._nfq_close % self.queue_num
        
        #setting up IPTables to recieve Egress Packets
        subprocess.run(setup, shell=True)
        print('Set up IPTables: ' + setup)
        # Create and run NFQ.
        nfqueue_instance = nfq.NetFilterQueue()
        nfqueue_instance.bind(self.queue_num, self.callback())
        try:
            nfqueue_instance.run()
        finally:
            subprocess.run(teardown, shell=True)
            print('\nTore down IPTables: ' + teardown + '\n')
            
    def callback(self, packet):
        """The callback called by IPTables for each egress packet."""
        # Parse packet
        ip_packet = IPPacket(packet.get_payload())
        tcp_packet = ip_packet.get_payload()
        logging.getLogger('defnd.egress').debug(unicode(ip_packet))

        # Accept non-TCP packets.
        if type(tcp_packet) is not TCPPacket:
            packet.accept()
            return

        # Send the packet to the connection tracker.
        tup = to_tuple(ip_packet, flip=True)
        self.mp_queue.put((tup, bool(tcp_packet.flag_syn),
                           bool(tcp_packet.flag_ack),
                           bool(tcp_packet.flag_fin)))
        packet.accept()