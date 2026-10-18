# Feature completeness as a delivery contract

Use for feature design, implementation plans, documentation changes and completion
claims. Begin with the user's observable result and list the capabilities required
to reach it. Do not infer requirements solely from existing files, and do not add
speculative capabilities: identify confirmed requirements, necessary dependencies,
proposed choices and unresolved decisions separately.

## Eight dimensions every feature entrance must answer

| Dimension | Required explanation |
|---|---|
| Purpose and completion | Starting point, observable outcome, necessary sub-capabilities and scoped exit conditions |
| Actors and access | Resource owner, operator, viewer, producer/consumer roles, approval, access and partitions |
| Environment and release | Deployment versus account attributes, flags/audiences, versions and clients; code/build/deployed/observed evidence |
| Inputs and outputs | Which fields are copied, entered, uploaded or derived; interfaces and actual rendering; omissions/privacy projections |
| Dependencies and clients | Actual producers, writers, readers and displays; applicable notifications/money/calendar/other domains and Web/mobile consumption |
| State and failure | Normal/rejected paths, partial commits, retries/idempotency, backlinks, withdrawal/deletion, compensation and recovery limits |
| Edit and verification | Actual edit seams, shared authority, impact pages, narrow tests and real workflow acceptance; evidence limits |
| Remaining capability | Required but missing entries/fields/writers/consumers/design/acceptance, and tracked unknown facts |

Each dimension has an explicit outcome: evidence reviewed, implementation gap,
not yet verified, or not applicable with a reason. Link the explanation to the
local mechanism and source; gaps/unknowns have the project's existing work/debt
tracking destination. A reusable summary table is useful, but use the project's
native format. Mechanism leaves may link to the enclosing feature contract rather
than duplicate it. Whether a page is really a feature entrance requires review;
classification is not a waiver for a page that routes a user workflow.

## Two distinct completion claims

Documentation is usable when it answers the dimensions honestly and exposes all
known unresolved work. Product completion additionally requires the necessary
capabilities to be connected and scoped actors/clients/failure paths to have the
appropriate acceptance evidence. A record with tracked gaps can pass a structure
check while the feature remains incomplete. Never relabel missing implementation
as merely a documentation omission, or mark all dimensions checked just because
locators resolve.

Derive at least one ordinary end-to-end scenario, relevant role/viewer and
configuration variants, and a meaningful failure/partial-success scenario. Verify
fields at the real writer and consumer. Do not use admin visibility, a declaration,
a generated index or a renderer as proof of another actor's workflow. Do not
silently combine a share checkbox, an independent composer and a media uploader
into an integrated one-click feature.

## Enforce through the existing workflow

Put the contract in the project's page template, task plan, closeout and developer
entry. Reuse native parsers/gates where available; structural checks should catch
omitted dimensions, empty placeholders, unsupported status values, absent evidence,
missing tracking for gaps and removal/downgrade of an adopted record. Exercise
those omissions as mutants. Report gaps/unknowns distinctly even when structure
passes. Evidence-linked prose still needs semantic review.

For existing large wikis, inventory unclassified/unreviewed material rather than
mass-filling fake passes. Require classification and the applicable contract for
new/changed pages; preserve adopted records and make remaining coverage visible.
A reduction-only legacy count can complement change checks. Explain exactly which
pages and changes are enforced, and record rollout gaps. Do not describe a partial
migration as site-wide review. Legitimate scope restructuring needs an explicit
reviewed migration, not a silent downgrade to evade validation.

SoulNest's native implementation uses its existing wikiModel parser, check-wiki-touch
and COVERAGE generator. It exemplifies enforcement without requiring this skill's
Python manifest or copying its TypeScript parser into unrelated repositories.

For each functional unit, the producer/consumer dimension needs both a complete
scoped textual inventory and an identity-matched rendered relationship graph; see
[producer–consumer views](producer-consumer-views.md). A summary link alone cannot
stand in for the actual endpoints and relations.

For framework/design audits, also assess design fitness independently from code
completion; use [systematic design review](systematic-design-review.md). Necessary
capabilities may require completing an already reasonable framework, correcting a
weak boundary, or a dependency-triggered decision. A gap list alone is not a design.

## Configuration that changes presentation

For configurable presentation (themes, page builders, skins), trace selection,
effective configuration and actual rendering separately. A registered resource,
typed option or provider is not evidence that the selected resource is consumed.
Record ownership and precedence: platform default, viewer preference, public
owner configuration and temporary preview may have different write and render scopes.
Where applicable, inspect CSS inheritance, component context and portal destinations
independently; a boundary in one does not establish the others. Check pre-paint and
live updates against the same policy, and preserve deliberate reading preferences
rather than silently changing a null/default contract during isolation work.

If local recipes are generated from source tokens, verify all relevant declaration
blocks and test freshness; exclude responsive and accessibility rules that must keep
cascading. A new skin in a showcase establishes framework adoption there, not every
legacy page, cross-device persistence, another client or production rollout.

## Platform policy activation

For a service-wide toggle, inventory the actual protocol operations it intercepts,
not just screens labelled with the feature name. Include SDK calls, server-side
raw requests, background clients and other applications; a settings form can
consume the same operation as an anonymous entry form. Trace build-time public
configuration separately from runtime secrets and the effective service policy.

Distinguish provisioned resource, wired client, enabled policy and accepted runtime
behavior. A dashboard success or an env file is evidence only for its own stage.
Avoid claims such as "configuration only" or "zero risk" until every affected
caller and deployed client version has been checked. Document the rollout order,
compatibility decision, missing/error/retry behavior and positive/negative exit
evidence before enabling the shared policy. One-use artifacts must have a single
final consumer; a preliminary check may consume the artifact needed downstream.
