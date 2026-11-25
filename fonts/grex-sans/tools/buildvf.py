"""Assemble masters into the variable font: wght 100-700 (Plex avar curve kept), GRAN 0-100."""
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor
from fontTools import varLib
from fontTools.ttLib import TTFont
from fontTools.otlLib.builder import buildStatTable
import sys
FAMILY = sys.argv[1] if len(sys.argv) > 1 else 'Grex Sans'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'out/GrexSans[GRAN,wght].ttf'
# Plex Sans avar for wght, expressed as a user->design map (design == user at 100/400/700)
avar = {100: -1.0, 200: -0.76324462890625, 300: -0.38916015625, 400: 0.0, 450: 0.19097900390625,
        500: 0.427001953125, 600: 0.70501708984375, 700: 1.0}
wmap = [(u, 400 + m * 300) for u, m in avar.items()]
ds = DesignSpaceDocument()
a = AxisDescriptor(); a.tag = 'wght'; a.name = 'Weight'; a.minimum, a.default, a.maximum = 100, 400, 700; a.map = wmap; ds.addAxis(a)
g = AxisDescriptor(); g.tag = 'GRAN'; g.name = 'Grain'; g.minimum, g.default, g.maximum = 0, 100, 100; ds.addAxis(g)
for w in (100, 400, 700):
    for gr in (0, 100):
        s = SourceDescriptor(); s.path = f'masters/w{w}-g{gr}.ttf'; s.name = f'w{w}g{gr}'
        s.location = {'Weight': w, 'Grain': gr}; ds.addSource(s)
# Plex's light-weight currency alternates
r = RuleDescriptor(); r.name = 'light-won-naira'
r.conditionSets.append([dict(name='Weight', minimum=100, maximum=300)])
r.subs = [('uni20A6', 'uni20A6.rvrn'), ('uni20A9', 'uni20A9.rvrn')]
ds.rules = []  # won/naira rvrn glyphs are outside the Latin subset
names = {100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular', 450: 'Text', 500: 'Medium', 600: 'SemiBold', 700: 'Bold'}
for w, n in names.items():
    i = InstanceDescriptor(); i.familyName = FAMILY; i.styleName = n
    i.location = {'Weight': w, 'Grain': 100}; ds.addInstance(i)
ds.write('GrexSans.designspace')
vf, _, _ = varLib.build(ds, exclude=['STAT'])
# names
nm = vf['name']
ps = FAMILY.replace(' ', '')
for rec in list(nm.names):
    if rec.nameID in (1, 3, 4, 6, 16, 17, 21, 22, 25):
        nm.removeNames(nameID=rec.nameID)
nm.setName(FAMILY, 1, 3, 1, 0x409); nm.setName('Regular', 2, 3, 1, 0x409)
nm.setName(f'{ps}-Variable;1.000', 3, 3, 1, 0x409); nm.setName(FAMILY, 4, 3, 1, 0x409)
nm.setName('Version 1.000; derived from IBM Plex Sans Var 3.000', 5, 3, 1, 0x409)
nm.setName(f'{ps}-Regular', 6, 3, 1, 0x409); nm.setName(ps, 25, 3, 1, 0x409)
nm.setName('JC Morales (grain treatment); IBM Plex by Mike Abbink, Bold Monday', 9, 3, 1, 0x409)
nm.setName('Modified version of IBM Plex Sans. Copyright 2017 IBM Corp. Licensed under the SIL Open Font License 1.1.', 0, 3, 1, 0x409)
nm.setName('This Font Software is licensed under the SIL Open Font License, Version 1.1.', 13, 3, 1, 0x409)
nm.setName('https://openfontlicense.org', 14, 3, 1, 0x409)
# rename fvar instances and axes
for ax in vf['fvar'].axes:
    ax.axisNameID = nm.addMultilingualName({'en': 'Weight' if ax.axisTag == 'wght' else 'Grain'}, mac=False)
for inst, (w, n) in zip(vf['fvar'].instances, names.items()):
    inst.subfamilyNameID = nm.addMultilingualName({'en': n}, mac=False)
    inst.postscriptNameID = nm.addMultilingualName({'en': f'{ps}-{n}'}, mac=False)
buildStatTable(vf, [
    dict(tag='wght', name='Weight', values=[dict(value=w, name=n, **({'flags': 2, 'linkedValue': 700} if w == 400 else {})) for w, n in names.items()]),
    dict(tag='GRAN', name='Grain', values=[dict(value=0, name='Clean'), dict(value=100, name='Grain', flags=2)]),
], elidedFallbackName=2)
import os; os.makedirs('out', exist_ok=True)
vf.save(OUT)
print('saved', OUT, os.path.getsize(OUT) // 1024, 'KB')
