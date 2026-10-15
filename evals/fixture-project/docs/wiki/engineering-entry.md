# Engineering entry

This is a synthetic fixture. It has an injected article dependency, a legacy
data/null client and small tag rules. There is no HTTP server, account system,
installed provider, external model or live evidence.

| Change question | Route | Local section |
|---|---|---|
| Preserve service/client failures | public-api | [Public API](interfaces.md#public-api) |
| Replace provider or optional counts | external-source | [External dependency](interfaces.md#external-source) |
| Replace tag suggestions | tagger | [Model interface](interfaces.md#tagger) |
| Change conflict resolution | tag-rules | [Tag policy](interfaces.md#tag-rules) |
| Timeout, late reply, retry bound | recovery | [Recovery model and diagrams](engineering-contracts.md#recovery) |
| Byte offsets, endian and mask | wire-format | [Serializer contract](engineering-contracts.md#wire-format) |
| System responsibilities and runtime | project-views | [Architecture and deployment](project-views.md#architecture) |

The project uses all six view kinds: architecture/deployment in project-views,
article flow there via public-api, wire data model there via wire-format, and
recovery sequence/state views in engineering-contracts. Local tasks need only the
views that answer their question; six kinds are checked at project scope.

Query the skill helper against this fixture root. The generated
[route index](route-index.md) shows current positions. Read the relevant section,
draft a plan, then inspect only the cited implementation before editing.
