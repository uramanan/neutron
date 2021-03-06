# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Locaweb.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @author: Juliano Martinez, Locaweb.

import inspect
import os

import mox

from neutron.agent.linux import iptables_manager
from neutron.tests import base


IPTABLES_ARG = {'bn': iptables_manager.binary_name}

NAT_DUMP = ('# Generated by iptables_manager\n'
            '*nat\n'
            ':neutron-postrouting-bottom - [0:0]\n'
            ':%(bn)s-OUTPUT - [0:0]\n'
            ':%(bn)s-snat - [0:0]\n'
            ':%(bn)s-PREROUTING - [0:0]\n'
            ':%(bn)s-float-snat - [0:0]\n'
            ':%(bn)s-POSTROUTING - [0:0]\n'
            '[0:0] -A PREROUTING -j %(bn)s-PREROUTING\n'
            '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
            '[0:0] -A POSTROUTING -j %(bn)s-POSTROUTING\n'
            '[0:0] -A POSTROUTING -j neutron-postrouting-bottom\n'
            '[0:0] -A neutron-postrouting-bottom -j %(bn)s-snat\n'
            '[0:0] -A %(bn)s-snat -j '
            '%(bn)s-float-snat\n'
            'COMMIT\n'
            '# Completed by iptables_manager\n' % IPTABLES_ARG)

FILTER_DUMP = ('# Generated by iptables_manager\n'
               '*filter\n'
               ':neutron-filter-top - [0:0]\n'
               ':%(bn)s-FORWARD - [0:0]\n'
               ':%(bn)s-INPUT - [0:0]\n'
               ':%(bn)s-local - [0:0]\n'
               ':%(bn)s-OUTPUT - [0:0]\n'
               '[0:0] -A FORWARD -j neutron-filter-top\n'
               '[0:0] -A OUTPUT -j neutron-filter-top\n'
               '[0:0] -A neutron-filter-top -j %(bn)s-local\n'
               '[0:0] -A INPUT -j %(bn)s-INPUT\n'
               '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
               '[0:0] -A FORWARD -j %(bn)s-FORWARD\n'
               'COMMIT\n'
               '# Completed by iptables_manager\n' % IPTABLES_ARG)


class IptablesManagerStateFulTestCase(base.BaseTestCase):

    def setUp(self):
        super(IptablesManagerStateFulTestCase, self).setUp()
        self.mox = mox.Mox()
        self.root_helper = 'sudo'
        self.iptables = (iptables_manager.
                         IptablesManager(root_helper=self.root_helper))
        self.mox.StubOutWithMock(self.iptables, "execute")
        self.addCleanup(self.mox.UnsetStubs)

    def test_binary_name(self):
        self.assertEqual(iptables_manager.binary_name,
                         os.path.basename(inspect.stack()[-1][1])[:16])

    def test_get_chain_name(self):
        name = '0123456789' * 5
        # 28 chars is the maximum length of iptables chain name.
        self.assertEqual(iptables_manager.get_chain_name(name, wrap=False),
                         name[:28])
        # 11 chars is the maximum length of chain name of iptable_manager
        # if binary_name is prepended.
        self.assertEqual(iptables_manager.get_chain_name(name, wrap=True),
                         name[:11])

    def test_add_and_remove_chain_custom_binary_name(self):
        bn = ("abcdef" * 5)

        self.iptables = (iptables_manager.
                         IptablesManager(root_helper=self.root_helper,
                                         binary_name=bn))
        self.mox.StubOutWithMock(self.iptables, "execute")

        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        iptables_args = {'bn': bn[:16]}

        filter_dump = ('# Generated by iptables_manager\n'
                       '*filter\n'
                       ':neutron-filter-top - [0:0]\n'
                       ':%(bn)s-FORWARD - [0:0]\n'
                       ':%(bn)s-INPUT - [0:0]\n'
                       ':%(bn)s-local - [0:0]\n'
                       ':%(bn)s-filter - [0:0]\n'
                       ':%(bn)s-OUTPUT - [0:0]\n'
                       '[0:0] -A FORWARD -j neutron-filter-top\n'
                       '[0:0] -A OUTPUT -j neutron-filter-top\n'
                       '[0:0] -A neutron-filter-top -j %(bn)s-local\n'
                       '[0:0] -A INPUT -j %(bn)s-INPUT\n'
                       '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                       '[0:0] -A FORWARD -j %(bn)s-FORWARD\n'
                       'COMMIT\n'
                       '# Completed by iptables_manager\n' % iptables_args)

        filter_dump_mod = ('# Generated by iptables_manager\n'
                           '*filter\n'
                           ':neutron-filter-top - [0:0]\n'
                           ':%(bn)s-FORWARD - [0:0]\n'
                           ':%(bn)s-INPUT - [0:0]\n'
                           ':%(bn)s-local - [0:0]\n'
                           ':%(bn)s-filter - [0:0]\n'
                           ':%(bn)s-OUTPUT - [0:0]\n'
                           '[0:0] -A FORWARD -j neutron-filter-top\n'
                           '[0:0] -A OUTPUT -j neutron-filter-top\n'
                           '[0:0] -A neutron-filter-top -j %(bn)s-local\n'
                           '[0:0] -A INPUT -j %(bn)s-INPUT\n'
                           '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                           '[0:0] -A FORWARD -j %(bn)s-FORWARD\n'
                           'COMMIT\n'
                           '# Completed by iptables_manager\n'
                           % iptables_args)

        nat_dump = ('# Generated by iptables_manager\n'
                    '*nat\n'
                    ':neutron-postrouting-bottom - [0:0]\n'
                    ':%(bn)s-OUTPUT - [0:0]\n'
                    ':%(bn)s-snat - [0:0]\n'
                    ':%(bn)s-PREROUTING - [0:0]\n'
                    ':%(bn)s-float-snat - [0:0]\n'
                    ':%(bn)s-POSTROUTING - [0:0]\n'
                    '[0:0] -A PREROUTING -j %(bn)s-PREROUTING\n'
                    '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                    '[0:0] -A POSTROUTING -j %(bn)s-POSTROUTING\n'
                    '[0:0] -A POSTROUTING -j neutron-postrouting-bottom\n'
                    '[0:0] -A neutron-postrouting-bottom -j %(bn)s-snat\n'
                    '[0:0] -A %(bn)s-snat -j '
                    '%(bn)s-float-snat\n'
                    'COMMIT\n'
                    '# Completed by iptables_manager\n' % iptables_args)

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=nat_dump + filter_dump_mod,
                              root_helper=self.root_helper).AndReturn(None)

        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=nat_dump + filter_dump,
                              root_helper=self.root_helper).AndReturn(None)

        self.mox.ReplayAll()

        self.iptables.ipv4['filter'].add_chain('filter')
        self.iptables.apply()

        self.iptables.ipv4['filter'].empty_chain('filter')
        self.iptables.apply()

        self.mox.VerifyAll()

    def test_empty_chain_custom_binary_name(self):
        bn = ("abcdef" * 5)[:16]

        self.iptables = (iptables_manager.
                         IptablesManager(root_helper=self.root_helper,
                                         binary_name=bn))
        self.mox.StubOutWithMock(self.iptables, "execute")

        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        iptables_args = {'bn': bn}

        filter_dump = ('# Generated by iptables_manager\n'
                       '*filter\n'
                       ':neutron-filter-top - [0:0]\n'
                       ':%(bn)s-FORWARD - [0:0]\n'
                       ':%(bn)s-INPUT - [0:0]\n'
                       ':%(bn)s-local - [0:0]\n'
                       ':%(bn)s-OUTPUT - [0:0]\n'
                       '[0:0] -A FORWARD -j neutron-filter-top\n'
                       '[0:0] -A OUTPUT -j neutron-filter-top\n'
                       '[0:0] -A neutron-filter-top -j %(bn)s-local\n'
                       '[0:0] -A INPUT -j %(bn)s-INPUT\n'
                       '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                       '[0:0] -A FORWARD -j %(bn)s-FORWARD\n'
                       'COMMIT\n'
                       '# Completed by iptables_manager\n' % iptables_args)

        filter_dump_mod = ('# Generated by iptables_manager\n'
                           '*filter\n'
                           ':neutron-filter-top - [0:0]\n'
                           ':%(bn)s-FORWARD - [0:0]\n'
                           ':%(bn)s-INPUT - [0:0]\n'
                           ':%(bn)s-local - [0:0]\n'
                           ':%(bn)s-filter - [0:0]\n'
                           ':%(bn)s-OUTPUT - [0:0]\n'
                           '[0:0] -A FORWARD -j neutron-filter-top\n'
                           '[0:0] -A OUTPUT -j neutron-filter-top\n'
                           '[0:0] -A neutron-filter-top -j %(bn)s-local\n'
                           '[0:0] -A INPUT -j %(bn)s-INPUT\n'
                           '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                           '[0:0] -A FORWARD -j %(bn)s-FORWARD\n'
                           '[0:0] -A %(bn)s-filter -s 0/0 -d 192.168.0.2\n'
                           'COMMIT\n'
                           '# Completed by iptables_manager\n'
                           % iptables_args)

        nat_dump = ('# Generated by iptables_manager\n'
                    '*nat\n'
                    ':neutron-postrouting-bottom - [0:0]\n'
                    ':%(bn)s-OUTPUT - [0:0]\n'
                    ':%(bn)s-snat - [0:0]\n'
                    ':%(bn)s-PREROUTING - [0:0]\n'
                    ':%(bn)s-float-snat - [0:0]\n'
                    ':%(bn)s-POSTROUTING - [0:0]\n'
                    '[0:0] -A PREROUTING -j %(bn)s-PREROUTING\n'
                    '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                    '[0:0] -A POSTROUTING -j %(bn)s-POSTROUTING\n'
                    '[0:0] -A POSTROUTING -j neutron-postrouting-bottom\n'
                    '[0:0] -A neutron-postrouting-bottom -j %(bn)s-snat\n'
                    '[0:0] -A %(bn)s-snat -j '
                    '%(bn)s-float-snat\n'
                    'COMMIT\n'
                    '# Completed by iptables_manager\n' % iptables_args)

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=nat_dump + filter_dump_mod,
                              root_helper=self.root_helper).AndReturn(None)

        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=nat_dump + filter_dump,
                              root_helper=self.root_helper).AndReturn(None)

        self.mox.ReplayAll()

        self.iptables.ipv4['filter'].add_chain('filter')
        self.iptables.ipv4['filter'].add_rule('filter',
                                              '-s 0/0 -d 192.168.0.2')
        self.iptables.apply()

        self.iptables.ipv4['filter'].remove_chain('filter')
        self.iptables.apply()

        self.mox.VerifyAll()

    def test_add_and_remove_chain(self):
        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        filter_dump_mod = ('# Generated by iptables_manager\n'
                           '*filter\n'
                           ':neutron-filter-top - [0:0]\n'
                           ':%(bn)s-FORWARD - [0:0]\n'
                           ':%(bn)s-INPUT - [0:0]\n'
                           ':%(bn)s-local - [0:0]\n'
                           ':%(bn)s-filter - [0:0]\n'
                           ':%(bn)s-OUTPUT - [0:0]\n'
                           '[0:0] -A FORWARD -j neutron-filter-top\n'
                           '[0:0] -A OUTPUT -j neutron-filter-top\n'
                           '[0:0] -A neutron-filter-top -j %(bn)s-local\n'
                           '[0:0] -A INPUT -j %(bn)s-INPUT\n'
                           '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                           '[0:0] -A FORWARD -j %(bn)s-FORWARD\n'
                           'COMMIT\n'
                           '# Completed by iptables_manager\n'
                           % IPTABLES_ARG)

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=NAT_DUMP + filter_dump_mod,
                              root_helper=self.root_helper).AndReturn(None)

        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=NAT_DUMP + FILTER_DUMP,
                              root_helper=self.root_helper).AndReturn(None)

        self.mox.ReplayAll()

        self.iptables.ipv4['filter'].add_chain('filter')
        self.iptables.apply()

        self.iptables.ipv4['filter'].remove_chain('filter')
        self.iptables.apply()

        self.mox.VerifyAll()

    def test_add_filter_rule(self):
        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        filter_dump_mod = ('# Generated by iptables_manager\n'
                           '*filter\n'
                           ':neutron-filter-top - [0:0]\n'
                           ':%(bn)s-FORWARD - [0:0]\n'
                           ':%(bn)s-INPUT - [0:0]\n'
                           ':%(bn)s-local - [0:0]\n'
                           ':%(bn)s-filter - [0:0]\n'
                           ':%(bn)s-OUTPUT - [0:0]\n'
                           '[0:0] -A FORWARD -j neutron-filter-top\n'
                           '[0:0] -A OUTPUT -j neutron-filter-top\n'
                           '[0:0] -A neutron-filter-top -j %(bn)s-local\n'
                           '[0:0] -A INPUT -j %(bn)s-INPUT\n'
                           '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                           '[0:0] -A FORWARD -j %(bn)s-FORWARD\n'
                           '[0:0] -A %(bn)s-filter -j DROP\n'
                           '[0:0] -A %(bn)s-INPUT -s 0/0 -d 192.168.0.2 -j '
                           '%(bn)s-filter\n'
                           'COMMIT\n'
                           '# Completed by iptables_manager\n'
                           % IPTABLES_ARG)

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=NAT_DUMP + filter_dump_mod,
                              root_helper=self.root_helper).AndReturn(None)

        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=NAT_DUMP + FILTER_DUMP,
                              root_helper=self.root_helper
                              ).AndReturn(None)

        self.mox.ReplayAll()

        self.iptables.ipv4['filter'].add_chain('filter')
        self.iptables.ipv4['filter'].add_rule('filter', '-j DROP')
        self.iptables.ipv4['filter'].add_rule('INPUT',
                                              '-s 0/0 -d 192.168.0.2 -j'
                                              ' %(bn)s-filter' % IPTABLES_ARG)
        self.iptables.apply()

        self.iptables.ipv4['filter'].remove_rule('filter', '-j DROP')
        self.iptables.ipv4['filter'].remove_rule('INPUT',
                                                 '-s 0/0 -d 192.168.0.2 -j'
                                                 ' %(bn)s-filter'
                                                 % IPTABLES_ARG)
        self.iptables.ipv4['filter'].remove_chain('filter')

        self.iptables.apply()
        self.mox.VerifyAll()

    def test_add_nat_rule(self):
        nat_dump = ('# Generated by iptables_manager\n'
                    '*nat\n'
                    ':neutron-postrouting-bottom - [0:0]\n'
                    ':%(bn)s-float-snat - [0:0]\n'
                    ':%(bn)s-POSTROUTING - [0:0]\n'
                    ':%(bn)s-PREROUTING - [0:0]\n'
                    ':%(bn)s-OUTPUT - [0:0]\n'
                    ':%(bn)s-snat - [0:0]\n'
                    '[0:0] -A PREROUTING -j %(bn)s-PREROUTING\n'
                    '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                    '[0:0] -A POSTROUTING -j %(bn)s-POSTROUTING\n'
                    '[0:0] -A POSTROUTING -j neutron-postrouting-bottom\n'
                    '[0:0] -A neutron-postrouting-bottom -j %(bn)s-snat\n'
                    '[0:0] -A %(bn)s-snat -j %(bn)s-float-snat\n'
                    'COMMIT\n'
                    '# Completed by iptables_manager\n'
                    % IPTABLES_ARG)

        nat_dump_mod = ('# Generated by iptables_manager\n'
                        '*nat\n'
                        ':neutron-postrouting-bottom - [0:0]\n'
                        ':%(bn)s-float-snat - [0:0]\n'
                        ':%(bn)s-POSTROUTING - [0:0]\n'
                        ':%(bn)s-PREROUTING - [0:0]\n'
                        ':%(bn)s-nat - [0:0]\n'
                        ':%(bn)s-OUTPUT - [0:0]\n'
                        ':%(bn)s-snat - [0:0]\n'
                        '[0:0] -A PREROUTING -j %(bn)s-PREROUTING\n'
                        '[0:0] -A OUTPUT -j %(bn)s-OUTPUT\n'
                        '[0:0] -A POSTROUTING -j %(bn)s-POSTROUTING\n'
                        '[0:0] -A POSTROUTING -j neutron-postrouting-bottom\n'
                        '[0:0] -A neutron-postrouting-bottom -j %(bn)s-snat\n'
                        '[0:0] -A %(bn)s-snat -j %(bn)s-float-snat\n'
                        '[0:0] -A %(bn)s-PREROUTING -d 192.168.0.3 -j '
                        '%(bn)s-nat\n'
                        '[0:0] -A %(bn)s-nat -p tcp --dport 8080 -j '
                        'REDIRECT --to-port 80\n'
                        'COMMIT\n'
                        '# Completed by iptables_manager\n'
                        % IPTABLES_ARG)

        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=nat_dump_mod + FILTER_DUMP,
                              root_helper=self.root_helper).AndReturn(None)

        self.iptables.execute(['iptables-save', '-c'],
                              root_helper=self.root_helper).AndReturn('')

        self.iptables.execute(['iptables-restore', '-c'],
                              process_input=nat_dump + FILTER_DUMP,
                              root_helper=self.root_helper).AndReturn(None)

        self.mox.ReplayAll()
        self.iptables.ipv4['nat'].add_chain('nat')
        self.iptables.ipv4['nat'].add_rule('PREROUTING',
                                           '-d 192.168.0.3 -j '
                                           '%(bn)s-nat' % IPTABLES_ARG)
        self.iptables.ipv4['nat'].add_rule('nat',
                                           '-p tcp --dport 8080' +
                                           ' -j REDIRECT --to-port 80')

        self.iptables.apply()

        self.iptables.ipv4['nat'].remove_rule('nat',
                                              '-p tcp --dport 8080 -j'
                                              ' REDIRECT --to-port 80')
        self.iptables.ipv4['nat'].remove_rule('PREROUTING',
                                              '-d 192.168.0.3 -j '
                                              '%(bn)s-nat' % IPTABLES_ARG)
        self.iptables.ipv4['nat'].remove_chain('nat')

        self.iptables.apply()
        self.mox.VerifyAll()

    def test_add_rule_to_a_nonexistent_chain(self):
        self.assertRaises(LookupError, self.iptables.ipv4['filter'].add_rule,
                          'nonexistent', '-j DROP')

    def test_remove_nonexistent_chain(self):
        self.mox.StubOutWithMock(iptables_manager, "LOG")
        iptables_manager.LOG.warn(('Attempted to remove chain %s which does '
                                   'not exist'), 'nonexistent')
        self.mox.ReplayAll()
        self.iptables.ipv4['filter'].remove_chain('nonexistent')
        self.mox.VerifyAll()

    def test_remove_nonexistent_rule(self):
        self.mox.StubOutWithMock(iptables_manager, "LOG")
        iptables_manager.LOG.warn('Tried to remove rule that was not there: '
                                  '%(chain)r %(rule)r %(wrap)r %(top)r',
                                  {'wrap': True, 'top': False,
                                   'rule': '-j DROP',
                                   'chain': 'nonexistent'})
        self.mox.ReplayAll()
        self.iptables.ipv4['filter'].remove_rule('nonexistent', '-j DROP')
        self.mox.VerifyAll()

    def test_get_traffic_counters_chain_notexists(self):
        iptables_dump = (
            'Chain OUTPUT (policy ACCEPT 400 packets, 65901 bytes)\n'
            '    pkts      bytes target     prot opt in     out     source'
            '               destination         \n'
            '     400   65901 chain1     all  --  *      *       0.0.0.0/0'
            '            0.0.0.0/0           \n'
            '     400   65901 chain2     all  --  *      *       0.0.0.0/0'
            '            0.0.0.0/0           \n')

        self.iptables.execute(['iptables', '-t', 'filter', '-L', 'OUTPUT',
                               '-n', '-v', '-x'],
                              root_helper=self.root_helper
                              ).AndReturn(iptables_dump)
        self.iptables.execute(['iptables', '-t', 'nat', '-L', 'OUTPUT', '-n',
                               '-v', '-x'],
                              root_helper=self.root_helper
                              ).AndReturn('')
        self.iptables.execute(['ip6tables', '-t', 'filter', '-L', 'OUTPUT',
                               '-n', '-v', '-x'],
                              root_helper=self.root_helper
                              ).AndReturn(iptables_dump)

        self.mox.ReplayAll()
        acc = self.iptables.get_traffic_counters('chain1')
        self.assertIsNone(acc)

    def test_get_traffic_counters(self):
        iptables_dump = (
            'Chain OUTPUT (policy ACCEPT 400 packets, 65901 bytes)\n'
            '    pkts      bytes target     prot opt in     out     source'
            '               destination         \n'
            '     400   65901 chain1     all  --  *      *       0.0.0.0/0'
            '            0.0.0.0/0           \n'
            '     400   65901 chain2     all  --  *      *       0.0.0.0/0'
            '            0.0.0.0/0           \n')

        self.iptables.execute(['iptables', '-t', 'filter', '-L', 'OUTPUT',
                               '-n', '-v', '-x'],
                              root_helper=self.root_helper
                              ).AndReturn(iptables_dump)
        self.iptables.execute(['iptables', '-t', 'nat', '-L', 'OUTPUT', '-n',
                               '-v', '-x'],
                              root_helper=self.root_helper
                              ).AndReturn('')

        self.iptables.execute(['ip6tables', '-t', 'filter', '-L', 'OUTPUT',
                               '-n', '-v', '-x'],
                              root_helper=self.root_helper
                              ).AndReturn(iptables_dump)

        self.mox.ReplayAll()
        acc = self.iptables.get_traffic_counters('OUTPUT')
        self.assertEquals(acc['pkts'], 1600)
        self.assertEquals(acc['bytes'], 263604)

        self.mox.VerifyAll()

    def test_get_traffic_counters_with_zero(self):
        iptables_dump = (
            'Chain OUTPUT (policy ACCEPT 400 packets, 65901 bytes)\n'
            '    pkts      bytes target     prot opt in     out     source'
            '               destination         \n'
            '     400   65901 chain1     all  --  *      *       0.0.0.0/0'
            '            0.0.0.0/0           \n'
            '     400   65901 chain2     all  --  *      *       0.0.0.0/0'
            '            0.0.0.0/0           \n')

        self.iptables.execute(['iptables', '-t', 'filter', '-L', 'OUTPUT',
                               '-n', '-v', '-x', '-Z'],
                              root_helper=self.root_helper
                              ).AndReturn(iptables_dump)
        self.iptables.execute(['iptables', '-t', 'nat', '-L', 'OUTPUT', '-n',
                               '-v', '-x', '-Z'],
                              root_helper=self.root_helper
                              ).AndReturn('')

        self.iptables.execute(['ip6tables', '-t', 'filter', '-L', 'OUTPUT',
                               '-n', '-v', '-x', '-Z'],
                              root_helper=self.root_helper
                              ).AndReturn(iptables_dump)

        self.mox.ReplayAll()
        acc = self.iptables.get_traffic_counters('OUTPUT', zero=True)
        self.assertEquals(acc['pkts'], 1600)
        self.assertEquals(acc['bytes'], 263604)

        self.mox.VerifyAll()


class IptablesManagerStateLessTestCase(base.BaseTestCase):

    def setUp(self):
        super(IptablesManagerStateLessTestCase, self).setUp()
        self.iptables = (iptables_manager.IptablesManager(state_less=True))

    def test_nat_not_found(self):
        self.assertFalse('nat' in self.iptables.ipv4)
