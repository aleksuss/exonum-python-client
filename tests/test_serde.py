from exonum.datatypes import EncodingStruct, SocketAddr, Str, Vec, i64, u8, u16, Uuid, Decimal
from uuid import uuid4

def test_simple():
    class X(metaclass=EncodingStruct):
        first = u8
        second = u8
        third = i64

    x1 = X(first=1, second=2, third=-658979879)
    b = x1.to_bytes()
    x2 = X.read_buffer(b)

    assert x1.first == x2.first
    assert x1.second == x2.second
    assert x1.third == x2.third


def test_simple_string():
    class X(metaclass=EncodingStruct):
        first = Str
        second = u8
        third = i64
        fourth = Str

    x1 = X(first="Это строка",
           second=2,
           third=-658979879,
           fourth="یہ بھی ایک تار ہے")

    b = x1.to_bytes()
    x2 = X.read_buffer(b)
    assert x1.first == x2.first
    assert x1.second == x2.second
    assert x1.third == x2.third
    assert x1.fourth == x2.fourth


def test_vec():
    class X(metaclass=EncodingStruct):
        first = Vec(u16)
        second = Str

    x1 = X(first=[1, 2, 3, 4, 5],
           second="фывапролдж!")
    b = x1.to_bytes()
    x2 = X.read_buffer(b)

    assert x1.first == x2.first
    assert x1.second == x2.second


def test_vec_from_rust():
    class X(metaclass=EncodingStruct):
        first = Vec(u16)
        second = Str

    with open("tests/test_data/boo.bin", "rb") as f:
        x = X.read_buffer(f.read())

    assert x.first == [65, 1, 63]
    assert x.second == "Привет из exonum"


def test_inner():
    class X(metaclass=EncodingStruct):
        first = Vec(u16)
        second = Str

    class Y(metaclass=EncodingStruct):
        k = i64
        j = Vec(X)

    y = Y(k=-1000000,
          j=[X(first=[1, 2, 3, 4, 5], second="x one"),
             X(first=[6, 7, 8, 9], second="x two")])
    b = y.to_bytes()

    y2 = Y.read_buffer(b)

    assert y.k == y2.k
    assert y.j == y2.j

    s = ("Y (k = i64(-1000000), "
         "j = Vec<X> ["
         "X (first = Vec<u16> [u16(1), u16(2), u16(3), u16(4), u16(5)], "
         "second = Str(x one)), "
         "X (first = Vec<u16> [u16(6), u16(7), u16(8), u16(9)],"
         " second = Str(x two))"
         "])")

    assert str(y) == s
    assert str(y2) == s


def test_ip_uuid():
    class U(metaclass=EncodingStruct):
        soc = Vec(SocketAddr)
        ids = Vec(Uuid)

    u = U(soc=[("10.1.1.1", 8080), ("192.168.1.1", 9000)],
          ids=[uuid4(), uuid4()])

    b = u.to_bytes()
    u2 = U.read_buffer(b)
    assert u == u2

def test_decimals():
    class D(metaclass=EncodingStruct):
        d = Decimal
    d = D(d="192837.123")
    b = d.to_bytes()
    d2 = D.read_buffer(b)
    assert d.d == d2.d
