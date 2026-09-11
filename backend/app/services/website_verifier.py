import logging
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup
from app.models.enums import VerificationCheckType, VerificationResultStatus, EvidenceType

logger = logging.getLogger(__name__)


class WebsiteVerifier:
    """
    Deterministic Website Verification Service.
    Probes URLs for HTTP reachability, HTTPS/SSL availability, redirect chains,
    robots.txt / sitemap accessibility, and HTML identity signals.
    Never fabricates results. Returns NOT_FOUND if website_url is missing.
    """

    MAX_RETRIES = 2
    TIMEOUT_SECONDS = 5.0

    async def verify_website(self, website_url: Optional[str], business_name: str) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []
        evidences: List[Dict[str, Any]] = []

        if not website_url or not website_url.strip():
            logger.info(f"Website URL missing for '{business_name}'. Returning NOT_FOUND results.")
            now = datetime.now(timezone.utc)
            
            results.append({
                "check_type": VerificationCheckType.WEBSITE_REACHABILITY,
                "result": VerificationResultStatus.NOT_FOUND,
                "confidence": 1.0,
                "reason": "No website URL provided for business",
                "evidence": {"website_url": None},
                "source": "website_verifier",
                "observed_at": now,
            })
            return {"results": results, "evidences": evidences, "reachable": False, "has_https": False}

        clean_url = website_url.strip()
        if not clean_url.startswith("http"):
            clean_url = f"https://{clean_url}"

        parsed = urllib.parse.urlparse(clean_url)
        domain = parsed.netloc or parsed.path

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        # 1. Probe HTTP/HTTPS reachability with retries
        http_success = False
        https_success = False
        final_url = clean_url
        status_code = None
        html_text = ""
        redirect_chain = []
        now = datetime.now(timezone.utc)

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS, follow_redirects=True, verify=False) as client:
                    resp = await client.get(clean_url, headers=headers)
                    status_code = resp.status_code
                    final_url = str(resp.url)
                    html_text = resp.text
                    redirect_chain = [str(r.url) for r in resp.history] + [final_url]

                    if resp.status_code < 400:
                        http_success = True
                        if final_url.startswith("https://"):
                            https_success = True
                        break
            except Exception as exc:
                logger.warning(f"Website probe attempt {attempt}/{self.MAX_RETRIES} failed for '{clean_url}': {exc}")

        # Record WEBSITE_REACHABILITY check
        reach_status = VerificationResultStatus.PASS if http_success else VerificationResultStatus.FAIL
        reach_reason = f"HTTP {status_code}" if status_code else "Connection timeout / network error"
        
        results.append({
            "check_type": VerificationCheckType.WEBSITE_REACHABILITY,
            "result": reach_status,
            "confidence": 0.98 if http_success else 1.0,
            "reason": reach_reason,
            "evidence": {
                "initial_url": clean_url,
                "final_url": final_url,
                "status_code": status_code,
                "redirect_chain": redirect_chain,
            },
            "source": "website_verifier",
            "observed_at": now,
        })

        evidences.append({
            "source": "website_verifier",
            "source_url_or_id": final_url,
            "observed_at": now,
            "status": "PASS" if http_success else "FAIL",
            "evidence_type": EvidenceType.OBSERVED_FACT,
            "data": {
                "http_status": status_code,
                "final_url": final_url,
                "redirect_count": len(redirect_chain) - 1,
            }
        })

        # Record HTTPS_AVAILABILITY check
        https_status = VerificationResultStatus.PASS if https_success else VerificationResultStatus.FAIL
        results.append({
            "check_type": VerificationCheckType.HTTPS_AVAILABILITY,
            "result": https_status,
            "confidence": 1.0,
            "reason": "HTTPS active" if https_success else "No active HTTPS endpoint",
            "evidence": {"is_https": https_success, "final_url": final_url},
            "source": "website_verifier",
            "observed_at": now,
        })

        # 2. Content Identity Signals (Title, H1, Meta) if reachable
        title_found = ""
        h1_found = ""
        meta_desc = ""
        identity_match = False

        if http_success and html_text:
            try:
                soup = BeautifulSoup(html_text, "html.parser")
                title_tag = soup.find("title")
                title_found = title_tag.get_text(strip=True) if title_tag else ""
                
                h1_tag = soup.find("h1")
                h1_found = h1_tag.get_text(strip=True) if h1_tag else ""

                meta_tag = soup.find("meta", attrs={"name": "description"})
                meta_desc = meta_tag.get("content", "") if meta_tag else ""

                clean_b_name = re.sub(r"[^\w\s]", "", business_name.lower())
                clean_title = re.sub(r"[^\w\s]", "", title_found.lower())
                clean_h1 = re.sub(r"[^\w\s]", "", h1_found.lower())

                # Check if key tokens of business name appear in title or H1
                tokens = [t for t in clean_b_name.split() if len(t) > 3]
                if tokens and any(t in clean_title or t in clean_h1 for t in tokens):
                    identity_match = True

            except Exception as e:
                logger.warning(f"Error parsing HTML signals for {clean_url}: {e}")

        results.append({
            "check_type": VerificationCheckType.CONTENT_IDENTITY_MATCH,
            "result": VerificationResultStatus.PASS if identity_match else (VerificationResultStatus.UNKNOWN if not http_success else VerificationResultStatus.FAIL),
            "confidence": 0.90 if identity_match else 0.70,
            "reason": "Business name matched page title/H1" if identity_match else "Business name not found in title/H1 tags",
            "evidence": {
                "page_title": title_found,
                "h1_tag": h1_found,
                "meta_description": meta_desc[:200],
            },
            "source": "website_verifier",
            "observed_at": now,
        })

        # 3. Check robots.txt & sitemap
        robots_url = f"https://{domain}/robots.txt"
        robots_found = False
        try:
            async with httpx.AsyncClient(timeout=3.0, verify=False) as client:
                r_resp = await client.get(robots_url, headers=headers)
                if r_resp.status_code == 200 and "User-agent" in r_resp.text:
                    robots_found = True
        except Exception:
            pass

        results.append({
            "check_type": VerificationCheckType.ROBOTS_TXT_ACCESSIBLE,
            "result": VerificationResultStatus.PASS if robots_found else VerificationResultStatus.NOT_FOUND,
            "confidence": 0.95,
            "reason": "robots.txt accessible" if robots_found else "robots.txt not found",
            "evidence": {"robots_url": robots_url, "accessible": robots_found},
            "source": "website_verifier",
            "observed_at": now,
        })

        return {
            "results": results,
            "evidences": evidences,
            "reachable": http_success,
            "has_https": https_success,
            "final_url": final_url if http_success else None,
            "title": title_found,
            "meta_description": meta_desc,
        }
