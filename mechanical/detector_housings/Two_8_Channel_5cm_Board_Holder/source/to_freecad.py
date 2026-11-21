#!/usr/bin/env python3
"""Import the organized mechanical-only STEP into an editable FreeCAD document."""
from pathlib import Path
import sys
import FreeCAD as App
import Import

step = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
doc = App.newDocument('Two_8_Channel_5cm_Board_Holder')
Import.insert(str(step),doc.Name)
shape_objects = [obj for obj in doc.Objects if hasattr(obj, 'Shape') and not obj.Shape.isNull()]
assert shape_objects and all(obj.Shape.isValid() for obj in shape_objects)
assert not any('pcb' in obj.Label.lower() or 'kiCad'.lower() in obj.Label.lower() for obj in shape_objects)
print(f'{len(shape_objects)} valid mechanical CAD shapes')
sheet=doc.addObject('Spreadsheet::Sheet','DesignDimensions')
sheet.Label='Rev 02 Design Dimensions'
for i,(n,v) in enumerate([('Tube length','609.60 mm'),('Tube OD','101.6 mm'),('Nominal wall','3.175 mm'),('Accepted minimum bore','93.50 mm'),('Guide diameter','91.00 mm'),('Collar diameter','92.50 mm'),('Board envelope length','443.0 mm'),('Board envelope width','49.10 mm'),('Board plane separation','37.0 mm'),('Four panel ports','32 × 36 mm'),('Front cap thickness','3.175 mm')],2):
    sheet.set('A'+str(i),n);sheet.set('B'+str(i),v)
sheet.setColumnWidth('A',240);sheet.setColumnWidth('B',120)
doc.recompute()
doc.saveAs(str(out))
App.closeDocument(doc.Name)
reopened=App.openDocument(str(out))
assert any(hasattr(obj, 'Shape') and not obj.Shape.isNull() for obj in reopened.Objects)
