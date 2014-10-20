#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic integration tests for the AxiSEM database Python interface.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2014
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
from __future__ import absolute_import

import inspect
import numpy as np
import os

from ..instaseisdb import InstaSeisDB
from ..source import Source, Receiver


# Most generic way to get the data folder path.
DATA = os.path.join(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))), "data")


def test_fwd_vs_bwd():
    """
    Test fwd against bwd mode
    """
    instaseis_fwd = InstaSeisDB(os.path.join(DATA, "100s_db_fwd"),
                                reciprocal=False)
    instaseis_bwd = InstaSeisDB(os.path.join(DATA, "100s_db_bwd"))

    source_fwd = Source(latitude=4., longitude=3.0, depth_in_m=None,
                        m_rr=4.71e+17, m_tt=3.81e+17, m_pp=-4.74e+17,
                        m_rt=3.99e+17, m_rp=-8.05e+17, m_tp=-1.23e+17)
    source_bwd = Source(latitude=4., longitude=3.0, depth_in_m=0,
                        m_rr=4.71e+17, m_tt=3.81e+17, m_pp=-4.74e+17,
                        m_rt=3.99e+17, m_rp=-8.05e+17, m_tp=-1.23e+17)

    receiver_fwd = Receiver(latitude=10., longitude=20., depth_in_m=0)
    receiver_bwd = Receiver(latitude=10., longitude=20., depth_in_m=None)

    st_fwd = instaseis_fwd.get_seismograms(
        source=source_fwd, receiver=receiver_fwd, components=('Z', 'N', 'E', 'R', 'T'))
    st_bwd = instaseis_bwd.get_seismograms(
        source=source_bwd, receiver=receiver_bwd, components=('Z', 'N', 'E', 'R', 'T'))

    st_bwd.filter('lowpass', freq=0.002)
    st_fwd.filter('lowpass', freq=0.002)

    np.testing.assert_allclose(st_fwd.select(component="Z")[0].data,
                               st_bwd.select(component="Z")[0].data,
                               rtol=1E-3, atol=1E-10)

    np.testing.assert_allclose(st_fwd.select(component="N")[0].data,
                               st_bwd.select(component="N")[0].data,
                               rtol=1E-3, atol=1E-10)

    np.testing.assert_allclose(st_fwd.select(component="E")[0].data,
                               st_bwd.select(component="E")[0].data,
                               rtol=1E-3, atol=1E-10)

    np.testing.assert_allclose(st_fwd.select(component="R")[0].data,
                               st_bwd.select(component="R")[0].data,
                               rtol=1E-3, atol=1E-10)

    np.testing.assert_allclose(st_fwd.select(component="T")[0].data,
                               st_bwd.select(component="T")[0].data,
                               rtol=1E-3, atol=1E-10)


def test_fwd_vs_bwd_axial():
    """
    Test fwd against bwd mode, axial element. Differences are a bit larger then
    in non axial case, presumably because the close source, which is not
    exactly a point source in the SEM representation.
    """
    instaseis_fwd = InstaSeisDB(os.path.join(DATA, "100s_db_fwd_deep"),
                                reciprocal=False)
    instaseis_bwd = InstaSeisDB(os.path.join(DATA, "100s_db_bwd"))

    source_fwd = Source(latitude=0., longitude=0., depth_in_m=None,
                        m_rr=4.71e+17, m_tt=3.81e+17, m_pp=-4.74e+17,
                        m_rt=3.99e+17, m_rp=-8.05e+17, m_tp=-1.23e+17)
    source_bwd = Source(latitude=0., longitude=0., depth_in_m=310000,
                        m_rr=4.71e+17, m_tt=3.81e+17, m_pp=-4.74e+17,
                        m_rt=3.99e+17, m_rp=-8.05e+17, m_tp=-1.23e+17)

    receiver_fwd = Receiver(latitude=0., longitude=0.1, depth_in_m=0)
    receiver_bwd = Receiver(latitude=0., longitude=0.1, depth_in_m=None)

    st_fwd = instaseis_fwd.get_seismograms(
        source=source_fwd, receiver=receiver_fwd, components=('Z', 'N', 'E', 'R', 'T'))
    st_bwd = instaseis_bwd.get_seismograms(
        source=source_bwd, receiver=receiver_bwd, components=('Z', 'N', 'E', 'R', 'T'))

    st_bwd.filter('lowpass', freq=0.01)
    st_fwd.filter('lowpass', freq=0.01)
    st_bwd.filter('lowpass', freq=0.01)
    st_fwd.filter('lowpass', freq=0.01)
    st_bwd.differentiate()
    st_fwd.differentiate()

    np.testing.assert_allclose(st_fwd.select(component="Z")[0].data,
                               st_bwd.select(component="Z")[0].data,
                               rtol=1E-2, atol=5E-9)

    np.testing.assert_allclose(st_fwd.select(component="N")[0].data,
                               st_bwd.select(component="N")[0].data,
                               rtol=1E-2, atol=5E-9)

    np.testing.assert_allclose(st_fwd.select(component="E")[0].data,
                               st_bwd.select(component="E")[0].data,
                               rtol=1E-2, atol=6E-9)

    np.testing.assert_allclose(st_fwd.select(component="R")[0].data,
                               st_bwd.select(component="R")[0].data,
                               rtol=1E-2, atol=6E-9)

    np.testing.assert_allclose(st_fwd.select(component="T")[0].data,
                               st_bwd.select(component="T")[0].data,
                               rtol=1E-2, atol=5E-9)


def test_incremental_bwd():
    """
    incremental tests of bwd mode
    """
    instaseis_bwd = InstaSeisDB(os.path.join(DATA, "100s_db_bwd/"))

    receiver = Receiver(latitude=42.6390, longitude=74.4940)
    source = Source(
        latitude=89.91, longitude=0.0, depth_in_m=12000,
        m_rr=4.710000e+24 / 1E7,
        m_tt=3.810000e+22 / 1E7,
        m_pp=-4.740000e+24 / 1E7,
        m_rt=3.990000e+23 / 1E7,
        m_rp=-8.050000e+23 / 1E7,
        m_tp=-1.230000e+24 / 1E7)

    st_bwd = instaseis_bwd.get_seismograms(
        source=source, receiver=receiver, components=('Z', 'N', 'E', 'R', 'T'))

    z_data = np.array([
        -3.81669935e-39, -3.35652626e-37,  3.57062429e-35,  5.06588589e-34,
        1.94696809e-32,  1.89072798e-31,  2.41251539e-28, -5.05942607e-27,
        -2.86760440e-25, -5.18421933e-24,  1.38887860e-22, -1.05029638e-21,
        9.59017864e-21, -5.51049004e-20,  3.27795998e-19,  3.66801598e-19,
        -3.62193631e-16, -4.75828883e-13, -9.34584127e-11, -3.92586924e-09,
        -3.48405306e-08, -7.17413831e-08, -4.98682132e-08, -3.48290709e-08,
        -3.06076206e-08, -5.12560088e-08, -4.93613106e-08,  9.23245204e-09,
        6.96333155e-08,  1.14468643e-07,  1.32974215e-07,  1.31444119e-07,
        1.30096351e-07,  1.25612507e-07,  1.28841749e-07,  1.62760082e-07,
        5.61877362e-08, -2.75919368e-07, -1.68349522e-07,  6.77548378e-08,
        6.12303545e-08,  5.23862687e-09, -5.59636764e-08, -6.57385329e-08,
        -1.05490967e-07, -8.09880336e-08, -4.07608006e-08, -5.50961014e-08,
        -1.82779995e-09,  3.98513859e-08,  3.83581746e-07, -3.77968643e-07,
        8.65527067e-08,  1.60996515e-06,  6.42389620e-07, -9.54976389e-07,
        -1.34522764e-06, -7.05372983e-07, -1.93699307e-08,  3.72837700e-07,
        4.26616234e-07,  3.06510952e-07,  1.16393236e-07, -1.65212277e-08,
        -9.96772346e-08, -1.14188573e-07])

    n_data = np.array([
        -5.96958190e-39, -5.89781130e-37, 2.83102215e-35, 2.56623118e-33,
        -5.10888221e-33, -4.16161621e-30, 1.67933008e-29, 2.04600795e-26,
        -6.59883324e-25, 5.28510811e-24, -5.83013590e-23, 7.83984748e-22,
        1.16609069e-20, -1.72158484e-19, 8.39366383e-19, -6.51025720e-19,
        -2.50960666e-17, 3.46178406e-13, 7.27449661e-11, 3.09476063e-09,
        2.82341121e-08, 6.57350773e-08, 7.00736863e-08, 8.74377643e-08,
        1.15063434e-07, 1.74533015e-07, 2.13544672e-07, 1.68080983e-07,
        1.06248829e-07, 4.50717945e-08, 3.60849044e-09, 1.44347709e-08,
        6.75163602e-08, 1.42474601e-07, 1.96200936e-07, 8.96202061e-08,
        -1.75033495e-07, -2.08592057e-07, 1.76976252e-07, 1.99391816e-07,
        1.33150566e-07, 1.00995467e-07, 1.02955473e-07, 9.80975901e-08,
        8.32742618e-08, 5.52240391e-08, -6.04359949e-08, -1.33982954e-07,
        -2.34621555e-08, -1.09880012e-07, 1.17431183e-07, 1.47581535e-07,
        -5.97205640e-07, -4.74928195e-08, 1.03865310e-06, 7.82422099e-07,
        5.02526701e-08, -4.30853146e-07, -4.10889299e-07, -2.40001809e-07,
        -8.01653007e-09, 1.05567943e-07, 1.61960044e-07, 1.40885921e-07,
        9.17636544e-08, 4.84211284e-08])

    e_data = np.array([
        1.15974698e-41, 1.05877338e-39, -5.31725007e-38, -4.36036084e-36,
        2.84916680e-35, 7.52473224e-33, -4.62279208e-32, -3.77515990e-29,
        1.38842091e-27, -1.49159509e-26, 8.99877513e-26, -4.05121461e-25,
        -3.00692098e-23, 3.76955317e-22, -1.74838407e-21, 6.65926876e-22,
        -3.38783935e-18, -2.03079411e-15, -2.80238719e-13, -8.47140012e-12,
        -4.30027468e-11, 3.71617561e-11, 2.97648621e-10, 5.34631634e-10,
        8.21952612e-10, 1.14353949e-09, 1.66616870e-09, 2.36990685e-09,
        2.96538284e-09, 3.41398317e-09, 3.70200166e-09, 3.84298249e-09,
        3.96385800e-09, 4.16369765e-09, 4.60881372e-09, 5.54941252e-09,
        6.24290656e-09, -4.35558007e-09, -1.82028654e-08, -1.33653999e-08,
        -1.07268491e-08, -1.04735277e-08, -1.18887443e-08, -1.36243647e-08,
        -2.25339355e-08, -5.58518081e-08, -3.16411314e-08, 8.10034292e-08,
        8.76700281e-08, 1.22798799e-08, -1.15736258e-08, -1.42783066e-08,
        -9.21718159e-09, -8.39552781e-09, -6.76709284e-09, -3.93653495e-09,
        9.29348648e-10, 6.55616912e-10, 1.66073119e-09, -7.88372632e-10,
        7.31150846e-10, -1.23458217e-09, 1.25831683e-11, -9.86027370e-10,
        2.33252099e-10, -7.74174495e-10])

    r_data = np.array([
        5.96959313e-39, 5.89782060e-37, -2.83102710e-35, -2.56623472e-33,
        5.10893003e-33, 4.16162289e-30, -1.67933604e-29, -2.04601139e-26,
        6.59884784e-25, -5.28512762e-24, 5.83014207e-23, -7.83983921e-22,
        -1.16609441e-20, 1.72158896e-19, -8.39368203e-19, 6.51025711e-19,
        2.50890400e-17, -3.46181853e-13, -7.27453888e-11, -3.09477151e-09,
        -2.82341408e-08, -6.57348616e-08, -7.00729252e-08, -8.74364786e-08,
        -1.15061498e-07, -1.74530292e-07, -2.13540790e-07, -1.68075749e-07,
        -1.06242500e-07, -4.50646718e-08, -3.60086273e-09, -1.44268301e-08,
        -6.75080581e-08, -1.42465729e-07, -1.96191034e-07, -8.96085935e-08,
        1.75045974e-07, 2.08582650e-07, -1.77013345e-07, -1.99418904e-07,
        -1.33172364e-07, -1.01016811e-07, -1.02979726e-07, -9.81254262e-08,
        -8.33204684e-08, -5.53388854e-08, 6.03707380e-08, 1.34149404e-07,
        2.36425626e-08, 1.09905055e-07, -1.17454757e-07, -1.47610612e-07,
        5.97185402e-07, 4.74754379e-08, -1.03866482e-06, -7.82428544e-07,
        -5.02506508e-08, 4.30853583e-07, 4.10891847e-07, 2.39999677e-07,
        8.01801806e-09, -1.05570260e-07, -1.61959675e-07, -1.40887653e-07,
        -9.17629799e-08, -4.84226194e-08])

    t_data = np.array([
        6.90125029e-43, 1.55212888e-40, -5.10034208e-39, -9.21885320e-37,
        -1.79756703e-35, 1.04140314e-33, 1.16611034e-32, -4.36276452e-30,
        -3.01381328e-29, 4.03724505e-27, 3.00178360e-26, -1.20860509e-24,
        6.06675951e-24, -2.25897561e-23, 2.06591338e-23, 6.74122196e-22,
        3.43948900e-18, 1.31822876e-15, 1.30502533e-13, 2.10123947e-12,
        -1.51134137e-11, -1.72468370e-10, -4.41885117e-10, -7.14609215e-10,
        -1.05879326e-09, -1.50278948e-09, -2.10571776e-09, -2.71587361e-09,
        -3.18407528e-09, -3.50675008e-09, -3.70942140e-09, -3.87268635e-09,
        -4.10282282e-09, -4.45695337e-09, -5.01265682e-09, -5.73387174e-09,
        -5.88261075e-09, 4.78492915e-09, 1.78385454e-08, 1.29549507e-08,
        1.04527541e-08, 1.02656201e-08, 1.16767993e-08, 1.34224153e-08,
        2.23624790e-08, 5.57380186e-08, 3.17654637e-08, -8.07274720e-08,
        -8.76215487e-08, -1.20536809e-08, 1.13318852e-08, 1.39744999e-08,
        1.04464284e-08, 8.49326752e-09, 4.62915275e-09, 2.32601743e-09,
        -1.03278495e-09, 2.31236920e-10, -8.14968084e-10, 1.28238196e-09,
        -7.14648363e-10, 1.01728234e-09, -3.45955805e-10, 6.96030825e-10,
        -4.22134573e-10, 6.74504566e-10])

    np.testing.assert_allclose(st_bwd.select(component='Z')[0].data, z_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='N')[0].data, n_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='E')[0].data, e_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='R')[0].data, r_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='T')[0].data, t_data,
                               rtol=1E-7, atol=1E-12)

    # vertical only DB
    instaseis_bwd = InstaSeisDB(os.path.join(DATA, "100s_db_bwd_PZ/"))

    st_bwd = instaseis_bwd.get_seismograms(
        source=source, receiver=receiver, components=('Z'))

    np.testing.assert_allclose(st_bwd.select(component='Z')[0].data, z_data,
                               rtol=1E-7, atol=1E-12)

    # horizontal only DB
    instaseis_bwd = InstaSeisDB(os.path.join(DATA, "100s_db_bwd_PX/"))

    st_bwd = instaseis_bwd.get_seismograms(
        source=source, receiver=receiver, components=('N'))

    np.testing.assert_allclose(st_bwd.select(component='N')[0].data, n_data,
                               rtol=1E-7, atol=1E-12)

    # read on init
    instaseis_bwd = InstaSeisDB(os.path.join(DATA, "100s_db_bwd/"),
                                read_on_demand=False)

    st_bwd = instaseis_bwd.get_seismograms(
        source=source, receiver=receiver, components=('Z', 'N', 'E', 'R', 'T'))

    np.testing.assert_allclose(st_bwd.select(component='Z')[0].data, z_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='N')[0].data, n_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='E')[0].data, e_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='R')[0].data, r_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='T')[0].data, t_data,
                               rtol=1E-7, atol=1E-12)

    # read the same again to test buffer
    st_bwd = instaseis_bwd.get_seismograms(
        source=source, receiver=receiver, components=('Z', 'N', 'E', 'R', 'T'))
    np.testing.assert_allclose(st_bwd.select(component='Z')[0].data, z_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='N')[0].data, n_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='E')[0].data, e_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='R')[0].data, r_data,
                               rtol=1E-7, atol=1E-12)
    np.testing.assert_allclose(st_bwd.select(component='T')[0].data, t_data,
                               rtol=1E-7, atol=1E-12)

    # test resampling
    dt = instaseis_bwd.dt
    st_bwd = instaseis_bwd.get_seismograms(
        source=source, receiver=receiver, components=('Z'), dt=dt)
    np.testing.assert_allclose(st_bwd.select(component='Z')[0].data, z_data,
                               rtol=1E-7, atol=1E-12)


def test_incremental_fwd():
    """
    incremental tests of fwd mode
    """
    instaseis_fwd = InstaSeisDB(os.path.join(DATA, "100s_db_fwd"),
                                reciprocal=False)

    receiver = Receiver(latitude=42.6390, longitude=74.4940)
    source = Source(
        latitude=89.91, longitude=0.0, depth_in_m=None,
        m_rr=4.710000e+24 / 1E7,
        m_tt=3.810000e+22 / 1E7,
        m_pp=-4.740000e+24 / 1E7,
        m_rt=3.990000e+23 / 1E7,
        m_rp=-8.050000e+23 / 1E7,
        m_tp=-1.230000e+24 / 1E7)

    st_fwd = instaseis_fwd.get_seismograms(
        source=source, receiver=receiver, components=('Z', 'N', 'E', 'R', 'T'))

    z_data = np.array([
        -4.05130050e-39, 1.18143139e-36, 2.74070476e-34, -2.17753206e-33,
        2.24870888e-32, -2.97897814e-30, 4.35393435e-28, -2.91575774e-26,
        1.16624902e-25, -5.43645090e-24, 4.64538470e-22, -7.41396886e-21,
        4.88933049e-20, -7.73084100e-20, -8.99641408e-19, -1.80542628e-17,
        -1.60475237e-14, -2.68348506e-12, -2.14458150e-10, -6.38909514e-09,
        -4.36153968e-08, -6.84710839e-08, -4.22740921e-08, -3.29152593e-08,
        -3.16327608e-08, -5.38883520e-08, -4.59771788e-08, 1.33398909e-08,
        7.23766588e-08, 1.13321925e-07, 1.29550253e-07, 1.29147418e-07,
        1.28760201e-07, 1.23260252e-07, 1.26735241e-07, 1.58788596e-07,
        5.13654241e-08, -2.34847102e-07, -1.49230626e-07, 5.29356978e-08,
        4.73639076e-08, -7.85615130e-09, -5.48621956e-08, -7.01396310e-08,
        -8.58697608e-08, -9.93042468e-08, -8.30175896e-08, -5.91832289e-08,
        8.17326009e-08, -1.03750882e-07, 5.86545423e-07, -5.07725133e-07,
        -2.06001601e-07, 2.12479505e-06, 8.79514605e-07, -1.18594410e-06,
        -1.64692353e-06, -7.98518592e-07, 3.91671142e-08, 4.48087546e-07,
        5.21543798e-07, 3.26319762e-07, 1.36250506e-07, -4.74254088e-08,
        -1.06125346e-07, -1.45335127e-07])

    n_data = np.array([
        -1.67557648e-39, 1.16346948e-36, 2.59132386e-34, -1.79557933e-33,
        2.56362583e-32, -2.82327248e-30, 3.99233123e-28, -2.71409199e-26,
        9.52113831e-26, -5.30627242e-24, 4.15604506e-22, -6.16527674e-21,
        4.30705503e-20, -1.49800801e-19, -2.10158076e-19, 1.20087297e-17,
        1.07156708e-14, 1.94138476e-12, 1.62873196e-10, 4.96696603e-09,
        3.52024483e-08, 6.52452724e-08, 6.69432349e-08, 8.78961262e-08,
        1.15236024e-07, 1.77972368e-07, 2.08325189e-07, 1.60708553e-07,
        1.00559938e-07, 4.16285374e-08, 2.95686813e-09, 1.48251236e-08,
        6.76853143e-08, 1.44531653e-07, 1.93253851e-07, 8.56857529e-08,
        -1.48725230e-07, -1.87876782e-07, 1.42435462e-07, 1.93464272e-07,
        1.37049322e-07, 1.07985513e-07, 1.05652761e-07, 1.01419409e-07,
        8.63033331e-08, 5.41702843e-08, -5.88945006e-08, -1.51695375e-07,
        -6.24887101e-09, -1.35808475e-07, 7.31740134e-08, 3.48703949e-07,
        -8.54940276e-07, -1.97130939e-07, 1.31894338e-06, 9.45809560e-07,
        3.78350168e-08, -5.62235612e-07, -4.71921664e-07, -2.93208995e-07,
        3.36482461e-08, 9.53978933e-08, 2.24948694e-07, 1.11234077e-07,
        1.37668094e-07, 1.70508011e-08])

    e_data = np.array([
        3.19160217e-42, -2.57005909e-39, -5.80297431e-37, 3.69023105e-36,
        -2.47643012e-35, 7.81070549e-33, -8.26147631e-31, 5.87408574e-29,
        -1.57485921e-28, 4.25443069e-27, -9.53367431e-25, 1.49786868e-23,
        -1.07418989e-22, 4.22563640e-22, 2.15076418e-22, -2.98695005e-20,
        -1.79852531e-17, -2.86746669e-15, -2.41055964e-13, -5.42837962e-12,
        -1.82342835e-14, 1.49403915e-10, 3.80522180e-10, 6.27474550e-10,
        9.23978421e-10, 1.25193283e-09, 1.80268910e-09, 2.47343709e-09,
        3.04292432e-09, 3.47804223e-09, 3.75884256e-09, 3.90556658e-09,
        4.04025352e-09, 4.28017196e-09, 4.70628902e-09, 5.46133129e-09,
        3.39339712e-09, -1.12286137e-08, -1.46665643e-08, -1.17285588e-08,
        -9.90297341e-09, -1.03839581e-08, -1.19133999e-08, -1.47093864e-08,
        -3.10049456e-08, -5.23373500e-08, -1.26686233e-08, 7.74259771e-08,
        8.56009515e-08, 9.96378574e-09, -1.36933244e-08, -1.45441539e-08,
        -9.56649417e-09, -8.09822738e-09, -8.12379521e-09, -3.46165126e-09,
        5.12904785e-10, 1.01061526e-09, 1.83647695e-09, 1.17065733e-10,
        -6.40068677e-10, 9.27899296e-11, -1.44814992e-09, 1.41196163e-10,
        -6.60389092e-10, -1.94308571e-10])

    r_data = np.array([
        1.67557950e-39, -1.16347230e-36, -2.59133032e-34, 1.79558312e-33,
        -2.56362549e-32, 2.82328258e-30, -3.99233977e-28, 2.71409833e-26,
        -9.52115055e-26, 5.30626994e-24, -4.15605588e-22, 6.16529451e-21,
        -4.30706801e-20, 1.49801354e-19, 2.10158074e-19, -1.20087657e-17,
        -1.07156851e-14, -1.94138655e-12, -1.62873348e-10, -4.96696668e-09,
        -3.52023737e-08, -6.52448267e-08, -6.69423099e-08, -8.78946484e-08,
        -1.15233878e-07, -1.77969414e-07, -2.08321037e-07, -1.60703121e-07,
        -1.00553461e-07, -4.16212901e-08, -2.94912480e-09, -1.48170531e-08,
        -6.76768546e-08, -1.44522537e-07, -1.93243754e-07, -8.56743299e-08,
        1.48731900e-07, 1.87853271e-07, -1.42465349e-07, -1.93488004e-07,
        -1.37069416e-07, -1.08006658e-07, -1.05677059e-07, -1.01449472e-07,
        -8.63669697e-08, -5.42778989e-08, 5.88682992e-08, 1.51854424e-07,
        6.42505565e-09, 1.35828696e-07, -7.32020442e-08, -3.48733148e-07,
        8.54918773e-07, 1.97113852e-07, -1.31895730e-06, -9.45814682e-07,
        -3.78338809e-08, 5.62236501e-07, 4.71924444e-07, 2.93208615e-07,
        -3.36494923e-08, -9.53975002e-08, -2.24951199e-07, -1.11233551e-07,
        -1.37669162e-07, -1.70511650e-08])

    t_data = np.array([
        2.57350260e-43, 1.75210397e-40, 4.69075234e-38, 5.73194241e-39,
        -2.80044928e-35, -1.99936756e-33, 4.37894319e-33, -2.87485066e-30,
        -3.84940599e-29, 6.66781647e-27, 9.79002141e-26, -2.28827371e-24,
        1.87639078e-23, -1.14218224e-22, 2.17505777e-22, 5.15110485e-21,
        -4.07153208e-18, -1.12861516e-15, -9.41968100e-14, -4.79545410e-12,
        -7.24412048e-11, -2.83702094e-10, -5.18314894e-10, -8.08395409e-10,
        -1.16117410e-09, -1.61826202e-09, -2.23149428e-09, -2.80422849e-09,
        -3.24990679e-09, -3.56372153e-09, -3.76492091e-09, -3.93607381e-09,
        -4.17956595e-09, -4.57766159e-09, -5.10406575e-09, -5.63769215e-09,
        -3.08725933e-09, 1.16153087e-08, 1.43733492e-08, 1.13303141e-08,
        9.62085510e-09, 1.01616627e-08, 1.16959029e-08, 1.45005972e-08,
        3.08272363e-08, 5.22257369e-08, 1.27898227e-08, -7.71135688e-08,
        -8.55879077e-08, -9.68422141e-09, 1.35426766e-08, 1.38263636e-08,
        1.13262519e-08, 8.50397738e-09, 5.40891293e-09, 1.51482393e-09,
        -5.90781921e-10, 1.46672210e-10, -8.65086673e-10, 4.86465246e-10,
        5.70806995e-10, -2.89153287e-10, 9.85120645e-10, -3.70156042e-10,
        3.77016695e-10, 1.59211410e-10])

    np.testing.assert_allclose(st_fwd.select(component='Z')[0].data, z_data,
                               rtol=1E-7, atol=1E-16)
    np.testing.assert_allclose(st_fwd.select(component='N')[0].data, n_data,
                               rtol=1E-7, atol=1E-16)
    np.testing.assert_allclose(st_fwd.select(component='E')[0].data, e_data,
                               rtol=1E-7, atol=1E-16)
    np.testing.assert_allclose(st_fwd.select(component='R')[0].data, r_data,
                               rtol=1E-7, atol=1E-16)
    np.testing.assert_allclose(st_fwd.select(component='T')[0].data, t_data,
                               rtol=1E-7, atol=1E-16)

    # read the same again to test buffer
    st_fwd = instaseis_fwd.get_seismograms(
        source=source, receiver=receiver, components=('Z', 'N', 'E', 'R', 'T'))
    np.testing.assert_allclose(st_fwd.select(component='Z')[0].data, z_data,
                               rtol=1E-7, atol=1E-16)
    np.testing.assert_allclose(st_fwd.select(component='N')[0].data, n_data,
                               rtol=1E-7, atol=1E-16)
    np.testing.assert_allclose(st_fwd.select(component='E')[0].data, e_data,
                               rtol=1E-7, atol=1E-16)
    np.testing.assert_allclose(st_fwd.select(component='R')[0].data, r_data,
                               rtol=1E-7, atol=1E-16)
    np.testing.assert_allclose(st_fwd.select(component='T')[0].data, t_data,
                               rtol=1E-7, atol=1E-16)
