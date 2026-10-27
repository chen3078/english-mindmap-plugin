"""Render and bind the final connected map. Usage: manifest.json base.png plan.json output.png"""
import json
import sys
from pathlib import Path
from PIL import Image
from connector_checks import render, write_record

def main():
    if len(sys.argv)!=5: raise SystemExit(__doc__)
    mf,base,pf,out=[Path(s).resolve() for s in sys.argv[1:]]
    folder=mf.parent
    if any(p==out for p in [mf,base,pf]): raise ValueError("Keep base, plan and final output as separate files")
    for p in [base,pf,out]: p.relative_to(folder)
    manifest=json.loads(mf.read_text(encoding="utf-8-sig"));plan=json.loads(pf.read_text(encoding="utf-8-sig"))
    with Image.open(base) as im: result=render(manifest,im,plan)
    out.parent.mkdir(parents=True,exist_ok=True);result.save(out,"PNG")
    receipt=write_record(folder,out,base,pf)
    print("CONNECTOR GEOMETRY/RASTER PASS:",len(plan["branches"]),"curves;",receipt)
    print("Still inspect whole-page neatness, true anchors and semantic destinations against approved references.")

if __name__=="__main__": main()
