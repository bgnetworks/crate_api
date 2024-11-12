
from crate_api import Environment
import pathlib

from scapy.all import load_layer, load_contrib, conf
import can

load_layer("can")
load_contrib('automotive.uds')
load_contrib('automotive.ecu')
conf.contribs["CANSocket"] = {"use-python-can": True}
conf.contribs["ISOTP"] = {"use-can-isotp-kernel-module": False}
conf.verb=3

port = 2
tx_id=0x14DAF100
rx_id=0x14DA00F1

env = Environment('environments/crate-x6-v1_windows.yaml')
canport = env.get_target(str(port)).get_driver('CANDriver')
s = CANSocket(interface=canport.interface, channel=canport.ifname,
              fd=True,
              timing=can.BitTimingFd.from_bitrate_and_segments(
                f_clock=80e6,
                nom_bitrate=500000,
                nom_tseg1=12,
                nom_tseg2=3,
                nom_sjw=1,
                data_bitrate=2000000,
                data_tseg1=7,
                data_tseg2=2,
                data_sjw=1,
                strict=True))

example_responses = \
    [EcuResponse(EcuState(session=1, security_level=0),
                 responses=UDS() / UDS_DSCPR(diagnosticSessionType='extendedDiagnosticSession')),
     EcuResponse(EcuState(session=3, security_level=0),
                 responses=UDS() / UDS_DSCPR(diagnosticSessionType=1)),
     EcuResponse(EcuState(session=2, security_level=0),
                 responses=UDS() / UDS_RDBIPR(dataIdentifier=2) / Raw(b"deadbeef1")),
     EcuResponse(EcuState(session=range(3,5), security_level=0), 
                 responses=UDS() / UDS_RDBIPR(dataIdentifier=3) / Raw(b"deadbeef2")),
     EcuResponse(EcuState(session=[5,6,7], security_level=0), 
                 responses=UDS() / UDS_RDBIPR(dataIdentifier=5) / Raw(b"deadbeef3")),
     EcuResponse(EcuState(session=lambda x: 8 < x <= 10, security_level=0), 
                 responses=UDS() / UDS_RDBIPR(dataIdentifier=9) / Raw(b"deadbeef4"))]



def print_reply(req, reply):
    # type: (Packet, _T) -> None
    print("%s ==> %s" % (repr(req),
        [repr(res) for res in reply]))

try:
    with s, ISOTPSocket(s, tx_id=tx_id, rx_id=rx_id, basecls=UDS) as ecu:
        answering_machine = EcuAnsweringMachine(supported_responses=example_responses, 
                                                initial_ecu_state=EcuState(session=1, security_level=0),
                                                main_socket=ecu, 
                                                basecls=UDS)
        #answering_machine.print_reply = print_reply
        answering_machine(**{'timeout': None, 'stop_filter': None, 'verbose': True})
except KeyboardInterrupt:
    pass
