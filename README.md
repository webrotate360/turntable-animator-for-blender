# WebRotate 360 Turntable Animator for Blender

Create highly interactive **360° and multi-row 3D product views** straight from Blender. This add-on turns your existing 3D models into smooth turntable animations with clickable hotspots and interactive polygonal areas, ready for online or offline publishing.

It integrates directly into Blender's **Scene Properties** and uses the 3D Viewport as a live "viewfinder" to set up your shot. Instead of moving the camera, it animates the selected object, so your lighting rigs and backdrops stay put for photo-realistic, studio-style results.

## Demo

▶️ [Watch the demo video](https://s1.pixriot.com/433181dfa6/Blog/2026-turntable-animator/webrotate-360-turntable-animator.mp4?t=1769475405)

🔎 [Browse live interactive examples](https://www.webrotate360.com/examples/browse-all-examples.aspx) to see what you can build.

> Learn more on the official product page: [WebRotate 360 Turntable Animator for Blender](https://www.webrotate360.com/products/cms-and-e-commerce-plugins/plugin-for-blender.aspx)
>
> Read the full [User Guide](https://www.webrotate360.com/products/cms-and-e-commerce-plugins/plugin-for-blender.aspx?section=User%20Guide) for step-by-step instructions.

---

## Features

- Seamlessly integrates into Blender's Scene Properties (`Properties > Scene > WebRotate 360`).
- Uses the 3D Viewport as a camera "viewfinder" for quick animation setup.
- Animates the **selected object** instead of the camera, keeping lights and environment stationary.
- Simple, intuitive setup for both single-row 360° spins and **multi-row 3D / hemispherical** views.
- Create **indicator hotspots** from Blender *Empties* tied to points of interest.
- Create **polygonal hotspots** from vertex groups or meshes (2D and 3D surfaces).
- Integrated camera and crop-region controls for fast framing adjustments.
- **Fast Render** option for quick draft previews before committing to a full render.
- Multiple build targets: a plain image sequence, a [SpotEditor](https://www.webrotate360.com/products/webrotate-360-product-viewer.aspx) project, or a web-ready interactive 360° asset.
- Works with the free **QuickView** app (Windows) for instant offline previews.
- Published 360° assets are ready to upload to [PixRiot](https://www.webrotate360.com/services/pixriot.aspx) for fast CDN hosting, sharing, and analytics, and can be integrated via [CMS plugins](https://www.webrotate360.com/products/cms-and-e-commerce-plugins.aspx) or the [ImageRotator API](https://webrotate360.s3.amazonaws.com/sites/webrotate360/downloads/Resources/IntegrationTemplates.zip) ([npm component](https://github.com/webrotate360/imagerotator)).

---

## Requirements

- **Blender 2.80 or newer.**
- Optional companion apps from WebRotate 360 (free):
  - **QuickView** - instantly preview and test published interactive 360° views. [Download (QuickView for Windows)](https://www.webrotate360.com/products/webrotate-360-product-viewer.aspx#other).
  - **SpotEditor** - desktop publishing software for advanced editing (non-destructive image processing, image filters, advanced 360 viewer tuning, hotspot styling, custom skins, templates, and more). [Download (WebRotate 360 Product Viewer)](https://www.webrotate360.com/products/webrotate-360-product-viewer.aspx) | [SpotEditor Readme (PDF)](https://webrotate360.s3.amazonaws.com/sites/webrotate360/downloads/Resources/Readme.pdf).

---

## Installation

This repository **is** the add-on source. The `__init__.py` at the repo root is the add-on entry point, so the whole folder needs to be installed into Blender.

### Option A: Install from a ZIP (recommended)

1. Download this repository as a ZIP (use the green **Code → Download ZIP** button on GitHub, or `git clone` and zip it yourself).
2. Make sure the ZIP contains a **single folder** with `__init__.py` directly inside it, e.g.:
  ```
   webrotate360_blender/
   ├── __init__.py
   ├── wr360_panel.py
   ├── ...
   ├── assets/
   └── icons/
  ```
  > GitHub's "Download ZIP" already wraps everything in a folder named like `webrotate360_blender-main`, which is exactly the structure Blender expects.
3. In Blender, open **Edit → Preferences → Add-ons**.
4. Click **Install from Disk...** (top-right) and select the ZIP file.
5. Enable the add-on by ticking the checkbox next to **WebRotate 360 Turntable Animator**.
6. (Optional) Click **Save Preferences** so it stays enabled.

### Option B: Manual install (clone into the add-ons folder)

Copy or clone this repo into Blender's `addons` directory so that `__init__.py` lives at `.../addons/webrotate360_blender/__init__.py`.

- **Windows:** `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\`
- **macOS:** `~/Library/Application Support/Blender/<version>/scripts/addons/`
- **Linux:** `~/.config/blender/<version>/scripts/addons/`

Example using git:

```bash
cd "%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons"   # adjust for your OS
git clone https://github.com/<your-org>/webrotate360_blender.git
```

Then restart Blender, open **Edit → Preferences → Add-ons**, search for **WebRotate 360**, and enable it.

### Verify it's installed

Open the **Properties** editor, select the **Scene** tab, and you should see a **WebRotate 360** section. Hotspot tools appear in the 3D Viewport sidebar under the **WR360** tab.

---

## Quick Start

1. **Set the project folder & object.** In `Properties > Scene > WebRotate 360`, pick a **Project Folder** on disk and choose the **Selected Object** to animate. (If your model has multiple meshes, parent them to an *Empty* at the rotation center and select that *Empty*.)
2. **Frame the shot.** Position the object in the 3D Viewport at the angle and distance you want as the animation's starting point.
3. **Set up the animation.** Enter **Frames Per Row** (20–80 is a good range), optionally set **Rows Up/Down** and **Vertical Step** for multi-row views, then click **Setup animation**. Scrub the Timeline playhead to review.
4. **Fine-tune the camera.** Use the **Camera** section to adjust distance, focal length, and resolution.
5. **Add hotspots (optional).** Use the **WR360** sidebar tab in the 3D Viewport to create indicator hotspots (from *Empties*) or polygonal hotspots (from vertex groups or meshes).
6. **Build the target.** Under **Render and view**, optionally check **Use Fast Render** for a draft, choose a **Target**, and press **Build Target**.

For a draft pass, check **Use Fast Render** and choose **"Publish view and open in QuickView"**. Published 360° assets land in your project folder under `published/360_assets/`. When happy, uncheck Fast Render to use your real engine (Cycles/Eevee) and rebuild.

---

## Build Targets

You can output any of the following:

- **Image sequence**: a set of standalone PNG or JPG images (e.g. for marketplaces like Amazon, marketing decks, or import into SpotEditor).
- **Interactive 360° view**: web-ready viewer you can upload to your site, integrate via free [CMS plugins](https://www.webrotate360.com/products/cms-and-e-commerce-plugins.aspx) (WordPress, Adobe Commerce, etc.) or the [ImageRotator API](https://webrotate360.s3.amazonaws.com/sites/webrotate360/downloads/Resources/IntegrationTemplates.zip) ([npm component](https://github.com/webrotate360/imagerotator)), view offline in QuickView, or host on [PixRiot](https://www.webrotate360.com/services/pixriot.aspx).
- **SpotEditor project**: `.wr360` project for advanced editing and publishing in SpotEditor.

Target options in the panel:

- *Publish view* / *Publish view and open in QuickView*
- *Publish project* / *Publish project and open in SpotEditor*
- *Do not publish and just render images*

> Tip: enable **Skip Re-render on Publish** when you only change viewer/hotspot settings (skin, first frame, new hotspot) to re-publish instantly without re-rendering images.

### Hosting & sharing

Published 360° assets can be hosted on **[PixRiot](https://www.webrotate360.com/services/pixriot.aspx)**, a dedicated CDN platform for 360 product media. Drag and drop your published folder to get a shareable link or embed code, organize assets in (optionally password-protected) folders, use your own domain, and view usage analytics. A free account includes up to 500 MB of storage and 2 GB of monthly traffic.

---

## Hotspots

Two interactive hotspot types are supported, each with a click/tap info popup:

- **Indicator hotspot** - a small configurable graphic that spins with a chosen point of interest. Add an `Empty → Plain Axes`, snap it to a vertex, parent it to your selected object, then click **Hotspot From Empty** in the WR360 panel.
- **Polygonal hotspot** - an active polygonal area over a region:
  - **From Vertex Group**: best for flat 2D areas (projection: *Gift wrap* or *2D polygon*).
  - **From Mesh**: best for 3D surfaces (projection: *Gift wrap* or *Consecutive quads*).

All hotspots can be styled and extended further in [WebRotate 360 SpotEditor](https://www.webrotate360.com/products/webrotate-360-product-viewer.aspx) (video/image/HTML popups, custom indicators, connecting lines, scripted actions, JavaScript callbacks, and more).

---

## Project Structure


| Path                                          | Purpose                                                                |
| --------------------------------------------- | ---------------------------------------------------------------------- |
| `__init__.py`                                 | Add-on entry point, `bl_info`, and module registration.                |
| `wr360_panel.py`                              | Main Scene Properties panel (animation, camera, render & view).        |
| `wr360_panel_hotspots.py`                     | 3D Viewport sidebar panel (WR360 tab) for hotspots.                    |
| `wr360_settings.py` / `wr360_settings_mac.py` | Property definitions / settings (platform-specific variant for macOS). |
| `wr360_settings_hotspot.py`                   | Hotspot-related properties.                                            |
| `wr360_state.py`                              | Scene/state synchronization.                                           |
| `wr360_ot_animate.py`                         | Animation setup operator.                                              |
| `wr360_ot_render_view.py`                     | Render & build-target operator.                                        |
| `wr360_ot_make_hotspot.py`                    | Hotspot creation/removal operator.                                     |
| `wr360_publisher.py`                          | Publishing logic for viewer / project / image targets.                 |
| `assets/`                                     | Project and viewer templates used when publishing.                     |
| `icons/`                                      | Hotspot indicator graphics.                                            |


---

## Support

- **Product page & user guide:** [https://www.webrotate360.com/products/cms-and-e-commerce-plugins/plugin-for-blender.aspx](https://www.webrotate360.com/products/cms-and-e-commerce-plugins/plugin-for-blender.aspx)
- **Email:** [support@webrotate360.com](mailto:support@webrotate360.com)
- **Forum:** [https://www.webrotate360.com/support/forum.aspx](https://www.webrotate360.com/support/forum.aspx)

---

## License

Released under the [MIT License](LICENSE). Copyright (c) WebRotate 360 LLC.