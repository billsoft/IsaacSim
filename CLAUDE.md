# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

NVIDIA Isaac Sim is a robotics simulation platform built on NVIDIA Omniverse. It uses a modular extension-based architecture with 97+ extensions for robot simulation, synthetic data generation, ROS integration, and AI training workflows.

## Windows-Specific Information

**System:** Windows 11
**Python Environment:**
- Conda environment: `isaac` (Python 3.12) - for general development
- Isaac Sim local Python: `D:\code\IsaacSim\_repo\python` (Python 3.11) - used by Isaac Sim internally

**Visual Studio Installations:**
- VS2022 Professional: `C:\Program Files\Microsoft Visual Studio\2022\Professional`
- VS2026 Professional: `C:\Program Files\Microsoft Visual Studio\18\Professional`

**Available MSVC Toolsets:**
- 14.32.31326
- 14.33.31629
- 14.35.32215 (has known issues with `zmmintrin.h` - avoid)
- 14.44.35207 (recommended)

## Build Commands

### Important Build Notes
**ALWAYS** activate the correct Python environment before running Python commands:
```powershell
# For general Python commands (use with caution)
conda activate isaac

# For Isaac Sim builds - use Isaac's own Python environment
# The build system automatically uses: D:\code\IsaacSim\_repo\python
```

### Building
```powershell
# Full clean build (recommended after fixing compiler issues)
build.bat -x

# Build with specific configuration
build.bat -r                        # Release only
build.bat -d                        # Debug only

# Build options
build.bat --help                    # Show all options
build.bat -j 8                      # Limit to 8 parallel jobs
build.bat --fetch-only              # Only download dependencies
build.bat --generate                # Generate project files only
build.bat --build-only              # Build without regenerating
build.bat --skip-compiler-version-check  # Skip compiler version validation

# Use newer MSVC version (if issues with default)
# Edit repo.toml [repo_build.msbuild] section to specify msvc_version
```

### Running Isaac Sim
```powershell
# Set environment variables (recommended)
set ISAACSIM_PATH="%cd%\_build\windows-x86_64\release"
set ISAACSIM_PYTHON_EXE="%ISAACSIM_PATH:"=%\python.bat"

# Run Isaac Sim UI
%ISAACSIM_PATH%\isaac-sim.bat

# Run standalone example
%ISAACSIM_PYTHON_EXE% %ISAACSIM_PATH%\standalone_examples\api\isaacsim.core.api\add_cubes.py

# First-time user data reset
%ISAACSIM_PATH%\isaac-sim.bat --reset-user
```

### Testing
```powershell
# Run test suites via repo tool
.\repo.bat test -s startup_tests -c release       # Smoke tests
.\repo.bat test -s pythontests -c release         # Integration tests
.\repo.bat test -s nativepythontests -c release   # Standalone examples

# Test output location: _testoutput\
```

## Known Build Issues on Windows

### MSVC Compiler Error: zmmintrin.h

**Error:**
```
D:\code\IsaacSim\_build\host-deps\msvc\VC\Tools\MSVC\14.35.32215\include\zmmintrin.h(5429,24): error C2220
warning C4392: "__m128h _mm_cvtss_sh(__m128h,__m128,const int)": incorrect number of parameters
```

**Root Cause:**
MSVC 14.35 has a bug in `zmmintrin.h` where F16C (half-precision float) scalar intrinsics `_mm_cvtss_sh` and `_mm_cvtsh_ss` are incorrectly declared. MSVC does not properly support these scalar intrinsics.

**Solution 1 - Use Newer MSVC (Recommended):**
The newer MSVC toolset (14.44.35207) available in your VS2022 installation may have this fixed.

Edit `repo.toml` and add/modify in the `[repo_build.msbuild]` section:
```toml
[repo_build.msbuild]
vs_version = "vs2022"
msvc_version = "v143"  # This uses the latest v143 toolset
# Or specify exact version:
# msvc_path = "C:\\Program Files\\Microsoft Visual Studio\\2022\\Professional\\VC\\Tools\\MSVC\\14.44.35207"
```

Then rebuild:
```powershell
build.bat -x  # Clean rebuild with new compiler
```

**Solution 2 - Disable Problematic Extensions:**
If the above doesn't work, you may need to temporarily skip building the C++ extension that fails:
- The failing extension is: `omni.kit.loop-isaac.plugin`
- Location: `source\extensions\omni.kit.loop-isaac\`

**Solution 3 - Compiler Workaround (Advanced):**
The F16C scalar intrinsics can be replaced with packed versions. However, since the error occurs in MSVC's own header file, this would require either:
1. Patching the MSVC header (not recommended)
2. Defining preprocessor macros to avoid the problematic intrinsics
3. Using `/arch:AVX` or `/arch:AVX2` instead of allowing AVX-512

### Extension Precache Failures
If you see:
```
error running: kit.exe --ext-precache-mode
SystemExit: 55
```

This is often caused by missing C++ extension modules. The build must complete successfully first before precaching can work.

## Architecture Overview

### Extension System
Isaac Sim uses Omniverse Kit's extension architecture. All functionality is organized into extensions located in `source\extensions\` (current) and `source\deprecated\` (legacy).

**Key Extension Categories:**
- **Core**: `isaacsim.core.*` - Foundation APIs
- **Assets**: `isaacsim.asset.*` - Import/export (URDF, MJCF, USD)
- **Sensors**: `isaacsim.sensors.*` - Camera, physics sensors, RTX sensors
- **Robots**: `isaacsim.robot.*` - Manipulators, wheeled robots, grippers
- **Robot Motion**: `isaacsim.robot_motion.*` - Motion generation, kinematics
- **Replicator**: `isaacsim.replicator.*` - Synthetic data generation
- **ROS**: `isaacsim.ros2.*` - ROS2 bridge integration
- **GUI**: `isaacsim.gui.*` - User interface components

### Extension Structure
```
extension_name\
├── config\
│   └── extension.toml          # Metadata, dependencies, settings
├── plugins\                    # C++ plugin implementations
│   └── CMakeLists.txt or premake5.lua
├── python\
│   ├── impl\                   # Python implementation
│   ├── tests\                  # Unit tests
│   └── __init__.py
├── bindings\                   # C++ Python bindings (pybind11)
├── include\                    # C++ headers
├── nodes\                      # Omnigraph node definitions
├── premake5.lua               # Build configuration
└── docs\                       # Documentation
```

### Application (.kit) Files
Located in `source\apps\`, these define different Isaac Sim configurations:
- `isaacsim.exp.full.kit` - Full Isaac Sim with UI
- `isaacsim.exp.base.kit` - Headless runtime
- `isaacsim.exp.base.python.kit` - Python-only variant
- `isaacsim.exp.full.fabric.kit` - Fabric-accelerated version

### Build System
Uses Premake5-based build system managed by `repo` tool:
- `premake5.lua` - Main build configuration
- `premake5-isaacsim.lua` - Isaac Sim-specific settings
- `premake5-tests.lua` - Test definitions
- `repo.toml` - Repository phases (fetch, build, test, package)

Build output: `_build\<platform>\<config>\`

### Python vs C++
- **Python**: High-level APIs, user scripts, tests (`python\impl\`, `python\tests\`)
- **C++**: Performance-critical code, physics, rendering (`plugins\`, `include\`)
- **Bindings**: pybind11 exposes C++ to Python (`bindings\`)
- **Entry Point**: `source\python_packages\isaacsim\__init__.py` bootstraps Kit kernel
- **Isaac Sim Python**: `D:\code\IsaacSim\_repo\python` - Separate from system/conda Python

## Development Guidelines

### Compiler Requirements
- **VS 2022** with MSVC v143
- **Windows SDK**: 10.0.22621.0 or newer
- **Python**: 3.11 (managed by build system in `_repo\python`)

**Note:** Always prefer MSVC 14.44+ over 14.35 to avoid known intrinsics bugs.

### Working with Extensions

#### Modifying Existing Extensions
1. Navigate to `source\extensions\<extension_name>\`
2. Edit Python code in `python\impl\` or C++ in `plugins\`
3. Update tests in `python\tests\`
4. Rebuild: `build.bat --build-only` (incremental) or `build.bat -x` (clean)
5. Test changes with appropriate test suite

#### Creating New Extensions
1. Copy an existing extension as template
2. Update `config\extension.toml` with metadata and dependencies
3. Add build configuration to `premake5.lua`
4. Implement functionality in `python\impl\` or `plugins\`
5. Add tests in `python\tests\`

### Running Standalone Examples
Located in `source\standalone_examples\`:
```powershell
cd _build\windows-x86_64\release
.\python.bat ..\..\..\source\standalone_examples\api\isaacsim.core.api\hello_world.py
```

### Path Length (Windows)
Windows has 260-character path limit. If build fails with missing files, move repository to shorter path (e.g., `C:\isaac\`).

### First-Time Startup
Initial launch takes several minutes for extension and shader caching. Subsequent startups: 10-30 seconds.

## Important Build Phases

1. **Fetch**: Downloads Kit SDK, PhysX, dependencies via Packman
2. **Generate**: Creates Visual Studio solutions
3. **Build**: Compiles C++ extensions and Python bindings
4. **Post-Build**: Precaches extensions, generates VSCode settings, processes USD schemas

## Documentation Resources

- Main Docs: https://docs.isaacsim.omniverse.nvidia.com/latest/index.html
- Quick Tutorials: https://docs.isaacsim.omniverse.nvidia.com/latest/introduction/quickstart_index.html
- FAQ: https://docs.isaacsim.omniverse.nvidia.com/latest/overview/faq_index.html
- Troubleshooting: https://docs.isaacsim.omniverse.nvidia.com/latest/overview/troubleshooting.html
- Per-extension docs in `source\extensions\<name>\docs\`

## Support Channels

- GitHub Discussions: Questions and feature requests
- GitHub Issues: Bug reports and tracked work items only

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| MSVC zmmintrin.h error | Use MSVC 14.44+ or add `msvc_version` in repo.toml |
| Path too long errors | Move repo to `C:\isaac\` or shorter path |
| Extension precache fails | Ensure C++ build completed successfully first |
| Missing Python modules | Use Isaac's Python: `_repo\python`, not conda |
| Wrong compiler version | Run `build.bat --skip-compiler-version-check` or update VS |
