def build_resource_file(client, platform):
    selected_features = client.selected_features_json

    sections = []

    if selected_features.get("macros"):
        sections.append(build_macros_section(client))

    if selected_features.get("views"):
        sections.append(build_views_section(client))

    if selected_features.get("rules"):
        sections.append(build_rules_section(client))

    return {
        "client": client.name,
        "platform": platform.name,
        "sections": sections,
    }