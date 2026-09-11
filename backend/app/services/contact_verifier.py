import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.models.enums import VerificationCheckType, VerificationResultStatus, EvidenceType

logger = logging.getLogger(__name__)


class ContactVerifier:
    """
    Deterministic Contact Information Verification Service.
    Validates phone formats (E.164), email syntax, and email-domain relationships.
    Compares contact values across sources (Google Places, Yelp, Website) to detect conflicts.
    Never fabricates emails or phone numbers.
    """

    PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def verify_contacts(
        self,
        phone: Optional[str],
        emails: List[str],
        source_records_data: List[Dict[str, Any]],
        website_domain: Optional[str]
    ) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []
        evidences: List[Dict[str, Any]] = []
        conflicts: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc)

        # 1. Phone Format & Conflict Check
        phones_by_source: Dict[str, str] = {}

        if phone:
            phones_by_source["canonical"] = phone

        # Extract phones across source records
        for sr in source_records_data:
            s_name = sr.get("source_name", "unknown")
            r_data = sr.get("raw_data", {})
            s_phone = r_data.get("phone")
            if s_phone:
                phones_by_source[s_name] = s_phone

        unique_phones = list(set(self._normalize_phone(p) for p in phones_by_source.values() if p))
        
        if not phones_by_source:
            results.append({
                "check_type": VerificationCheckType.CONTACT_PHONE_VALIDITY,
                "result": VerificationResultStatus.NOT_FOUND,
                "confidence": 1.0,
                "reason": "No phone number discovered from any source",
                "evidence": {"discovered_phones": {}},
                "source": "contact_verifier",
                "observed_at": now,
            })
        elif len(unique_phones) > 1:
            # Conflicting phone numbers detected!
            conflict_item = {
                "field": "phone",
                "values": phones_by_source,
                "message": f"Conflicting phone numbers detected across sources: {phones_by_source}"
            }
            conflicts.append(conflict_item)

            results.append({
                "check_type": VerificationCheckType.CONTACT_PHONE_VALIDITY,
                "result": VerificationResultStatus.CONFLICT,
                "confidence": 0.80,
                "reason": f"Conflicting phone numbers found across sources ({len(unique_phones)} unique numbers)",
                "evidence": {"phones_by_source": phones_by_source, "unique_phones": unique_phones},
                "source": "contact_verifier",
                "observed_at": now,
            })
        else:
            # Single phone, validate format
            norm_phone = unique_phones[0]
            is_valid = bool(self.PHONE_REGEX.match(norm_phone))
            results.append({
                "check_type": VerificationCheckType.CONTACT_PHONE_VALIDITY,
                "result": VerificationResultStatus.PASS if is_valid else VerificationResultStatus.FAIL,
                "confidence": 0.95 if is_valid else 0.50,
                "reason": "Valid phone format" if is_valid else "Invalid phone number format",
                "evidence": {"normalized_phone": norm_phone, "raw_phone": phone, "sources": list(phones_by_source.keys())},
                "source": "contact_verifier",
                "observed_at": now,
            })

            evidences.append({
                "source": "contact_verifier",
                "source_url_or_id": None,
                "observed_at": now,
                "status": "PASS" if is_valid else "FAIL",
                "evidence_type": EvidenceType.OBSERVED_FACT,
                "data": {"phone": norm_phone, "sources": phones_by_source}
            })

        # 2. Email Syntax & Domain Match Check
        if not emails:
            results.append({
                "check_type": VerificationCheckType.CONTACT_EMAIL_SYNTAX,
                "result": VerificationResultStatus.NOT_FOUND,
                "confidence": 1.0,
                "reason": "No email address discovered for this business",
                "evidence": {"email": None},
                "source": "contact_verifier",
                "observed_at": now,
            })
        else:
            for email in emails:
                clean_email = email.strip()
                is_syntax_valid = bool(self.EMAIL_REGEX.match(clean_email))

                results.append({
                    "check_type": VerificationCheckType.CONTACT_EMAIL_SYNTAX,
                    "result": VerificationResultStatus.PASS if is_syntax_valid else VerificationResultStatus.FAIL,
                    "confidence": 0.99 if is_syntax_valid else 1.0,
                    "reason": "Valid email syntax" if is_syntax_valid else "Invalid email syntax",
                    "evidence": {"email": clean_email},
                    "source": "contact_verifier",
                    "observed_at": now,
                })

                # Check domain relationship
                if is_syntax_valid and website_domain:
                    email_domain = clean_email.split("@")[-1].lower()
                    clean_w_domain = website_domain.lower().replace("www.", "")

                    domain_match = email_domain == clean_w_domain or email_domain.endswith(f".{clean_w_domain}")
                    results.append({
                        "check_type": VerificationCheckType.CONTACT_EMAIL_DOMAIN_MATCH,
                        "result": VerificationResultStatus.PASS if domain_match else VerificationResultStatus.FAIL,
                        "confidence": 0.95 if domain_match else 0.60,
                        "reason": f"Email domain '{email_domain}' matches website domain '{clean_w_domain}'" if domain_match else f"Email domain '{email_domain}' does not match website '{clean_w_domain}'",
                        "evidence": {"email": clean_email, "email_domain": email_domain, "website_domain": clean_w_domain},
                        "source": "contact_verifier",
                        "observed_at": now,
                    })

        return {
            "results": results,
            "evidences": evidences,
            "conflicts": conflicts,
            "has_conflicts": bool(conflicts),
        }

    def _normalize_phone(self, phone: str) -> str:
        digits = re.sub(r"\D", "", phone)
        if len(digits) == 10:
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith("1"):
            return f"+{digits}"
        elif digits:
            return f"+{digits}"
        return phone
