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
/// and browses the shop. Both now swap in the character's own rig first (combat rig in the shop,
/// the recoloured rest-site rig at the campfire) and keep the CharacterSkins material as fallback.
/// </summary>
internal static class RoomSkins
{
    /// <summary>
    /// The rest-site scene is the placeholder's, but its body is a dedicated rest-site skeleton
    /// (restsite_&lt;donor&gt;, with the act loops overgrowth/hive/glory). A character that ships
    /// spine/&lt;name&gt;/restsite/ — the same skeleton, recoloured by the workbench — gets it
    /// swapped onto every SpineSprite here, before _Ready picks the act loop. Otherwise the
    /// shader repaint of the inherited art stays as the fallback.
    /// </summary>
    [HarmonyPatch(typeof(NRestSiteCharacter), nameof(NRestSiteCharacter.Create))]
    private static class RestSite
    {
        [HarmonyPostfix]
        private static void Reskin(Player player, NRestSiteCharacter __result)
        {
            if (__result == null) return;
            if (CharacterSkeletons.SkeletonFor(player.Character, "restsite") is { } rig && SwapRig(__result, rig))
                return;
            if (CharacterSkins.MaterialFor(player.Character) is { } material)
                CharacterSkins.ApplyToSpines(__result, material);
        }

        private static bool SwapRig(Godot.Node root, MegaSkeletonDataResource rig)
        {
            try
            {
                var swapped = 0;
                foreach (var child in root.GetChildren())
                {
                    if (child.GetClass() != "SpineSprite") continue;
                    new MegaSprite((Node2D)child).SetSkeletonDataRes(rig);
                    swapped++;
                }
                return swapped > 0;
            }
            catch (System.Exception e)
            {
                GD.PushWarning($"[HelloSpire] rest-site rig swap failed, falling back to the shader repaint: {e.Message}");
                return false;
            }
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
