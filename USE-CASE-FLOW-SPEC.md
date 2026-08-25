# Use-Case Flow Specification

## Use Case: Vote in Monthly Poll

**Actor(s):** Club Member
**Related Requirements:** FR-005, NFR-001
**Trigger:** A Discussion Lead has published an active monthly poll listing candidate next-book options, and a Club Member navigates to it intending to cast a vote.

---

### Preconditions
- The Club Member is authenticated and has an active, verified session.
- A monthly poll is currently open (i.e., within its configured voting window) and contains at least two candidate book options.
- The Club Member has not already cast a vote in this specific poll.

### Postconditions
**Success:**
- Exactly one vote is recorded for the Club Member against their chosen candidate in this poll.
- The poll's live tally is updated in real time and reflects the new vote.
- The Club Member's vote is marked as "cast," preventing a further duplicate submission.

**Failure:**
- No vote is recorded, the tally is unchanged, and the Club Member is shown an explanatory message.

---

### Main Success Scenario
1. The Club Member opens the "Monthly Poll" section of the portal.
2. The system verifies the Club Member's session («include» Verify User Session) and confirms no prior vote exists for this poll.
3. The system displays the list of candidate books along with the current live tally.
4. The Club Member selects one candidate book.
5. The Club Member confirms their vote submission.
6. The system records the vote against the Club Member's verified session/account and timestamps it.
7. The system updates the poll tally in real time and marks the poll as "voted" for this Club Member.
8. The system displays a confirmation message along with the updated live results.

---

### Alternate Flow A1: Duplicate Vote Attempt
**Branch point:** Step 2 of the Main Success Scenario.

1. The system verifies the Club Member's session and detects that a vote already exists for this Club Member on this poll.
2. The system blocks the new vote submission and does not alter the existing tally.
3. The system displays a message informing the Club Member that they have already voted, along with their previously selected choice.
4. The Club Member may view the live results but cannot submit an additional vote.
5. The use case ends; the system returns the Club Member to the poll results view.

---

### Notes
- Session verification in Step 2 satisfies NFR-001's duplicate-vote-prevention requirement.
- Real-time tally updates in Steps 3, 6–7 must meet the latency target defined under NFR-001's acceptance criteria.
