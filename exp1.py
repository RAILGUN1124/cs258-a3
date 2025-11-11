#!/usr/bin/env python3
"""
exp1.py

Creates the requested Mininet topology with two routers (r1, r2) and three hosts (h1, h2, h3).
Configures IP addresses and static routes, runs pings, and writes the ping outputs to result1.txt.

Run with sudo (Mininet requires root):
    sudo python3 exp1.py

Note: This script configures routers as simple Linux hosts with IP forwarding enabled.
"""
import os
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel


def run():
    """Create topology, configure interfaces/routes, run pings, write results."""
    net = Mininet()

    # Create hosts
    h1 = net.addHost('h1', ip='10.0.0.1/24')   # will use gateway 10.0.0.3 (r1)
    h2 = net.addHost('h2', ip='10.0.3.2/24')   # will use gateway 10.0.3.4 (r1)
    h3 = net.addHost('h3', ip='10.0.2.2/24')   # will use gateway 10.0.2.1 (r2)

    # Create router nodes (Linux hosts with ip_forward enabled)
    r1 = net.addHost('r1', cls=Node, ip='10.0.0.3/24')
    r2 = net.addHost('r2', cls=Node, ip='10.0.1.2/24')

    # Links (the order determines the ethN numbering on nodes)
    # 1) h1 <-> r1
    net.addLink(h1, r1)
    # 2) r1 <-> r2
    net.addLink(r1, r2)
    # 3) r2 <-> h3
    net.addLink(r2, h3)
    # 4) r1 <-> h2 (vertical link in the diagram)
    net.addLink(r1, h2)

    net.start()

    # Configure IPs on router interfaces explicitly to match the diagram
    # Link order results in the following eth numbering for routers:
    # - r1: r1-eth0 (to h1), r1-eth1 (to r2), r1-eth2 (to h2)
    # - r2: r2-eth0 (to r1), r2-eth1 (to h3)
    r1.cmd('ifconfig r1-eth0 10.0.0.3/24')
    r1.cmd('ifconfig r1-eth1 10.0.1.1/24')
    r1.cmd('ifconfig r1-eth2 10.0.3.4/24')

    r2.cmd('ifconfig r2-eth0 10.0.1.2/24')
    r2.cmd('ifconfig r2-eth1 10.0.2.1/24')

    # Enable IP forwarding on routers
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Set default routes on hosts to point to their router/gateway
    h1.cmd('ip route add default via 10.0.0.3')
    h2.cmd('ip route add default via 10.0.3.4')
    h3.cmd('ip route add default via 10.0.2.1')

    # Static routes on routers so they know how to reach remote subnets
    # r1 knows how to reach 10.0.2.0/24 via r2
    r1.cmd('ip route add 10.0.2.0/24 via 10.0.1.2')
    # r2 needs to reach 10.0.0.0/24 (h1) and 10.0.3.0/24 (h2) via r1
    r2.cmd('ip route add 10.0.0.0/24 via 10.0.1.1')
    r2.cmd('ip route add 10.0.3.0/24 via 10.0.1.1')

    # Commands to run and capture
    ping_tests = [
        (h1, '10.0.2.2'),  # from h1 to h3
        (h2, '10.0.2.2'),  # from h2 to h3
        (h3, '10.0.0.1'),  # from h3 to h1
        (h3, '10.0.3.2'),  # from h3 to h2
    ]

    results = []
    for host, dst in ping_tests:
        src = host.name
        cmd = 'ping -c 1 %s' % dst
        print('Running on %s: %s' % (src, cmd))
        output = host.cmd(cmd)
        results.append('From %s to %s:\n' % (src, dst))
        results.append(output)
        results.append('\n' + ('-' * 60) + '\n')

    # Write results to result1.txt in the current working directory
    result_path = os.path.join(os.getcwd(), 'result1.txt')
    with open(result_path, 'w') as f:
        f.writelines(results)

    print('\nPing results written to %s' % result_path)

    # Stop the network and clean up
    net.stop()

    # Optional: cleanup leftover state (requires sudo)
    os.system('mn -c > /dev/null 2>&1 || true')


if __name__ == '__main__':
    setLogLevel('info')
    run()
