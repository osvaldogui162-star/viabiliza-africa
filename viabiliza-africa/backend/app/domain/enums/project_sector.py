from enum import Enum


class ProjectSector(str, Enum):
    """Setores económicos suportados (foco mercado africano)."""

    AGRICULTURE = "agriculture"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    ENERGY = "energy"
    CONSTRUCTION = "construction"
    TOURISM = "tourism"
    TECHNOLOGY = "technology"
    HEALTH = "health"
    EDUCATION = "education"
    MINING = "mining"
    RETAIL = "retail"
    TRANSPORT = "transport"
    REAL_ESTATE = "real_estate"
    OTHER = "other"

    @classmethod
    def values(cls) -> list[str]:
        return [s.value for s in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()

    @property
    def label_pt(self) -> str:
        labels = {
            ProjectSector.AGRICULTURE: "Agricultura",
            ProjectSector.MANUFACTURING: "Indústria",
            ProjectSector.SERVICES: "Serviços",
            ProjectSector.ENERGY: "Energia",
            ProjectSector.CONSTRUCTION: "Construção",
            ProjectSector.TOURISM: "Turismo",
            ProjectSector.TECHNOLOGY: "Tecnologia",
            ProjectSector.HEALTH: "Saúde",
            ProjectSector.EDUCATION: "Educação",
            ProjectSector.MINING: "Mineração",
            ProjectSector.RETAIL: "Retalho",
            ProjectSector.TRANSPORT: "Transportes",
            ProjectSector.REAL_ESTATE: "Imobiliário",
            ProjectSector.OTHER: "Outro",
        }
        return labels.get(self, self.value)
