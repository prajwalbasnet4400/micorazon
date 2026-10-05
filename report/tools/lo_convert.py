"""Convert a .docx into native LibreOffice .odt (and a preview .pdf), refreshing all indexes.

Runs under LibreOffice's bundled Python, which ships the `uno` module:
    /Applications/LibreOffice.app/Contents/Resources/python report/tools/lo_convert.py in.docx out.odt [out.pdf]
"""

import os
import subprocess
import sys
import time

import uno
from com.sun.star.beans import PropertyValue

SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
PORT = 2083


def prop(name, value):
    p = PropertyValue()
    p.Name, p.Value = name, value
    return p


def connect():
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(60):
        try:
            return resolver.resolve(f"uno:socket,host=127.0.0.1,port={PORT};urp;StarOffice.ComponentContext")
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("could not connect to LibreOffice")


def main(src, odt, pdf=None):
    profile = "file:///tmp/hfp_lo_profile"
    proc = subprocess.Popen(
        [SOFFICE, "--headless", "--invisible", "--norestore", f"-env:UserInstallation={profile}",
         f"--accept=socket,host=127.0.0.1,port={PORT};urp;"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        ctx = connect()
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(os.path.abspath(src)), "_blank", 0,
                                           (prop("Hidden", True),))
        # Refresh fields first (page numbers), then indexes twice so page numbers settle.
        doc.getTextFields().refresh()
        for _ in range(2):
            indexes = doc.getDocumentIndexes()
            for i in range(indexes.getCount()):
                indexes.getByIndex(i).update()
            doc.refresh()
        doc.storeToURL(uno.systemPathToFileUrl(os.path.abspath(odt)), (prop("FilterName", "writer8"),))
        if pdf:
            doc.storeToURL(uno.systemPathToFileUrl(os.path.abspath(pdf)), (prop("FilterName", "writer_pdf_Export"),))
        print(f"indexes updated: {doc.getDocumentIndexes().getCount()}")
        doc.close(True)
    finally:
        try:
            desktop.terminate()
        except Exception:
            pass
        proc.wait(timeout=30)


if __name__ == "__main__":
    main(*sys.argv[1:])
