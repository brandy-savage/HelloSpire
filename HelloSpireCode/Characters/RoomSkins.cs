using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Bindings.MegaSpine;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Nodes.RestSite;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Screens.Shops;

namespace HelloSpire.HelloSpireCode.Characters;

/// <summary>
/// The combat repaint, everywhere else the character body shows up. Rest sites and the shop
/// instantiate the character's spine scenes directly (RestSiteAnimPath / MerchantAnimPath, both
/// inherited from the Ironclad), so without this the unpainted Ironclad sits at the campfire
/// and browses the shop. The rest site gets the CharacterSkins materials on every SpineSprite in
/// the instantiated scene; the shop swaps in the character's own rig first (see Merchant).
/// </summary>
internal static class RoomSkins
{
    [HarmonyPatch(typeof(NRestSiteCharacter), nameof(NRestSiteCharacter.Create))]
    private static class RestSite
    {
        [HarmonyPostfix]
        private static void Reskin(Player player, NRestSiteCharacter __result)
        {
            if (CharacterSkins.MaterialFor(player.Character) is { } material)
                CharacterSkins.ApplyToSpines(__result, material);
        }
    }

    /// <summary>
    /// The shop scene is still the placeholder's (Ironclad for the Paladin and Gunslinger, Silent
    /// for the Alchemist), so a character with its own rig gets the same swap as in combat:
    /// its baked skeleton goes onto the shop's SpineSprite and relaxed_loop, the merchant idle
    /// every rig carries, restarts on it. Anyone without a rig keeps the shader repaint.
    /// </summary>
    [HarmonyPatch(typeof(NMerchantRoom), "AfterRoomIsLoaded")]
    private static class Merchant
    {
        private const string MerchantIdle = "relaxed_loop";

        [HarmonyPostfix]
        private static void Reskin(NMerchantRoom __instance)
        {
            var players = __instance._players;
            var visuals = __instance._playerVisuals;
            for (var i = 0; i < players.Count && i < visuals.Count; i++)
            {
                var character = players[i].Character;
                if (CharacterSkeletons.SkeletonFor(character) is { } rig && SwapRig(visuals[i], rig)) continue;
                if (CharacterSkins.MaterialFor(character) is { } material)
                    CharacterSkins.ApplyToSpines(visuals[i], material);
            }
        }

        private static bool SwapRig(NMerchantCharacter visual, MegaSkeletonDataResource rig)
        {
            // Same rule as CharacterSkeletons: never throw out of a room-load postfix.
            try
            {
                if (visual.GetChildCount() == 0 || visual.GetChild(0) is not Node2D body ||
                    body.GetClass() != "SpineSprite") return false;
                var sprite = new MegaSprite(body);
                sprite.SetSkeletonDataRes(rig);
                if (sprite.GetSkeleton()?.GetData()?.HasAnimation(MerchantIdle) == true)
                    visual.PlayAnimation(MerchantIdle, loop: true);
                return true;
            }
            catch (System.Exception e)
            {
                GD.PushWarning($"[HelloSpire] shop rig swap failed, falling back to the shader repaint: {e.Message}");
                return false;
            }
        }
    }
}
