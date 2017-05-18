"""
Integration tests for stem.descriptor.networkstatus.
"""

import os
import unittest

import stem
import stem.descriptor
import stem.descriptor.remote
import stem.version
import test.require
import test.runner

from test.util import register_new_capability


class TestNetworkStatus(unittest.TestCase):
  @test.require.only_run_once
  @test.require.online
  @test.require.cryptography
  def test_signature_validation(self):
    """
    The full consensus is pretty sizable so rather than storing a copy of it
    using the remote module. Chekcing the signature on the current consensus.
    """

    stem.descriptor.remote.get_consensus(document_handler = stem.descriptor.DocumentHandler.DOCUMENT, validate = True).run()

  @test.require.only_run_once
  def test_cached_consensus(self):
    """
    Parses the cached-consensus file in our data directory.
    """

    consensus_path = test.runner.get_runner().get_test_dir('cached-consensus')

    if not os.path.exists(consensus_path):
      self.skipTest('(no cached-consensus)')
      return
    elif stem.util.system.is_windows():
      # Unable to check memory usage on windows, so can't prevent hanging the
      # system if things go bad.

      self.skipTest('(unavailable on windows)')
      return

    count, reported_flags = 0, []

    with open(consensus_path, 'rb') as descriptor_file:
      for router in stem.descriptor.parse_file(descriptor_file, 'network-status-consensus-3 1.0', validate = True):
        count += 1

        for flag in router.flags:
          if flag not in stem.Flag and flag not in reported_flags:
            register_new_capability('Flag', flag)
            reported_flags.append(flag)

        for line in router.get_unrecognized_lines():
          register_new_capability('Consensus Line', line, suppression_token = line.split()[0])

    # Sanity test that there's at least a hundred relays. If that's not the
    # case then this probably isn't a real, complete tor consensus.

    self.assertTrue(count > 100)

  @test.require.only_run_once
  def test_cached_microdesc_consensus(self):
    """
    Parses the cached-microdesc-consensus file in our data directory.
    """

    consensus_path = test.runner.get_runner().get_test_dir('cached-microdesc-consensus')

    if not os.path.exists(consensus_path):
      self.skipTest('(no cached-microdesc-consensus)')
      return
    elif stem.util.system.is_windows():
      self.skipTest('(unavailable on windows)')
      return

    count, reported_flags = 0, []

    with open(consensus_path, 'rb') as descriptor_file:
      for router in stem.descriptor.parse_file(descriptor_file, 'network-status-microdesc-consensus-3 1.0', validate = True):
        count += 1

        for flag in router.flags:
          if flag not in stem.Flag:
            register_new_capability('Flag (microdescriptor)', flag)
            reported_flags.append(flag)

        for line in router.get_unrecognized_lines():
          register_new_capability('Microdescriptor Consensus Line', line, suppression_token = line.split()[0])

    self.assertTrue(count > 100)
