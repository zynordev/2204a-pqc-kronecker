"""H1 dış doğrulaması: NIST ACVP resmî test vektörleri (ADR 0002)."""

import gzip
import json
import pathlib

import pytest

from pqc import mlkem
from pqc.parametreler import PARAMETRELER

_KLASOR = pathlib.Path(__file__).parent / "vektorler"


def _vakalar(dosya: str, fonksiyon: str | None = None) -> list:
    return list(_vaka_uret(dosya, fonksiyon))


def _vaka_uret(dosya: str, fonksiyon: str | None):
    with gzip.open(_KLASOR / f"{dosya}.json.gz", "rt") as f:
        veri = json.load(f)
    for grup in veri["testGroups"]:
        if fonksiyon is not None and grup["function"] != fonksiyon:
            continue
        p = PARAMETRELER[grup["parameterSet"]]
        for vaka in grup["tests"]:
            yield pytest.param(p, vaka, id=f"{p.ad}-tc{vaka['tcId']}")


def _b(hex_metin: str) -> bytes:
    return bytes.fromhex(hex_metin)


@pytest.mark.parametrize("p,vaka", _vakalar("ML-KEM-keyGen-FIPS203"))
def test_keygen(p, vaka):
    ek, dk = mlkem.keygen_internal(_b(vaka["d"]), _b(vaka["z"]), p)
    assert ek == _b(vaka["ek"])
    assert dk == _b(vaka["dk"])


@pytest.mark.parametrize("p,vaka", _vakalar("ML-KEM-encapDecap-FIPS203", "encapsulation"))
def test_encaps(p, vaka):
    K, c = mlkem.encaps_internal(_b(vaka["ek"]), _b(vaka["m"]), p)
    assert c == _b(vaka["c"])
    assert K == _b(vaka["k"])


@pytest.mark.parametrize("p,vaka", _vakalar("ML-KEM-encapDecap-FIPS203", "decapsulation"))
def test_decaps(p, vaka):
    # "modified ciphertext" vakaları örtük reddetmeyi (K̄ = J(z‖c)) sınar.
    assert mlkem.decaps_internal(_b(vaka["dk"]), _b(vaka["c"]), p) == _b(vaka["k"])


@pytest.mark.parametrize("p,vaka", _vakalar("ML-KEM-encapDecap-FIPS203", "encapsulationKeyCheck"))
def test_ek_kontrolu(p, vaka):
    assert mlkem.ek_gecerli(_b(vaka["ek"]), p) == vaka["testPassed"]


@pytest.mark.parametrize("p,vaka", _vakalar("ML-KEM-encapDecap-FIPS203", "decapsulationKeyCheck"))
def test_dk_kontrolu(p, vaka):
    assert mlkem.dk_gecerli(_b(vaka["dk"]), p) == vaka["testPassed"]
