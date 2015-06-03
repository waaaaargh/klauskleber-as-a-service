#!/usr/bin/env python3

import serial
import qrcode
from io import BytesIO
import sys
from urllib.parse import urljoin

#SOH = "\x0H"
STX = "\x02"
CR  = "\x0D"
ESC = "\x1B"


# 191100001800020OpenLab Augsburg
#  |||||||||||||||_ text
#  ||||||||||||||_ x coord
#  ||||||||||_ y coord
#  ||||||_ fixed
#  |||_ fixed
#  |_ font



class LabelPrinter(serial.Serial):
    def __init__(self, port):
        super(LabelPrinter, self).__init__(
                #bytessize=8,
                baudrate=19200,
                port=port,
                timeout=0,
                parity="N",
                stopbits=1,
                xonxoff=1,
                rtscts=1)
        return

    def print_label(self, label, count=1):
        if not self.isOpen():
            self.open()

        for line in label.build():
            self.write(line)

        if count > 1:
            self.write(STX+"E"+str(count).zfill(4)+CR)
            self.write(STX+"G"+CR)

        self.close()
        return


class Label:

    thing_base_url = "https://dinge.openlab-augsburg.de/ding/"
    labelbuf = []

    def __init__(
            self,
            thing_id,
            thing_name,
            thing_maintainer,
            thing_owner = "OpenLab",
            thing_use_pol = "",
            thing_discard_pol = ""):

        if len(thing_id) > 10 or not thing_id.isdigit():
            raise ValueError("Not a valid thing_id: field must contain max "
                             "10 digits ranging from 0-9")
        self.thing_id = thing_id.zfill(10)

        if len(thing_name) > 19:
            self.thing_name = thing_name[:16] + "..."
        else:
            self.thing_name = thing_name

        if len(thing_owner) > 13:
            raise ValueError("Not a valid thing_owner: field must contain "
                             "less then 13 characters")
        self.thing_owner = thing_owner

        if len(thing_maintainer) > 13:
            raise ValueError("Not a valid thing_maintainer: field must "
                             "contain less then 13 characters")
        self.thing_maintainer = thing_maintainer

        if len(thing_use_pol) > 12:
            raise ValueError("Not a valid thing_use_pol: field must contain "
                             "less then 12 characters")
        self.thing_use_pol = thing_use_pol

        if len(thing_discard_pol) > 12:
            raise ValueError("Not a valid thing_discard_pol: field must "
                             "contain less then 12 characters")
        self.thing_discard_pol = thing_discard_pol

        return


    def _gen_qrcode(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=2,
            border=0)

        qr.add_data(urljoin(self.thing_base_url,self.thing_id))
        qr.make()
        img = qr.make_image()

        bmp = BytesIO()
        img.save(bmp, kind="BMP")
        bmp.seek(0)

        return bmp.read()

    def _labelbuf_append_string(self, string):
        self.labelbuf.append(bytes(string, "CP437"))

    def build(self):
        self.labelbuf = []
        ### GENERAL SETTINGS reseted after turn off ###
        self._labelbuf_append_string(STX+"KI<5"+CR)     # german char set
        self._labelbuf_append_string(STX+"m"+CR)        # use metric system
        self._labelbuf_append_string(STX+"KX0025"+CR)   # 25mm label[0] height
        self._labelbuf_append_string(STX+"f740"+CR)     # stop position for back feed

        ### QR-Code transmitting ###
        self._labelbuf_append_string(STX+"IAbqrcode"+CR) # write bmp into ram as "qrcode"
        self.labelbuf.append(self._gen_qrcode())


        self._labelbuf_append_string(STX+"L"+CR) # enter label[0] formatting mode

        self._labelbuf_append_string("1Y1100000110030qrcode"+CR) # qrcode

        self._labelbuf_append_string("191100001830030Eingetragenes Inventar des OpenLab Augsburg e. V."+CR) # header

        self._labelbuf_append_string("121100001310225"+self.thing_name+CR)             # Name
        self._labelbuf_append_string("111100000900225ID: "+self.thing_id+CR)           # ID

        self._labelbuf_append_string("111100000420225OWN: "+self.thing_owner+CR)       # Owner
        self._labelbuf_append_string("111100000070225MNT: "+self.thing_maintainer+CR)  # Maintainer

        self._labelbuf_append_string("111100000420670USE: "+self.thing_use_pol+CR)     # Usage
        self._labelbuf_append_string("111100000070670DIS: "+self.thing_discard_pol+CR) # Discard

        self._labelbuf_append_string("1d2108500920853"+self.thing_id+CR)               # EAN

        self._labelbuf_append_string("E"+CR) # end label[0] formatting mode

        return self.labelbuf
