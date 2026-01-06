import os
import re

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Creates a new app inside the 'apps/' folder and automatically adds it to INSTALLED_APPS."

    def add_arguments(self, parser):
        parser.add_argument(
            "name", type=str, help='App name (without the "apps" prefix)'
        )

    def handle(self, *args, **options):
        app_name = options["name"].strip()
        base_dir = os.getcwd()
        apps_dir = os.path.join(base_dir, "apps")
        app_path = os.path.join(apps_dir, app_name)

        # 👇 Create apps folder if it doesn't exist
        os.makedirs(apps_dir, exist_ok=True)

        # Check if the app already exists
        if os.path.exists(app_path):
            raise CommandError(f"The folder '{app_path}' already exists.")

        # 👇 Create the app within apps/
        os.chdir(apps_dir)
        call_command("startapp", app_name)
        os.chdir(base_dir)

        self.stdout.write(
            self.style.SUCCESS(f"✅ App '{app_name}' created on {app_path}")
        )

        # 👇 Automatically add to INSTALLED_APPS
        settings_path = os.path.join(base_dir, "config", "settings.py")
        app_full_name = f"apps.{app_name}"

        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Search the INSTALLED_APPS list
            pattern = r"INSTALLED_APPS\s*=\s*\[(.*?)\]"
            match = re.search(pattern, content, re.S)
            if not match:
                self.stdout.write(
                    self.style.WARNING("⚠️ INSTALLED_APPS not found in settings.py")
                )
                return

            # Check if it's already included
            if app_full_name in match.group(1):
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️ '{app_full_name}' was already in INSTALLED_APPS"
                    )
                )
                return

            # Insert before list close
            new_installed = match.group(1).rstrip() + f"\n    '{app_full_name}',"
            new_content = re.sub(
                pattern, f"INSTALLED_APPS = [{new_installed}\n]", content, flags=re.S
            )

            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            self.stdout.write(
                self.style.SUCCESS(
                    f"🧩 '{app_full_name}' added to INSTALLED_APPS in settings.py"
                )
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR("❌ The settings.py file was not found.")
            )
