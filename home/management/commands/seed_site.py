"""Create a demo page tree and the `main` / `footer` menus.

uv run python manage.py seed_site          # no-op if a HomePage already exists
uv run python manage.py seed_site --force  # delete demo content and recreate it
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Page, Site

from home.models import ContactPage, FormField, HomePage, StandardPage
from navigation.models import Menu, MenuItem, SubMenuItem


def heading(text, size="h2"):
    return {"type": "heading", "value": {"text": text, "size": size}}


def paragraph(html):
    return {"type": "paragraph", "value": html}


def quote(text, attribution=""):
    return {"type": "quote", "value": {"quote": text, "attribution": attribution}}


def cta(text, page=None, url=""):
    return {"type": "cta", "value": {"text": text, "page": page.pk if page else None, "url": url}}


class Command(BaseCommand):
    help = "Seed a demo site: HomePage, About, Services (+2 children), Contact, main/footer menus."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete existing HomePage tree and menus before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, force=False, **options):
        if HomePage.objects.exists():
            if not force:
                self.stdout.write(
                    self.style.WARNING("Site already seeded; use --force to recreate.")
                )
                return
            self._delete_existing()

        root = Page.get_first_root_node()
        self._delete_default_welcome_page(root)

        home = self._create_pages(root)
        self._configure_site(home)
        self._create_menus()

        self.stdout.write(self.style.SUCCESS("Demo site seeded."))

    # ------------------------------------------------------------------ helpers

    def _delete_existing(self):
        for home in HomePage.objects.all():
            # Point sites away first so the protected FK doesn't block deletion.
            Site.objects.filter(root_page=home).update(root_page=Page.get_first_root_node())
            home.delete()
        Menu.objects.all().delete()
        self.stdout.write("Deleted existing demo content.")

    def _delete_default_welcome_page(self, root):
        """Remove the plain `Page` Wagtail creates in its initial migration."""
        for page in root.get_children().filter(content_type__model="page"):
            Site.objects.filter(root_page=page).update(root_page=root)
            page.delete()

    def _add(self, parent, page):
        parent.add_child(instance=page)
        page.save_revision().publish()
        return page

    def _create_pages(self, root):
        home = self._add(
            root,
            HomePage(
                title="Home",
                slug="home",
                seo_title="Wagtail Home — a demo site",
                search_description="A demo Wagtail 7.4 site with editable menus.",
                show_in_menus=True,
                hero_title="Build better websites with Wagtail",
                hero_subtitle="A clean starting point: editable pages, menus and a contact form.",
            ),
        )

        about = self._add(
            home,
            StandardPage(
                title="About",
                slug="about",
                show_in_menus=True,
                search_description="Who we are and what we do.",
                intro="<p>We are a small team that builds content-driven websites.</p>",
                body=[
                    heading("Our story"),
                    paragraph("<p>Founded to make publishing simple, fast and accessible.</p>"),
                    quote("Simplicity is the ultimate sophistication.", "Leonardo da Vinci"),
                ],
            ),
        )

        services = self._add(
            home,
            StandardPage(
                title="Services",
                slug="services",
                show_in_menus=True,
                search_description="Services we offer.",
                intro="<p>From design to long-term support.</p>",
                body=[paragraph("<p>Pick a service below to learn more.</p>")],
            ),
        )
        for title, slug, text in [
            ("Web Design", "web-design", "Responsive, accessible design systems."),
            ("Consulting", "consulting", "Architecture reviews and Wagtail training."),
        ]:
            self._add(
                services,
                StandardPage(
                    title=title,
                    slug=slug,
                    show_in_menus=True,
                    search_description=text,
                    intro=f"<p>{text}</p>",
                ),
            )

        contact = ContactPage(
            title="Contact",
            slug="contact",
            show_in_menus=True,
            search_description="Send us a message.",
            intro="<p>We usually reply within one business day.</p>",
            thank_you_text="<p>Thanks for your message! We'll be in touch soon.</p>",
            to_address=settings.DEFAULT_FROM_EMAIL,
            from_address=settings.DEFAULT_FROM_EMAIL,
            subject="New contact form submission",
        )
        contact.form_fields = [
            FormField(sort_order=0, label="Name", field_type="singleline", required=True),
            FormField(sort_order=1, label="Email", field_type="email", required=True),
            FormField(sort_order=2, label="Message", field_type="multiline", required=True),
        ]
        self._add(home, contact)

        # Home page CTA + body reference pages that now exist.
        home.hero_cta_text = "Get in touch"
        home.hero_cta_page = contact
        home.body = [
            heading("Welcome"),
            paragraph(
                "<p>This site was generated by <code>seed_site</code>. Edit it in the admin.</p>"
            ),
            cta("Learn more about us", page=about),
        ]
        home.save_revision().publish()
        return home

    def _configure_site(self, home):
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            site = Site(is_default_site=True, hostname="localhost", port=80)
        site.root_page = home
        site.site_name = settings.WAGTAIL_SITE_NAME
        site.save()

    def _create_menus(self):
        pages = {p.slug: p for p in Page.objects.filter(depth__gte=2).specific()}

        main = Menu(title="Main navigation", slug="main")
        services = MenuItem(sort_order=2, link_page=pages["services"])
        services.sub_items = [
            SubMenuItem(sort_order=0, link_page=pages["web-design"]),
            SubMenuItem(sort_order=1, link_page=pages["consulting"]),
        ]
        main.menu_items = [
            MenuItem(sort_order=0, link_page=pages["home"]),
            MenuItem(sort_order=1, link_page=pages["about"]),
            services,
            MenuItem(sort_order=3, link_page=pages["contact"]),
        ]
        main.save()

        footer = Menu(title="Footer", slug="footer")
        footer.menu_items = [
            MenuItem(sort_order=0, link_page=pages["about"], link_title="About us"),
            MenuItem(sort_order=1, link_page=pages["contact"]),
            MenuItem(
                sort_order=2,
                link_title="Built with Wagtail",
                link_url="https://wagtail.org/",
                open_in_new_tab=True,
            ),
        ]
        footer.save()
