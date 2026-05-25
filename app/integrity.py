from __future__ import annotations

import hashlib
import json

from app.models import StoredObject


class IntegrityService:
    def generate_hash(self, stored: StoredObject) -> str:
        metadata_blob = json.dumps(stored.metadata, sort_keys=True).encode("utf-8")
        digest_input = stored.ciphertext + metadata_blob + stored.storage_ref.encode("utf-8")
        return hashlib.sha256(digest_input).hexdigest()
