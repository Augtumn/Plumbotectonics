# -*- coding: utf-8 -*-
"""Version I plumbotectonics model (Zartman & Doe, 1981).

Each orogeny has two stages, following the equation numbers of the paper:

* extraction (eqs. 14-16): every reservoir contributes a mass fraction of
  itself, and the contribution carries the reservoir's composition times an
  enrichment factor ``E`` (``E_m = 4`` for the mantle, ``E_u = E_l = 1``);
* redistribution (eqs. 17-19): the orogene content is split between the three
  returning increments -- the material going back to the mantle (mass
  ``M_or - 2.6 - 2.6``) and the new upper and lower crust (``2.6`` each) --
  in proportion to ``mass x partitioning ratio``, normalised by
  ``s = sum(mass_i * F_i)``.  ``F_PB``/``F_U``/``F_TH`` are therefore
  *concentration* ratios, not fractions of the orogene content.

With the Table II parameters this reproduces Table IV (all 126 values) and
the Table II section III ending inventories to the precision printed in the
paper; see ``docs/validation.md``.

Implementation notes:
    Each reservoir carries its six isotope inventories as one row of a NumPy
    array ordered ``ISO_KEYS``, so extraction, redistribution and decay act on
    whole segments at once instead of looping over isotopes and segments.  The
    public return value is unchanged: ``history`` entries hold plain ratio
    dicts and ``upper_segs``/``lower_segs`` stay lists of dicts.

Reference:
    Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics - the model.
    Tectonophysics, 75(1-2), 135-162.
    https://doi.org/10.1016/0040-1951(81)90213-4
"""
import numpy as np

# Decay constants per Ga
L238 = 0.155125
L235 = 0.98485
L232 = 0.049475
U8U5 = 137.88

MASS0 = 800.0
PB2040 = 38.0
U2380 = 349.0
TH2320 = 1335.0
R2060, R2070, R2080 = 10.36, 12.12, 30.55
NEW_U = 2.6
NEW_L = 2.6

F_PB = (0.028, 0.754, 0.218)
F_U  = (0.024, 0.854, 0.122)
F_TH = (0.020, 0.788, 0.192)
E_M = 4.0
E_U = 1.0
E_L = 1.0

ERO_U = 0.37      # f_v + f_h - f_v*f_h, upper crust
ERO_L = 0.10      # areal erosion, lower crust

# Fixed isotope order for the internal state arrays.
ISO_KEYS = ("204", "206", "207", "208", "232", "238")
_I204, _I206, _I207, _I208, _I232, _I238 = range(6)

# Partition ratios laid out on the ISO_KEYS axis: Pb for the four lead
# isotopes, Th for 232, U for 238.
_F_RET = np.array([F_PB[0]] * 4 + [F_TH[0], F_U[0]])
_F_UP = np.array([F_PB[1]] * 4 + [F_TH[1], F_U[1]])
_F_LOW = np.array([F_PB[2]] * 4 + [F_TH[2], F_U[2]])


def ratios(res):
    """{'206/204', '207/204', '208/204'} from a reservoir dict or row."""
    if isinstance(res, np.ndarray):
        pb204 = res[_I204]
        if pb204 == 0:
            return None
        return {'206/204': res[_I206]/pb204, '207/204': res[_I207]/pb204,
                '208/204': res[_I208]/pb204}
    if res['204'] == 0:
        return None
    return {'206/204': res['206']/res['204'],
            '207/204': res['207']/res['204'],
            '208/204': res['208']/res['204']}


def row_to_dict(row, mass):
    """Segment row -> the legacy dict shape (the documented public API)."""
    out = {'mass': float(mass)}
    for key, value in zip(ISO_KEYS, row):
        out[key] = float(value)
    return out


def avg_res(segs):
    """Mole-weighted average composition of a list of segment dicts."""
    a = {'mass': sum(s['mass'] for s in segs), '204': sum(s['204'] for s in segs),
         '206': sum(s['206'] for s in segs), '207': sum(s['207'] for s in segs),
         '208': sum(s['208'] for s in segs)}
    return ratios(a)


def _mean_ratio(rows, masses):
    """Composition of a stack of segments, summed over the segment axis."""
    if len(rows) == 0:
        return None
    return ratios(rows.sum(axis=0))


def run():
    # Internal state: one row per reservoir, columns ordered ISO_KEYS.
    mantle = np.array([PB2040, PB2040*R2060, PB2040*R2070, PB2040*R2080,
                       TH2320, U2380], dtype=float)
    mantle_mass = MASS0
    # crustal segments: (n_segs, 6) inventories plus their masses
    upper_x = np.zeros((0, 6))
    upper_m = np.zeros(0)
    lower_x = np.zeros((0, 6))
    lower_m = np.zeros(0)
    history = []

    times = []
    for i in range(11):
        # integer tenths: 4.0, 3.6, ... 0.0 without binary-float drift
        t = (40 - 4 * i) / 10
        frac = 1/8 if i==0 else 1/16 if i==1 else 1/32 if i==2 else 1/64 if i==3 else 1/128
        times.append((t, frac))

    for j, (t, f_m) in enumerate(times):
        # record state before orogeny (after decay from previous)
        history.append({'t': t,
                        'mantle': ratios(mantle),
                        'orogene': None,
                        'upper': _mean_ratio(upper_x, upper_m),
                        'lower': _mean_ratio(lower_x, lower_m)})

        # --- increments to orogene ---
        dm = mantle_mass * f_m
        du = upper_m * ERO_U
        dl = lower_m * ERO_L
        d_or = dm + du.sum() + dl.sum()

        # --- isotope increments (eqs. 14-16) ---
        inc = mantle * (f_m * E_M)
        if len(upper_x):
            inc = inc + (upper_x * (du / upper_m)[:, None] * E_U).sum(axis=0)
        if len(lower_x):
            inc = inc + (lower_x * (dl / lower_m)[:, None] * E_L).sum(axis=0)

        # record orogene after mixing (same t)
        history[-1]['orogene'] = ratios(inc)

        # --- redistribution (eqs. 17-19) ---
        # F_PB/F_U/F_TH are *concentration* ratios among the three returning
        # increments, not fractions of the orogene content.  Each increment
        # therefore receives a share weighted by its own mass: the material
        # going back to the mantle (m_ret), and the new upper/lower crust
        # (NEW_U/NEW_L).  s normalises the three shares to 1, so the orogene
        # content is redistributed without loss.
        m_ret = d_or - NEW_U - NEW_L
        s = m_ret * _F_RET + NEW_U * _F_UP + NEW_L * _F_LOW
        if np.all(s > 0):
            ret_m = inc * (m_ret * _F_RET) / s
            new_u = inc * (NEW_U * _F_UP) / s
            new_l = inc * (NEW_L * _F_LOW) / s
        else:  # degenerate parameters only; unreachable for Table II
            keep = s > 0
            ret_m = np.where(keep, inc * (m_ret * _F_RET) / np.where(keep, s, 1.0), 0.0)
            new_u = np.where(keep, inc * (NEW_U * _F_UP) / np.where(keep, s, 1.0), 0.0)
            new_l = np.where(keep, inc * (NEW_L * _F_LOW) / np.where(keep, s, 1.0), 0.0)

        # --- update reservoirs after orogeny ---
        mantle_mass = mantle_mass - dm + m_ret
        mantle = mantle - mantle * (f_m * E_M) + ret_m
        upper_x = upper_x * (1 - ERO_U)
        upper_m = upper_m * (1 - ERO_U)
        lower_x = lower_x * (1 - ERO_L)
        lower_m = lower_m * (1 - ERO_L)
        upper_x = np.vstack([upper_x, new_u])
        upper_m = np.append(upper_m, NEW_U)
        lower_x = np.vstack([lower_x, new_l])
        lower_m = np.append(lower_m, NEW_L)

        # --- decay until next orogeny ---
        if j < len(times) - 1:
            t_next = times[j+1][0]
            g238 = np.exp(L238*t) - np.exp(L238*t_next)
            g235 = np.exp(L235*t) - np.exp(L235*t_next)
            g232 = np.exp(L232*t) - np.exp(L232*t_next)

            def decay(res):
                res[..., _I206] += res[..., _I238] * g238
                res[..., _I207] += (res[..., _I238]/U8U5) * g235
                res[..., _I208] += res[..., _I232] * g232

            decay(mantle)
            if len(upper_x):
                decay(upper_x)
            if len(lower_x):
                decay(lower_x)

    upper_segs = [row_to_dict(r, m) for r, m in zip(upper_x, upper_m)]
    lower_segs = [row_to_dict(r, m) for r, m in zip(lower_x, lower_m)]
    return history, row_to_dict(mantle, mantle_mass), upper_segs, lower_segs


if __name__ == '__main__':
    hist, mantle, ups, los = run()
    print('t     Mantle                 Orogene                 Upper                  Lower')
    for h in hist:
        def fmt(d):
            if not d: return '-'
            return f"{d['206/204']:.2f}/{d['207/204']:.2f}/{d['208/204']:.2f}"
        print(f"{h['t']:.1f}  {fmt(h['mantle'])}  {fmt(h['orogene'])}  {fmt(h['upper'])}  {fmt(h['lower'])}")


__all__ = ['run', 'ratios', 'avg_res']
