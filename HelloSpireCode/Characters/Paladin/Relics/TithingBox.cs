using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;

namespace HelloSpire.HelloSpireCode.Characters.PaladinContent.Relics;

/// <summary>
/// Shop relic: whenever a Tithe triggers, gain 2 Block. A build-around, the way shop relics are:
/// worthless to a deck with no Tithe faces, and the thing that makes discarding a healing card a
/// defensive play in one that has several.
///
/// Rides the ITitheListener funnel in PaladinCard, so it hears every Tithe face and nothing else --
/// a plain discard of a card without a Tithe pays nothing.
/// </summary>
public sealed class TithingBox : PaladinRelic, ITitheListener
{
    public override RelicRarity Rarity => RelicRarity.Shop;

    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Block", 2m)];

    public async Task OnTithed(PlayerChoiceContext ctx, PaladinCard card)
    {
        Flash();
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars["Block"].BaseValue, ValueProp.Unpowered, null);
    }
}
