# Independent review — fixed PAPER provisioning

Scope: the separate human-console staging command, its installer/sudo policy,
protected execution activation consumer, and associated regressions. The reviewer
did not author these controls. This is not a new review of settled console,
journal traversal or database architecture.

## Disposition

No blocking source finding remains in the reviewed staging/activation design.
Approval is limited to preparing the documented human checkpoint. No privileged
installation, real credential entry or Alpaca request was performed by this
review. Gate 2 and both qualification authorization flags remain false.

The HTTP LAN workspace remains public-research/status-only. Server-side
provisioning does not authorize disclosing balances, positions, account identifiers
or trade approvals through an unauthenticated, unencrypted browser connection.

## Findings and corrections

| Finding | Disposition |
| --- | --- |
| Directory creation lacked parent fsync. | Service-directory and parent fsync added before input. |
| Temporary filename could be replaced between open/publication, and cleanup could remove the replacement. | Open-file identity is compared with temporary/final names; unexpected replacement is refused and not unlinked. Regression and independent substitution fixture passed. |
| Nonblocking input readiness can race a read. | BlockingIOError retries within the original deadline; regression passed. |
| Initial consumer actor label violated the existing database actor constraint. | Replaced with a fixed namespaced SHA256 marker, explicitly not a client certificate; regression validates its representation. Database integration evidence is recorded separately. |
| Outcome reporting could imply definite failure after a published candidate. | Fixed UNKNOWN/refused-or-incomplete result preserves uncertainty; neither Connected nor qualification approval is inferred. |
| Clock and buying-power observations were not implemented by the old dashboard reader. | Fixed PAPER clock retrieval and allowlisted buying-power projection added; mocked HTTP-byte tests exercise the production reader. No real connectivity is claimed. |

## Boundaries examined

- Sudo grants one digest-pinned installed executable with **no arguments**,
  PASSWD/NOSETENV and fresh authentication. PTY, environment and I/O-log defaults
  are command-specific; no generic runner or global sudo change is introduced.
- Installed helpers and policy use pinned bytes and root-owned non-writable
  ancestry. Candidate and aggregate sudo syntax validation precede installation.
  Exclusive installation preserves pre-existing artifacts; rollback removes only
  this exact policy and retains helper/evidence copies.
- Existing console, operator, local login/session and host checks run before the
  fixed bounded worker. Worker verifies effective cgroup/no-swap state, zero core
  limits and non-dumpable state before hidden input and again before publication.
- No network, fork or exec occurs after the input worker receives credentials.
  The later execution container receives them through its encrypted mount, not
  Docker stdin, command arguments, environment or daemon request payload.
- Candidate schema, role and PAPER mode are fixed. Activation resolves the tenant
  from PostgreSQL session identity, requires an empty initial connection set,
  uses existing advisory ownership, validates PAPER reads, and commits the active
  file reference with an audit event. Ambiguous saves preserve protected material
  and are not blindly retried.
- Research/HTTP processes receive no credential mount or brokerage authority.
  Fixed sanitized results contain no account/credential values or raw exceptions.

## Independently executed evidence

- 20 focused staging/installer tests passed: actual isolated PTY input/restoration,
  synthetic file publication/refusal, mocked protection ordering, exact policy
  hashes and failure reporting. Three additional isolated installer tests cover
  successful validation, rollback of created artifacts after final validation
  failure, and preservation of a replaced artifact. Root ownership/privilege and
  visudo execution are mocked in those installer fixtures. These are not
  physical-console authorization or privileged installation tests.
- 30 web/activation tests passed in the guarded non-root image with network
  disabled, read-only root, bounded tmpfs and no production mounts. Eight exercise
  activation; broker/database responses are fixtures. Existing HTTPS tests use
  temporary test-only certificates, not deployed certificate provisioning.
- Four separate isolated filesystem assertions passed: exclusive 0600/nlink1
  publication, no overwrite, substitution refusal, and preservation of an
  unexpected replacement. Ownership changes were mocked; no real credentials.
- Installed visudo accepted the proposed candidate policy. This is grammar
  validation, not evidence that the human has installed or exercised the grant.

The implementation author separately ran the guarded real-PostgreSQL
`tests/web/runtime_actor.py` test: the namespaced actor was accepted, the old
label produced CheckViolation, and all synthetic rows were rolled back. The
reviewer inspected that test but did not count its execution as an independent
reviewer runtime trial. No brokerage was contacted.

## Residual limits and human checkpoint

The credential-owning execution UID is a trusted writer to its own directory.
Observed inode checks do not protect against fully compromised root, kernel or
that execution identity. The trusted physical console, keyboard/input stack and
kernel buffers are outside process cgroup assurance. Python memory copies are
not promised to be securely erased; workers must exit after bounded use.

SIGKILL, parent-death termination and host failure can prevent terminal
restoration. The checkpoint must instruct the human to stop typing and use a
trusted console recovery path, never paste secrets into a shell. PAPER-CHECK
tests hidden input mechanics only; it does not qualify recovery-output handling,
prove universal crash/log non-retention or reactivate the deferred --io-test.

An interrupted install may leave inert reviewed helpers. An interrupted publish
or ambiguous activation may retain protected staging/version files. Do not
overwrite or delete them automatically. Policy rollback is not Alpaca key
revocation. Production rotation/recovery, authenticated financial views, real
PAPER risk/order/reconciliation and actual credential-entry evidence remain
separate unfinished requirements.
