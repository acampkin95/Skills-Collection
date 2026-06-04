# AI Asset Generation Prompt Library

Ready-to-use prompt templates for generating brand assets with **Recraft** (SVG logos, icons, backgrounds, illustrations) and **ElevenLabs Image & Video** (brand videos, motion content, storyboards).

## Table of Contents
1. [Recraft Prompts — SVG & Image](#recraft)
2. [ElevenLabs Prompts — Image & Video](#elevenlabs)
3. [Prompt Engineering Principles](#principles)

---

## Recraft Prompts — SVG & Image

### Platform Notes
- **Recraft V4** supports native SVG output — real vector paths, not traced rasters
- Set mode to **Vector / SVG** for all logo, icon, and background pattern work
- Set mode to **Image** for photographic mockups, textures, and marketing visuals
- Use **Brand Style** feature to upload reference images for consistent generations
- Export as SVG for logos/icons, PNG for rasters

### R1: Primary Logomark (SVG)

```
Minimalist logomark for a brand called [BRAND_NAME]. The mark represents
[CORE_CONCEPT — e.g., "a mould cross-section with pour channels feeding
into a casting cavity"]. 

Style: clean geometric line art, stroked outlines only, no solid fills.
Stroke weight: 2px consistent throughout. Rounded stroke caps and joins.
Single colour: [PRIMARY_HEX]. Transparent background.

The mark must work as a 24px favicon and a 512px splash screen.
No text. No gradients. No shadows. Pure vector geometry.
```

**Model**: Recraft V4 SVG
**Iterations**: Generate 4-8 variants, select strongest, refine with "Make the [element] thicker/thinner/more geometric/simpler"

### R2: Alternate Logo Concepts (SVG)

```
Three distinct logomark concepts for [BRAND_NAME], a [PRODUCT_DESCRIPTION].
Each concept explores a different visual metaphor:

Concept A: [METAPHOR_1 — e.g., "layered cross-section view"]
Concept B: [METAPHOR_2 — e.g., "transformation arrow / before-after"]
Concept C: [METAPHOR_3 — e.g., "technical blueprint / grid construction"]

Style for all: minimalist line art, stroked outlines only, 2px stroke,
rounded caps, single colour [PRIMARY_HEX], transparent background.
No text, no gradients, no fills.
```

**Model**: Recraft V4 SVG

### R3: App Icon / Favicon Source (SVG)

```
App icon for [BRAND_NAME]. Simplified version of the brand logomark
optimised for small sizes (16px–512px). The icon must be legible at
16×16 pixels.

Style: bold geometric shapes, maximum 3-4 distinct elements, thick
strokes (2.5px), single colour [PRIMARY_HEX] on transparent background.
Square aspect ratio. No text. No fine detail that disappears at small sizes.
```

**Model**: Recraft V4 SVG
**Note**: Generate at large size, test by scaling down to 16px preview

### R4: Background Pattern (SVG)

```
Seamless tiling background pattern for [BRAND_NAME]. The pattern
represents [CONCEPT — e.g., "engineering blueprint grid with subtle
technical drawing elements"].

Style: very subtle, low-opacity line work. Stroke weight: 0.5–1px.
Single colour: [PRIMARY_HEX] at approximately 5-8% opacity appearance.
Must tile seamlessly. Grid-based composition with [GRID_SIZE]px repeat.
Transparent background. Minimal, restrained — this sits behind content.
```

**Model**: Recraft V4 SVG
**Post-processing**: Set opacity to 4-8% in CSS/code

### R5: Supporting Illustration Set (SVG)

```
Set of 6 supporting illustrations for [BRAND_NAME], a [PRODUCT_DESCRIPTION].
Each illustration represents a different feature or workflow step:

1. [STEP/FEATURE_1 — e.g., "uploading reference photos"]
2. [STEP/FEATURE_2 — e.g., "automated validation"]
3. [STEP/FEATURE_3 — e.g., "configuring mould parameters"]
4. [STEP/FEATURE_4 — e.g., "3D mesh generation"]
5. [STEP/FEATURE_5 — e.g., "quality review"]
6. [STEP/FEATURE_6 — e.g., "final STL export"]

Style: clean line art matching the brand logomark. Consistent 1.5px
stroke weight, rounded caps, [PRIMARY_HEX] colour. Minimalist,
abstract, no human figures. Each fits within a 48×48px frame.
Transparent background.
```

**Model**: Recraft V4 SVG
**Style note**: Upload the primary logomark as a style reference for consistency

### R6: Icon Set (SVG)

```
Set of [N] clean vector icons in a consistent style for [BRAND_NAME].
All icons share: [STROKE_WEIGHT]px stroked outlines, rounded line caps,
single colour [PRIMARY_HEX], no fills, no gradients, no shadows.
Transparent background. Each icon fits a 24×24 grid.

Icons needed:
- [ICON_1 — e.g., "upload/cloud with upward arrow"]
- [ICON_2 — e.g., "shield with checkmark for validation"]
- [ICON_3 — e.g., "slider/controls for configuration"]
- [ICON_4 — e.g., "eye for review/preview"]
- [ICON_5 — e.g., "play button in circle for run/start"]
- [ICON_6 — e.g., "download arrow for export"]
```

**Model**: Recraft V4 SVG
**Note**: Good for hero/marketing use; for UI icons, prefer react-icons/ri

### R7: OG Image / Social Card (Raster)

```
Open Graph social share image for [BRAND_NAME]. Dimensions: 1200×630px.

Layout: dark background ([BACKGROUND_HEX]), the [BRAND_NAME] logomark
centred-left at 40% opacity as a watermark, the brand wordmark
"[BRAND_NAME]" in large bold text upper-right, and the tagline
"[TAGLINE]" in smaller text below.

Subtle [PATTERN — e.g., "blueprint grid pattern"] overlay at 3-5%
opacity. Clean, minimal, typographic focus. Colours: [PRIMARY_HEX]
for accents, [FOREGROUND_HEX] for text.
```

**Model**: Recraft V4 (raster mode)
**Export**: PNG, 1200×630px

### R8: Mockup / Product Context (Raster)

```
Product mockup showing [BRAND_NAME] running on a [DEVICE — e.g.,
"MacBook Pro on a workshop desk"]. The screen displays a dark-themed
UI with [UI_DESCRIPTION — e.g., "a pipeline dashboard with green
progress indicators"].

Environment: [SETTING — e.g., "clean maker's workshop with wooden
surface, soft natural light, slight depth of field"]. Photorealistic
style. [BRAND_NAME] branding visible but not dominant.
```

**Model**: Recraft V4 (raster, photorealistic)
**Export**: PNG, 2000×1200px or 1:1

---

## ElevenLabs Prompts — Image & Video

### Platform Notes
- **ElevenLabs Image & Video** (Beta) supports text-to-image and text-to-video
- Image models: Nanobanana, Flux Kontext, GPT Image, Seedream
- Video models: Veo, Sora, Kling, Wan, Seedance
- Videos can be enhanced with lip-sync, voiceover, music, and SFX
- Use **Flows** for chained multi-step pipelines (image → video → audio)

### E1: Brand Reveal / Logo Animation Video

```
A cinematic brand reveal for [BRAND_NAME]. Dark background slowly
illuminates to reveal the [BRAND_NAME] logomark being drawn stroke
by stroke in [PRIMARY_COLOUR_NAME] light, as if being etched by a
laser or precision tool. The strokes glow softly as they appear.

Once the logomark completes, the wordmark "[BRAND_NAME]" fades in
below with a subtle tracking animation. Hold for 2 seconds.
Ambient particles drift slowly in the background.

Mood: precise, technical, crafted. Colour palette: [PRIMARY_HEX]
on [BACKGROUND_HEX]. Duration: 5 seconds. Cinematic quality.
```

**Model**: Google Veo or OpenAI Sora (highest quality)
**Post**: Add brand music/SFX in ElevenLabs Studio

### E2: Product Demo / Walkthrough Video

```
Screen recording style video showing [BRAND_NAME]'s interface.
The camera smoothly pans across a dark-themed dashboard UI with
[COLOUR_DESCRIPTION — e.g., "sage green accent colours and glass
morphism panels"].

The video shows the workflow: uploading photos on the left panel,
then a progress animation running through pipeline stages, then
the final 3D mould output rotating on screen. Smooth, slow
camera movement. No text overlays needed.

Mood: clean, professional, technical. Duration: 8-10 seconds.
```

**Model**: Kling 2.5 or Wan (good for UI/screen content)
**Post**: Add voiceover narration in ElevenLabs TTS

### E3: Hero Background Ambient Loop

```
Slow-moving abstract 3D wireframe geometry rotating in dark space.
Thin [PRIMARY_COLOUR_NAME] glowing lines form geometric shapes —
icosahedrons and torus knots — against a near-black background.
Very subtle, atmospheric, meant as a background element.

The movement is slow and hypnotic. Lines pulse gently with soft
glow. Depth of field blurs distant geometry. The overall feeling
is technical precision meets calm elegance.

Duration: 10 seconds, seamless loop. Dark background.
```

**Model**: Seedance or Wan (good for abstract/loop content)
**Post**: Export as WebM for website hero background, loop seamlessly

### E4: Social Media Short (Stories/Reels)

```
Vertical video (9:16) for [BRAND_NAME] social media. Quick-cut
sequence showing:

1. Close-up of hands photographing an object from multiple angles
2. The [BRAND_NAME] interface processing the images
3. A 3D wireframe mould appearing and rotating
4. The final physical silicone mould being revealed

Fast cuts (1-2 seconds each). [PRIMARY_COLOUR_NAME] colour grading.
Modern, punchy editing. Text overlay: "[TAGLINE]" appears mid-video.

Duration: 6-8 seconds. Mood: capable, impressive, fast.
```

**Model**: Kling 2.5 (fast, good motion)
**Post**: Add music + text overlays in Studio

### E5: Storyboard Frame Generation (Image)

```
A clean storyboard frame showing [SCENE_DESCRIPTION]. The image
is rendered in a semi-realistic illustration style with a muted
[PRIMARY_COLOUR_NAME] and [NEUTRAL_COLOUR_NAME] colour palette.

Composition: [COMPOSITION — e.g., "medium shot of a maker's hands
positioning an object on a turntable with camera visible in
background"]. Lighting: [LIGHTING — e.g., "soft studio lighting,
slight depth of field"]. Style: editorial photography meets
technical illustration.
```

**Model**: Nanobanana or Flux Kontext (image mode)
**Use**: Generate 4-6 frames for a brand video storyboard

### E6: Brand Identity Presentation Video

```
A polished brand presentation video for [BRAND_NAME]. The video
reveals the brand identity system in sequence:

1. Logo reveal on dark background (2s)
2. Colour palette swatches appearing in a modern grid (2s)
3. Typography samples with the display and body fonts (2s)
4. UI mockup on a device (2s)
5. Closing with logomark and tagline (2s)

Each transition is smooth and precise. [PRIMARY_COLOUR_NAME] accents
against dark backgrounds. Minimal, no clutter. Typography is large
and confident. Total duration: 10 seconds.
```

**Model**: Sora (best for structured/composed content)
**Post**: Add brand voiceover + music in Studio

---

## Prompt Engineering Principles

### For Recraft SVG

1. **Be specific about stroke weight** — "2px stroke" not "thin lines"
2. **Specify "no fills, no gradients, no shadows"** explicitly
3. **Name the exact colour** — HEX value, not "green" or "blue"
4. **State the target size** — "must work at 24px" forces simplicity
5. **Iterate with targeted adjustments** — "Make the handle thicker", "Remove the detail in the centre", "Simplify to 3 elements maximum"
6. **Upload style references** — your existing logomark maintains consistency
7. **One concept per generation** — don't ask for "5 different logos in one image"

### For ElevenLabs Video

1. **Describe the camera, not just the subject** — "slow pan across", "static shot with subtle zoom", "overhead tracking shot"
2. **Specify duration** — keeps the model focused on pacing
3. **Name the mood** — "precise", "cinematic", "punchy", "atmospheric"
4. **Keep colour references concrete** — HEX values or Pantone names, not "greenish"
5. **Describe transitions** — "fade in", "cut to", "dissolve into"
6. **Use Flows for multi-step** — chain image → video → audio for complex sequences
7. **Model selection matters**:
   - Veo / Sora → highest quality, cinematic
   - Kling → fast, good motion, character consistency
   - Wan → abstract, artistic, loop-friendly
   - Seedance → multi-shot sequences, action

### Adapting Prompts to Your Brand

When using these templates, replace all bracketed `[PLACEHOLDERS]` with:
- `[BRAND_NAME]` → the brand name in UPPERCASE
- `[PRIMARY_HEX]` → the Pantone-derived primary HEX value
- `[BACKGROUND_HEX]` → the dark background colour
- `[FOREGROUND_HEX]` → the light text colour
- `[PRIMARY_COLOUR_NAME]` → descriptive name (e.g., "sage green", "deep indigo")
- `[TAGLINE]` → the brand tagline
- `[PRODUCT_DESCRIPTION]` → one-line product summary
- `[CORE_CONCEPT]` → the visual metaphor for the logomark
- All other `[PLACEHOLDERS]` → context-specific details
