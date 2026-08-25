# Requirements Table
### Problem Statement #55 — Book Club Reading Challenge & Discussion Portal

**Actors:** Club Member, Discussion Lead

---

## Functional Requirements

### FR-001 — Spoiler-Tagged Comment Masking
**Priority:** High

**Description:** The system shall hide content inside spoiler-tagged discussion comments until the user explicitly clicks to reveal it, or has marked the relevant chapter as read.

**Acceptance Criteria:**
- Pass: Spoiler text is masked with a blur filter and excluded from search-result previews.
- Fail: Spoiler content is exposed in a comment preview, notification, or search result before the user reveals it or marks the chapter read.

**Rationale:** Members read at different paces; without masking, browsing the discussion board would spoil the book for anyone behind schedule.

---

### FR-002 — Set and Track Personal Reading Goal
**Priority:** High

**Description:** The system shall allow a Club Member to set a personal page-count goal for the current book and log daily/periodic reading progress against it.

**Acceptance Criteria:**
- Pass: Member sets a goal (e.g., 300 pages by a target date); logged progress updates a visible progress bar/percentage.
- Fail: Progress entries are not saved, or the goal cannot be edited once set.

**Rationale:** Personal goal tracking is the core engagement hook that keeps members motivated to keep pace with the group.

---

### FR-003 — Post and Reply to Chapter Discussion Threads
**Priority:** High

**Description:** The system shall allow a Club Member to create a comment or threaded reply under a specific chapter's discussion thread, optionally tagging it as containing spoilers.

**Acceptance Criteria:**
- Pass: Comment is saved, attributed to the author, timestamped, and appears nested under the correct chapter thread.
- Fail: Comment posts under the wrong chapter, loses thread nesting, or the spoiler-tag checkbox is ignored on save.

**Rationale:** Chapter-scoped threads are the primary discussion mechanism the portal exists to support.

---

### FR-004 — Mark Chapter as Read
**Priority:** Medium

**Description:** The system shall allow a Club Member to mark a chapter as read, which automatically unmasks previously hidden spoiler content for that chapter in the member's view.

**Acceptance Criteria:**
- Pass: After marking a chapter read, all spoiler-tagged comments for that chapter display unmasked on next page load.
- Fail: Spoilers remain masked after marking read, or marking one chapter unmasks spoilers for a later, unread chapter.

**Rationale:** Automatic unmasking removes friction for members who are caught up, without exposing spoilers to those who aren't.

---

### FR-005 — Create and Vote in Monthly Book Poll
**Priority:** High

**Description:** The system shall allow a Discussion Lead to create a monthly poll listing candidate next-book options, and allow each Club Member to cast exactly one vote per poll.

**Acceptance Criteria:**
- Pass: Poll shows live tallies to voters; each member's vote is recorded once and can be changed but not duplicated.
- Fail: A member's vote count is not enforced, or poll creation is available to Club Members rather than only the Discussion Lead.

**Rationale:** Monthly book selection is a stated core function of the portal and needs controlled poll creation plus fair, single-vote tallying.

---

## Non-Functional Requirements

### NFR-001 — Poll Vote Integrity & Real-Time Tally
**Type:** Performance & Security

**Description:** Monthly poll voting results must prevent duplicate votes using user session verification, and update tallies in real time as votes are cast.

**Acceptance Criteria:** Pass: Benchmarking tests confirm tally updates propagate within target latency, and repeated vote attempts from the same authenticated session are rejected under simulated peak load.

**Rationale:** Poll results directly determine the club's next book; both fairness (no duplicate votes) and responsiveness (live tallies) are essential to member trust in the outcome.

---

### NFR-002 — Discussion Thread Availability & Data Durability
**Type:** Reliability & Availability

**Description:** The discussion board and reading-progress data must remain available and durable, with posted comments and logged progress persisted such that no data is lost across sessions or minor service interruptions.

**Acceptance Criteria:** Pass: System meets a defined uptime target (e.g., 99.5% monthly) and recovers posted comments/progress data intact after a simulated service restart. Fail: Any committed comment or progress entry is lost after a restart, or downtime exceeds the target threshold.

**Rationale:** Discussions unfold over weeks and reading goals are tracked daily — members need confidence that their contributions and progress persist reliably over the life of a reading cycle.
