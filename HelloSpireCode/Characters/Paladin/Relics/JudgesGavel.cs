using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Powers;

namespace HelloSpire.HelloSpireCode.Characters.PaladinContent.Relics;

/// <summary>
/// Pool relic (Uncommon): the first time you Judge each turn, gain 3 Plating. The bridge between
/// the Retribution lane's verb and the Protection lane's stat -- a judging deck gets a reason to
/// stand in front, a Plating deck gets a reason to draft a Judge.
///
/// Rides the IJudgeTrigger funnel in Seals, so it fires on a seal-less Judge too. Once per turn,
/// not per instance: Holy Wrath and Tribunal already multiply judge instances, and 3 Plating per
/// instance would let one X-cost card out-armour the whole Protection lane.
/// </summary>
public sealed class JudgesGavel : PaladinRelic, IJudgeTrigger
{
    public override RelicRarity Rarity => RelicRarity.Uncommon;

    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Plating", 3m)];

    private bool _usedThisTurn;

    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        if (player == Owner) _usedThisTurn = false;
        await Task.CompletedTask;
    }

    public async Task OnJudgeInstance(PlayerChoiceContext ctx, Creature target)
    {
        if (_usedThisTurn) return;
        _usedThisTurn = true;
        Flash();
        await PowerCmd.Apply<PlatingPower>(ctx, Owner.Creature,
            DynamicVars["Plating"].BaseValue, Owner.Creature, null);
    }
}
