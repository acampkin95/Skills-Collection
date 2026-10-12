#!/usr/bin/env python3
"""
Clerk Authentication Setup Script - Automated Clerk configuration for Next.js.

Usage:
    python3 setup-clerk.py init <project-path> [--template <basic|organization|mfa>]
    python3 setup-clerk.py env <project-path>
    python3 setup-clerk.py middleware <project-path>
    python3 setup-clerk.py verify <project-path>
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Any

def create_env_file(project_path: Path, template: str = "basic") -> None:
    """Create .env.local with Clerk configuration."""
    env_content = f"""# Clerk Authentication - Generated {datetime.now().strftime('%Y-%m-%d')}

# Get these from https://dashboard.clerk.com/
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here

# For multi-tenant (organizations)
NEXT_PUBLIC_CLERK_ORGANIZATION_TEMPLATE={template}

# Webhook signing secret (for production)
CLERK_WEBHOOK_SECRET=whsec_your_secret_here

# Optional: Custom login/signup pages
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
"""

    env_file = project_path / ".env.local"
    with open(env_file, 'w') as f:
        f.write(env_content)
    print(f"Created: {env_file}")

def create_middleware(project_path: Path) -> None:
    """Create Clerk middleware for route protection."""
    middleware_content = '''import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isPublicRoute = createRouteMatcher([
  "/",
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/webhook(.*)",
]);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    "/((?!_next|[^?]*\\\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
'''

    middleware_file = project_path / "middleware.ts"
    with open(middleware_file, 'w') as f:
        f.write(middleware_content)
    print(f"Created: {middleware_file}")

def create_layout_wrapper(project_path: Path) -> None:
    """Create ClerkProvider wrapper component."""
    wrapper_content = '''"use client";

import { ClerkProvider } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
import { ReactNode } from "react";

interface ClerkWrapperProps {
  children: ReactNode;
}

export function ClerkWrapper({ children }: ClerkWrapperProps) {
  return (
    <ClerkProvider
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: "#3b82f6",
          colorBackground: "#1e293b",
          colorText: "#f8fafc",
        },
      }}
    >
      {children}
    </ClerkProvider>
  );
}
'''

    components_dir = project_path / "src" / "components"
    components_dir.mkdir(parents=True, exist_ok=True)

    wrapper_file = components_dir / "clerk-wrapper.tsx"
    with open(wrapper_file, 'w') as f:
        f.write(wrapper_content)
    print(f"Created: {wrapper_file}")

def create_sign_in_page(project_path: Path) -> None:
    """Create custom sign-in page."""
    signin_content = '''import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <SignIn
        appearance={{
          elements: {
            formButtonPrimary: "bg-blue-600 hover:bg-blue-700",
            card: "bg-gray-900 border border-gray-800",
          },
        }}
      />
    </div>
  );
}
'''

    app_dir = project_path / "src" / "app" / "sign-in" / "[[...sign-in]]"
    app_dir.mkdir(parents=True, exist_ok=True)

    page_file = app_dir / "page.tsx"
    with open(page_file, 'w') as f:
        f.write(signin_content)
    print(f"Created: {page_file}")

def create_sign_up_page(project_path: Path) -> None:
    """Create custom sign-up page."""
    signup_content = '''import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <SignUp
        appearance={{
          elements: {
            formButtonPrimary: "bg-blue-600 hover:bg-blue-700",
            card: "bg-gray-900 border border-gray-800",
          },
        }}
      />
    </div>
  );
}
'''

    app_dir = project_path / "src" / "app" / "sign-up" / "[[...sign-up]]"
    app_dir.mkdir(parents=True, exist_ok=True)

    page_file = app_dir / "page.tsx"
    with open(page_file, 'w') as f:
        f.write(signup_content)
    print(f"Created: {page_file}")

def create_user_button(project_path: Path) -> None:
    """Create user menu component."""
    user_button_content = '''"use client";

import { UserButton, useUser } from "@clerk/nextjs";
import { usePathname } from "next/navigation";
import Link from "next/link";

export function UserMenu() {
  const { user, isLoaded } = useUser();
  const pathname = usePathname();

  if (!isLoaded || !user) {
    return null;
  }

  return (
    <div className="flex items-center gap-4">
      <Link
        href="/dashboard"
        className={`text-sm font-medium ${
          pathname === "/dashboard" ? "text-blue-400" : "text-gray-400"
        }`}
      >
        Dashboard
      </Link>
      <UserButton
        appearance={{
          elements: {
            avatarBox: "w-8 h-8",
          },
        }}
      />
    </div>
  );
}
'''

    components_dir = project_path / "src" / "components"
    components_dir.mkdir(parents=True, exist_ok=True)

    user_button_file = components_dir / "user-menu.tsx"
    with open(user_button_file, 'w') as f:
        f.write(user_button_content)
    print(f"Created: {user_button_file}")

def init_project(project_path: Path, template: str) -> None:
    """Initialize Clerk for a Next.js project."""
    print(f"Initializing Clerk for: {project_path}")
    print(f"Template: {template}")
    print()

    create_env_file(project_path, template)
    create_middleware(project_path)
    create_layout_wrapper(project_path)
    create_sign_in_page(project_path)
    create_sign_up_page(project_path)
    create_user_button(project_path)

    print()
    print("Clerk setup complete!")
    print("Next steps:")
    print("1. Add your Clerk keys to .env.local")
    print("2. Run: npm install @clerk/nextjs")
    print("3. Add ClerkWrapper to your layout.tsx")
    print("4. Test: npm run dev")

def verify_setup(project_path: Path) -> bool:
    """Verify Clerk setup is correct."""
    print(f"Verifying Clerk setup: {project_path}")
    print()

    checks = []

    # Check environment file
    env_file = project_path / ".env.local"
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
        has_publishable = "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" in content
        has_secret = "CLERK_SECRET_KEY" in content
        checks.append(("Environment file", True, f"Keys: {'✓' if has_publishable and has_secret else 'Missing'}"))
    else:
        checks.append(("Environment file", False, "Missing"))

    # Check middleware
    middleware_file = project_path / "middleware.ts"
    if middleware_file.exists():
        with open(middleware_file) as f:
            content = f.read()
        has_clerk = "clerkMiddleware" in content
        checks.append(("Middleware", True, f"Clerk: {'✓' if has_clerk else 'Missing'}"))
    else:
        checks.append(("Middleware", False, "Missing"))

    # Check package.json
    pkg_file = project_path / "package.json"
    if pkg_file.exists():
        with open(pkg_file) as f:
            pkg = json.load(f)
        deps = list(pkg.get("dependencies", {}).keys())
        has_clerk = any("@clerk/" in d for d in deps)
        checks.append(("Package.json", True, f"Clerk deps: {'✓' if has_clerk else 'Missing'}"))
    else:
        checks.append(("Package.json", False, "Missing"))

    # Print results
    print("Checklist:")
    for name, passed, details in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}: {details}")

    all_passed = all(c[1] for c in checks)
    print()
    if all_passed:
        print("All checks passed!")
    else:
        print("Some checks failed. Review the output above.")

    return all_passed

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    project_path = Path.cwd()

    if len(sys.argv) > 2:
        project_path = Path(sys.argv[2])

    if command == "init":
        template = "basic"
        if len(sys.argv) > 3 and sys.argv[3] == "--template":
            template = sys.argv[4] if len(sys.argv) > 4 else "basic"
        init_project(project_path, template)

    elif command == "env":
        create_env_file(project_path)

    elif command == "middleware":
        create_middleware(project_path)

    elif command == "verify":
        verify_setup(project_path)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
