using System.Collections.Generic;
using System.IO;
using System.Linq;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Bindings.MegaSpine;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace HelloSpire.HelloSpireCode.Characters;

/// <summary>
/// Per-character spine skeletons. A character that ships plain Spine files in the mod's
/// spine/&lt;character&gt;/ folder (one .atlas, its .skel beside it, page .png files as the
/// atlas names them) gets its combat body swapped to that rig when visuals are created —
/// the inherited Ironclad rig is replaced for that character only, and nothing else in
/// the game (vanilla Ironclad included) sees the custom assets.
///
/// Loading technique borrowed from CustomSkeletonLoader: the game's spine-godot module
/// loads plain files from any filesystem path (SpineAtlasResource.load_from_atlas_file +
/// SpineSkeletonFileResource.load_from_file composed into a SpineSkeletonDataResource) —
/// no .spskel/.spatlas wrappers or pck import required.
///
/// Missing folder or failed load degrades silently to the CharacterSkins shader repaint,
/// same spirit as that patch's own fallback. The shop swaps to the same rig, and the rest site
/// to the character's spine/<name>/restsite/ rig (see RoomSkins).
/// </summary>
[HarmonyPatch(typeof(Creature), nameof(Creature.CreateVisuals))]
internal static class CharacterSkeletons
{
    private static readonly Dictionary<string, MegaSkeletonDataResource?> Cache = new();

    private static string? FolderFor(MegaCrit.Sts2.Core.Models.CharacterModel? character) => character switch
    {
        Paladin => "paladin",
        Gunslinger => "gunslinger",
        Alchemist => "alchemist",
        _ => null,
    };

    /// <summary>The custom rig for a HelloSpire character, or null to keep the inherited one.
    /// <paramref name="variant"/> selects a sub-rig folder: null = the combat body
    /// (spine/&lt;name&gt;/), "restsite" = the campfire body (spine/&lt;name&gt;/restsite/, the
    /// donor's own rest-site skeleton with its act loops, recoloured).</summary>
    internal static MegaSkeletonDataResource? SkeletonFor(MegaCrit.Sts2.Core.Models.CharacterModel? character,
                                                          string? variant = null)
    {
        if (FolderFor(character) is not { } folder) return null;
        if (variant != null) folder = Path.Combine(folder, variant);
        if (Cache.TryGetValue(folder, out var cached)) return cached;
        var built = Build(folder, optional: variant != null);
        Cache[folder] = built; // negative results cached too — one disk probe per run
        return built;
    }

    private static MegaSkeletonDataResource? Build(string folder, bool optional = false)
    {
        var modDir = Path.GetDirectoryName(typeof(CharacterSkeletons).Assembly.Location);
        if (modDir == null) return null;
        var dir = Path.Combine(modDir, "spine", folder);
        if (!Directory.Exists(dir))
        {
            if (optional) return null;   // a variant rig is allowed to be absent
            // Loud on purpose: a missing folder means an incomplete install (the mod was
            // copied without spine/), and the character silently degrades to the shader
            // repaint. This line is how a co-op partner's godot.log proves which it is.
            GD.PushWarning($"[HelloSpire] spine/{folder}/ not found beside the mod DLL — " +
                           "incomplete install? Falling back to the shader repaint.");
            return null;
        }
        var atlasPath = AtlasIn(dir);
        if (atlasPath == null) return null;
        var skelPath = Path.ChangeExtension(atlasPath, ".skel");
        if (!File.Exists(skelPath)) return null;

        var atlas = ClassDB.Instantiate("SpineAtlasResource").AsGodotObject();
        if (atlas == null) return null;
        if (atlas.Call("load_from_atlas_file", atlasPath).AsInt64() != 0)
        {
            GD.PushWarning($"[HelloSpire] spine atlas failed to load: {atlasPath}");
            return null;
        }
        var skelFile = ClassDB.Instantiate("SpineSkeletonFileResource").AsGodotObject();
        if (skelFile == null) return null;
        if (skelFile.Call("load_from_file", skelPath).AsInt64() != 0)
        {
            GD.PushWarning($"[HelloSpire] spine skeleton failed to load: {skelPath}");
            return null;
        }
        var data = ClassDB.Instantiate("SpineSkeletonDataResource").AsGodotObject();
        if (data == null) return null;
        data.Set("atlas_res", atlas);
        data.Set("skeleton_file_res", skelFile);
        GD.Print($"[HelloSpire] loaded custom skeleton for '{folder}' from {dir}");
        return new MegaSkeletonDataResource(data);
    }

    /// <summary>
    /// The folder's rig atlas. SOURCE.txt names the donor, and that is the atlas to load:
    /// an install updated by copying over the old one can still hold a previous donor's
    /// .atlas (the stick-figure ironclad.atlas beside silent.atlas), and "first *.atlas"
    /// picks it alphabetically.
    /// </summary>
    private static string? AtlasIn(string dir)
    {
        var atlases = Directory.GetFiles(dir, "*.atlas");
        if (atlases.Length > 1)
        {
            try
            {
                var source = Json.ParseString(File.ReadAllText(Path.Combine(dir, "SOURCE.txt"))).AsGodotDictionary();
                var donor = source["donor"].AsString();
                var named = atlases.FirstOrDefault(a => Path.GetFileNameWithoutExtension(a) == donor);
                if (named != null) return named;
            }
            catch { /* no or unreadable SOURCE.txt: fall through */ }
            GD.PushWarning($"[HelloSpire] {atlases.Length} atlases in {dir} — stale install? " +
                           "Delete the folder and redeploy.");
        }
        return atlases.OrderBy(a => a).FirstOrDefault();
    }

    [HarmonyPostfix]
    private static void SwapSkeleton(Creature __instance, NCreatureVisuals? __result)
    {
        // NEVER throw out of this postfix: an exception here aborts the combat setup
        // loop and every creature in the fight loses its node (learned the hard way).
        try
        {
            if (__result == null || SkeletonFor(__instance.Player?.Character) is not { } rig) return;
            var body = __result.GetNodeOrNull<Node2D>("%Visuals");
            if (body == null || body.GetClass() != "SpineSprite") return;

            var sprite = new MegaSprite(body);
            // The animation state may not exist yet at CreateVisuals time —
            // GetAnimationState THROWS in that case (per sts2.xml, prefer Try*).
            string? current = null;
            try { current = sprite.GetAnimationState()?.GetCurrent(0)?.GetAnimation()?.GetName(); }
            catch { /* no state yet; the game starts idle right after */ }

            sprite.SetSkeletonDataRes(rig);

            try
            {
                if (current != null && sprite.GetSkeleton()?.GetData()?.HasAnimation(current) == true)
                    sprite.GetAnimationState()?.SetAnimation(current, true, 0);
            }
            catch { /* restore is best-effort; default idle takes over */ }
        }
        catch (System.Exception e)
        {
            GD.PushWarning($"[HelloSpire] skeleton swap failed, keeping inherited rig: {e.Message}");
        }
    }
}
