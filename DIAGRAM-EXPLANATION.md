# Use-Case Diagram — Explanation

This document explains the actors, use cases, and relationships shown in [`diagrams/usecase-diagram.svg`](./diagrams/usecase-diagram.svg).

## Actors

**Club Member** — any registered user participating in the reading challenge and discussions. Can set goals, log progress, post/read discussion comments, mark chapters read, and vote in the monthly poll.

**Discussion Lead** — a Club Member with elevated privileges responsible for running the club's monthly cycle. Can do everything a Club Member can (hence also associates with *View Discussion Thread*), plus create polls and moderate the board.

## Use Cases

| Use Case | Actor | Description |
|---|---|---|
| Set Reading Goal | Club Member | Set a personal page-count target for the current book. |
| Update Reading Progress | Club Member | Log pages read against the active goal. |
| Post Discussion Comment | Club Member | Write a comment/reply under a chapter thread, optionally spoiler-tagged. |
| View Discussion Thread | Club Member, Discussion Lead | Browse a chapter's comment thread. |
| Reveal Spoiler Content | Club Member | Unmask a spoiler-tagged comment on demand. |
| Mark Chapter as Read | Club Member | Flags a chapter complete, which auto-unmasks its spoilers. |
| Vote in Monthly Poll | Club Member | Cast one vote for the next book from the Lead's candidate list. |
| Verify User Session | *(system-internal)* | Confirms the requester is authenticated before a state-changing action is allowed. |
| Create Monthly Poll | Discussion Lead | Publish the candidate book list and open voting for the month. |
| Moderate Discussion Comments | Discussion Lead | Edit/remove comments that violate club guidelines. |

## Relationships

**`<<include>>`: Post Discussion Comment → Verify User Session** and **Vote in Monthly Poll → Verify User Session**
Both actions change persistent state (a comment is written, a vote is tallied), so both *always* pass through session verification as a mandatory sub-step before they can complete — this is what `<<include>>` means: the base use case cannot finish without it. It is also the mechanism that directly satisfies NFR-001 (duplicate-vote prevention).

**`<<extend>>`: Reveal Spoiler Content → View Discussion Thread**
Revealing a spoiler is *optional* and only happens conditionally — only when the member is viewing a thread AND clicks to unmask a specific spoiler-tagged comment. Since it's an optional, condition-triggered add-on to the base flow rather than a mandatory step, it's modeled as `<<extend>>` rather than `<<include>>`.

**Associations (plain lines)**
Each actor is connected directly to every use case they can initiate. Discussion Lead is associated with *View Discussion Thread* in addition to their own two use cases, because moderating comments (Moderate Discussion Comments) requires first viewing the thread — that association reflects the Lead's day-to-day workflow, not a separate diagram error.
