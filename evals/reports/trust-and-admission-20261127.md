# Admission layers and sender-asserted fields, 2026-11-27

Evidence for two additions to the shipped references:
[reachability is a chain of gates](../../project-wiki/references/feature-completeness.md#reachability-is-a-chain-of-gates)
and
[who asserts an identity or role field](../../project-wiki/references/engineering-depth.md#who-asserts-an-identity-or-role-field).

## Observation (one real feature task, generic description)

A consumer project with an established native wiki added a shared, real-time tool
to an existing multi-party session feature. The wiki was read first. Three
statements in it were each true at one layer and wrong as a description of what a
user could do:

| Wiki statement (paraphrased) | Layer where it held | What a three-client run on a pre-production deployment showed |
|---|---|---|
| "Primary and additional participants can enter" | The credential-issuing interface | The page in front of that interface only recognised the two original roles, and assigned the operator role to anyone who was not the primary client. The additional participant never reached the interface. |
| (no statement about capacity on the feature page) | A global setting documented on a networking page | The room was created with a cap of two. After the page guard was fixed, the third participant connected with a valid credential and was disconnected. |
| "The role in the message is self-reported, not authorization; the real boundary is the save endpoint" | The save endpoint checked who was saving | Every receiving client, including the one that saves, applied state-replacing control messages from any sender whose payload named the privileged role. The save endpoint then persisted that state. The disclaimer had no enforcement point on the path to the protected record. |

The first two were found by running the real path with a third account. The third
was found by an automated review of the committed change and confirmed by reading
the receiving code; it was not demonstrated with a modified client.

## What changed in the method

- Feature completeness gains a rule for the Actors and access dimension: name each
  gate on the path, give each an outcome, and treat people/session/seat limits as
  access gates. Later-added actor classes get an explicit search of layers that
  still enumerate the earlier ones.
- Engineering depth gains a rule for identity and role fields in a data contract:
  record whether the sender asserts the value or the transport attests it, name the
  enforcement point and the protected asset, follow the unprotected path, and ask
  the same of control messages. The ordering profile states whether multi-writer
  state depends on cross-sender arrival order and what proves independence.

## Limits

- One task in one project. No second project, no blind-agent trial, no measurement
  of whether the new text changes what an agent finds.
- The wiki-first read happened; the three defects were still not predicted from the
  wiki alone. Two needed a real multi-client run and one needed a code review, so
  this is evidence that the pages were incomplete, not that reading them is enough.
- Documentation change only: no helper, schema, hook or test change, and no
  package build or installation.
