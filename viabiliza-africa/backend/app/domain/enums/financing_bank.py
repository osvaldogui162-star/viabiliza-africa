from enum import Enum





class FinancingBank(str, Enum):

    """Bancos angolanos para financiamento / taxa de desconto do projeto."""



    BFA = "bfa"

    BAI = "bai"

    BIC = "bic"

    ATL = "atl"

    SBA = "sba"

    BPC = "bpc"

    BDA = "bda"

    SOL = "sol"

    BNI = "bni"

    KEVE = "keve"

    BCGA = "bcga"

    BCI = "bci"

    ECONOMICO = "economico"



    @classmethod

    def values(cls) -> list[str]:

        return [b.value for b in cls]



    @classmethod

    def is_valid(cls, value: str) -> bool:

        return value in cls.values()



    @property

    def label_pt(self) -> str:

        return {

            FinancingBank.BFA: "Banco de Fomento Angola (BFA)",

            FinancingBank.BAI: "Banco Angolano de Investimentos (BAI)",

            FinancingBank.BIC: "Banco BIC",

            FinancingBank.ATL: "Banco Millennium Atlântico (BMA)",

            FinancingBank.SBA: "Standard Bank Angola (SBA)",

            FinancingBank.BPC: "Banco de Poupança e Crédito (BPC)",

            FinancingBank.BDA: "Banco de Desenvolvimento de Angola (BDA)",

            FinancingBank.SOL: "Banco Sol",

            FinancingBank.BNI: "Banco de Negócios Internacional (BNI)",

            FinancingBank.KEVE: "Banco Keve",

            FinancingBank.BCGA: "Banco Caixa Geral Angola (BCGA)",

            FinancingBank.BCI: "Banco de Comércio e Indústria (BCI)",

            FinancingBank.ECONOMICO: "Banco Económico",

        }[self]



    @property

    def website(self) -> str:

        return {

            FinancingBank.BFA: "https://www.bfa.ao",

            FinancingBank.BAI: "https://www.bancobai.ao",

            FinancingBank.BIC: "https://www.bancobic.ao",

            FinancingBank.ATL: "https://www.atlantico.ao",

            FinancingBank.SBA: "https://www.standardbank.co.ao",

            FinancingBank.BPC: "https://www.bpc.ao",

            FinancingBank.BDA: "https://www.bda.ao",

            FinancingBank.SOL: "https://www.bancosol.ao",

            FinancingBank.BNI: "https://www.bni.ao",

            FinancingBank.KEVE: "https://www.bancokeve.ao",

            FinancingBank.BCGA: "https://www.caixaangola.ao",

            FinancingBank.BCI: "https://www.bci.ao",

            FinancingBank.ECONOMICO: "https://www.bancoeconomico.ao",

        }[self]



    @property

    def logo_path(self) -> str:

        """Caminho público do logótipo (frontend/public/banks)."""

        return {

            FinancingBank.BFA: "/banks/bfa.svg",

            FinancingBank.BAI: "/banks/bai.svg",

            FinancingBank.BIC: "/banks/bic.svg",

            FinancingBank.ATL: "/banks/atl.png",

            FinancingBank.SBA: "/banks/sba.png",

            FinancingBank.BPC: "/banks/bpc.png",

            FinancingBank.BDA: "/banks/bda.png",

            FinancingBank.SOL: "/banks/sol.svg",

            FinancingBank.BNI: "/banks/bni.svg",

            FinancingBank.KEVE: "/banks/keve.png",

            FinancingBank.BCGA: "/banks/bcga.svg",

            FinancingBank.BCI: "/banks/bci.svg",

            FinancingBank.ECONOMICO: "/banks/economico.svg",

        }[self]


