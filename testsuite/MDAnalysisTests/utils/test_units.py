# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDAnalysis --- http://www.mdanalysis.org
# Copyright (c) 2006-2017 The MDAnalysis Development Team and contributors
# (see the file AUTHORS for the full list of names)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# R. J. Gowers, M. Linke, J. Barnoud, T. J. E. Reddy, M. N. Melo, S. L. Seyler,
# D. L. Dotson, J. Domanski, S. Buchoux, I. M. Kenney, and O. Beckstein.
# MDAnalysis: A Python package for the rapid analysis of molecular dynamics
# simulations. In S. Benthall and S. Rostrup editors, Proceedings of the 15th
# Python in Science Conference, pages 102-109, Austin, TX, 2016. SciPy.
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#
from __future__ import unicode_literals, absolute_import
import six
import pytest

import numpy as np
from numpy.testing import assert_equal, assert_almost_equal, assert_raises

from MDAnalysis import units
from MDAnalysis.core import flags


class TestDefaultUnits(object):
    def test_length(self):
        assert_equal(flags['length_unit'], 'Angstrom',
                     u"The default length unit should be Angstrom (in core.flags)")

    def test_time(self):
        assert_equal(flags['time_unit'], 'ps',
                     u"The default length unit should be pico seconds (in core.flags)")

    def test_convert_gromacs_trajectories(self):
        assert_equal(flags['convert_lengths'], True,
                     u"The default behaviour should be to auto-convert Gromacs trajectories")



class TestUnitEncoding(object):
    def test_unicode(self):
        try:
            assert_equal(units.lengthUnit_factor[u"\u212b"], 1.0)
        except KeyError:
            raise AssertionError("Unicode symbol for Angtrom not supported")

    def test_unicode_encoding_with_symbol(self):
        try:
            assert_equal(units.lengthUnit_factor[u"Å"], 1.0)
        except KeyError:
            raise AssertionError("UTF-8-encoded symbol for Angtrom not supported")


class TestConstants(object):
    # CODATA 2010 (NIST): http://physics.nist.gov/cuu/Constants/
    # (accessed 2015-02-15)
    # Add a reference value to this dict for every entry in
    # units.constants
    constants_reference = {
        'N_Avogadro': 6.02214129e+23,          # mol**-1
        'elementary_charge': 1.602176565e-19,  # As
        'calorie': 4.184,                      # J
        }

    @pytest.mark.parametrize('name, value', constants_reference.items())
    def test_constant(self, name, value):
        self.check_physical_constant(name, value)

    @staticmethod
    def check_physical_constant(name, reference):
        assert_almost_equal(units.constants[name], reference)


class TestConversion(object):
    @staticmethod
    def _assert_almost_equal_convert(value, u1, u2, ref):
        val = units.convert(value, u1, u2)
        assert_almost_equal(val, ref,
                            err_msg="Conversion {0} --> {1} failed".format(u1, u2))

    nm = 12.34567
    A = nm * 10.
    @pytest.mark.parametrize('quantity, unit1, unit2, ref', (
        (nm, 'nm', 'A', A),
        (A, 'Angstrom', 'nm', nm),
    ))
    def test_length(self, quantity, unit1, unit2, ref):
        self._assert_almost_equal_convert(quantity, unit1, unit2, ref)

    @pytest.mark.parametrize('quantity, unit1, unit2, ref', (
        (1, 'ps', 'AKMA', 20.45482949774598),
        (1, 'AKMA', 'ps', 0.04888821),
    ))
    def test_time(self, quantity, unit1, unit2, ref):
        self._assert_almost_equal_convert(quantity, unit1, unit2, ref)

    @pytest.mark.parametrize('quantity, unit1, unit2, ref', (
        (1, 'kcal/mol', 'kJ/mol', 4.184),
        (1, 'kcal/mol', 'eV', 0.0433641),
    ))
    def test_energy(self, quantity, unit1, unit2, ref):
        self._assert_almost_equal_convert(quantity, unit1, unit2, ref)

    @pytest.mark.parametrize('quantity, unit1, unit2, ref', (
        (1, 'kJ/(mol*A)', 'J/m', 1.66053892103219e-11),
        (2.5, 'kJ/(mol*nm)', 'kJ/(mol*A)', 0.25),
        (1, 'kcal/(mol*Angstrom)', 'kJ/(mol*Angstrom)', 4.184),
    ))
    def test_force(self, quantity, unit1, unit2, ref):
        self._assert_almost_equal_convert(quantity, unit1, unit2, ref)

    @pytest.mark.parametrize('quantity, unit1, unit2, ref', (
        pytest.mark.raises((nm, 'Stone', 'nm', None), exception=ValueError),
        pytest.mark.raises((nm, 'nm', 'Stone', None), exception=ValueError),
    ))
    def test_unit_unknown(self, quantity, unit1, unit2, ref):
        val = units.convert(quantity, unit1, unit2)
        assert_almost_equal(val, ref,
                            err_msg="Conversion {0} --> {1} failed".format(unit1, unit2))

    def test_unit_unconvertable(self):
        nm = 12.34567
        A = nm * 10.
        assert_raises(ValueError, units.convert, A, 'A', 'ps')

