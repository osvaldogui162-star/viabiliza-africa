"""Divisões administrativas de Angola (províncias e municípios — referência INE)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Municipality:
    code: str
    label: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class Province:
    code: str
    label: str
    latitude: float
    longitude: float
    municipalities: tuple[Municipality, ...]


# Coordenadas aproximadas dos centros administrativos (referência INE / OpenStreetMap)
ANGOLA_PROVINCES: tuple[Province, ...] = (
    Province(
        "bengo",
        "Bengo",
        -8.5725,
        13.6644,
        (
            Municipality("ambriz", "Ambriz", -7.8628, 13.1206),
            Municipality("dande", "Dande", -8.4500, 13.3833),
            Municipality("dondo", "Dondo", -9.0500, 14.1167),
            Municipality("nambuangongo", "Nambuangongo", -8.6333, 13.7833),
            Municipality("caxito", "Caxito", -8.5725, 13.6644),
        ),
    ),
    Province(
        "benguela",
        "Benguela",
        -12.5763,
        13.4055,
        (
            Municipality("ambriz", "Ambriz", -7.8628, 13.1206),
            Municipality("baia_farta", "Baía Farta", -12.6167, 13.2000),
            Municipality("balombo", "Balombo", -12.3500, 14.0833),
            Municipality("benguela", "Benguela", -12.5763, 13.4055),
            Municipality("bocoio", "Bocoio", -12.4333, 14.0167),
            Municipality("caimbambo", "Caimbambo", -12.9500, 13.9000),
            Municipality("catumbela", "Catumbela", -12.4167, 13.5500),
            Municipality("chongoroi", "Chongoroi", -13.2833, 13.9333),
            Municipality("cubal", "Cubal", -13.0333, 14.0167),
            Municipality("ganda", "Ganda", -12.5500, 14.1333),
            Municipality("lobito", "Lobito", -12.3644, 13.5361),
        ),
    ),
    Province(
        "bie",
        "Bié",
        -12.3592,
        17.2667,
        (
            Municipality("andulo", "Andulo", -11.4833, 16.7167),
            Municipality("camacupa", "Camacupa", -12.0167, 17.4833),
            Municipality("catabola", "Catabola", -12.1500, 17.2833),
            Municipality("chinguar", "Chinguar", -12.5667, 16.3333),
            Municipality("chitembo", "Chitembo", -12.8333, 16.6333),
            Municipality("cuemba", "Cuemba", -12.1500, 16.9000),
            Municipality("cunhinga", "Cunhinga", -12.9333, 16.3167),
            Municipality("kuito", "Kuito", -12.3592, 17.2667),
            Municipality("nkurenkuru", "Nharea", -12.2000, 17.2500),
        ),
    ),
    Province(
        "cabinda",
        "Cabinda",
        -5.5600,
        12.1900,
        (
            Municipality("belize", "Belize", -4.6667, 12.5833),
            Municipality("buco_zau", "Buco-Zau", -4.7833, 12.1333),
            Municipality("cabinda", "Cabinda", -5.5600, 12.1900),
            Municipality("cacongo", "Cacongo", -5.1833, 12.1333),
        ),
    ),
    Province(
        "cuando_cubango",
        "Cuando Cubango",
        -14.9167,
        19.9167,
        (
            Municipality("calai", "Calai", -17.8833, 19.5667),
            Municipality("cuangar", "Cuangar", -17.0333, 18.6500),
            Municipality("cuchi", "Cuchi", -14.6500, 18.9167),
            Municipality("cuito_cuanavale", "Cuito Cuanavale", -15.1500, 19.1667),
            Municipality("dirico", "Dirico", -16.5500, 21.3333),
            Municipality("mavinga", "Mavinga", -15.8333, 20.3500),
            Municipality("menongue", "Menongue", -14.9167, 19.9167),
            Municipality("nancova", "Nancova", -16.5000, 20.5000),
            Municipality("rivungo", "Rivungo", -17.0667, 20.7833),
        ),
    ),
    Province(
        "cuanza_norte",
        "Cuanza Norte",
        -9.3000,
        14.9167,
        (
            Municipality("ambaca", "Ambaca", -8.2167, 15.8500),
            Municipality("banga", "Banga", -9.4333, 14.7333),
            Municipality("bolongongo", "Bolongongo", -9.0667, 15.1333),
            Municipality("cambambe", "Cambambe", -9.2167, 14.2833),
            Municipality("cazengo", "Cazengo", -9.3000, 14.9167),
            Municipality("golungo_alto", "Golungo Alto", -9.1500, 15.2500),
            Municipality("gonguembo", "Gonguembo", -9.7833, 14.9667),
            Municipality("lucala", "Lucala", -9.2667, 15.3333),
            Municipality("ngonguembo", "Ngonguembo", -9.5000, 15.0833),
            Municipality("quiculungo", "Quiculungo", -9.1333, 15.1333),
        ),
    ),
    Province(
        "cuanza_sul",
        "Cuanza Sul",
        -11.2027,
        15.1743,
        (
            Municipality("amboim", "Amboim", -10.7333, 14.7833),
            Municipality("cassongue", "Cassongue", -11.3167, 15.0833),
            Municipality("conda", "Conda", -11.1333, 14.9333),
            Municipality("esuma", "Esuma", -11.4167, 15.3167),
            Municipality("libolo", "Libolo", -10.0333, 14.5833),
            Municipality("mussende", "Mussende", -10.7333, 15.3500),
            Municipality("porto_amboim", "Porto Amboim", -10.7333, 13.7667),
            Municipality("quibala", "Quibala", -10.7333, 14.9167),
            Municipality("quilenda", "Quilenda", -11.0167, 14.7667),
            Municipality("seles", "Seles", -11.4167, 15.0833),
            Municipality("sumbe", "Sumbe", -11.2027, 15.1743),
        ),
    ),
    Province(
        "cunene",
        "Cunene",
        -17.0667,
        15.7333,
        (
            Municipality("cahama", "Cahama", -16.2833, 14.3167),
            Municipality("cuanhama", "Cuanhama", -16.0667, 15.3167),
            Municipality("curoca", "Curoca", -17.2833, 14.4833),
            Municipality("cuvelai", "Cuvelai", -15.4667, 16.0500),
            Municipality("namacunde", "Namacunde", -17.3833, 14.9667),
            Municipality("ombadja", "Ombadja", -17.0667, 15.7333),
        ),
    ),
    Province(
        "huambo",
        "Huambo",
        -12.7761,
        15.7392,
        (
            Municipality("bailundo", "Bailundo", -12.3833, 15.5833),
            Municipality("caala", "Caála", -12.8500, 15.5667),
            Municipality("catchiungo", "Catchiungo", -12.5667, 15.9000),
            Municipality("ecunha", "Ecunha", -12.9500, 15.7333),
            Municipality("huambo", "Huambo", -12.7761, 15.7392),
            Municipality("londuimbali", "Londuimbali", -12.9833, 15.8833),
            Municipality("longonjo", "Longonjo", -12.9167, 15.2500),
            Municipality("municipio_ekunha", "Municipio da Ekunha", -12.9500, 15.7333),
            Municipality("tchicala_tcholoanga", "Tchicala-Tcholoanga", -12.9333, 15.3500),
            Municipality("tchindjenje", "Tchindjenje", -12.8167, 14.9333),
            Municipality("ucuma", "Ucuma", -12.6833, 15.0833),
        ),
    ),
    Province(
        "huila",
        "Huíla",
        -14.9175,
        13.4925,
        (
            Municipality("caconda", "Caconda", -13.7333, 15.0667),
            Municipality("cacula", "Cacula", -14.6500, 13.9000),
            Municipality("caluquembe", "Caluquembe", -13.7833, 14.6833),
            Municipality("chibia", "Chibia", -15.1833, 13.6833),
            Municipality("chicomba", "Chicomba", -14.9167, 13.7500),
            Municipality("chipindo", "Chipindo", -14.7333, 13.4167),
            Municipality("cuvango", "Cuvango", -14.2667, 16.9000),
            Municipality("gambos", "Gambos", -15.3500, 13.5500),
            Municipality("humpata", "Humpata", -15.0167, 13.3667),
            Municipality("jamba", "Jamba", -14.7667, 13.3500),
            Municipality("lubango", "Lubango", -14.9175, 13.4925),
            Municipality("matala", "Matala", -14.4167, 16.0167),
            Municipality("quilengues", "Quilengues", -14.5667, 13.7667),
            Municipality("quipungo", "Quipungo", -14.5500, 14.5500),
        ),
    ),
    Province(
        "luanda",
        "Luanda",
        -8.8390,
        13.2894,
        (
            Municipality("belas", "Belas", -8.9983, 13.2650),
            Municipality("cacuaco", "Cacuaco", -8.7867, 13.3733),
            Municipality("cazenga", "Cazenga", -8.8583, 13.3333),
            Municipality("icolo_e_bengo", "Ícolo e Bengo", -9.2500, 13.7333),
            Municipality("luanda", "Luanda", -8.8390, 13.2894),
            Municipality("quicama", "Quiçama", -9.3833, 13.2833),
            Municipality("kilamba_kiaxi", "Kilamba Kiaxi", -8.9333, 13.2333),
            Municipality("talatona", "Talatona", -8.9167, 13.1833),
            Municipality("viana", "Viana", -8.9000, 13.3667),
        ),
    ),
    Province(
        "lunda_norte",
        "Lunda Norte",
        -8.5833,
        20.5500,
        (
            Municipality("ambaca_ln", "Ambaca", -8.2167, 15.8500),
            Municipality("bangalas", "Bangalas", -8.7500, 20.5000),
            Municipality("cambulo", "Cambulo", -8.5833, 20.5500),
            Municipality("capenda_camulemba", "Capenda-Camulemba", -9.4333, 19.4333),
            Municipality("caungula", "Caungula", -8.3167, 19.3167),
            Municipality("chitato", "Chitato", -7.3500, 20.8167),
            Municipality("cuango", "Cuango", -9.1500, 18.3500),
            Municipality("cuilo", "Cuilo", -8.3500, 19.9000),
            Municipality("lubalo", "Lubalo", -8.5833, 20.5500),
            Municipality("lucapa", "Lucapa", -8.4167, 20.7500),
            Municipality("x_muteba", "Xá-Muteba", -8.5833, 20.5500),
        ),
    ),
    Province(
        "lunda_sul",
        "Lunda Sul",
        -10.7333,
        20.7833,
        (
            Municipality("cacolo", "Cacolo", -10.1500, 19.2667),
            Municipality("cucui", "Cucuí", -9.4167, 20.8000),
            Municipality("cameia", "Cameia", -10.4833, 20.1500),
            Municipality("dala", "Dala", -10.7333, 20.7833),
            Municipality("muconda", "Muconda", -10.6000, 20.8667),
            Municipality("saurimo", "Saurimo", -9.6167, 20.4000),
        ),
    ),
    Province(
        "malanje",
        "Malanje",
        -9.5400,
        16.3410,
        (
            Municipality("cacuso", "Cacuso", -9.4167, 15.7500),
            Municipality("calandula", "Calandula", -9.1167, 16.1333),
            Municipality("cambundi_catembo", "Cambundi-Catembo", -9.5833, 16.5833),
            Municipality("cangandala", "Cangandala", -9.7833, 16.0667),
            Municipality("caombo", "Caombo", -9.7500, 16.3333),
            Municipality("cuaba_nzogo", "Cuaba Nzogo", -9.5833, 16.3333),
            Municipality("cunda_dia_baze", "Cunda-Dia-Baze", -9.5833, 16.3333),
            Municipality("luquembo", "Luquembo", -9.5833, 16.3333),
            Municipality("malanje", "Malanje", -9.5400, 16.3410),
            Municipality("marimba", "Marimba", -9.5833, 16.3333),
            Municipality("massango", "Massango", -9.5833, 16.3333),
            Municipality("mucari", "Mucari", -9.5833, 16.3333),
            Municipality("quela", "Quela", -9.5833, 16.3333),
            Municipality("quirima", "Quirima", -9.5833, 16.3333),
        ),
    ),
    Province(
        "moxico",
        "Moxico",
        -11.3167,
        22.2333,
        (
            Municipality("alto_zambeze", "Alto Zambeze", -11.3167, 22.2333),
            Municipality("bundas", "Bundas", -11.3167, 22.2333),
            Municipality("camanongue", "Camanongue", -11.4333, 19.8833),
            Municipality("leua", "Léua", -11.6500, 20.9833),
            Municipality("luacano", "Luacano", -11.3167, 22.2333),
            Municipality("luau", "Luau", -10.7000, 22.2333),
            Municipality("luchazes", "Luchazes", -11.3167, 22.2333),
            Municipality("luena", "Luena", -11.3167, 22.2333),
            Municipality("moxico_leste", "Moxico Leste", -11.3167, 22.2333),
        ),
    ),
    Province(
        "namibe",
        "Namibe",
        -15.1961,
        12.1522,
        (
            Municipality("bibala", "Bibala", -14.7667, 13.3500),
            Municipality("camucuio", "Camucuio", -14.9000, 12.1333),
            Municipality("namibe", "Namibe", -15.1961, 12.1522),
            Municipality("tombua", "Tômbua", -15.8000, 11.8500),
            Municipality("virei", "Virei", -15.7167, 12.5333),
        ),
    ),
    Province(
        "uige",
        "Uíge",
        -7.6167,
        15.0500,
        (
            Municipality("ambuila", "Ambuila", -7.6167, 15.0500),
            Municipality("bungo", "Bungo", -7.6167, 15.0500),
            Municipality("bungo_nginga", "Bungo-Nginga", -7.6167, 15.0500),
            Municipality("cangola", "Cangola", -7.6167, 15.0500),
            Municipality("damba", "Damba", -7.6167, 15.0500),
            Municipality("macocola", "Macocola", -7.6167, 15.0500),
            Municipality("mucaba", "Mucaba", -7.6167, 15.0500),
            Municipality("negage", "Negage", -7.7500, 15.2833),
            Municipality("puri", "Puri", -7.6167, 15.0500),
            Municipality("quimbele", "Quimbele", -7.6167, 15.0500),
            Municipality("quitexe", "Quitexe", -7.6167, 15.0500),
            Municipality("songo", "Songo", -7.6167, 15.0500),
            Municipality("uige", "Uíge", -7.6167, 15.0500),
            Municipality("zombo", "Zombo", -7.6167, 15.0500),
        ),
    ),
    Province(
        "zaire",
        "Zaire",
        -6.2667,
        14.2500,
        (
            Municipality("cuimba", "Cuimba", -6.6500, 14.9000),
            Municipality("mbanza_kongo", "M'banza Kongo", -6.2667, 14.2500),
            Municipality("noqui", "Nóqui", -5.8667, 13.4333),
            Municipality("soyo", "Soyo", -6.1333, 12.3667),
            Municipality("tomboco", "Tomboco", -6.7667, 13.0167),
        ),
    ),
)

_PROVINCE_BY_CODE = {p.code: p for p in ANGOLA_PROVINCES}


def list_provinces() -> list[dict]:
    return [
        {
            "value": p.code,
            "label": p.label,
            "latitude": p.latitude,
            "longitude": p.longitude,
        }
        for p in ANGOLA_PROVINCES
    ]


def list_municipalities(province_code: str) -> list[dict]:
    province = _PROVINCE_BY_CODE.get(province_code.lower().strip())
    if province is None:
        return []
    return [
        {
            "value": m.code,
            "label": m.label,
            "latitude": m.latitude,
            "longitude": m.longitude,
        }
        for m in province.municipalities
    ]


def resolve_location(
    province_code: str,
    municipality_code: str,
) -> tuple[Municipality, Province] | None:
    province = _PROVINCE_BY_CODE.get(province_code.lower().strip())
    if province is None:
        return None
    municipality_code = municipality_code.lower().strip()
    for m in province.municipalities:
        if m.code == municipality_code:
            return m, province
    return None


def is_valid_province(code: str) -> bool:
    return code.lower().strip() in _PROVINCE_BY_CODE


def is_valid_municipality(province_code: str, municipality_code: str) -> bool:
    return resolve_location(province_code, municipality_code) is not None
