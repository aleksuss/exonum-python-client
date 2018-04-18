import struct
import sys
import io

import ipaddress
import nanotime
from datetime import datetime
from uuid import UUID


from types import FunctionType
from collections import OrderedDict

# do we need this at all?

SIGNATURE_LEN = 64  # bytes
SERVICE_DATA_LEN = 10  # bytes


class ExonumField:
    sz = 1
    fmt = None

    def __init__(self, val):
        self.val = val

    @classmethod
    def read(cls, buf, offset):
        val, =  struct.unpack_from(cls.fmt, buf, offset=offset)
        return cls(val)

    def write(self):
        return struct.pack(self.fmt, self.val)

    def __str__(self):
        return "{} {}".format(self.__class__, self.val)

class Exonum:
    class boolean(ExonumField):
        fmt = '<B'

    class u8(ExonumField):
        fmt = '<B'

    class u16(ExonumField):
        sz = 2
        fmt = '<H'

    class u32(ExonumField):
        sz = 4
        fmt = '<I'

    class u64(ExonumField):
        sz = 8
        fmt = '<Q'

    class i8(ExonumField):
        fmt = '<b'

    class i16(ExonumField):
        sz = 2
        fmt = '<h'

    class i32(ExonumField):
        sz = 4
        fmt = '<i'

    class i64(ExonumField):
        sz = 8
        fmt = '<q'

    class UnsupportedDatatype(Exception):
        pass

    class DateTime(ExonumField):
        sz = 12
        fmt = '<qI'

        def __init__(self, val):
            if isinstance(val, (float, int)):
                self.val = nanotime.timestamp(val)
            elif isinstance(val, datetime):
                self.val = nanotime.datetime(val)
            elif isinstance(val, nanotime.nanotime):
                self.val = val
            else:
                raise Exonum.UnsupportedDatatype(
                    "Type {} is not supported for initializing DateTime"
                    .format(type(val)))

        def write(self):
            sec = int(self.val.seconds())
            nan = (self.val - nanotime.seconds(sec)).nanoseconds()
            print(struct.pack(self.fmt, sec, nan))
            return struct.pack(self.fmt, sec, nan)

        @classmethod
        def read(cls, buf, offset):
            sec, nan = struct.unpack_from(cls.fmt, buf, offset=offset)
            return cls(nanotime.seconds(sec) + nanotime.nanoseconds(nan))

    class Uuid(ExonumField):
        sz =16
        fmt = "<16B"

        def __init__(self, val):
            if isinstance(val, UUID):
                self.val = val
            else:
                self.val = UUID(val)

        def write(self):
            return self.val.bytes

        @classmethod
        def read(cls, buf, offset):
            data, = struct.unpack_from(cls.fmt, buf, offset=offset)
            return cls(UUID(bytes=data))

    class SocketAddr(ExonumField):
        sz = 6
        fmt = "<4BH"

        def __init__(self, val):
            ip = ipaddress.IPv4Address(val[0])
            self.val = (ip, val[1])

        def write(self):
            return self.val[0].packed + struct.pack("<H", self.val[1])

        @classmethod
        def read(cls, buf, offset):
            data = struct.unpack_from(cls.fmt, buf, offset=offset)
            return cls(data)


    # dyn size
    class vec(ExonumField):
        pass

    class str(ExonumField):
        pass


class ExonumBase:
    def __init__(self, **kwargs):
        for field in self.__exonum_fields__:
            cls = getattr(self.__class__, field)
            setattr(self, field,  cls(kwargs[field]))

    def write(self):
        b = io.BytesIO()
        for field in self.__exonum_fields__:
            field = getattr(self, field)
            data = field.write()
            b.write(data)
        return b.getvalue()

    @classmethod
    def read(cls, bytestring):
        data = {}
        offset = 0
        for field in cls.__exonum_fields__:
            fcls = getattr(cls, field)
            val = fcls.read(bytestring, offset)
            offset += fcls.sz
            print(val)
            data[field] = val
        return cls(**data)


class ExonumMeta(type):
    _exclude = set(dir(type))
    def __new__(self, name, bases, classdict):
        fields = [k for k, v in classdict.items()
                  if k not in self._exclude
                  and not isinstance(v, (FunctionType, classmethod, staticmethod))]
        classdict['__exonum_fields__'] = fields
        return type(name, (ExonumBase, *bases), classdict)


# https://www.python.org/dev/peps/pep-0520/
if sys.version_info.major < 3 or \
       (sys.version_info.major == 3 and sys.version_info.minor < 6):
    ExonumMeta.__prepare__  = classmethod(lambda *_: OrderedDict())


class Fuck(metaclass = ExonumMeta):
    first = Exonum.u8
    second = Exonum.u8
    time = Exonum.DateTime
    u = Exonum.Uuid
    addr = Exonum.SocketAddr
