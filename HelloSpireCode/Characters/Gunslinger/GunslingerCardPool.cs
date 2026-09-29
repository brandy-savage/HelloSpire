using BaseLib.Abstracts;
using HelloSpire.HelloSpireCode.Extensions;
using Godot;

namespace HelloSpire.HelloSpireCode.Characters;

public class GunslingerCardPool : CustomCardPoolModel
{
    public override string Title => Gunslinger.CharacterId; //Not a display name.

    public override string BigEnergyIconPath => "big_energy.png".CharacterUiPath(Gunslinger.AssetFolder);
    public override string TextEnergyIconPath => "text_energy.png".CharacterUiPath(Gunslinger.AssetFolder);

    // The card frame is a shader tint over the base (Ironclad-red) frame, driven from the
    // character colour — same as the Paladin and Alchemist pools.
    public override Color ShaderColor => Gunslinger.Color;

    public override Color DeckEntryCardColor => Gunslinger.Color;

    public override bool IsColorless => false;
}
