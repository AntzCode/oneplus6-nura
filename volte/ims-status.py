#!/usr/bin/env python3
"""Generic (not carrier-specific), but only used by the One NZ VoLTE scripts.

Read-only: bind IMSA/IMS Settings to SIM slot 0 and print IMS status."""
import sys
import gi
gi.require_version("Qmi", "1.0")
gi.require_version("Qrtr", "1.0")
from gi.repository import GLib, Qmi, Qrtr

NODE = int(sys.argv[1]) if len(sys.argv) > 1 else 0


def call(start, finish, *args):
    """Run an async GIO-style call synchronously."""
    loop = GLib.MainLoop()
    box = {}

    def done(src, res, *_):
        try:
            box["v"] = finish(res) if callable(finish) else getattr(src, finish)(res)
        except Exception as e:  # noqa: BLE001
            box["e"] = e
        loop.quit()

    start(*args, done)
    loop.run()
    if "e" in box:
        raise box["e"]
    return box["v"]


def dump(name, out):
    print(f"== {name}")
    for attr in sorted(dir(out)):
        if not attr.startswith("get_") or attr == "get_result":
            continue
        try:
            v = getattr(out, attr)()
        except Exception as e:  # noqa: BLE001
            v = f"<{e.__class__.__name__}>"
        if isinstance(v, tuple) and v and v[0] is True:
            v = v[1:] if len(v) > 2 else v[1]
        elif isinstance(v, tuple) and v and v[0] is False:
            continue
        print(f"  {attr[4:]}: {v}")


bus = call(Qrtr.Bus.new, Qrtr.Bus.new_finish, 1000, None)
node = call(bus.wait_for_node, "wait_for_node_finish", NODE, 5000, None)
dev = call(Qmi.Device.new_from_node, Qmi.Device.new_from_node_finish, node, None)
call(dev.open, "open_finish", Qmi.DeviceOpenFlags.AUTO, 10, None)

imsa = call(dev.allocate_client, "allocate_client_finish", Qmi.Service.IMSA, Qmi.CID_NONE, 10, None)
inp = Qmi.MessageImsaBindInput.new()
inp.set_binding(0)
call(imsa.bind, "bind_finish", inp, 10, None).get_result()
dump("IMSA registration", call(imsa.get_ims_registration_status, "get_ims_registration_status_finish", None, 10, None))
dump("IMSA services", call(imsa.get_ims_services_status, "get_ims_services_status_finish", None, 10, None))

ims = call(dev.allocate_client, "allocate_client_finish", Qmi.Service.IMS, Qmi.CID_NONE, 10, None)
inp = Qmi.MessageImsBindInput.new()
inp.set_binding(0)
call(ims.bind, "bind_finish", inp, 10, None).get_result()
dump("IMS settings", call(ims.get_ims_services_enabled_setting, "get_ims_services_enabled_setting_finish", None, 10, None))

for c in (imsa, ims):
    call(dev.release_client, "release_client_finish", c, Qmi.DeviceReleaseClientFlags.RELEASE_CID, 10, None)
