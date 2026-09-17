# Legacy V-Ray Advanced To Standard

Cinema 4D Python utility for recovering materials from old V-Ray for Cinema 4D scenes.

This script was originally created to help reopen and reuse architectural visualization projects made with old versions of V-Ray for Cinema 4D, especially scenes dating from around 2011.

---

## What it does

The script scans the Cinema 4D document for legacy:

**VRayAdvancedMaterial**

For every compatible V-Ray material found, it creates a new Cinema 4D Standard material.

The script attempts to detect texture types from their filenames and restore the most important material channels.

Texture detection includes keywords related to:

- Diffuse
- Albedo
- Base Color
- Alpha
- Opacity
- Transparency
- Emissive
- Luminance
- Normal
- Bump
- Roughness
- Specular
- Metallic

Texture detection is based partly on common keywords contained in texture filenames.

Examples:

```text
wall_diffuse.jpg
wall_albedo.jpg
glass_opacity.png
stone_normal.jpg
concrete_bump.jpg



How to use
1. Open the old Cinema 4D scene

Open the Cinema 4D project containing the old V-Ray materials.

Make sure the original texture files are still available and correctly linked to the scene.

2. Save a copy of the project

Before running the script, it is strongly recommended to save a copy of the Cinema 4D scene.

The script modifies material assignments throughout the document.

3. Open the Cinema 4D Script Manager

In Cinema 4D, open the Python Script Manager.

Load: Legacy_VRayAdvanced_To_Standard.py

4. Run the script

No object or material selection is required.

The script automatically scans all materials in the current Cinema 4D document.

5. Material conversion

For every compatible legacy V-Ray Advanced Material, a new Cinema 4D Standard material is created.

The new material receives the suffix:

_STD

Example:

Old_Wall_Material

becomes:

Old_Wall_Material_STD
6. Texture recovery

The script attempts to recover the main texture maps from the legacy V-Ray material.

The following Cinema 4D Standard channels are currently reconstructed:

Color / Diffuse
Alpha
Luminance / Emissive
Bump

Normal maps are currently imported into the Bump channel.

A basic GGX reflectance layer is also created.

7. Material replacement

After the new Standard material is created, the script searches the Cinema 4D object hierarchy.

Texture Tags using the original V-Ray material are automatically redirected to the newly created Standard material.

The original V-Ray material remains in the Material Manager and is not automatically deleted.

Compatibility

Created for very old V-Ray for Cinema 4D scenes using:

VRayAdvancedMaterial

Tested with:

Cinema 4D 2023.1.2
Legacy V-Ray for Cinema 4D scenes originally created around 2011

This script is not intended for current V-Ray material systems.

Compatibility with modern versions of V-Ray has not been tested.

Limitations

This is primarily a recovery utility.

It is not intended to perfectly reproduce every original V-Ray material.

Material reconstruction depends partly on texture filenames.

For best results, texture filenames should contain recognizable terms such as:

diffuse
albedo
basecolor
color
opacity
alpha
normal
bump
height
rough
gloss
specular
metallic
emissive
luminance

The script can detect Roughness, Specular and Metallic texture names, but these channels are not fully reconstructed in the current version.

A basic GGX reflectance layer is created instead, using a default roughness value.

V-Ray-specific settings such as advanced reflections, refraction, IOR behavior, procedural shaders and other renderer-specific parameters may require manual reconstruction.

Always check converted materials manually after conversion.

Warning

Before using the script:

Save your Cinema 4D project.
Preferably work on a copy of important archive files.
Make sure all texture files are available.
Verify the converted materials before production use.

The script modifies material assignments on Texture Tags throughout the Cinema 4D scene.

Typical use case

This tool can be useful for architecture and archviz studios with old Cinema 4D / V-Ray project archives that need to be reopened in newer versions of Cinema 4D.

Instead of rebuilding every material manually, the script attempts to recover the main texture maps and replace obsolete V-Ray materials with usable Cinema 4D Standard materials.



