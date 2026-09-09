# -*- coding: utf-8 -*-
"""Version I plumbotectonics model (Zartman & Doe, 1981).

Reference:
    Zartman, R. E., and Doe, B. R., 1981, Plumbotectonics-the model:
    Tectonophysics, 75, 135-162.
"""
import math

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

def ratios(res):
    if res['204'] == 0:
        return None
    return {'206/204': res['206']/res['204'],
            '207/204': res['207']/res['204'],
            '208/204': res['208']/res['204']}

def avg_res(segs):
    a = {'mass': sum(s['mass'] for s in segs), '204': sum(s['204'] for s in segs),
         '206': sum(s['206'] for s in segs), '207': sum(s['207'] for s in segs),
         '208': sum(s['208'] for s in segs)}
    return ratios(a)

def run():
    mantle = {'mass': MASS0, '204': PB2040, '206': PB2040*R2060,
              '207': PB2040*R2070, '208': PB2040*R2080,
              '232': TH2320, '238': U2380}
    upper_segs = []
    lower_segs = []
    history = []

    times = []
    for i in range(11):
        t = 4.0 - i*0.4
        frac = 1/8 if i==0 else 1/16 if i==1 else 1/32 if i==2 else 1/64 if i==3 else 1/128
        times.append((t, frac))

    for j, (t, f_m) in enumerate(times):
        # record state before orogeny (after decay from previous)
        history.append({'t': t,
                        'mantle': ratios(mantle),
                        'orogene': None,
                        'upper': avg_res(upper_segs),
                        'lower': avg_res(lower_segs)})

        # --- increments to orogene ---
        dm = mantle['mass'] * f_m
        du_segs = [seg['mass'] * 0.37 for seg in upper_segs]
        dl_segs = [seg['mass'] * 0.10 for seg in lower_segs]
        d_or = dm + sum(du_segs) + sum(dl_segs)

        # --- isotope increments ---
        inc = {'204':0., '206':0., '207':0., '208':0., '232':0., '238':0.}
        for isok in inc:
            inc[isok] += mantle[isok] * f_m * E_M
        for seg, du in zip(upper_segs, du_segs):
            for isok in inc:
                inc[isok] += seg[isok] * (du / seg['mass']) * E_U
        for seg, dl in zip(lower_segs, dl_segs):
            for isok in inc:
                inc[isok] += seg[isok] * (dl / seg['mass']) * E_L

        oro = dict(inc)

        # record orogene after mixing (same t)
        history[-1]['orogene'] = ratios(oro)

        # --- redistribution fractions ---
        def part_fraction(isok):
            if isok in ('204','206','207','208'): return F_PB
            if isok == '238': return F_U
            if isok == '232': return F_TH
            return (0,0,0)

        new_u = {'mass': NEW_U, '204':0., '206':0., '207':0., '208':0., '232':0., '238':0.}
        new_l = {'mass': NEW_L, '204':0., '206':0., '207':0., '208':0., '232':0., '238':0.}
        for isok in ['204','206','207','208','232','238']:
            fr = part_fraction(isok)
            new_u[isok] = oro[isok] * fr[1]
            new_l[isok] = oro[isok] * fr[2]
        ret_m = {k: oro[k] * part_fraction(k)[0] for k in ['204','206','207','208','232','238']}

        # --- update reservoirs after orogeny ---
        mantle['mass'] = mantle['mass'] - dm + (d_or - NEW_U - NEW_L)
        inc_m = {k: mantle[k] * f_m * E_M for k in ['204','206','207','208','232','238']}
        for k in ['204','206','207','208','232','238']:
            mantle[k] = mantle[k] - inc_m[k] + ret_m[k]
        for seg in upper_segs:
            for k in ['204','206','207','208','232','238']:
                seg[k] *= (1 - 0.37)
            seg['mass'] *= (1 - 0.37)
        for seg in lower_segs:
            for k in ['204','206','207','208','232','238']:
                seg[k] *= (1 - 0.10)
            seg['mass'] *= (1 - 0.10)
        upper_segs.append(new_u)
        lower_segs.append(new_l)

        # --- decay until next orogeny ---
        if j < len(times) - 1:
            t_next = times[j+1][0]
            def decay(res):
                res['206'] += res['238'] * (math.exp(L238*t) - math.exp(L238*t_next))
                res['207'] += (res['238']/U8U5) * (math.exp(L235*t) - math.exp(L235*t_next))
                res['208'] += res['232'] * (math.exp(L232*t) - math.exp(L232*t_next))
            decay(mantle)
            for seg in upper_segs: decay(seg)
            for seg in lower_segs: decay(seg)

    return history, mantle, upper_segs, lower_segs

if __name__ == '__main__':
    hist, mantle, ups, los = run()
    print('t     Mantle                 Orogene                 Upper                  Lower')
    for h in hist:
        def fmt(d):
            if not d: return '-'
            return f"{d['206/204']:.2f}/{d['207/204']:.2f}/{d['208/204']:.2f}"
        print(f"{h['t']:.1f}  {fmt(h['mantle'])}  {fmt(h['orogene'])}  {fmt(h['upper'])}  {fmt(h['lower'])}")


__all__ = ['run']
