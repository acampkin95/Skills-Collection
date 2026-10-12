#!/usr/bin/env python3
"""
Frontend Stack Detection Script

Detects framework versions, Tailwind configuration, build tools, and common issues.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any


class StackDetector:
    """Detects frontend framework versions, build tools, and configuration."""

    def __init__(self, project_path: str) -> None:
        """Initialize stack detector for a project.

        Args:
            project_path: Path to the project directory.
        """
        self.project_path = Path(project_path).resolve()
        self.package_json: Optional[Dict[str, Any]] = None
        self.results: Dict[str, Any] = {
            "frameworks": {},
            "styling": {},
            "build_tools": {},
            "configuration": {},
            "issues": [],
            "recommendations": []
        }

    def load_package_json(self) -> bool:
        """Load and parse package.json from project.

        Returns:
            True if package.json was loaded successfully, False otherwise.
        """
        pkg_path = self.project_path / "package.json"
        if not pkg_path.exists():
            self.results["issues"].append("No package.json found")
            return False
        try:
            with open(pkg_path) as f:
                self.package_json = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.results["issues"].append(f"Invalid package.json: {e}")
            return False
    
    def get_dep_version(self, name: str) -> Optional[str]:
        """Get dependency version from package.json.

        Searches both dependencies and devDependencies, strips version
        specifiers (^, ~, >=, etc.) to get the actual version number.

        Args:
            name: Package name to look up.

        Returns:
            Version string without specifiers, or None if not found.
        """
        if not self.package_json:
            return None
        deps = self.package_json.get("dependencies", {})
        dev_deps = self.package_json.get("devDependencies", {})
        version = deps.get(name) or dev_deps.get(name)
        if version:
            return re.sub(r'^[\^~>=<]+', '', version)
        return None

    def detect_nextjs(self) -> None:
        """Detect Next.js framework and version.

        Checks for Next.js presence, extracts major version, detects app vs
        pages router, identifies async API requirements, and validates
        error.tsx files for 'use client' directive.

        Sets results with:
            - nextjs.version: Version string
            - nextjs.major: Major version number
            - nextjs.features: Feature support (app_router, async_params, turbopack_stable)
            - nextjs.router: Router type detection (app_router, pages_router)
            - issues: If error.tsx missing 'use client' directive

        Returns:
            None. Updates self.results in-place.
        """
        version = self.get_dep_version("next")
        if not version:
            return
            
        major = int(version.split('.')[0])
        self.results["frameworks"]["nextjs"] = {
            "version": version,
            "major": major,
            "features": {
                "app_router": major >= 13,
                "async_params": major >= 15,
                "turbopack_stable": major >= 15,
            }
        }
        
        # Check router type
        app_dir = self.project_path / "app"
        src_app = self.project_path / "src" / "app"
        pages_dir = self.project_path / "pages"
        src_pages = self.project_path / "src" / "pages"
        
        uses_app = app_dir.exists() or src_app.exists()
        uses_pages = pages_dir.exists() or src_pages.exists()
        
        self.results["frameworks"]["nextjs"]["router"] = {
            "app_router": uses_app,
            "pages_router": uses_pages,
        }
        
        if major >= 15:
            self.results["recommendations"].append(
                "Next.js 15: params, searchParams, cookies(), headers() must be awaited"
            )
        
        # Check error.tsx files
        error_files = list(self.project_path.rglob("**/error.tsx")) + \
                     list(self.project_path.rglob("**/global-error.tsx"))
        for f in error_files:
            if "node_modules" in str(f):
                continue
            try:
                content = f.read_text()
                if "'use client'" not in content and '"use client"' not in content:
                    self.results["issues"].append(
                        f"{f.relative_to(self.project_path)} missing 'use client'"
                    )
            except (OSError, IOError):
                pass
    
    def detect_vite(self) -> None:
        """Detect Vite build tool presence and configuration.

        Checks for Vite in dependencies, extracts version, and identifies
        which Vite config file exists (ts, js, or mjs).

        Sets results with:
            - vite.version: Version string
            - vite.config: Config file name (vite.config.ts/js/mjs)

        Returns:
            None. Updates self.results in-place.
        """
        version = self.get_dep_version("vite")
        if version:
            self.results["build_tools"]["vite"] = {"version": version}
            for cfg in ["vite.config.ts", "vite.config.js", "vite.config.mjs"]:
                if (self.project_path / cfg).exists():
                    self.results["build_tools"]["vite"]["config"] = cfg
                    break

    def detect_tailwind(self) -> None:
        """Detect Tailwind CSS version and configuration.

        Identifies Tailwind version (v3 vs v4), checks for configuration files
        (tailwind.config.js/ts for v3, or uses @theme directive for v4),
        detects PostCSS configuration format, identifies CSS syntax
        (@import vs @tailwind directives), and flags compatibility issues.

        Sets results with:
            - tailwind.version: Version string
            - tailwind.is_v4: Boolean flag for v4 detection
            - tailwind.config: Configuration file presence (tailwind_config, postcss_mjs, postcss_js)
            - tailwind.css_syntax: CSS syntax type (v4_import, v3_directives, unknown)
            - issues: Configuration mismatches (v4 with postcss.config.js, v4 with @tailwind)

        Returns:
            None. Updates self.results in-place.
        """
        version = self.get_dep_version("tailwindcss")
        if not version:
            return
            
        major = int(version.split('.')[0])
        is_v4 = major >= 4
        
        self.results["styling"]["tailwind"] = {
            "version": version,
            "is_v4": is_v4,
        }
        
        # Check configuration
        has_config_js = (self.project_path / "tailwind.config.js").exists()
        has_config_ts = (self.project_path / "tailwind.config.ts").exists()
        has_postcss_mjs = (self.project_path / "postcss.config.mjs").exists()
        has_postcss_js = (self.project_path / "postcss.config.js").exists()
        
        self.results["styling"]["tailwind"]["config"] = {
            "tailwind_config": has_config_js or has_config_ts,
            "postcss_mjs": has_postcss_mjs,
            "postcss_js": has_postcss_js,
        }
        
        # Detect CSS syntax
        css_syntax = self._detect_css_syntax()
        self.results["styling"]["tailwind"]["css_syntax"] = css_syntax
        
        # Check for issues
        if is_v4:
            if has_postcss_js and not has_postcss_mjs:
                self.results["issues"].append(
                    "Tailwind v4 requires postcss.config.mjs (not .js)"
                )
            if css_syntax == "v3_directives":
                self.results["issues"].append(
                    "Tailwind v4 uses @import 'tailwindcss' not @tailwind directives"
                )
        else:
            if not (has_config_js or has_config_ts):
                self.results["recommendations"].append(
                    "Tailwind v3 typically needs tailwind.config.js"
                )
    
    def _detect_css_syntax(self) -> str:
        """Detect Tailwind CSS syntax style in project CSS files.

        Scans CSS files across common locations (src/, app/, styles/, root)
        to identify whether the project uses Tailwind v4 (@import directive)
        or v3 (@tailwind directives).

        Returns:
            "v4_import" if @import 'tailwindcss' found,
            "v3_directives" if @tailwind directives found,
            "unknown" if neither pattern detected.
        """
        for pattern in ["src/**/*.css", "app/**/*.css", "styles/**/*.css", "*.css"]:
            for css_file in self.project_path.glob(pattern):
                if "node_modules" in str(css_file):
                    continue
                try:
                    content = css_file.read_text()
                    if '@import "tailwindcss"' in content or "@import 'tailwindcss'" in content:
                        return "v4_import"
                    if "@tailwind base" in content:
                        return "v3_directives"
                except (OSError, IOError):
                    pass
        return "unknown"

    def detect_turbopack(self) -> None:
        """Detect Turbopack build configuration and plugin compatibility.

        Checks if Turbopack is enabled via --turbo or --turbopack flags in
        the dev script, identifies incompatible plugins that may conflict
        with Turbopack bundling.

        Sets results with:
            - turbopack.enabled: Boolean flag
            - turbopack.incompatible: List of conflicting packages (if any)
            - issues: Warning message if incompatible plugins detected

        Returns:
            None. Updates self.results in-place.
        """
        if not self.package_json:
            return
        scripts = self.package_json.get("scripts", {})
        dev_script = scripts.get("dev", "")
        
        if "--turbo" in dev_script or "--turbopack" in dev_script:
            self.results["build_tools"]["turbopack"] = {"enabled": True}
            
            # Check for incompatible plugins
            incompatible = []
            for pkg in ["@next/bundle-analyzer", "@sentry/nextjs", "@payloadcms/next"]:
                if self.get_dep_version(pkg):
                    incompatible.append(pkg)
            
            if incompatible:
                self.results["build_tools"]["turbopack"]["incompatible"] = incompatible
                self.results["issues"].append(
                    f"Turbopack may not work with: {', '.join(incompatible)}"
                )
    
    def detect_react(self) -> None:
        """Detect React framework presence and version.

        Checks for React in dependencies (unless already detected as part
        of a framework like Next.js), extracts major version number.

        Sets results with:
            - react.version: Version string
            - react.major: Major version number

        Returns:
            None. Updates self.results in-place.
        """
        version = self.get_dep_version("react")
        if version and "react" not in self.results["frameworks"]:
            major = int(version.split('.')[0])
            self.results["frameworks"]["react"] = {
                "version": version,
                "major": major,
            }

    def detect_typescript(self) -> None:
        """Detect TypeScript configuration and presence.

        Checks for TypeScript in dependencies and identifies presence of
        tsconfig.json configuration file.

        Sets results with:
            - typescript.version: Version string
            - typescript.has_tsconfig: Boolean flag for tsconfig.json presence

        Returns:
            None. Updates self.results in-place.
        """
        version = self.get_dep_version("typescript")
        if version:
            self.results["configuration"]["typescript"] = {
                "version": version,
                "has_tsconfig": (self.project_path / "tsconfig.json").exists()
            }

    def check_common_issues(self) -> None:
        """Check for common frontend configuration issues.

        Scans layout files for CSS imports and component files for
        dynamic Tailwind classes that may cause build issues.

        Adds recommendations for:
            - Missing CSS imports in layout files
            - Potential dynamic Tailwind class names (string interpolation)

        Returns:
            None. Updates self.results in-place.
        """
        # Check for globals.css import in layout
        layouts = list(self.project_path.rglob("app/**/layout.tsx")) + \
                  list(self.project_path.rglob("app/**/layout.jsx"))

        for layout in layouts:
            if "node_modules" in str(layout):
                continue
            try:
                content = layout.read_text()
                if "globals" not in content.lower() and "global.css" not in content.lower():
                    self.results["recommendations"].append(
                        f"Check CSS import in {layout.relative_to(self.project_path)}"
                    )
            except (OSError, IOError):
                pass
        
        # Check for dynamic Tailwind classes
        for ext in ["tsx", "jsx"]:
            for f in self.project_path.rglob(f"**/*.{ext}"):
                if "node_modules" in str(f):
                    continue
                try:
                    content = f.read_text()
                    if re.search(r'className.*\$\{', content):
                        self.results["recommendations"].append(
                            f"Potential dynamic Tailwind classes in {f.relative_to(self.project_path)}"
                        )
                        break
                except (OSError, IOError):
                    pass

    def run(self) -> Dict[str, Any]:
        """Execute complete frontend stack detection.

        Loads package.json and runs all detection methods in sequence
        (Next.js, Vite, React, Tailwind, Turbopack, TypeScript), then
        checks for common configuration issues.

        Returns:
            Dictionary with detected frameworks, styling, build_tools,
            configuration, issues, and recommendations.
        """
        if not self.load_package_json():
            return self.results
        
        self.detect_nextjs()
        self.detect_vite()
        self.detect_react()
        self.detect_tailwind()
        self.detect_turbopack()
        self.detect_typescript()
        self.check_common_issues()
        
        return self.results


def print_report(results: Dict[str, Any]) -> None:
    """Print formatted detection report to stdout.

    Displays detected frameworks, styling tools, build tools, issues, and
    recommendations in a human-readable format with organized sections and
    emoji indicators.

    Args:
        results: Dictionary with keys 'frameworks', 'styling', 'build_tools',
                'issues', 'recommendations' containing detection results from
                StackDetector.run().

    Returns:
        None. Output is printed to stdout.
    """
    print("\n" + "=" * 50)
    print("  FRONTEND STACK DETECTION")
    print("=" * 50)
    
    if results["frameworks"]:
        print("\n📦 FRAMEWORKS")
        for name, info in results["frameworks"].items():
            v = info.get("version", "detected")
            print(f"   • {name}: {v}")
    
    if results["styling"]:
        print("\n🎨 STYLING")
        for name, info in results["styling"].items():
            v = info.get("version", "detected")
            v4 = " (v4)" if info.get("is_v4") else " (v3)"
            print(f"   • {name}: {v}{v4}")
            syntax = info.get("css_syntax", "unknown")
            print(f"     Syntax: {syntax}")
    
    if results["build_tools"]:
        print("\n🔧 BUILD TOOLS")
        for name, info in results["build_tools"].items():
            v = info.get("version") or ("enabled" if info.get("enabled") else "detected")
            print(f"   • {name}: {v}")
    
    if results["issues"]:
        print("\n⚠️  ISSUES")
        for issue in results["issues"]:
            print(f"   • {issue}")
    
    if results["recommendations"]:
        print("\n💡 RECOMMENDATIONS")
        for rec in results["recommendations"]:
            print(f"   • {rec}")
    
    print("\n" + "=" * 50)


def main() -> None:
    """Entry point for frontend stack detection CLI tool.

    Parses command-line arguments, runs stack detection on the specified project
    directory, and outputs results in either human-readable or JSON format.

    Command-line Arguments:
        project_path: Optional path to project directory (defaults to current directory).
        --json: Optional flag to output results as JSON instead of formatted report.

    Exit Codes:
        0: Detection completed successfully.
        1: Invalid project directory path provided.

    Returns:
        None. Output is printed to stdout or file.
    """
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.isdir(project_path):
        print(f"Error: '{project_path}' is not a valid directory")
        sys.exit(1)
    
    detector = StackDetector(project_path)
    results = detector.run()
    
    if "--json" in sys.argv:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)


if __name__ == "__main__":
    main()
