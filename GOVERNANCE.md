# Proposed successor governance

Status: proposal for review, not adopted. David Molik and Adam Wright retain full
schema/release authority until they explicitly record adoption and complete the
handover below. v0.3 implementation proceeds under that current authority.

## Goals and options

Keep decisions transparent, make review possible for users and repository
operators, and sustain a small provenance standard without adding unnecessary
process. A two-person maintainer model is simple but has continuity risks. A
formal external foundation is disproportionate at current scale. A small rotating
steering group with public decisions is the recommended successor model.

## Recommended model

Create a steering group of three to five members, including at least one schema
maintainer, one converter maintainer, and one genome-data user or repository
representative. No outside organization is presumed to have accepted a role.
Members serve two-year terms, staggered initially for continuity. Contributors
with demonstrated project participation may nominate themselves or others in a
public nomination period. The existing group selects replacements by majority
vote, records its rationale, and invites objections for fourteen days. A member
may serve two consecutive terms before a one-term break.

Maintainers review and implement changes and administer repositories. The group
approves changes to the metadata contract, compatibility policy, and governance.
Routine documentation and implementation fixes need one independent maintainer
review and passing checks. Reviewers declare conflicts; authors do not approve
their own changes. If no independent reviewer is available, the group records
that limitation and appoints a reviewer before approval.

## Decisions and releases

Schema proposals state the use case, field semantics, examples, mappings,
compatibility, and effects on tools. Discuss publicly for at least fourteen days,
except urgent security fixes. Seek consensus first; unresolved proposals use a
recorded vote. Quorum is a majority of non-conflicted members, with at least two
participants. Approval needs a majority of participating voters. A tie defers the
proposal for revision. Appeals receive a fresh review by non-conflicted members;
if quorum cannot be reached, defer and recruit an independent temporary reviewer.

Release changes are documented in a changelog. Package/release versioning and
schemaVersion are distinct. Additive optional fields may be minor releases;
required-field/type changes need explicit compatibility review and a migration
plan. Deprecations must be documented for at least one release before removal,
unless a security issue makes that impractical. Record emergency decisions and
obtain retrospective group review within fourteen days.

Governance amendments follow the public proposal process and need two-thirds of
non-conflicted group members, with quorum. Review the model annually and publish
a short record of membership and decisions. Participation remains subject to the
code of conduct and its documented private reporting and appeal routing.

## Transition and adoption checklist

- [ ] David and Adam approve or revise this model and record an effective date.
- [ ] Publish nominations and appoint the initial group, confirming consent and roles.
- [ ] Record initial term lengths, voting membership, and contact channels.
- [ ] Hand over repository administration, release credentials, and archival ownership;
      grant only the access needed for each role.
- [ ] Record a first meeting and establish the public decision log.
- [ ] Update CONTRIBUTING and this status banner to distinguish effective rules from drafts.

Preparing this proposal does not appoint members or transfer authority.
