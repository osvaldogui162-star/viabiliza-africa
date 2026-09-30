from app.domain.enums.project_capability import ProjectCapability
from app.domain.enums.share_permission import SharePermission


def default_capabilities(permission: SharePermission) -> dict[str, bool]:
    base = {key: False for key in ProjectCapability.keys()}
    base[ProjectCapability.VIEW_PROJECT.value] = True
    if permission == SharePermission.COLLABORATE:
        base[ProjectCapability.MANAGE_COLLABORATION.value] = True
    return base


def merge_capabilities(
    permission: SharePermission,
    overrides: dict[str, bool] | None,
) -> dict[str, bool]:
    caps = default_capabilities(permission)
    if not overrides:
        return caps
    for key, value in overrides.items():
        if key in caps and isinstance(value, bool):
            caps[key] = value
    if not caps[ProjectCapability.VIEW_PROJECT.value]:
        caps[ProjectCapability.VIEW_PROJECT.value] = True
    return caps


def capability_labels_pt() -> dict[str, str]:
    return {
        ProjectCapability.VIEW_PROJECT.value: "Ver projecto",
        ProjectCapability.EDIT_PROJECT.value: "Editar dados do projecto",
        ProjectCapability.MANAGE_COSTS.value: "Gerir custos e orçamento",
        ProjectCapability.RUN_ANALYSIS.value: "Executar análises financeiras",
        ProjectCapability.MANAGE_REPORTS.value: "Gerar e exportar relatórios",
        ProjectCapability.MANAGE_COLLABORATION.value: "Tarefas, chat e equipa",
        ProjectCapability.MANAGE_INGESTION.value: "Importar e ingerir dados",
        ProjectCapability.VIEW_FINANCING.value: "Ver financiamento bancário",
    }
