#!/usr/bin/env python3
"""
exp2.py

Creates a Mininet topology with two OVS switches (s1, s2) and three hosts (h1, h2, h3).
Runs pings before and after manually adding OpenFlow rules via ovs-ofctl.

Topology:
    h1 --- s1 --- s2 --- h3
            |
           h2

Run with sudo:
    sudo python3 exp2.py

Instructions:
1. The script runs initial pings (h1->h3, h2->h3) and writes to result2.txt.
2. Script pauses and prompts you to open ANOTHER TERMINAL and run:
       sudo ovs-ofctl show s1
       sudo ovs-ofctl dump-flows s1
   Then add flow rules:
       sudo ovs-ofctl add-flow s1 "priority=100,in_port=2,actions=drop"
       sudo ovs-ofctl add-flow s1 "priority=100,in_port=1,actions=output:3"
3. After you press Enter, the script runs the pings again and appends results.
"""
import os
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.log import setLogLevel
from mininet.cli import CLI


def run():
    """Create topology, run pings, pause for manual ovs-ofctl configuration, run pings again."""
    net = Mininet(switch=OVSKernelSwitch)

    # Create hosts (no need to specify IP; Mininet will assign automatically)
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')

    # Create OVS switches
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    # Links (order determines port numbering on switches)
    # s1 ports: 1=h1, 2=h2, 3=s2
    # s2 ports: 1=s1, 2=h3
    net.addLink(h1, s1)  # h1-eth0 <-> s1-eth1
    net.addLink(h2, s1)  # h2-eth0 <-> s1-eth2
    net.addLink(s1, s2)  # s1-eth3 <-> s2-eth1
    net.addLink(s2, h3)  # s2-eth2 <-> h3-eth0

    net.start()

    # Configure switches to behave as learning switches initially
    # This allows normal L2 forwarding for Phase 1
    print('\nConfiguring switches with normal L2 learning behavior...')
    s1.cmd('ovs-ofctl add-flow s1 action=normal')
    s2.cmd('ovs-ofctl add-flow s2 action=normal')

    result_path = os.path.join(os.getcwd(), 'result2.txt')

    # Phase 1: Run pings BEFORE adding custom flow rules
    print('\n' + '=' * 60)
    print('PHASE 1: Pings with normal L2 switching (BEFORE custom OpenFlow rules)')
    print('=' * 60)
    results = ['=' * 60 + '\n']
    results.append('PHASE 1: Pings with normal L2 switching (BEFORE custom OpenFlow rules)\n')
    results.append('=' * 60 + '\n\n')

    ping_tests = [
        (h1, h3.IP(), 'h1', 'h3'),
        (h2, h3.IP(), 'h2', 'h3'),
    ]

    for src_host, dst_ip, src_name, dst_name in ping_tests:
        cmd = 'ping -c 1 %s' % dst_ip
        print('Running on %s: %s' % (src_name, cmd))
        output = src_host.cmd(cmd)
        results.append('From %s to %s:\n' % (src_name, dst_name))
        results.append(output)
        results.append('\n' + ('-' * 60) + '\n')

    # Write phase 1 results
    with open(result_path, 'w') as f:
        f.writelines(results)

    print('\nPhase 1 results written to %s' % result_path)

    # Pause for manual configuration
    print('\n' + '=' * 60)
    print('MANUAL STEP: Open ANOTHER TERMINAL and run the following commands:')
    print('=' * 60)
    print('1. Check port state and flow table of s1:')
    print('   $ sudo ovs-ofctl show s1')
    print('   $ sudo ovs-ofctl dump-flows s1')
    print('')
    print('2. CLEAR existing flows and add NEW specific flow rules:')
    print('   $ sudo ovs-ofctl del-flows s1')
    print('')
    print('   - Drop all flows from port s1-eth2 (port 2):')
    print('     $ sudo ovs-ofctl add-flow s1 "priority=100,in_port=2,actions=drop"')
    print('')
    print('   - Forward all flows from port s1-eth1 (port 1) to s1-eth3 (port 3):')
    print('     $ sudo ovs-ofctl add-flow s1 "priority=100,in_port=1,actions=output:3"')
    print('')
    print('   - Forward return traffic from s1-eth3 (port 3) to s1-eth1 (port 1):')
    print('     $ sudo ovs-ofctl add-flow s1 "priority=100,in_port=3,actions=output:1"')
    print('')
    print('3. Verify the flows were added:')
    print('   $ sudo ovs-ofctl dump-flows s1')
    print('=' * 60)
    
    input('\nPress ENTER after you have added the flow rules...')

    # Phase 2: Run pings AFTER adding custom flow rules
    print('\n' + '=' * 60)
    print('PHASE 2: Pings AFTER adding custom OpenFlow rules')
    print('=' * 60)
    results2 = ['\n\n' + '=' * 60 + '\n']
    results2.append('PHASE 2: Pings AFTER adding custom OpenFlow rules\n')
    results2.append('=' * 60 + '\n')
    results2.append('\nOpenFlow commands used (run from another terminal):\n')
    results2.append('$ sudo ovs-ofctl show s1\n')
    results2.append('$ sudo ovs-ofctl dump-flows s1\n')
    results2.append('$ sudo ovs-ofctl del-flows s1\n')
    results2.append('$ sudo ovs-ofctl add-flow s1 "priority=100,in_port=2,actions=drop"\n')
    results2.append('$ sudo ovs-ofctl add-flow s1 "priority=100,in_port=1,actions=output:3"\n')
    results2.append('$ sudo ovs-ofctl add-flow s1 "priority=100,in_port=3,actions=output:1"\n')
    results2.append('\n' + ('-' * 60) + '\n\n')

    for src_host, dst_ip, src_name, dst_name in ping_tests:
        cmd = 'ping -c 1 %s' % dst_ip
        print('Running on %s: %s' % (src_name, cmd))
        output = src_host.cmd(cmd)
        results2.append('From %s to %s:\n' % (src_name, dst_name))
        results2.append(output)
        results2.append('\n' + ('-' * 60) + '\n')

    # Append phase 2 results
    with open(result_path, 'a') as f:
        f.writelines(results2)

    print('\nPhase 2 results appended to %s' % result_path)
    print('\n' + '=' * 60)
    print('All results written to %s' % result_path)
    print('=' * 60)

    # Optional: Start CLI for debugging
    # print('\nStarting Mininet CLI for debugging (type "exit" to quit)...')
    # CLI(net)

    # Stop the network
    net.stop()

    # Cleanup leftover state
    os.system('mn -c > /dev/null 2>&1 || true')


if __name__ == '__main__':
    setLogLevel('info')
    run()
