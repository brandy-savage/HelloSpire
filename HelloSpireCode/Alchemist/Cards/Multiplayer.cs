using HelloSpire.HelloSpireCode.Alchemist.Lab;
using HelloSpire.HelloSpireCode.Alchemist.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;

namespace HelloSpire.HelloSpireCode.Alchemist.Cards;

// The five multiplayer cards. See design/multiplayer-cards.md for the set they belong to.
//
// The Alchemist's job in a party is supply: it hands other players real, permanent Potions and
// Gold, and gets tempo and fresh Brews back when they use what it gave them. Potions given to
// another player are never Volatile -- Volatile tracking lives on this character's own bench and
// does not follow a Potion into someone else's belt.

/// <summary>
/// Base for the multiplayer five: the one place the MultiplayerOnly gate goes, same as
/// GunslingerMultiplayerCard. Every card below still has a defined solo behaviour (house rule 3),
/// because save continuation or an emptied lobby can still put one in a solo deck.
/// </summary>
public abstract class AlchemistMultiplayerCard(int cost, CardType type, CardRarity rarity, TargetType target)
    : AlchemistCard(cost, type, rarity, target)
{
    public override CardMultiplayerConstraint MultiplayerConstraint => CardMultiplayerConstraint.MultiplayerOnly;
}

/// <summary>
/// Give another player one of your Potions; they gain Energy.
///
/// The ping: free, and the Potion arrives permanent even if it was Brewed Volatile. Solo it
/// Distills the Potion for your own Energy instead, which is the design doc's solo line.
/// </summary>
public sealed class PassTheBottle() : AlchemistMultiplayerCard(0, CardType.Skill, CardRarity.Uncommon, TargetType.AnyAlly)
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new EnergyVar(1), new CardsVar(0)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    protected override IEnumerable<IHoverTip> ExtraHoverTips => [Tip(AlchemistTips.Distill)];

    protected override async Task OnPlay(PlayerChoiceContext ctx, CardPlay play)
    {
        await CreatureCmd.TriggerAnim(Owner.Creature, "Cast", Owner.Character.CastAnimDelay);

        var ally = AlchemistEffects.ResolveAlly(Lab, play.Target);
        if (ally == Owner) await Belt.Distill(ctx, Lab);
        else await Belt.Give(ctx, Lab, ally);

        await AlchemistEffects.GainEnergyFor(ally, DynamicVars.Energy.BaseValue);
        await AlchemistEffects.DrawFor(ctx, ally, DynamicVars.Cards.IntValue);
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1m);
}

/// <summary>
/// Another player gains a random Common Potion from their own pool -- a real one, kept after the
/// fight. Upgraded, the Alchemist picks from 3. Solo it Brews into your own belt, Volatile as
/// usual, so the card never becomes a permanent-Potion printer in single-player.
/// </summary>
public sealed class SharedFlask() : AlchemistMultiplayerCard(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyAlly)
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Choices", 1m)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    protected override IEnumerable<IHoverTip> ExtraHoverTips => [Tip(AlchemistTips.Brew)];

    protected override async Task OnPlay(PlayerChoiceContext ctx, CardPlay play)
    {
        await CreatureCmd.TriggerAnim(Owner.Creature, "Cast", Owner.Character.CastAnimDelay);

        var choices = DynamicVars["Choices"].IntValue;
        var ally = AlchemistEffects.ResolveAlly(Lab, play.Target);

        if (ally != Owner) await Belt.Gift(ctx, Lab, ally, choices);
        else if (choices > 1) await Belt.BrewChoice(ctx, Lab, choices);
        else await Belt.BrewRandom(ctx, Lab);
    }

    protected override void OnUpgrade() => DynamicVars["Choices"].UpgradeValueBy(2m);
}

/// <summary>
/// ALL players draw a card; every other player gains Gold.
///
/// The Gold goes out, not in: the Alchemist is the party's bank. Exhausts, so it pays once a
/// combat. Solo there is nobody to pay, so the Gold is yours.
/// </summary>
public sealed class BulkOrder() : AlchemistMultiplayerCard(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self)
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new CardsVar(1), new DynamicVar("Gold", 10m)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    protected override async Task OnPlay(PlayerChoiceContext ctx, CardPlay play)
    {
        await CreatureCmd.TriggerAnim(Owner.Creature, "Cast", Owner.Character.CastAnimDelay);

        foreach (var player in AlchemistEffects.AllPlayers(Lab))
            await AlchemistEffects.DrawFor(ctx, player, DynamicVars.Cards.IntValue);

        var gold = DynamicVars["Gold"].BaseValue;
        var allies = AlchemistEffects.Allies(Lab);
        if (allies.Count == 0)
        {
            await PlayerCmd.GainGold(gold, Owner);
            return;
        }

        foreach (var ally in allies)
            await PlayerCmd.GainGold(gold, ally);
    }

    protected override void OnUpgrade() => DynamicVars["Gold"].UpgradeValueBy(5m);
}

/// <summary>
/// Damage to ALL enemies, more for each other player who has already attacked this turn.
///
/// The only card in the set that rewards going last. The count lives on the bench
/// (<see cref="LabPower.AlliesAttackedThisTurn"/>), which the starting relic opens at combat
/// start; without a bench yet, the bonus is simply zero. Solo it is a plain AoE.
/// </summary>
public sealed class SympatheticDetonation() : AlchemistMultiplayerCard(1, CardType.Attack, CardRarity.Uncommon, TargetType.AllEnemies)
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(7m, ValueProp.Move), new DynamicVar("Bonus", 4m)];

    protected override async Task OnPlay(PlayerChoiceContext ctx, CardPlay play)
    {
        var attackers = AlchemistEffects.Peek(Lab)?.AlliesAttackedThisTurn.Count ?? 0;
        var damage = DynamicVars.Damage.BaseValue + DynamicVars["Bonus"].BaseValue * attackers;

        await DamageCmd.Attack(damage).FromCard(this)
            .TargetingAllOpponents(CombatState)
            .WithHitFx("vfx/vfx_heavy_blunt")
            .Execute(ctx);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(2m);
        DynamicVars["Bonus"].UpgradeValueBy(1m);
    }
}

/// <summary>
/// Whenever another player uses a Potion, they gain Gold and you Brew a random Common Potion --
/// up to 3 times a combat (5 upgraded). Closes the loop with Pass the Bottle and Shared Flask:
/// hand a Potion over, they drink it, both of you are paid. Blank solo, like Ride Together.
/// </summary>
public sealed class JointVenture() : AlchemistMultiplayerCard(2, CardType.Power, CardRarity.Uncommon, TargetType.Self)
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new PowerVar<JointVenturePower>(3m), new DynamicVar("Gold", JointVenturePower.Gold)];

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        [Tip(AlchemistTips.Brew), HoverTipFactory.FromPower<JointVenturePower>()];

    protected override async Task OnPlay(PlayerChoiceContext ctx, CardPlay play)
    {
        await CreatureCmd.TriggerAnim(Owner.Creature, "Cast", Owner.Character.CastAnimDelay);
        await PowerCmd.Apply<JointVenturePower>(
            ctx, Owner.Creature, DynamicVars["JointVenturePower"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars["JointVenturePower"].UpgradeValueBy(2m);
}
