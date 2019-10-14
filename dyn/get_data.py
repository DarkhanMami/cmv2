import struct
from dyn import defines as df
import os


OUTPUT_FILENAME = ""


class ReadSKVFile():
    def __init__(self, filename):
        self.static_data = {}
        self.block_data = {}
        self.array_data = []
        self.filename = filename
        self.x = []
        self.y = []
        self.read_skv_file()

    def namedtuple_dict(self, d, data):
        return d['namedtuple']._asdict(d['namedtuple']._make(struct.unpack(d['struct'], data)))

    def read_skv_static(self, file_desc):
        d = df.SkvStaticData['SkvStaticData']
        data = file_desc.read(struct.calcsize(d['struct']))
        d['dict'] = self.namedtuple_dict(d, data)

    def read_skv_blocks(self, file_desc):
        blocks_count = df.SkvStaticData['SkvStaticData']['dict']['kolBlock']
        skv_blocks = []
        for kol in range(blocks_count):
            for item in df.SkvBlock:
                d = df.SkvBlock[item]
                if item == 'Data':
                    kol = df.SkvBlock['DataSkvKust']['dict']['PtUp'] + df.SkvBlock['DataSkvKust']['dict']['PtDn'] - 1
                    d['struct'] = '<%df' % kol
                    data = file_desc.read(struct.calcsize(d['struct']))
                    d['array'] = list(struct.unpack(d['struct'], data))
                else:
                    data = file_desc.read(struct.calcsize(d['struct']))
                    d['dict'] = self.namedtuple_dict(d, data)

            skv_blocks.append(df.SkvBlock)

        return skv_blocks

    def save_dict(self, d, f):
        for k, v in d.items():
            f.write('%s = %s\n' % (k, v))

    def read_skv_file(self):
        with open(self.filename, "rb") as f:
            self.read_skv_static(f)
            skv_blocks = self.read_skv_blocks(f)
        for ind in range(len(skv_blocks)):
            self.array_data = skv_blocks[ind]['Data']['array']
            self.block_data = dict(skv_blocks[ind]['DataSkvKust']['dict'])
            self.static_data = dict(df.SkvStaticData['SkvStaticData']['dict'])
            up = self.block_data['PtUp']
            dn = self.block_data['PtDn']
            lhoda = self.block_data['LHoda']
            x1 = []
            x2 = []
            tmp = 0
            for i in range(0, up):
                tmp += lhoda / up
                x1.append(tmp)
            tmp = lhoda
            for i in range(1, dn):
                tmp -= lhoda / dn
                x2.append(tmp)
            x = x1 + x2
            y = self.array_data
            self.x = x
            self.y = y
            if len(x) > 0 and len(y) > 0:
                return
