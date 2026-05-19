---
layout: layouts/base.njk
title: Editorial standards
permalink: /standards/
eleventyExcludeFromCollections: true
---

# Editorial standards

*Working draft. Last updated 2026-05-12. The publication's editorial standards are public because the publication's credibility depends on them being public. Readers should be able to test any entry against the standards on this page.*

## The standard

The publication documents events involving authoritarianism, anti-democratic behavior, and corruption — applied to any actor, regardless of party, position, or political alignment.

The standard is not "things the editor disagrees with." It is "things that erode small-d democratic norms," with the norms catalogued in the [twelve ideals](/ideals/) and the specific patterns catalogued in the [seventy-seven abuses](/ideals/).

The publication takes a broken-windows view of democratic decline: no anti-democratic action is too small to record. A precinct-level voter intimidation incident sits in the archive alongside a national overturning attempt — both fit the taxonomy, both are recorded with the same rigor. The premise is that democratic norms erode through the accumulation of small breaches at least as much as through dramatic single events, and the historical record should reflect that. There is no significance threshold beyond the inclusion criteria themselves.

Two operational tests are applied to every potential entry before it ships.

**The symmetry test.** Would the publication record this if the partisan valence were reversed? If a Democratic official did the same thing, would it be in the archive? If yes, file it. If no, the entry needs a different framing — or doesn't belong.

**The norm test.** Which specific ideal does this event erode, and how? The answer must point to a concrete pattern in the [abuse taxonomy](/ideals/). If no abuse fits, the event probably isn't in scope.

## Scope

**In scope.** Federal officials and federal agencies. Elected state officials, statewide officials, and state legislatures. Local officials and bodies — sheriffs, district attorneys, county boards, school boards, city councils, precinct-level election workers. Every level of government counts. A precinct-level abuse is as much a record as a federal one. Private actors exercising public-facing power: government contractors, platforms acting under government direction, foreign-state activity that implicates US governance, NGOs that exercise quasi-governmental authority. Candidates for office, party officials, and political organizations, where their actions or coordinated activity falls within the abuse taxonomy.

**Out of scope.** Private speech and private conduct by private individuals, even when politically distasteful — the publication is about exercises of public power. Routine policy disagreements within the lawful exercise of duly authorized power. The honest application of contested legal standards: disagreement with court rulings is not in scope; defiance of them is. Foreign-government conduct abroad that does not implicate US governance. Hypothetical or speculative concerns about what an actor might do.

When in doubt, the question is: does this event point to a specific abuse in the taxonomy, supported by specific sources, that erodes a specific democratic ideal? If three nouns can each be filled in, it's in scope.

## Sourcing

Every entry meets one of these floors, enforced at build time:

- **One primary source.** A primary source is the record that *is* the news — the document, recording, or first-hand evidence that establishes the event directly, not a later account that mentions it.
- **Two independent investigative sources.** Original investigative reporting from credentialed news outlets that have substantive editorial review. The two outlets must be genuinely independent — coverage from outlets that share a parent company, or that are merely repackaging the same wire story, does not count as two sources.

The publication classifies every source into one of three tiers:

- **primary** — court filings, OIG reports, agency records, sworn testimony, official statements, certified records, and citizen-captured first-hand documentation that meets the bar described below.
- **investigative** — original reporting from major credentialed outlets (AP, Reuters, the New York Times, the Washington Post, the Wall Street Journal, NPR, ProPublica, major regional newspapers, state-level investigative outlets, Lawfare, Just Security, the Marshall Project, and others of comparable rigor).
- **secondary** — wire reproductions, aggregator coverage, summaries of investigative reporting.

Secondary sources may appear but cannot satisfy the sourcing minimum.

Every source must be linkable and accessible to readers. Sources behind paywalls are permitted — you can't avoid paywalls if you want to cite serious reporting — but the entry should note when a source is paywalled.

### Citizen-captured evidence

Citizens with phones routinely document anti-democratic conduct — police violence, voter intimidation, election-worker harassment, the moment an officer ignores a court order — before any journalist or official record arrives. The publication treats verifiable citizen documentation as a primary source. This is essential to the broken-windows premise: the publication cannot record small accumulating breaches if it accepts only government-produced records, because most small breaches never produce one.

The bar for citizen-captured evidence:

- **Verifiable authenticity.** The recording appears unedited and first-hand — no visible cuts, splices, or post-processing that alters what was captured. The clip itself contains enough internal context (location markers, recognizable actors, contemporaneous reference points, environmental detail) to identify what is happening, when, and where. Available metadata is consistent with that claim. Deepfake risk is assessed: clips that show technical signs of synthetic generation do not meet the bar.
- **Documented context.** The entry describes when, where, who, and what was happening before and after the captured moment. Decontextualized clips on their own do not meet the bar; the entry's documentation can supply the context the clip itself does not carry.
- **Corroboration where attribution is absent.** Attribution to a named source is preferred but not required. Citizens who document government conduct often face real risks — retaliation, professional consequences, physical danger — and the publication protects source anonymity where the source needs it. When the source is anonymous, the verification work shifts to the recording and to corroborating signals: other recordings of the same event from different angles, contemporaneous social-media reports from the location, journalist verification, matching official records that surface later, or consistent secondary documentation. Where these signals converge, anonymous citizen documentation can stand as a primary source. Where they don't, the entry needs additional sourcing before it ships.

When the source is anonymous, the entry includes this disclaimer prominently in the body, above the sources list:

> *This entry relies on citizen-captured evidence from an anonymous source. The recording is published unedited; verification is documented in the sources. The publication protects source anonymity for citizens documenting government conduct, who can face retaliation for identifying themselves. See our [citizen-evidence policy](/standards/#citizen-captured-evidence) for the full verification approach.*

The "no anonymous sources" rule applies to claims that depend on someone whose identity is hidden — for example, an unnamed government employee said by a reporter to have confirmed something. A citizen-captured recording whose author is anonymous is a different category: the recording itself is the source, and its authenticity can be evaluated on its own terms without depending on the captor's identity. The captor remains anonymous; the evidence is published.

## Confidence

The `confidence` field calibrates how sure the publication is that the recorded event happened as described.

- **confirmed** — a primary source establishes the event directly. No meaningful dispute. A court has issued an order; the entry links to the order. The fact pattern speaks for itself.
- **well-reported** — multiple credible outlets converge on the same fact pattern with no significant contradictions in subsequent reporting. The publication is comfortable stating the event as fact but is not the original investigator.
- **developing** — active reporting. The basic fact pattern is documented but specific details may shift. The entry should note that the story is developing.
- **alleged** — a specific accusation has been made, with a named accuser. The publication is recording the allegation, not adjudicating it. Use this for active prosecutions, lawsuit allegations, and other not-yet-resolved claims.

Allegations are still in scope, but they are labeled as allegations, and the character of the source is made plain. A federal indictment is a different kind of allegation than a tabloid claim, and the entry reflects that.

## Anonymous sources

The publication distinguishes two categories that the phrase "anonymous source" tends to blur together: anonymous *institutional* sources and anonymous *citizen* documentation. The first is excluded; the second is accepted with conditions.

**Anonymous institutional sources are not credited.** The "unnamed senior official," the "former adviser who spoke on condition of anonymity," the claim that depends entirely on a person whose identity is hidden — these are the staple of much working journalism, but they are not how this publication anchors a claim. The publication's value to the historical record depends on every citation being traceable. Anonymous institutional sources may be load-bearing in the original reporting that the publication cites; that is the originating outlet's editorial choice, and the publication relies on the outlet — named — having vouched for the source. The publication does not add a further layer of anonymity on top.

**Anonymous citizen documentation is accepted, with conditions.** A citizen-captured recording whose author is anonymous is a different category: the recording itself is the source, not a person's account of an event. Its authenticity can be evaluated on its own terms — unedited, contextually clear, corroborated — without depending on the captor's identity. The captor remains anonymous; the evidence is published. This protects citizens documenting government conduct from retaliation while keeping the underlying record verifiable. The verification bar is set out in the [citizen-captured evidence](#citizen-captured-evidence) section.

The pattern across both: what gets excluded is claims that rest entirely on hidden identities. What gets accepted is evidence whose authenticity can be evaluated on its own terms.

## Tone and voice

The publication is documentary, not polemic. Read like a historian writing for the future, not like an advocate writing for the present.

**Headlines** are factual and neutral, in past tense for events that occurred, in active voice. "Federal agency declined to respond to House Oversight subpoena" — not "Outrageous agency stonewalls Congress." No editorializing adjectives or adverbs. The headline is the headline; the framing lives in the abuses tagged and the body prose.

**Summaries** are one to three sentences, neutral, factual. They state what happened, who was involved, and what the central document or finding establishes. They do not characterize, condemn, or interpret beyond what the underlying record states.

**Body prose** can provide more context but maintains the same standard. Quote primary documents when the wording matters. Avoid scare quotes; if a term is contested, say so directly rather than punctuating it with skepticism.

**Quotes** are limited to one per entry and fewer than fifteen words. The cited quote must come from a primary source listed in the entry's sources. The quote field is for the most factually load-bearing line in the underlying record, not the most damning or rhetorically effective line.

## Actor attribution

Every named actor should be unambiguously identified. The frontmatter `actors:` field should include role-at-time context where relevant — "Stephen Miller (Deputy Chief of Staff)" — because roles change and historical context should be preserved with the entry. Subsequent role moves are recorded in subsequent entries.

For institutions, use the canonical name from `taxonomy/aliases.yaml` if one exists. The build process normalizes obvious variants ("DOJ" and "Department of Justice" both resolve to "U.S. Department of Justice"), but the entry should use the canonical form where possible.

## Time horizon

An event is freshly archivable for approximately thirty days after it became publicly known. Older events can still be archived — the historical record is the whole point — but the entry's `archived` date reflects when the entry was created, not when the event occurred.

There is no expiration. Events from prior administrations are in scope when the symmetry standard would have them in.

## Corrections and retractions

Errors are inevitable. The protocol:

**Minor edits** — typos, broken links, formatting fixes — are committed directly. An entry in the `corrections:` array logs the date and a short description of what changed.

**Substantive corrections** — a fact was wrong, an attribution was wrong, the framing was misleading — are issued as a new entry with `corrects: [original-slug]` in the relationships. The original entry displays a banner at the top pointing to the correction, with disputed text crossed out. Both entries stay live forever. The original is never deleted.

**Retractions** — the entry should not have been published at all — are issued as a new entry with `retracts: [original-slug]`. The original entry displays the retraction prominently at the top. Both stay live. The publication does not memory-hole its mistakes.

Corrections and retractions are themselves part of the public record. Readers can browse them at [/corrections/](/corrections/).

## Conflict of interest

If the editor has a direct personal connection to an actor in a candidate entry — family relationship, current or former employer, close personal friendship, ongoing financial relationship — the editor recuses from drafting and approving that entry, and a second editor handles it.

When the publication is solo-edited and recusal is not practical, the entry discloses the connection in its body and leans conservatively on inclusion decisions. The publication's credibility depends on readers being able to trust its judgment on close calls; the cheapest way to lose that trust is to be insufficiently transparent about a connection.

## Defamation considerations

The publication operates under US law. The bar for defamation against public figures is high (actual malice); the bar against private individuals is lower (negligence in some states). Practical guidance:

For **public figures** — officeholders, candidates, agency leadership, prominent commentators — the publication describes what is documented. It avoids characterizing motive ("she did it because she hates X") unless the actor has stated the motive themselves. It avoids moral conclusions ("his conduct was disgraceful"); the [abuse taxonomy](/ideals/) carries that work.

For **private individuals**, the publication uses "alleged" where adjudication has not occurred, and is precise about what is documented versus what is claimed.

For **institutions**, the same rules apply.

When in doubt, link to the primary source and let it speak. If the publication can show the document, it can describe what is in it. If the publication can only describe an unattributed claim, it is outside the sourcing standard anyway.

## Six common judgment calls

Some patterns recur often enough that they deserve standing answers.

**"This event is small. Is it worth a separate entry?"** Yes. The broken-windows premise of the publication is that no anti-democratic action is too small to record. The precinct-level voter intimidation, the small-town clerk's refusal to certify, the single instance of a particular abuse — these are recorded with the same standards and the same care as their high-profile equivalents. Small accumulating breaches are themselves the pattern. The archive's value to future readers is precisely that it does not filter out the breaches that did not happen to draw national attention.

**"The other side does the same thing."** The defense does not change whether an entry is in. If the symmetry test is genuine — if the equivalent conduct by the other side *would* be archived — then this entry is also in. The whataboutism response is itself outside the publication's scope; the publication does not comparatively rank actors.

**"This isn't a norm violation; it's a routine practice that's just being noticed now."** This is the editor's hardest call. Resolution: if the conduct meets a specific abuse in the taxonomy and is supported by sources, it is in. The norm violation is named by the abuse, not by novelty. If the conduct is genuinely routine across administrations, the abuse may be the wrong one — and a different abuse may fit.

**"The actor disputes the characterization."** A dispute is itself recordable within the entry, but does not by itself remove the entry. If the underlying document is unambiguous — the order is the order, the testimony is the testimony — the entry stands and the dispute is noted.

**"The reporting is from an outlet with a known ideological slant."** The publication assesses the *reporting*, not the outlet's politics. A piece of original investigative reporting from any credentialed outlet — left, right, or center — can serve as a source if it meets the sourcing standard. The publication does not exclude sources for their politics; it excludes them only if their reporting is unreliable.

**"This event seems significant but I can't find a clean primary source."** Then it does not ship. The sourcing standard is the publication's most important guarantee to readers. The publication can wait. The story will still be the story when the document drops.

## Editor's working note

The publication is built on the bet that an honest, narrow, documentary record applied symmetrically across the political spectrum can be useful to citizens, journalists, and historians regardless of where they sit on contemporary debates. This works only if every entry can stand on its own as a record of what happened.

The temptation, especially on close calls, will be to lean toward inclusion when a high-profile event seems important. Resist it where the sourcing isn't there. The publication's claim to credibility is that the bar is the same yesterday, today, and across actors. The harder it is to ship something that fits the editorial standard, the more credible the publication is when something does.

## Contact

- **Corrections** — [editor@thestanding.us](mailto:editor@thestanding.us). Notes about errors of fact, attribution, framing, or formatting in any published entry. Substantive corrections and retractions become their own archive entries; minor edits are logged in the corrected entry's `corrections:` field. See [corrections and retractions](#corrections-and-retractions) above.
- **Tips and citizen documentation** — [tips@thestanding.us](mailto:tips@thestanding.us). For sources, eyewitnesses, and citizens with documentation (phone video, photographs, primary documents) of events that meet the publication's [scope](#scope). The publication protects source anonymity for citizens documenting government conduct (see [citizen-captured evidence](#citizen-captured-evidence) above); attribution is preferred but not required, and the verification work is done on the evidence rather than the identity of who captured it.

For genuinely sensitive sources where email is not secure enough — whistleblowers, government employees taking real risks — the publication will publish more secure channels (Signal, SecureDrop, or comparable) as the operation matures. Until those channels exist, sensitive sources should consider the operational-security implications of any communication channel and use what they trust.
