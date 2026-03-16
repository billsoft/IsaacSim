# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
NPC Walk Simple Demo (Lightweight, no IRA dependency)
=====================================================
Standalone script that uses omni.anim.people extension directly to:
  1. Load a warehouse scene with lighting
  2. Spawn NPC characters with Biped_Setup animation graph
  3. Drive them back and forth using omni.anim.people GoTo commands

This script writes commands to a USD stage attribute that the character
behavior script reads, similar to how IRA works but without the full
IRA framework overhead.

Usage (from Isaac Sim build root):
  python.bat standalone_examples/api/isaacsim.anim.people/npc_walk_simple.py

Optional arguments:
  --num_characters N    Number of NPC characters (default: 2)
  --walk_distance D     One-way walk distance in meters (default: 8.0)
  --headless            Run without GUI
  --assets_path PATH    Local path to Isaac assets root
"""

import argparse
import math
import os
import sys

# ---------------------------------------------------------------------------
# 1. Parse arguments
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="NPC Walk Simple Demo")
parser.add_argument("--num_characters", type=int, default=2, help="Number of NPC characters")
parser.add_argument("--walk_distance", type=float, default=8.0, help="One-way walk distance in meters")
parser.add_argument("--headless", action="store_true", help="Run without GUI")
parser.add_argument("--assets_path", type=str, default=None, help="Local Isaac assets root path")
args, _ = parser.parse_known_args()

# ---------------------------------------------------------------------------
# 2. Create SimulationApp
# ---------------------------------------------------------------------------
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": args.headless, "width": 1920, "height": 1080})

# ---------------------------------------------------------------------------
# 3. Imports (after SimulationApp)
# ---------------------------------------------------------------------------
import carb
import numpy as np
import omni.kit.app
import omni.timeline
import omni.usd
from isaacsim.core.utils.extensions import enable_extension
from isaacsim.core.utils.stage import is_stage_loading
from pxr import Gf, Sdf, Usd, UsdGeom, UsdLux, UsdSkel

# ---------------------------------------------------------------------------
# 4. Enable animation extensions
# ---------------------------------------------------------------------------
REQUIRED_EXTENSIONS = [
    "omni.anim.timeline",
    "omni.anim.graph.bundle",
    "omni.anim.graph.core",
    "omni.anim.retarget.core",
    "omni.anim.navigation.core",
    "omni.anim.navigation.bundle",
    "omni.anim.people",
    "omni.kit.scripting",
]

print("[NPC Simple] Enabling extensions...")
for ext in REQUIRED_EXTENSIONS:
    enable_extension(ext)
    simulation_app.update()

simulation_app.update()
simulation_app.update()
print("[NPC Simple] Extensions ready.")

# ---------------------------------------------------------------------------
# 5. Resolve asset paths
# ---------------------------------------------------------------------------
LOCAL_ASSETS = args.assets_path
if LOCAL_ASSETS is None:
    candidates = [
        "D:/code/IsaacLab/Assets/Isaac/5.1",
        os.path.expanduser("~/IsaacLab/Assets/Isaac/5.1"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            LOCAL_ASSETS = c
            break

if LOCAL_ASSETS is None:
    try:
        from isaacsim.storage.native import get_assets_root_path
        LOCAL_ASSETS = get_assets_root_path()
    except Exception:
        pass

if LOCAL_ASSETS is None:
    print("[NPC Simple] ERROR: Cannot find assets. Use --assets_path.", file=sys.stderr)
    simulation_app.close()
    sys.exit(1)

A = LOCAL_ASSETS.replace("\\", "/")
print(f"[NPC Simple] Assets root: {A}")

SCENE_USD = f"{A}/Isaac/Environments/Simple_Warehouse/warehouse.usd"
BIPED_USD = f"{A}/Isaac/People/Characters/Biped_Setup.usd"

CHARACTER_USDS = [
    f"{A}/Isaac/People/Characters/F_Business_02/F_Business_02.usd",
    f"{A}/Isaac/People/Characters/male_adult_construction_05_new/male_adult_construction_05_new.usd",
    f"{A}/Isaac/People/Characters/female_adult_police_01_new/female_adult_police_01_new.usd",
    f"{A}/Isaac/People/Characters/M_Medical_01/M_Medical_01.usd",
    f"{A}/Isaac/People/Characters/male_adult_construction_03/male_adult_construction_03.usd",
]

# Filter to actually existing models
CHARACTER_USDS = [c for c in CHARACTER_USDS if os.path.isfile(c)]
if not CHARACTER_USDS:
    print("[NPC Simple] ERROR: No character USD files found.", file=sys.stderr)
    simulation_app.close()
    sys.exit(1)

num_chars = min(args.num_characters, len(CHARACTER_USDS))
print(f"[NPC Simple] Will spawn {num_chars} character(s).")

# ---------------------------------------------------------------------------
# 6. Build scene: load environment + add characters + set commands
# ---------------------------------------------------------------------------
stage = omni.usd.get_context().get_stage()

# Create a fresh stage
omni.usd.get_context().new_stage()
simulation_app.update()
simulation_app.update()
stage = omni.usd.get_context().get_stage()

# Set stage meters
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)

# -- World Xform --
world_prim = stage.DefinePrim("/World", "Xform")

# -- Add environment --
print("[NPC Simple] Loading warehouse scene...")
env_prim = stage.DefinePrim("/World/Environment", "Xform")
env_prim.GetReferences().AddReference(SCENE_USD)
simulation_app.update()

# -- Add ground plane (in case warehouse doesn't have one) --
ground = stage.DefinePrim("/World/GroundPlane", "Xform")
ground_mesh = UsdGeom.Mesh.Define(stage, "/World/GroundPlane/Mesh")
ground_mesh.CreatePointsAttr([(-50, -50, 0), (50, -50, 0), (50, 50, 0), (-50, 50, 0)])
ground_mesh.CreateFaceVertexCountsAttr([4])
ground_mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
ground_mesh.CreateNormalsAttr([(0, 0, 1)] * 4)

# -- Add lights --
print("[NPC Simple] Setting up lighting...")
dome_light = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
dome_light.CreateIntensityAttr(1000)

distant_light = UsdLux.DistantLight.Define(stage, "/World/DistantLight")
distant_light.CreateIntensityAttr(3000)
distant_light.CreateAngleAttr(0.53)
xform = UsdGeom.Xformable(distant_light.GetPrim())
xform.AddRotateXYZOp().Set(Gf.Vec3f(-45, 30, 0))

# -- Add Biped_Setup (animation graph root for the character system) --
print("[NPC Simple] Loading Biped_Setup animation system...")
biped_prim = stage.DefinePrim("/World/Biped_Setup", "Xform")
biped_prim.GetReferences().AddReference(BIPED_USD)
simulation_app.update()

# -- Character root path (where omni.anim.people expects characters) --
char_root_path = "/World/Characters"
char_root = stage.DefinePrim(char_root_path, "Xform")

# Configure omni.anim.people settings
settings = carb.settings.get_settings()
settings.set("/exts/omni.anim.people/character_prim_path", char_root_path)
settings.set("/exts/omni.anim.people/navigation_settings/navmesh_enabled", True)
settings.set("/persistent/exts/omni.anim.navigation.core/navMesh/viewNavMesh", False)

# -- Spawn characters --
walk_dist = args.walk_distance
spacing = 3.0  # Y-axis spacing between characters

command_lines = []

for i in range(num_chars):
    char_name = f"Character_{i:02d}"
    char_path = f"{char_root_path}/{char_name}"
    model_usd = CHARACTER_USDS[i % len(CHARACTER_USDS)]

    # Start position
    start_x = 2.0
    start_y = 2.0 + i * spacing

    print(f"[NPC Simple] Spawning {char_name} at ({start_x}, {start_y}, 0) using {os.path.basename(model_usd)}")

    # Create character prim with reference to character USD
    char_prim = stage.DefinePrim(char_path, "Xform")
    char_prim.GetReferences().AddReference(model_usd)

    # Set initial position
    xformable = UsdGeom.Xformable(char_prim)
    xformable.AddTranslateOp().Set(Gf.Vec3d(start_x, start_y, 0))

    # Generate GoTo commands: walk back and forth along X-axis, face forward
    end_x = start_x + walk_dist
    for loop in range(50):
        # Walk to end point, facing +X direction (rotation=0)
        command_lines.append(f"{char_name} GoTo {end_x:.1f} {start_y:.1f} 0.0 0")
        # Walk back to start, facing -X direction (rotation=180)
        command_lines.append(f"{char_name} GoTo {start_x:.1f} {start_y:.1f} 0.0 180")

simulation_app.update()

# -- Write command file --
import tempfile

cmd_content = "\n".join(command_lines)
cmd_file_path = os.path.join(tempfile.gettempdir(), "npc_simple_commands.txt")
with open(cmd_file_path, "w") as f:
    f.write(cmd_content)

print(f"[NPC Simple] Command file: {cmd_file_path}")

# Set command file path in settings for omni.anim.people to pick up
settings.set("/exts/omni.anim.people/command_file", cmd_file_path)

# Wait for stage to finish loading
print("[NPC Simple] Waiting for stage to finish loading...")
while is_stage_loading():
    simulation_app.update()

simulation_app.update()
simulation_app.update()

# ---------------------------------------------------------------------------
# 7. Set up camera view
# ---------------------------------------------------------------------------
# Position camera to see the walking area
viewport = omni.kit.viewport.utility.get_active_viewport() if hasattr(omni.kit, "viewport") else None
try:
    from isaacsim.core.utils.viewports import set_camera_view

    center_y = (num_chars - 1) * spacing / 2.0 + 2.0
    center_x = 2.0 + walk_dist / 2.0
    set_camera_view(
        eye=[center_x, center_y - 15, 8],
        target=[center_x, center_y, 0],
        camera_prim_path="/OmniverseKit_Persp",
    )
except Exception as e:
    print(f"[NPC Simple] Could not set camera view: {e}")

# ---------------------------------------------------------------------------
# 8. Play timeline and run simulation
# ---------------------------------------------------------------------------
print("[NPC Simple] Starting simulation...")
print(f"[NPC Simple] {num_chars} NPC(s) walking back and forth ({walk_dist}m)")
print("[NPC Simple] Close the window or press Ctrl+C to stop.")

timeline = omni.timeline.get_timeline_interface()
timeline.play()

simulation_app.update()
simulation_app.update()

frame = 0
fps = 30.0
max_frames = int(args.walk_distance * 100 * 50)  # run long enough

try:
    while simulation_app.is_running() and frame < max_frames:
        simulation_app.update()
        frame += 1
        if frame % 300 == 0:
            elapsed = frame / fps
            print(f"[NPC Simple] Running... {elapsed:.0f}s elapsed, frame {frame}")
except KeyboardInterrupt:
    print("\n[NPC Simple] Stopped by user.")

print("[NPC Simple] Done. Closing...")
simulation_app.close()
