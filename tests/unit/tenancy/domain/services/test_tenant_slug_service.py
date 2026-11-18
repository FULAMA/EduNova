from src.tenancy.domain.services.tenant_slug_service import TenantSlugService


def test_normalize_slug_basic():
    assert TenantSlugService.normalize_slug("Collège Boboto") == "college-boboto"
    assert TenantSlugService.normalize_slug("Lycée Français de Kinshasa") == "lycee-francais-de-kinshasa"


def test_normalize_slug_with_accents_and_punctuation():
    raw = "  Établissement Sainte-Thérèse d'Avila & Co. (Kinshasa)!!  "
    expected = "etablissement-sainte-therese-d-avila-co-kinshasa"
    assert TenantSlugService.normalize_slug(raw) == expected


def test_normalize_slug_empty_fallback():
    assert TenantSlugService.normalize_slug("") == "etablissement"
    assert TenantSlugService.normalize_slug("   ") == "etablissement"
    assert TenantSlugService.normalize_slug("!@#$%^&*()") == "etablissement"


def test_generate_unique_slug_no_collision():
    existing_slugs = {"lycee-bosangani", "cs-cardinal-malula"}

    def is_taken(slug: str) -> bool:
        return slug in existing_slugs

    slug = TenantSlugService.generate_unique_slug("Collège Boboto", is_taken)
    assert slug == "college-boboto"


def test_generate_unique_slug_with_single_collision():
    existing_slugs = {"college-boboto"}

    def is_taken(slug: str) -> bool:
        return slug in existing_slugs

    slug = TenantSlugService.generate_unique_slug("Collège Boboto", is_taken)
    assert slug == "college-boboto-2"


def test_generate_unique_slug_with_multiple_collisions():
    existing_slugs = {
        "college-boboto",
        "college-boboto-2",
        "college-boboto-3",
        "college-boboto-4",
    }

    def is_taken(slug: str) -> bool:
        return slug in existing_slugs

    slug = TenantSlugService.generate_unique_slug("Collège Boboto", is_taken)
    assert slug == "college-boboto-5"
