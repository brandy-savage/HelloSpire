# The Multiplayer Cards — 15

**Status (2026-09-28):** design agreed. The Gunslinger's and the Alchemist's five are implemented and
gated; none has had a real two-player test yet. **The Paladin section below is stale** — it was written
against the Faith system, which the 2026-08-31 rework cut (`design/paladin-rework-2026-08-31.md`).
The Paladin now carries *nine* party cards built around Plating, Regen and Thorns rather than the
five Faith cards described here: Aura of Devotion, Aura of Protection, Aura of Vitality, Beacon of
Light, Circle of Healing, Crusader Aura, Divine Hymn, Retribution Aura and Tyr's Deliverance. Read
this document's Paladin table as design history, and the trinity/house-rules sections — which still
hold — as current.

Every shipped Slay the Spire 2 character carries **five multiplayer cards** outside its 80-card
pool. This document is the pack's whole set — five each for the Paladin, the Gunslinger and the
Alchemist — designed together rather than three times separately, because the point of shipping
one mod is that the three characters are expected to sit at the same table.

Each character already had a draft five (`design/gunslinger.md` §10, issue #2 §27). Those drafts
were written before the other two existed, and it showed: two of the Gunslinger's five were both
"ALL players gain Block", two of the Alchemist's were both "spend to give the party Block", and
between all fifteen there was no card whose value came from *which* other character was standing
next to you. This revision fixes that. Cuts and the reasons for them are in
[Cuts from the earlier drafts](#cuts-from-the-earlier-drafts).

---

## The trinity

Three characters, three things a party runs out of. Each character's five cards give away the one
resource the other two cannot manufacture:

| Character | Gives the party | Fixes | Its own weakness, fixed by |
|---|---|---|---|
| **Gunslinger** | **amplification** — Weak, Debilitate, a covering turn | the party's damage ceiling | slow setup turns → Alchemist's tempo |
| **Paladin** | **protection** — Block, heals, redirected damage | the party's floor | slow Faith ramp → everyone else's Block and heals |
| **Alchemist** | **acceleration** — Energy, cards, Potions | the party's tempo | low raw damage → Gunslinger's debuffs |

That is a closed loop, not a list. It is the reason these fifteen cards are worth designing
together: each character's structural weakness is a different character's structural surplus.

---

## The five slots

Every character's five hit the same template, so a player who has learned one character's
multiplayer package can read another's at a glance:

| # | Slot | Shape | Cost |
|---:|---|---|---:|
| 1 | **Ping** | cheap, always playable, small gift to one ally, feeds your own resource | 0–1 |
| 2 | **Amplifier** | makes *other people's* next actions better | 1 |
| 3 | **Save** | the emergency button, pointed at someone else | 1 |
| 4 | **Payload** | the big party-wide turn, keyed to your own resource | 1–2 |
| 5 | **Engine** | a Power that turns *allies' actions* into your resource | 2 |

**Slot 5 is the design heart.** A Power that reads "whenever another player does X, you gain Y" is
a shape no single-player card can have. It is what makes co-op mechanically different rather than
just numerically bigger, and it is why each character's engine keys off a *different* ally verb:
allies gaining Block feeds the Paladin, allies attacking feeds the Gunslinger, allies drinking
feeds the Alchemist. A three-character party fires all three at once off the same turn.

---

## House rules

These are constraints, not suggestions. They exist so fifteen cards written for three different
kits behave like one set.

1. **Allies receive generic things; you receive character-specific things.** A card may give an
   ally Block, HP, Energy, cards, or a damage bonus. It may **never** give an ally Faith, Armor,
   Deadeye, Potency, a Round, or a Potion Slot. Cross-character keyword contamination makes
   every card a compatibility matrix; keeping the gift generic means each card has one behaviour
   regardless of who else is in the lobby.

   The one deliberate exception is `Shared Flask`, which puts a Potion in an ally's belt — Potion
   Slots are a game-wide system every character already has, not an Alchemist keyword.

2. **Balance at four players, not at one.** `ALL players gain 5 Block` is 5 Block solo and 20 in a
   four-player lobby. Party-wide numbers therefore run at roughly **60% of the self-only rate** for
   the same cost, and every per-ally engine carries a **once per turn per ally** cap. A card that
   is merely good in a duo and broken in a four-stack is a bad card.

3. **Nothing may be dead solo.** These cards should only ever be offered in co-op (see
   [Open questions](#open-questions)), but a player can carry one into a solo run through save
   continuation or a lobby that empties out. Every card in this set has a defined single-player
   behaviour, listed per card. None of them brick.

4. **No card requires a specific other character.** The synergies below are amplifications, not
   prerequisites. `Softened Up` is playable next to a Silent; it is *exciting* next to a Paladin.

5. **Every card must still be a card.** The base effect has to justify the cost on its own. The
   ally clause is the reason to be pleased you drew it, never the reason it is playable.

---

## The Paladin — 5

Faith is a standing value held per deity, generated by verbs — Torm from gaining Block, Ilmater
from healing, Tyr from attacking — and reset every combat. See `design/paladin.md`.

**Ruling this set depends on:** *Torm counts Block granted to an ally exactly as it counts Block
gained by you.* This mirrors the existing Ilmater rule (healing an ally already generates Faith)
and is the same argument: the verb is the thing you did, not who received it. Without it, four of
the Paladin's five cards would be Faith-neutral and the character would be *worse* in a party,
which is backwards.

| # | Card | Type | Cost | Effect | Upgrade |
|---:|---|---|---:|---|---|
| 1 | **Shield Another** | Skill | 0 | Grant an ally 5 Block. Gain 1 Faith in Torm. | Grant 8 Block. |
| 2 | **Mark for Judgment** | Attack | 1 | Deal 7 damage. Apply 2 Vulnerable. Until the start of your next turn, allies' Attacks against that enemy deal 3 additional damage. Gain 1 Faith in Tyr. | Apply 3 Vulnerable; allies deal 5 additional. |
| 3 | **Bear the Weight** | Skill | 1 | Grant an ally 8 Block. Until the start of your next turn, damage that ally would take is dealt to you instead, halved. Gain 2 Faith in Torm. | Grant 12 Block. |
| 4 | **Communion** | Skill | 2 | All allies gain Block equal to your Faith in Torm and heal equal to your Faith in Ilmater. | Costs 1. |
| 5 | **Oath of the Company** | Power | 2 | Whenever an ally plays a card that gains Block, gain 1 Faith in Torm. Whenever an ally heals, gain 1 Faith in Ilmater. Whenever an ally kills an enemy, gain 2 Faith in Tyr. *(Once per turn per ally, per clause.)* | Also gain 2 Block each time. |

**Solo behaviour.** `Shield Another` and `Bear the Weight` target the Paladin (Block, no
redirection). `Communion` reads as "gain Block equal to Faith in Torm, heal equal to Faith in
Ilmater" — smaller, still fine. `Oath of the Company` does nothing; it is the one card in the set
that is genuinely a blank solo, and it is a Power, so a solo player simply never plays it.

**Why these five.**

`Shield Another` at 0 Energy is deliberate. The Paladin's problem is that Faith ramps and combats
do not wait — a free card that advances Torm by one and keeps someone alive is exactly the
Paladin's turn-one play, and it is why the character's opening is stronger in a party than alone.

`Mark for Judgment` is the Paladin's contribution to the pack's damage. Note that it supplies
**Vulnerable**, which the Gunslinger explicitly does not have — see Loop 1.

`Bear the Weight` was named as a multiplayer risk piece in `design/paladin.md` and is the single
highest-desync-risk card in this document: damage redirection has to survive a host/client
disagreement about who took a hit. Build it last, test it first.

`Communion` is the wide build's payoff. It reads two deities at once, which means the split-Faith
deck that pays a tax everywhere else finally gets a card that wants exactly that. It scales with
party size *and* with Faith, so it is the Paladin's late-fight party turn.

`Oath of the Company` is the set's best idea and the reason slot 5 exists. Oaths make a verb
passive; this one makes *someone else's* verb passive. In a three-player party with a Gunslinger
playing `Covering Partner` and an Alchemist handing out Block Potions, the Paladin ramps Torm
without spending a single card on it — which is precisely the ramp problem the character has
solo. Per-clause, per-ally, once per turn: in a four-stack that is at most 9 Faith a turn, and
realistically 3–4.

---

## The Gunslinger — 5

Six chambers, a hammer, and ammunition that costs cards to load. Weak is a core strength;
Vulnerable deliberately is not. See `design/gunslinger.md`.

| # | Card | Type | Cost | Effect | Upgrade |
|---:|---|---|---:|---|---|
| 1 | **Hand Me That** | Skill | 1 | Another player draws 2 cards. Load 2 Rounds of the kind their class carries. | They draw 3 cards. |
| 2 | **Softened Up** | Skill | 1 | Apply 1 Debilitate to ALL enemies. Exhaust. | Apply 2 Debilitate. |
| 3 | **Covering Partner** | Skill | 1 | ALL players gain 5 Block. Cycle 1. If the new chamber is loaded, ALL players gain 3 more Block. | Gain 7 Block; the bonus becomes 4. |
| 4 | **Suppressive Volley** | Attack | 2 | Fire 2. Apply 1 Weak to ALL enemies. | Apply 2 Weak. |
| 5 | **Ride Together** | Power | 2 | The first time each turn each other player plays an Attack, Load 1 Lead Round. | Also gain 2 Deadeye. |

**Solo behaviour.** `Hand Me That` draws 2 for you. `Covering Partner` is a 5-Block Cycle card —
under-rate for 1 Energy against the 7-Block common `Take Cover`, correctly. `Ride Together` does
nothing. `Softened Up` and `Suppressive Volley` are unchanged.

**Why these five.**

`Softened Up` is the most important card in this document. Debilitate doubles Weak *and*
Vulnerable, and the Gunslinger has almost no native Vulnerable — so solo, a card that Debilitates
the whole room is a Weak-doubler and little else. Next to a Paladin's `Mark for Judgment` or an
Alchemist's Vulnerable Potion, it doubles a debuff the Gunslinger could not have applied. This is
a card whose ceiling is set by *who else is at the table*, which is the whole brief.

`Hand Me That` is the two-for-one that defines the character's role in a party: the Gunslinger's
worst turn is a load turn, and this makes a load turn also a teammate's good turn. Two Rounds into
the gun and two cards to someone who can spend them.

What comes back depends on who you asked. Borrowing from an Ironclad gets you something heavy;
borrowing from a Defect gets you something that goes through plating. The table is deliberately
lossy — there are more classes than there is interesting ammunition, so overlaps are fine:

| Class | Lends | Class | Lends |
|---|---|---|---|
| Ironclad | Heavy Round | Necrobinder | Rending Round |
| Silent | Crippling Round | Paladin | Guard Round |
| Defect | Piercing Round | Alchemist | Smoke Round |
| Regent | Guard Round | anyone else, and yourself | Lead Round |

The mapping lives in `AmmoAffinity`, matched on the character class name rather than on its type,
so a modded fourth party member still gets an answer instead of an exception. This makes the card
read differently in every lobby, which is the point of a multiplayer card, and it makes Rending
Rounds — otherwise Rare-only ammunition — reachable at Uncommon if you brought the right friend.

`Covering Partner` was originally a flat party-Block card, which any character could have printed.
Tying the bonus to a Cycle makes it a *Gunslinger* card — it advances the hammer, which is
sometimes exactly what you wanted and sometimes ruins a lined-up Heavy Round. The party Block is
free; the sequencing cost is real.

`Suppressive Volley` is the payload: the burst turn that also turns down the incoming damage on
everyone. Kept from the original draft unchanged.

`Ride Together` replaces `Stand Together`. The Gunslinger's structural weakness is that
ammunition costs cards, and in a party the other players are already attacking every turn — so
their attacks load the gun. Capped at once per turn per ally: in a three-player party that is 2
free Lead a turn, against the 2-Energy rare `Bottomless Bandolier`'s 1 specialist Round a turn.
Stronger, and correctly so, because it requires other people.

---

## The Alchemist — 5

**Built** — `HelloSpireCode/Alchemist/Cards/Multiplayer.cs`, gated on `AlchemistMultiplayerCard`.
Revised 2026-09-28 from the first draft: the Alchemist is the party's **supplier**. It hands
other players real Potions and Gold, and is paid in tempo and fresh Brews when they use them.

**Ruling this set depends on:** *a Potion given to another player is permanent.* Volatile
tracking lives on the Alchemist's own bench and never follows a Potion into someone else's belt,
so a gift is kept after the fight exactly like a Potion that player found. This also means no
Alchemist state is ever attached to a non-Alchemist creature.

| # | Card | Type | Cost | Effect | Upgrade |
|---:|---|---|---:|---|---|
| 1 | **Pass the Bottle** | Skill | 0 | Give another player one of your Potions. They gain 1 Energy. Exhaust. | They also draw 1 card. |
| 2 | **Shared Flask** | Skill | 1 | Another player gains a random Common Potion (from their own pool). Exhaust. | You choose it from 3. |
| 3 | **Bulk Order** | Skill | 1 | ALL players draw 1 card. Every other player gains 10 Gold. Exhaust. | 15 Gold. |
| 4 | **Sympathetic Detonation** | Attack | 1 | Deal 7 damage to ALL enemies, plus 4 for each other player who has played an Attack this turn. | 9 damage; the bonus becomes 5. |
| 5 | **Joint Venture** | Power | 2 | Whenever another player uses a Potion, they gain 5 Gold and you Brew a random Common Potion. Up to 3 times per combat. | Up to 5 times per combat. |

**Solo behaviour.** `Pass the Bottle` Distills the Potion and gives *you* the Energy (and the
card, upgraded). `Shared Flask` Brews into your own belt — Volatile, as every self-Brew is, so the
card never becomes a permanent-Potion printer solo. `Bulk Order` pays the Gold to you, since there
is no one else. `Sympathetic Detonation` is a plain 7 AoE. `Joint Venture` does nothing.

**Why these five.**

`Pass the Bottle` is a Potion literally changing hands. A Potion given away arrives permanent even
if it was Brewed Volatile — that conversion is the card's value, and Exhaust keeps it to once a
combat per copy. The Alchemist's bench-bound Potions (Unstable Concoction, Residual Reagent) cannot
be given; they mean nothing in another belt. If the recipient's belt is full, the Potion stays put
and they still get the Energy.

`Shared Flask` is the only card in these fifteen that breaks house rule 1, and it earns it — the
Alchemist is the character who hands people objects. The gift is drawn from the **recipient's**
Common pool (`ILabBridge.GiftPotionOptions`), so an Ironclad gets Potions an Ironclad could roll,
never the Alchemist's weaker Volatile-only set.

`Bulk Order` is the Alchemist as the party's bank. The first draft had it *spend* Gold (Invest 8)
for party Energy; it now *gives* Gold out, which is simpler to read and is the character's party
role in one line. Tuning knob if co-op Gold inflates: lower the payout, keep the draw.

`Sympathetic Detonation` reads the party's turn rather than its roster and rewards going *last*.
The count lives on the bench (`LabPower.AlliesAttackedThisTurn`, fed by the base game's
`AfterCardPlayed`), which the starting relic opens at combat start. An Alchemist who has lost the
Satchel and has done nothing else yet this combat reads a bonus of zero — a known, harmless edge.

`Joint Venture` closes the loop: give a Potion, they drink it, they get Gold and you get a fresh
Brew. It is fed from `PotionUsePatch` for every player's Potion use. The per-combat cap is issue
#4's Gold guardrail — any repeatable Gold trigger needs one, or stalling becomes correct.

---

## The synergy web

Five named loops. Each one is a pair or triple of cards that is worth more together than the sum
of its halves, and each one is checkable in a playtest.

### Loop 1 — Judgment · Paladin → Gunslinger → everyone

```
Paladin      Mark for Judgment    apply 2 Vulnerable
Gunslinger   Softened Up          apply 1 Debilitate to ALL enemies
                                  -> Debilitate doubles Weak AND Vulnerable
Everyone                          hits a 4-Vulnerable target
```

Neither half is impressive alone. The Gunslinger has no Vulnerable to double; the Paladin's 2
Vulnerable is an ordinary debuff. Together they are the party's damage turn, and the Gunslinger's
own `Suppressive Volley` Weak is doubled in the same breath. This is the pack's flagship
interaction and the one to build a playtest around.

### Loop 2 — The Loaded Turn · Alchemist ↔ Gunslinger

```
Alchemist    Pass the Bottle       -> Gunslinger gains 1 Energy on a load turn
Alchemist    Bulk Order            -> everyone draws a card
Gunslinger   Ride Together         -> every ally Attack loads a Lead Round
Alchemist    Sympathetic Detonation-> is an Attack, so it loads the Gunslinger's gun
```

Runs both directions, which is what makes it a loop rather than a favour. The Gunslinger's worst
structural problem is the turn spent loading instead of firing; the Alchemist's Energy and cards
compress load-and-fire into one turn. In return, the Alchemist's attacks are literally putting
bullets in the gun.

### Loop 3 — Faith from the Party · everyone → Paladin

```
Gunslinger   Covering Partner     ALL players gain Block
Alchemist    Shared Flask         -> ally drinks a Block Potion
Paladin      Oath of the Company  -> both of the above are Torm Faith
```

The Paladin's slow ramp is its defining weakness. `Oath of the Company` outsources the ramp to
teammates who were going to gain Block and heal anyway. A Paladin in a three-stack reaches an
8-Faith threshold turns earlier than a solo one — and, correctly, has to spend a 2-Energy Power
turn to buy that.

### Loop 4 — The Potion Round-Trip · Alchemist ↔ everyone

```
Alchemist    Shared Flask     -> permanent Potion into an ally's belt
Alchemist    Pass the Bottle  -> or hand over one already Brewed
Ally                          -> drinks it (costs them no Energy)
Alchemist    Joint Venture    -> ally +5 Gold, Alchemist Brews another
Alchemist    Bulk Order       -> more Gold out to the party
```

The Alchemist's economy runs through other people drinking — the Gold lands with them, the Brews with the Alchemist. Note that the loop is capped twice —
`Joint Venture` at 3 triggers a combat, `Bulk Order` by Exhaust — because an uncapped version is
exactly the stall-to-farm-Gold failure mode issue #4 warns about.

### Loop 5 — Who do I cover? · Paladin ↔ Gunslinger *(anti-synergy, deliberate)*

`Bear the Weight` redirects half an ally's incoming damage to the Paladin. The Gunslinger's Armor
reduces each *instance* of unblocked damage — so covering a Gunslinger who has Armor up means the
Paladin eats damage that Armor would have absorbed for free. The Alchemist, at 68 HP with no
mitigation keyword of its own, is the right target almost always.

This is the only intentional negative interaction in the set, and it is here on purpose: without
it, `Bear the Weight` is "cover whoever is lowest" and involves no thought at all.

### The full picture

```
                      ┌──────────────────────────────┐
                      │                              │
                      v                              │
              ┌───────────────┐  Vulnerable  ┌───────────────┐
              │    PALADIN    │─────────────>│  GUNSLINGER   │
              │  protection   │              │ amplification │
              └───────────────┘<─────────────└───────────────┘
                      ^          party Block          │
                      │          (-> Faith)           │ Debilitate
              heals   │                               │ Weak
              Block   │                               v
              (-> Faith)                      ┌───────────────┐
                      └───────────────────────│   ALCHEMIST   │
                                              │ acceleration  │
                                              └───────────────┘
                                                  ^      │
                                        Potions,  │      │ Energy, cards
                                        ally      │      │ Potions
                                        attacks   └──────┘
```

Every arrow is a card, not a vibe. The Paladin gets Faith from what the other two do; the
Gunslinger gets ammunition and targets; the Alchemist gets Gold and drinkers.

---

## Cuts from the earlier drafts

| Cut | From | Why |
|---|---|---|
| **Stand Together** *(2E, ALL players gain 8 Block, you gain 1 Dodge)* | `design/gunslinger.md` §10 | Duplicated `Covering Partner`. Two of five slots on party Block, and neither used the Cylinder. Replaced by `Ride Together`, which fills the missing Engine slot. |
| **Community Formula** *(2E, ALL players choose 1 of 3 random Common cards)* | issue #2 §27 | Four simultaneous card-choice prompts stalls a four-player turn on the slowest reader, every time. The good half — party card generation — lives on `Bulk Order` without any prompt. |
| **Shared Flask** *(1E, ally gains 8 Block, Brew a Block Potion for yourself)* | issue #2 §27 | Name kept, effect replaced. The original was a third party-Block card across the set. Handing over an actual Potion is the thing only this character can do. |
| **Joint Venture** *(once per **combat**, ALL players gain 3 Block)* | issue #2 §27 | 3 Block once, for 2 Energy, is not a Power. Rebuilt as a repeatable, capped Gold-and-Potion engine so it fills slot 5. |
| **Bulk Order** payout *(4 Block → 1 Energy)* | issue #2 §27 | Block was the fourth party-Block effect in a five-card set. Energy is the Alchemist's actual role in the trinity. |

---

## Balance watchlist

Ordered by how likely each is to be the thing that breaks.

1. **`Softened Up` in a four-stack.** Flagged in `design/gunslinger.md` already. Doubled Weak and
   Vulnerable multiply *every* player's damage, so its value scales with party size **and** with
   how much debuff the party brings. Test against a Silent (native Vulnerable) before testing
   against the Paladin.
2. **`Oath of the Company` in a four-stack.** Nine Faith a turn is the theoretical cap. If it lands
   anywhere near that in practice, cut the Tyr clause first — kills are the least countable of the
   three triggers.
3. **The Alchemist's Gold in a four-stack.** `Bulk Order` prints 30 Gold a play and `Joint Venture`
   up to 15–25 a combat, all into allies' pockets. Watch shop prices against a party's total Gold;
   lower the payouts before touching the caps.
4. **`Ride Together` plus `Empty the Cylinder`/`High Noon`.** Free ammunition into a Fire 6 is the
   Gunslinger's burst ceiling. Verify the salvo cards do not become one-card kills when the gun
   refills for free.
5. **`Bear the Weight` desync.** Not a balance risk, a correctness one. Damage redirection across
   clients is the highest-risk implementation in this document.
6. **`Communion` with `Heresy`.** `Heresy` makes every deity count as your highest, so `Communion`
   reads that highest value twice — Block *and* healing at full rate. Probably fine, since both
   cards are expensive and `Heresy` is the wide deck's entire payoff, but check it.

---

## Open questions

- ~~**How does the game gate a multiplayer card?**~~ **Resolved.** It is
  `CardModel.MultiplayerConstraint`, returning `CardMultiplayerConstraint.MultiplayerOnly`. A pool
  filters on `RunState.CardMultiplayerConstraint` when it is asked for its unlocked cards, so the
  gate needs no change to the `[Pool]` attribute these cards inherit. It sits once on
  `GunslingerMultiplayerCard`; the Paladin's party cards carry the same override per-card. House
  rule 3 still stands — the constraint keeps a card out of the solo *offer*, not out of a solo run
  that continues from a save or a lobby that empties out, so none of them may brick.
- **Can a card write a Potion into another player's belt?** Built on the assumption that it can:
  `Belt.Give`/`Belt.Gift` call `PotionCmd.TryToProcure` with the ally as the Player. Verify in a
  real two-player run that the Potion appears on both clients. If it does not, the fallback is
  "Brew a Potion; the next ally to use a Potion this combat draws 2 cards".
- **Does the game expose an ally-target `TargetType`?** `AnyAlly`, `AnyPlayer` and `AllAllies` are
  all in the enum per `TODO.md`, but their exact targeting semantics — can you target yourself with
  `AnyAlly`? what is `Target` when solo? — are unverified. The Gunslinger implementation routes
  every one of these through `GunslingerEffects` so there is one file to fix.
- **Do ally-facing effects need explicit sync?** Per `TODO.md` Phase 9, custom state must serialize.
  `Ride Together` and `Oath of the Company` both read other players' card plays, which means both
  clients must agree on play order. Test with two players before writing the third character's five.
- **Turn order.** `Sympathetic Detonation` and `Oath of the Company` both depend on what allies did
  "this turn". Whether Slay the Spire 2 co-op is simultaneous or sequential changes both cards; if
  simultaneous, "this turn" needs a precise definition before either can be built.
