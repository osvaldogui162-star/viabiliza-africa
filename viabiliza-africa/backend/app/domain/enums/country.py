from enum import Enum


class Country(str, Enum):
    """Países africanos e mercados-alvo prioritários."""

    ANGOLA = "AO"
    SOUTH_AFRICA = "ZA"
    NIGERIA = "NG"
    KENYA = "KE"
    GHANA = "GH"
    MOZAMBIQUE = "MZ"
    TANZANIA = "TZ"
    SENEGAL = "SN"
    CAMEROON = "CM"
    COTE_DIVOIRE = "CI"
    ETHIOPIA = "ET"
    EGYPT = "EG"
    MOROCCO = "MA"
    RWANDA = "RW"
    UGANDA = "UG"
    ZAMBIA = "ZM"
    BOTSWANA = "BW"
    NAMIBIA = "NA"
    CONGO_DRC = "CD"
    GABON = "GA"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value.upper() in cls.values()

    @property
    def label_pt(self) -> str:
        labels = {
            Country.ANGOLA: "Angola",
            Country.SOUTH_AFRICA: "África do Sul",
            Country.NIGERIA: "Nigéria",
            Country.KENYA: "Quénia",
            Country.GHANA: "Gana",
            Country.MOZAMBIQUE: "Moçambique",
            Country.TANZANIA: "Tanzânia",
            Country.SENEGAL: "Senegal",
            Country.CAMEROON: "Camarões",
            Country.COTE_DIVOIRE: "Costa do Marfim",
            Country.ETHIOPIA: "Etiópia",
            Country.EGYPT: "Egipto",
            Country.MOROCCO: "Marrocos",
            Country.RWANDA: "Ruanda",
            Country.UGANDA: "Uganda",
            Country.ZAMBIA: "Zâmbia",
            Country.BOTSWANA: "Botswana",
            Country.NAMIBIA: "Namíbia",
            Country.CONGO_DRC: "Rep. Dem. do Congo",
            Country.GABON: "Gabão",
        }
        return labels.get(self, self.value)
