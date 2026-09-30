"""Catálogo de agências bancárias angolanas por instituição."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BankBranch:
    code: str
    label: str
    bank_code: str
    province: str
    municipality: str
    address: str
    active: bool = True


# Agências de referência (sede + principais pontos de atendimento)
BANK_BRANCHES: tuple[BankBranch, ...] = (
    # BFA
    BankBranch("bfa_sede_luanda", "Sede — Luanda (Mutamba)", "bfa", "luanda", "luanda", "Largo Saydi Mingas, Mutamba"),
    BankBranch("bfa_kilamba", "Agência Kilamba", "bfa", "luanda", "belas", "Centralidade do Kilamba, Bloco C"),
    BankBranch("bfa_talatona", "Agência Talatona", "bfa", "luanda", "talatona", "Via S10, Condomínio Belas Business Park"),
    BankBranch("bfa_viana", "Agência Viana", "bfa", "luanda", "viana", "Estrada de Viana, Zona Industrial"),
    BankBranch("bfa_benguela", "Agência Benguela", "bfa", "benguela", "benguela", "Av. Ho Chi Minh, Centro"),
    BankBranch("bfa_huambo", "Agência Huambo", "bfa", "huambo", "huambo", "Av. Agostinho Neto"),
    # BAI
    BankBranch("bai_sede_luanda", "Sede — Luanda (Maculusso)", "bai", "luanda", "luanda", "Rua Amílcar Cabral, Maculusso"),
    BankBranch("bai_talatona", "Agência Talatona", "bai", "luanda", "talatona", "Belas Shopping, Talatona"),
    BankBranch("bai_cacuaco", "Agência Cacuaco", "bai", "luanda", "cacuaco", "Estrada de Cacuaco, Bairro Kikolo"),
    BankBranch("bai_lobito", "Agência Lobito", "bai", "benguela", "lobito", "Av. da Independência"),
    BankBranch("bai_lubango", "Agência Lubango", "bai", "huila", "lubango", "Rua Comandante Gika"),
    # BIC
    BankBranch("bic_sede_luanda", "Sede — Luanda", "bic", "luanda", "luanda", "Av. 4 de Fevereiro, Baixa de Luanda"),
    BankBranch("bic_kilamba_kiaxi", "Agência Kilamba Kiaxi", "bic", "luanda", "kilamba_kiaxi", "Av. Deolinda Rodrigues"),
    BankBranch("bic_viana", "Agência Viana", "bic", "luanda", "viana", "Estrada de Viana"),
    BankBranch("bic_benguela", "Agência Benguela", "bic", "benguela", "benguela", "Rua Henrique de Carvalho"),
    # ATL / Millennium
    BankBranch("atl_sede_luanda", "Sede — Luanda", "atl", "luanda", "luanda", "Rua Major Kanhangulo, Ingombota"),
    BankBranch("atl_maianga", "Agência Maianga", "atl", "luanda", "luanda", "Av. Comandante Valódia"),
    BankBranch("atl_benguela", "Agência Benguela", "atl", "benguela", "benguela", "Av. 1º de Agosto"),
    # BPC
    BankBranch("bpc_sede_luanda", "Sede — Luanda", "bpc", "luanda", "luanda", "Av. 4 de Fevereiro"),
    BankBranch("bpc_benfica", "Agência Benfica", "bpc", "luanda", "luanda", "Estrada de Benfica"),
    BankBranch("bpc_huambo", "Agência Huambo", "bpc", "huambo", "huambo", "Av. Agostinho Neto"),
    BankBranch("bpc_lubango", "Agência Lubango", "bpc", "huila", "lubango", "Av. Mártires de 27 de Maio"),
    # BDA
    BankBranch("bda_sede_luanda", "Sede — Luanda", "bda", "luanda", "luanda", "Av. Pedro de Castro Van-Dúnem Loy, Talatona"),
    BankBranch("bda_benguela", "Agência Benguela", "bda", "benguela", "benguela", "Rua Amílcar Cabral"),
    BankBranch("bda_huambo", "Agência Huambo", "bda", "huambo", "huambo", "Av. 21 de Janeiro"),
    # SOL
    BankBranch("sol_sede_luanda", "Sede — Luanda", "sol", "luanda", "luanda", "Rua Major Kanhangulo"),
    BankBranch("sol_talatona", "Agência Talatona", "sol", "luanda", "talatona", "Via AL2, Talatona"),
    # BNI
    BankBranch("bni_sede_luanda", "Sede — Luanda", "bni", "luanda", "luanda", "Av. 4 de Fevereiro"),
    BankBranch("bni_benguela", "Agência Benguela", "bni", "benguela", "benguela", "Av. Ho Chi Minh"),
    # KEVE
    BankBranch("keve_sede_luanda", "Sede — Luanda", "keve", "luanda", "luanda", "Rua Amílcar Cabral"),
    BankBranch("keve_viana", "Agência Viana", "keve", "luanda", "viana", "Estrada de Viana"),
    # BCGA
    BankBranch("bcga_sede_luanda", "Sede — Luanda", "bcga", "luanda", "luanda", "Av. Pedro de Castro Van-Dúnem Loy"),
    BankBranch("bcga_benguela", "Agência Benguela", "bcga", "benguela", "benguela", "Rua Henrique de Carvalho"),
    # BCI
    BankBranch("bci_sede_luanda", "Sede — Luanda", "bci", "luanda", "luanda", "Av. Comandante Valódia"),
    BankBranch("bci_kilamba", "Agência Kilamba", "bci", "luanda", "belas", "Centralidade do Kilamba"),
    # ECONÓMICO
    BankBranch("economico_sede_luanda", "Sede — Luanda", "economico", "luanda", "luanda", "Av. 4 de Fevereiro"),
    BankBranch("economico_talatona", "Agência Talatona", "economico", "luanda", "talatona", "Belas Business Park"),
    # SBA
    BankBranch("sba_sede_luanda", "Sede — Luanda", "sba", "luanda", "luanda", "Torres Rocha, Rua Major Kanhangulo"),
    BankBranch("sba_talatona", "Agência Talatona", "sba", "luanda", "talatona", "Via S10, Talatona"),
)


def list_bank_branches(
    bank_code: str,
    *,
    province: str | None = None,
    active_only: bool = True,
) -> list[dict]:
    code = bank_code.lower().strip()
    items = [b for b in BANK_BRANCHES if b.bank_code == code]
    if active_only:
        items = [b for b in items if b.active]
    if province:
        prov = province.lower().strip()
        items = [b for b in items if b.province == prov]
    return [
        {
            "value": b.code,
            "label": b.label,
            "province": b.province,
            "municipality": b.municipality,
            "address": b.address,
            "description": f"{b.municipality.replace('_', ' ').title()} · {b.address}",
        }
        for b in items
    ]
