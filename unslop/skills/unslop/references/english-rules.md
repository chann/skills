# English rules

Apply these to English passages after the hard rules in `SKILL.md`. Rule ids
(`E1`, `E2`, …) are stable: other skills and replies may cite them, so never
renumber. The goal is writing that sounds like a person, not text that has been
heavily edited. Each rule shows a direction, not a fixed phrase.

## Words and openers

**E1. Filler openers and chatbot phrases.** Delete lines that talk about the
reply instead of giving it: "Certainly!", "Great question!", "Hope that
helps!", "Feel free to reach out with any questions", "In today's fast-paced
world".
Start with the first sentence that carries content.

**E2. Praise or agreement openers.** Drop "You're absolutely right" and "That's
a great point" before an answer. If the user was right, the action shows it.

**E3. Vague attributions.** "Experts say", "studies show", "many believe": name
the source, or state the claim as the writer's own. If there is no source and
the claim is not the writer's to make, flag it in the reply instead of
rewriting it.

**E4. Inflated vocabulary.** Replace pivotal, crucial, robust, seamless,
vibrant, delve, testament, and their cousins with the plain claim or a
measurement. "A pivotal moment" becomes what happened. Keep a word that is the
literal technical term (a robust estimator in statistics, a seamless pipe in
manufacturing).

**E5. "Serves as" verbs.** "Serves as", "stands as", "acts as", "boasts",
"features", "offers" where "is" or "has" works. "The file serves as the entry
point" → "The file is the entry point."

**E6. Plain words.** "Use", not "utilize"; "help", not "facilitate"; "start",
not "commence"; "about", not "approximately" in speech-like text; "so", not
"therefore" when "so" fits.

**E7. Abstract metaphor nouns.** Landscape, journey, realm, ecosystem,
tapestry, cornerstone, and playground, where a concrete word exists. "The
evolving security landscape" → "current security threats", or the actual
threats.

## Sentence shape

**E8. "Not just X but Y".** Also "it's not X, it's Y" and "more than just".
State Y. Keep the contrast only when the reader really held the wrong belief.

**E9. Forced lists of three.** Triples exist because the pattern feels
complete. Keep as many items as there are, whether two or five.

**E10. One name per thing.** Pick one word for each concept and repeat it.
Rotating "the tool", "the solution", "the platform", and "the system" for one
thing makes the reader wonder whether there are four.

**E11. One idea per sentence.** Split sentences that chain three claims with
commas and "while". Do not split ones that have one idea and several details.

**E12. Active voice with a named actor.** "Mistakes were made" → "The build
script skipped the check." If the actor is unknown, say that; do not hide it
in the passive.

**E13. Stacked hedges.** "It might potentially possibly be argued that…" Keep at
most one hedge per claim, and only where the writer is really unsure.

**E14. Adverbs in place of numbers.** "Significantly faster", "dramatically
reduced": give the figure that is in the source. If the source has no figure,
drop the adverb rather than invent one.

**E15. Generic conclusions.** "In conclusion", "Overall", "Ultimately, this
shows…" followed by a restatement. Delete the paragraph unless it adds a
decision or a next step.

## Punctuation and formatting

**E16. Dashes as connectors.** An em or en dash used to join clauses reads as a
tic. Use a period, a comma, or parentheses. Keep a dash in a numeric range, a
quoted source, or a compound that needs one.

**E17. Colons as mid-sentence connectors.** "The result was clear: it failed."
Use a verb or a period. Colons that introduce a list or a code block stay.

**E18. Bold on every noun.** Bold marks the one thing a reader must not miss. If
more than a couple of phrases per screen are bold, unbold the rest.

**E19. Bold labels that restate their line.** "**Performance:** Performance
improved." Remove the label, or the repetition, whichever the line does not
need.

**E20. Sentence-case headings.** Title Case Headings In Every Section read as
templated. Use sentence case ("Getting started with caching"). Proper nouns
and product names keep their capitals.

**E21. Decorative emoji.** Remove emoji used as bullets, heading decorations,
or enthusiasm. Keep one that is part of a quoted string, a UI label the text
describes, or the user's own style.

## Keep list

Never change: code, identifiers, commands, quoted text, titles of works, product
names, numbers and dates, and established technical terms such as API, token,
prompt, commit, idempotent, latency, throughput, and cache. A word on this list
that also appears in E4 or E7 is slop only when used as decoration.

## Self-check

- [ ] Numbers, dates, names, identifiers, links, and quotes match the source
- [ ] Every sentence still maps to something in the source; nothing added or cut
- [ ] No keep-list term was replaced
- [ ] The text reads aloud without a snag, and sentence lengths vary
- [ ] Each change can be explained in one sentence by its rule id
