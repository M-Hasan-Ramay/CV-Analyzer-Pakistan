
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_DIR = PROJECT_ROOT / "09_CONFIG" / "taxonomy"


class TaxonomyLoader:
    """Load and index the editable CV-AI taxonomy JSON files."""

    FILES = [
        "taxonomy_metadata.json",
        "domains.json",
        "subdomains.json",
        "functions.json",
        "activities.json",
        "technologies.json",
        "architectures.json",
        "aliases.json"
    ]

    def __init__(self, taxonomy_dir=None):
        self.taxonomy_dir = Path(taxonomy_dir or TAXONOMY_DIR)
        self.data = {}

        for filename in self.FILES:
            self._load_file(filename)

        self.domain_index = {}
        self.subdomain_index = {}
        self.function_index = {}
        self.activity_index = {}
        self.technology_index = {}
        self.architecture_index = {}
        self.entity_index = {}
        self.alias_index = {}

        self._build_indexes()

    def _load_file(self, filename):
        path = self.taxonomy_dir / filename

        if not path.is_file():
            raise FileNotFoundError(
                f"Required taxonomy file not found: {path}"
            )

        try:
            with path.open("r", encoding="utf-8") as file:
                self.data[filename] = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in {path}: "
                f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
            ) from exc

    @staticmethod
    def _normalize(value):
        if value is None:
            return ""
        return " ".join(str(value).lower().strip().split())

    def _register_entities(self, index, items):
        for item in items:
            entity_id = item.get("id")

            if not entity_id:
                continue

            if entity_id in self.entity_index:
                raise ValueError(
                    f"Duplicate taxonomy entity ID: {entity_id}"
                )

            index[entity_id] = item
            self.entity_index[entity_id] = item

            for alias in item.get("aliases", []):
                self._add_alias(alias, entity_id)

            self._add_alias(item.get("name", ""), entity_id)

    def _add_alias(self, alias, entity_id):
        normalized = self._normalize(alias)

        if not normalized:
            return

        candidates = self.alias_index.setdefault(normalized, [])

        if entity_id not in candidates:
            candidates.append(entity_id)

    def _build_indexes(self):
        self._register_entities(
            self.domain_index,
            self.data["domains.json"].get("domains", [])
        )

        self._register_entities(
            self.subdomain_index,
            self.data["subdomains.json"].get("subdomains", [])
        )

        self._register_entities(
            self.function_index,
            self.data["functions.json"].get("functions", [])
        )

        self._register_entities(
            self.activity_index,
            self.data["activities.json"].get("activities", [])
        )

        self._register_entities(
            self.technology_index,
            self.data["technologies.json"].get("technologies", [])
        )

        self._register_entities(
            self.architecture_index,
            self.data["architectures.json"].get("architectures", [])
        )

        # Explicit aliases can intentionally map to multiple entities.
        for entry in self.data["aliases.json"].get("aliases", []):
            alias = entry.get("alias", "")
            normalized = self._normalize(alias)

            if not normalized:
                continue

            candidates = self.alias_index.setdefault(normalized, [])

            for entity_id in entry.get("entity_ids", []):
                if entity_id not in candidates:
                    candidates.append(entity_id)

    def get_metadata(self):
        return self.data["taxonomy_metadata.json"]

    def get_domain(self, domain_id):
        return self.domain_index.get(domain_id)

    def get_subdomain(self, subdomain_id):
        return self.subdomain_index.get(subdomain_id)

    def get_function(self, function_id):
        return self.function_index.get(function_id)

    def get_activity(self, activity_id):
        return self.activity_index.get(activity_id)

    def get_technology(self, technology_id):
        return self.technology_index.get(technology_id)

    def get_architecture(self, architecture_id):
        return self.architecture_index.get(architecture_id)

    def get_entity(self, entity_id):
        return self.entity_index.get(entity_id)

    def get_domains(self, branch=None):
        return self._filter_by_branch(
            self.domain_index.values(), branch
        )

    def get_subdomains(self, branch=None):
        return self._filter_by_branch(self.subdomain_index.values(), branch)

    def get_functions(self, branch=None):
        return self._filter_by_branch(
            self.function_index.values(), branch
        )

    def get_activities(self, branch=None):
        return self._filter_by_branch(
            self.activity_index.values(), branch
        )

    @staticmethod
    def _filter_by_branch(items, branch):
        items = list(items)

        if branch is None:
            return items

        return [
            item for item in items
            if item.get("branch") == branch
        ]

    def find_by_alias(self, alias):
        """Return all candidates; never silently resolve ambiguity."""
        normalized = self._normalize(alias)
        entity_ids = self.alias_index.get(normalized, [])

        return [
            self.entity_index[entity_id]
            for entity_id in entity_ids
            if entity_id in self.entity_index
        ]

    def resolve_alias(self, alias):
        """
        Return candidate entities and a simple resolution status.
        This does not perform semantic AI disambiguation.
        """
        candidates = self.find_by_alias(alias)

        if not candidates:
            status = "NOT_FOUND"
        elif len(candidates) == 1:
            status = "SINGLE_CANDIDATE"
        else:
            status = "AMBIGUOUS"

        return {
            "raw_value": alias,
            "normalized_value": self._normalize(alias),
            "status": status,
            "candidate_ids": [
                item["id"] for item in candidates
            ],
            "candidates": candidates
        }

    def get_children(self, parent_id):
        parent = self.entity_index.get(parent_id)

        if parent is None:
            return []

        return parent.get("children", [])

    def get_relationships(self, entity_id):
        relationships = []

        for domain in self.domain_index.values():
            if entity_id in domain.get("children", []):
                relationships.append({
                    "source_id": domain["id"],
                    "source_name": domain["name"],
                    "relationship": "CHILD_OF"
                })

        for function in self.function_index.values():
            if entity_id in function.get("activities", []):
                relationships.append({
                    "source_id": function["id"],
                    "source_name": function["name"],
                    "relationship": "ACTIVITY_OF"
                })

        for technology in self.technology_index.values():
            if entity_id in technology.get("domains", []):
                relationships.append({
                    "source_id": technology["id"],
                    "source_name": technology["name"],
                    "relationship": "ASSOCIATED_WITH_DOMAIN"
                })

        return relationships

    def get_counts(self):
        return {
            "domains": len(self.domain_index),
            "subdomains": len(self.subdomain_index),
            "functions": len(self.function_index),
            "activities": len(self.activity_index),
            "technologies": len(self.technology_index),
            "architectures": len(self.architecture_index),
            "indexed_entities": len(self.entity_index),
            "alias_forms": len(self.alias_index)
        }


def load_taxonomy():
    return TaxonomyLoader()


if __name__ == "__main__":
    taxonomy = load_taxonomy()

    print("=" * 60)
    print("CV-AI TAXONOMY LOADER TEST")
    print("=" * 60)

    metadata = taxonomy.get_metadata()
    print("Name:", metadata["taxonomy_name"])
    print("Version:", metadata["taxonomy_version"])

    print("\nEntity counts:")
    for name, count in taxonomy.get_counts().items():
        print(f"- {name}: {count}")

    print("\nTechnical domains:")
    for item in taxonomy.get_domains("TECHNICAL"):
        print(f"- {item['name']}")

    print("\nBusiness / Corporate domains:")
    for item in taxonomy.get_domains("BUSINESS_CORPORATE"):
        print(f"- {item['name']}")

    print("\nTechnology lookup: PostgreSQL")
    result = taxonomy.resolve_alias("Postgres")
    print("Status:", result["status"])
    print("Candidates:", result["candidate_ids"])

    print("\nAmbiguity test: Sass / SaaS")
    result = taxonomy.resolve_alias("SASS")
    print("Status:", result["status"])
    print("Candidates:", result["candidate_ids"])

    print("\nAmbiguity test: Oracle")
    result = taxonomy.resolve_alias("Oracle")
    print("Status:", result["status"])
    print("Candidates:", result["candidate_ids"])

    print("\nAmbiguity test: Three-tier architecture")
    result = taxonomy.resolve_alias("three-tier architecture")
    print("Status:", result["status"])
    print("Candidates:", result["candidate_ids"])

    print("\nTaxonomy loader test completed.")
