
"""
CV-AI Taxonomy Integrity Validator
Version: 0.1.0

Validates taxonomy JSON files without modifying them.

Checks:
- Required foundation files
- JSON syntax and structure
- Duplicate entity IDs
- Missing entity IDs/names in recognized entity collections
- Broken references to known entities
- Broken explicit alias mappings
- Ambiguous aliases
- Basic parent/child and relationship integrity

Exit codes:
    0 = No errors found (warnings may still exist)
    1 = Validation errors found
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_DIR = PROJECT_ROOT / "09_CONFIG" / "taxonomy"

REQUIRED_FILES = [
    "taxonomy_metadata.json",
    "domains.json",
    "functions.json",
    "activities.json",
    "technologies.json",
    "architectures.json",
    "aliases.json",
]

# Top-level collection names recognized by the current project.
COLLECTION_KEYS = {
    "domains",
    "subdomains",
    "functions",
    "activities",
    "technologies",
    "architectures",
    "occupations",
    "roles",
    "seniority",
    "career_tracks",
    "career_tracks",
    "skills",
    "competencies",
    "education",
    "certifications",
    "industries",
    "oems",
    "products",
    "tools",
    "protocols",
    "standards",
    "lifecycle",
    "solution_stack",
    "market_segments",
    "relationships",
    "aliases",
    "architectures",
    "functions",
    "activities",
}

# Fields which may contain references to entity IDs.
REFERENCE_FIELDS = {
    "domain",
    "domains",
    "domain_id",
    "domain_ids",
    "subdomain",
    "subdomains",
    "subdomain_id",
    "subdomain_ids",
    "function",
    "functions",
    "function_id",
    "function_ids",
    "activity",
    "activities",
    "activity_id",
    "activity_ids",
    "technology",
    "technologies",
    "technology_id",
    "technology_ids",
    "architecture",
    "architectures",
    "architecture_id",
    "architecture_ids",
    "entity_id",
    "entity_ids",
    "parent_id",
    "parent_ids",
    "child_id",
    "child_ids",
    "source_id",
    "target_id",
    "source_entity_id",
    "target_entity_id",
    "related_entity_ids",
    "depends_on",
    "requires",
    "members",
}

# A reference is checked only if it resembles a stable taxonomy ID.
# Ordinary text labels and descriptions are ignored.
ENTITY_ID_PATTERN = re.compile(
    r"^[A-Z][A-Z0-9_]*(?:\.[A-Z0-9_]+)+$"
)


class TaxonomyValidator:
    def __init__(self, taxonomy_dir=TAXONOMY_DIR):
        self.taxonomy_dir = Path(taxonomy_dir)

        self.errors = []
        self.warnings = []
        self.info = []

        self.documents = {}
        self.entities = {}
        self.entity_locations = defaultdict(list)
        self.alias_records = []

        self.files_checked = 0
        self.entities_checked = 0
        self.references_checked = 0

    # ---------------------------------------------------------
    # Reporting
    # ---------------------------------------------------------

    def error(self, message):
        self.errors.append(message)

    def warning(self, message):
        self.warnings.append(message)

    def note(self, message):
        self.info.append(message)

    # ---------------------------------------------------------
    # File loading
    # ---------------------------------------------------------

    def load_files(self):
        print("\n[1/5] Checking taxonomy files...")

        if not self.taxonomy_dir.exists():
            self.error(
                f"Taxonomy directory does not exist: "
                f"{self.taxonomy_dir}"
            )
            return

        for filename in REQUIRED_FILES:
            path = self.taxonomy_dir / filename

            if not path.exists():
                self.error(
                    f"Required file is missing: {filename}"
                )

        json_files = sorted(self.taxonomy_dir.rglob("*.json"))

        if not json_files:
            self.error("No JSON files found in taxonomy directory.")
            return

        for path in json_files:
            relative_path = str(
                path.relative_to(self.taxonomy_dir)
            )

            try:
                with path.open(
                    "r", encoding="utf-8-sig"
                ) as file:
                    data = json.load(file)

                if not isinstance(data, dict):
                    self.error(
                        f"{relative_path}: top-level JSON "
                        f"must be an object."
                    )
                    continue

                self.documents[relative_path] = data
                self.files_checked += 1

            except json.JSONDecodeError as exc:
                self.error(
                    f"{relative_path}: invalid JSON at "
                    f"line {exc.lineno}, column {exc.colno}: "
                    f"{exc.msg}"
                )

            except OSError as exc:
                self.error(
                    f"{relative_path}: could not read file: {exc}"
                )

        print(f"  JSON files loaded: {self.files_checked}")

    # ---------------------------------------------------------
    # Entity discovery
    # ---------------------------------------------------------

    def _walk_for_entities(self, value, path, collection=None):
        """
        Find entity records recursively.

        Entity records are dictionaries containing both 'id'
        and 'name'. Collection entries with missing fields are
        checked separately.
        """
        if isinstance(value, dict):
            entity_id = value.get("id")
            entity_name = value.get("name")

            if (
                isinstance(entity_id, str)
                and entity_id.strip()
                and isinstance(entity_name, str)
                and entity_name.strip()
            ):
                self.entity_locations[entity_id].append(path)

            for key, child in value.items():
                child_collection = (
                    key if key in COLLECTION_KEYS else collection
                )

                self._walk_for_entities(
                    child,
                    f"{path}.{key}",
                    child_collection,
                )

        elif isinstance(value, list):
            for index, item in enumerate(value):
                item_path = f"{path}[{index}]"

                if (
                    collection in COLLECTION_KEYS
                    and isinstance(item, dict)
                ):
                    self._check_entity_record(
                        item, item_path, collection
                    )

                self._walk_for_entities(
                    item, item_path, collection
                )

    def _check_entity_record(self, record, path, collection):
        """
        Report missing IDs/names for records in recognized
        entity collections. Alias mappings are handled separately.
        """
        if collection == "aliases":
            if "alias" in record and "entity_ids" in record:
                self.alias_records.append((record, path))
            return

        if "id" not in record:
            self.warning(
                f"{path}: record in '{collection}' has no ID."
            )
            return

        entity_id = record.get("id")

        if not isinstance(entity_id, str) or not entity_id.strip():
            self.error(
                f"{path}: entity ID must be a non-empty string."
            )
            return

        if not isinstance(record.get("name"), str) or not (
            record.get("name", "").strip()
        ):
            self.warning(
                f"{path}: entity '{entity_id}' has no valid name."
            )

    def build_entity_index(self):
        print("\n[2/5] Building entity index...")

        for filename, data in self.documents.items():
            self._walk_for_entities(data, filename)

        for entity_id, locations in self.entity_locations.items():
            if len(locations) > 1:
                self.error(
                    f"Duplicate entity ID '{entity_id}' found at: "
                    + "; ".join(locations)
                )
            else:
                self.entities[entity_id] = locations[0]

        self.entities_checked = len(self.entities)

        print(f"  Unique entity IDs: {len(self.entities)}")
        print(
            f"  Duplicate ID groups: "
            f"{sum(len(v) > 1 for v in self.entity_locations.values())}"
        )

    # ---------------------------------------------------------
    # Reference integrity
    # ---------------------------------------------------------


    def _check_reference_value(self, value, location):
        """Check nested reference values once per traversal."""

        if isinstance(value, str):
            candidate = value.strip()

            if not ENTITY_ID_PATTERN.fullmatch(candidate):
                return

            self.references_checked += 1

            if candidate not in self.entities:
                self.error(
                    f"Unresolved reference '{candidate}' at {location}"
                )

        elif isinstance(value, list):
            for index, item in enumerate(value):
                self._check_reference_value(
                    item, f"{location}[{index}]"
                )

        elif isinstance(value, dict):
            for key, item in value.items():
                if key.lower() in REFERENCE_FIELDS:
                    self._check_reference_value(
                        item, f"{location}.{key}"
                    )

    def _walk_for_references(self, value, path):
        """Traverse documents without rechecking a reference field."""

        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}"

                # Namespace declarations are metadata, not entity links.
                if (
                    path == "taxonomy_metadata.json"
                    and key.lower() == "namespaces"
                ):
                    continue

                if key.lower() in REFERENCE_FIELDS:
                    self._check_reference_value(
                        child, child_path
                    )
                    # The reference checker handles nested references.
                    continue

                if isinstance(child, (dict, list)):
                    self._walk_for_references(
                        child, child_path
                    )

        elif isinstance(value, list):
            for index, item in enumerate(value):
                self._walk_for_references(
                    item, f"{path}[{index}]"
                )


    def validate_references(self):
        """Validate references across loaded taxonomy files exactly once."""
        self.references_checked = 0

        for filename, data in self.documents.items():
            self._walk_for_references(data, filename)


    # ---------------------------------------------------------
    # Alias validation
    # ---------------------------------------------------------

    def validate_aliases(self):
        print("\n[4/5] Checking alias mappings...")

        alias_count = 0
        ambiguous_count = 0
        seen_aliases = defaultdict(list)

        for record, location in self.alias_records:
            alias = record.get("alias")
            entity_ids = record.get("entity_ids")

            if not isinstance(alias, str) or not alias.strip():
                self.error(
                    f"{location}: alias must be a non-empty string."
                )
                continue

            alias_count += 1
            normalized_alias = " ".join(alias.casefold().split())

            if not isinstance(entity_ids, list) or not entity_ids:
                self.error(
                    f"{location}: alias '{alias}' has no entity_ids."
                )
                continue

            valid_targets = []

            for entity_id in entity_ids:
                if not isinstance(entity_id, str):
                    self.error(
                        f"{location}: alias '{alias}' contains "
                        f"a non-string entity ID."
                    )
                    continue

                if entity_id not in self.entities:
                    self.error(
                        f"{location}: alias '{alias}' points to "
                        f"missing entity '{entity_id}'."
                    )
                else:
                    valid_targets.append(entity_id)

            seen_aliases[normalized_alias].append(
                (location, valid_targets)
            )

            if len(entity_ids) > 1:
                ambiguous_count += 1
                self.note(
                    f"Ambiguous alias '{alias}' has "
                    f"{len(entity_ids)} candidate(s): "
                    f"{', '.join(entity_ids)}"
                )

        for alias, entries in seen_aliases.items():
            if len(entries) > 1:
                targets = {
                    target
                    for _, ids in entries
                    for target in ids
                }

                if len(targets) > 1:
                    self.warning(
                        f"Alias '{alias}' appears in multiple "
                        f"records with different candidate sets."
                    )

        print(f"  Explicit alias records: {alias_count}")
        print(f"  Multi-candidate aliases: {ambiguous_count}")

    # ---------------------------------------------------------
    # Basic structural checks
    # ---------------------------------------------------------

    def validate_structure(self):
        print("\n[5/5] Checking basic structure...")

        metadata = self.documents.get("taxonomy_metadata.json")

        if metadata is not None:
            version = metadata.get("taxonomy_version")

            if not isinstance(version, str) or not version.strip():
                self.warning(
                    "taxonomy_metadata.json: version is missing "
                    "or is not a non-empty string."
                )

        for filename, data in self.documents.items():
            for key in COLLECTION_KEYS:
                if key not in data:
                    continue

                value = data[key]

                # Some files use metadata plus a collection.
                if not isinstance(value, list):
                    self.warning(
                        f"{filename}: '{key}' is not a list. "
                        f"Confirm that this is intentional."
                    )

    # ---------------------------------------------------------
    # Run and report
    # ---------------------------------------------------------

    def run(self):
        print("=" * 64)
        print("CV-AI TAXONOMY INTEGRITY VALIDATOR")
        print("=" * 64)
        print(f"Project root:  {PROJECT_ROOT}")
        print(f"Taxonomy path: {self.taxonomy_dir}")

        self.load_files()

        if self.documents:
            self.build_entity_index()
            self.validate_references()
            self.validate_aliases()
            self.validate_structure()

        print("\n" + "=" * 64)
        print("VALIDATION REPORT")
        print("=" * 64)

        print(f"Files checked:       {self.files_checked}")
        print(f"Unique entity IDs:   {self.entities_checked}")
        print(f"References checked:  {self.references_checked}")
        print(f"Errors:              {len(self.errors)}")
        print(f"Warnings:            {len(self.warnings)}")
        print(f"Information notes:   {len(self.info)}")

        if self.errors:
            print("\nERRORS")
            print("-" * 64)

            for index, message in enumerate(self.errors, 1):
                print(f"{index}. {message}")

        if self.warnings:
            print("\nWARNINGS")
            print("-" * 64)

            for index, message in enumerate(self.warnings, 1):
                print(f"{index}. {message}")

        if self.info:
            print("\nINFORMATION")
            print("-" * 64)

            for message in self.info:
                print(f"- {message}")

        print("\n" + "=" * 64)

        if self.errors:
            print("RESULT: FAILED — fix the reported errors.")
            return 1

        if self.warnings:
            print(
                "RESULT: PASSED WITH WARNINGS — "
                "review warnings before expanding the taxonomy."
            )
        else:
            print("RESULT: PASSED — no errors or warnings found.")

        return 0


if __name__ == "__main__":
    validator = TaxonomyValidator()
    sys.exit(validator.run())
