from __future__ import annotations

from typing import Literal, TypedDict

from .common import PaginatedResponse, PaginationParams

NewsletterStatus = Literal[
    "draft",
    "imported",
    "pending_approval",
    "approved",
    "scheduled",
    "in_review",
    "sending",
    "paused",
    "sent",
    "published",
    "cancelled",
    "failed",
]
# "public" lists an issue on the audience's newsletter website and feed. Defaults to "private".
NewsletterArchiveVisibility = Literal["private", "public"]
# Where an issue goes: "email_and_website" (the default), "email" only, or "website" only.
NewsletterPublishTarget = Literal["email_and_website", "email", "website"]
NewsletterStylingMode = Literal["styled", "plain"]
NewsletterDomainStatus = Literal["pending", "verifying", "verified", "failed", "disabled"]
NewsletterDomainRecordStatus = Literal["pending", "verified", "failed"]
NewsletterPreflightStatus = Literal["not_run", "passed", "warning", "failed"]
NewsletterPreflightItemStatus = Literal["pass", "warn", "fail"]
NewsletterTestSendStatus = Literal["pending", "sent", "failed"]
NewsletterAssetKind = Literal["image", "video"]
NewsletterAssetContentType = Literal[
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/webp",
    "video/mp4",
    "video/quicktime",
    "video/webm",
]
NewsletterUrlSource = Literal["href", "image_src", "video_href", "text"]
NewsletterChangelogTone = Literal["concise", "friendly", "technical"]
NewsletterCalloutVariant = Literal["accent", "info", "warning", "success"]
NewsletterColumnRatio = Literal["50-50", "33-67", "67-33"]
NewsletterColumnImageFit = Literal["natural", "contain", "cover"]
NewsletterButtonAlign = Literal["left", "center", "right"]
NewsletterRecipientStatus = Literal[
    "pending",
    "retrying",
    "sending",
    "sent",
    "delivered",
    "bounced",
    "complained",
    "failed",
    "skipped",
    "unsubscribed",
]
# Why a reader was skipped, or what happened after the send. Raw provider error text is never
# returned.
NewsletterRecipientReason = Literal[
    "opted_out",
    "suppressed",
    "never_email",
    "undeliverable_domain",
    "dormant",
    "last_chance_waiting",
    "no_longer_eligible",
    "cancelled",
    "content_in_review",
    "email_removed",
    "skipped_other",
    "bounced",
    "complained",
    "unsubscribed",
    "send_failed",
]


class NewsletterDomain(TypedDict):
    object: Literal["newsletter_domain"]
    id: str
    root_domain_name: str
    domain_name: str
    from_local_part: str
    from_address: str
    mail_from_domain: str
    reply_to_address: str | None
    status: NewsletterDomainStatus
    dkim_status: NewsletterDomainRecordStatus
    mail_from_status: NewsletterDomainRecordStatus
    spf_status: NewsletterDomainRecordStatus
    dmarc_status: NewsletterDomainRecordStatus
    verified_at: str | None
    # The records to publish at the DNS host before calling verify.
    dns_records: list[NewsletterDomainDnsRecord]
    created_at: str
    updated_at: str


class NewsletterDomainDnsRecord(TypedDict):
    key: Literal["dkim", "mail_from_mx", "mail_from_spf", "dmarc"]
    type: Literal["CNAME", "MX", "TXT"]
    host: str
    value: str
    priority: int | None
    ttl: int | None
    description: str


class _CreateNewsletterDomainRequired(TypedDict):
    root_domain: str
    reply_to_address: str


class CreateNewsletterDomainParams(_CreateNewsletterDomainRequired, total=False):
    # A label under root_domain ("news", the default) or the full name ("news.example.com").
    subdomain: str
    # The part before @ in the From address. Defaults to "updates".
    from_local_part: str
    reply_to_name: str


class NewsletterSenderIdentity(TypedDict):
    object: Literal["newsletter_sender_identity"]
    id: str
    newsletter_domain_id: str
    from_name: str
    from_address: str
    business_name: str
    postal_address: str | None
    footer_text: str | None
    domain_status: NewsletterDomainStatus
    is_default: bool
    created_at: str
    updated_at: str


# Each column requires a heading, body, image, or complete CTA label/URL pair.
class NewsletterColumnContent(TypedDict, total=False):
    title: str | None
    body: str
    image_url: str | None
    image_alt: str | None
    image_fit: NewsletterColumnImageFit
    cta_label: str | None
    cta_url: str | None


NewsletterBlockChannel = Literal["all", "email", "web"]
NewsletterBlockSegmentRule = Literal["in", "not_in"]


# Where a block shows and to which readers. The website, archive and feed show a block as a reader
# in no segment sees it. Segment membership is fixed when the send is scheduled. Welcome emails
# accept channel only.
class NewsletterBlockVisibility(TypedDict, total=False):
    channel: NewsletterBlockChannel
    segment_id: str | None
    segment_rule: NewsletterBlockSegmentRule


class NewsletterBlockConditions(TypedDict, total=False):
    visibility: NewsletterBlockVisibility


class NewsletterHeadingBlockRequired(NewsletterBlockConditions):
    type: Literal["heading"]
    text: str


class NewsletterHeadingBlock(NewsletterHeadingBlockRequired, total=False):
    level: Literal[1, 2, 3]


class NewsletterParagraphBlock(NewsletterBlockConditions):
    type: Literal["paragraph"]
    body: str


class NewsletterListBlockRequired(NewsletterBlockConditions):
    type: Literal["list"]
    items: list[str]


class NewsletterListBlock(NewsletterListBlockRequired, total=False):
    ordered: bool


class NewsletterCalloutBlockRequired(NewsletterBlockConditions):
    type: Literal["callout"]
    body: str


class NewsletterCalloutBlock(NewsletterCalloutBlockRequired, total=False):
    title: str | None
    variant: NewsletterCalloutVariant


class NewsletterButtonBlockRequired(NewsletterBlockConditions):
    type: Literal["button"]
    label: str
    url: str


class NewsletterButtonBlock(NewsletterButtonBlockRequired, total=False):
    align: NewsletterButtonAlign


class NewsletterImageBlockRequired(NewsletterBlockConditions):
    type: Literal["image"]
    url: str
    alt: str


class NewsletterImageBlock(NewsletterImageBlockRequired, total=False):
    align: NewsletterButtonAlign
    link_url: str | None
    caption: str | None
    caption_url: str | None


class NewsletterVideoBlock(NewsletterBlockConditions):
    type: Literal["video"]
    video_url: str
    thumbnail_url: str
    label: str


class NewsletterColumnsBlockRequired(NewsletterBlockConditions):
    type: Literal["columns"]
    left: NewsletterColumnContent
    right: NewsletterColumnContent


class NewsletterColumnsBlock(NewsletterColumnsBlockRequired, total=False):
    ratio: NewsletterColumnRatio


class NewsletterLinkListItemRequired(TypedDict):
    label: str
    url: str


class NewsletterLinkListItem(NewsletterLinkListItemRequired, total=False):
    description: str | None


class NewsletterLinkListBlockRequired(NewsletterBlockConditions):
    type: Literal["link_list"]
    items: list[NewsletterLinkListItem]


class NewsletterLinkListBlock(NewsletterLinkListBlockRequired, total=False):
    title: str | None


class NewsletterQuoteBlockRequired(NewsletterBlockConditions):
    type: Literal["quote"]
    body: str


class NewsletterQuoteBlock(NewsletterQuoteBlockRequired, total=False):
    cite: str | None


class NewsletterDividerBlock(NewsletterBlockConditions):
    type: Literal["divider"]


class NewsletterSpacerBlockRequired(NewsletterBlockConditions):
    type: Literal["spacer"]


class NewsletterSpacerBlock(NewsletterSpacerBlockRequired, total=False):
    height: int


class NewsletterCodeBlock(NewsletterBlockConditions):
    type: Literal["code"]
    code: str


class NewsletterEventBlock(NewsletterBlockConditions):
    type: Literal["event"]
    event_id: str


class NewsletterCustomHtmlBlock(NewsletterBlockConditions):
    type: Literal["custom_html"]
    html: str


NewsletterBlock = (
    NewsletterHeadingBlock
    | NewsletterParagraphBlock
    | NewsletterListBlock
    | NewsletterCalloutBlock
    | NewsletterButtonBlock
    | NewsletterImageBlock
    | NewsletterVideoBlock
    | NewsletterColumnsBlock
    | NewsletterLinkListBlock
    | NewsletterQuoteBlock
    | NewsletterDividerBlock
    | NewsletterSpacerBlock
    | NewsletterCodeBlock
    | NewsletterEventBlock
    | NewsletterCustomHtmlBlock
)


NewsletterSubjectVariant = Literal["a", "b"]


class Newsletter(TypedDict):
    object: Literal["newsletter"]
    id: str
    audience_id: str | None
    sender_identity_id: str | None
    newsletter_domain_id: str | None
    name: str
    subject: str | None
    preview_text: str | None
    from_name: str | None
    from_address: str
    reply_to_address: str | None
    blocks: list[NewsletterBlock] | None
    body_html: str | None
    body_text: str | None
    status: NewsletterStatus
    archive_visibility: NewsletterArchiveVisibility
    publish_target: NewsletterPublishTarget
    # Whether the email carries a View in browser link to the issue's own page.
    view_in_browser: bool
    feed_entry_url: str | None
    styling_mode: NewsletterStylingMode
    track_engagement: bool
    add_utm_tags: bool
    opened_count: int | None
    clicked_count: int | None
    send_limit: int | None
    held_count: int
    subject_b: str | None
    subject_test_percent: int | None
    subject_test_hours: int | None
    subject_test_winner: NewsletterSubjectVariant | None
    subject_test_decided_at: str | None
    preflight_status: NewsletterPreflightStatus
    preflight_results: dict[str, object]
    send_window_hours: int
    send_rate_per_hour: int
    recipient_count: int
    sent_count: int
    delivered_count: int
    bounced_count: int
    complained_count: int
    failed_count: int
    skipped_count: int
    last_test_sent_at: str | None
    last_test_recipient: str | None
    content_changed_since_test_send: bool
    scheduled_at: str | None
    approved_at: str | None
    started_at: str | None
    published_at: str | None
    archive_url: str | None
    completed_at: str | None
    cancelled_at: str | None
    created_at: str
    updated_at: str


class NewsletterPreflightItem(TypedDict):
    key: str
    label: str
    status: NewsletterPreflightItemStatus
    message: str


class NewsletterCountedUrl(TypedDict):
    url: str
    source: NewsletterUrlSource


class NewsletterUrlBreakdown(TypedDict):
    href_count: int
    image_src_count: int
    video_href_count: int
    text_url_count: int
    unique_url_count: int
    max_unique_urls: int
    urls: list[NewsletterCountedUrl]
    offending_urls: list[str]


class NewsletterPreflight(TypedDict):
    object: Literal["newsletter_preflight"]
    newsletter_id: str
    status: NewsletterPreflightStatus
    items: list[NewsletterPreflightItem]
    url_breakdown: NewsletterUrlBreakdown


class NewsletterPreviewWarning(TypedDict):
    kind: str
    severity: Literal["fail", "warn"]
    message: str


class NewsletterPreview(TypedDict):
    """The email exactly as one reader receives it: footer, unsubscribe link and list headers
    included. Preview links are never tracked."""

    object: Literal["newsletter_preview"]
    newsletter_id: str
    # With merge tags rendered for the reader.
    subject: str
    html: str
    archive_html: str
    text: str
    # Header name to value, such as List-Unsubscribe, List-Unsubscribe-Post and Reply-To.
    headers: dict[str, str]
    warnings: list[NewsletterPreviewWarning]
    url_breakdown: NewsletterUrlBreakdown


class NewsletterPreviewAsSample(TypedDict):
    type: Literal["sample"]


class NewsletterPreviewAsSubscriber(TypedDict):
    """Render for one reader a send would reach. Needs the audiences:read scope too."""

    type: Literal["subscriber"]
    subscriber_id: str


NewsletterPreviewAs = NewsletterPreviewAsSample | NewsletterPreviewAsSubscriber


class PreviewNewsletterParams(TypedDict, total=False):
    # Defaults to {"type": "sample"}.
    preview_as: NewsletterPreviewAs


class NewsletterRecipient(TypedDict):
    """One reader's result for an issue: sent, skipped and why, and what happened after."""

    object: Literal["newsletter_recipient"]
    id: str
    newsletter_id: str
    email_address: str
    status: NewsletterRecipientStatus
    reason: NewsletterRecipientReason | None
    # None when the reader has since been removed from the audience.
    subscriber_id: str | None
    sent_at: str | None
    delivered_at: str | None
    bounced_at: str | None
    complained_at: str | None
    unsubscribed_at: str | None
    created_at: str


class ListNewsletterRecipientsParams(PaginationParams, total=False):
    status: NewsletterRecipientStatus
    reason: NewsletterRecipientReason


class NewsletterTestSend(TypedDict):
    object: Literal["newsletter_test_send"]
    id: str
    newsletter_id: str
    message_id: str | None
    recipient_email: str
    status: NewsletterTestSendStatus
    last_error: str | None
    sent_at: str | None
    created_at: str


class _CreateNewsletterRequired(TypedDict):
    audience_id: str
    sender_identity_id: str
    name: str
    subject: str


class CreateNewsletterParams(_CreateNewsletterRequired, total=False):
    preview_text: str | None
    body_html: str | None
    body_text: str | None
    blocks: list[NewsletterBlock]
    content_markdown: str
    send_window_hours: int
    archive_visibility: NewsletterArchiveVisibility
    publish_target: NewsletterPublishTarget
    view_in_browser: bool
    feed_entry_url: str | None
    styling_mode: NewsletterStylingMode
    track_engagement: bool
    add_utm_tags: bool
    subject_b: str | None
    subject_test_percent: int | None
    subject_test_hours: int | None


class UpdateNewsletterParams(TypedDict, total=False):
    audience_id: str
    sender_identity_id: str
    name: str
    subject: str
    preview_text: str | None
    body_html: str | None
    body_text: str | None
    blocks: list[NewsletterBlock]
    content_markdown: str
    send_window_hours: int
    archive_visibility: NewsletterArchiveVisibility
    publish_target: NewsletterPublishTarget
    view_in_browser: bool
    feed_entry_url: str | None
    styling_mode: NewsletterStylingMode
    track_engagement: bool
    add_utm_tags: bool
    subject_b: str | None
    subject_test_percent: int | None
    subject_test_hours: int | None


class _NewsletterChangelogMediaImageRequired(TypedDict):
    kind: Literal["image"]
    url: str
    alt: str


class NewsletterChangelogMediaImage(_NewsletterChangelogMediaImageRequired, total=False):
    caption: str | None
    link_url: str | None


class NewsletterChangelogMediaVideo(TypedDict):
    kind: Literal["video"]
    video_url: str
    thumbnail_url: str
    label: str


NewsletterChangelogMedia = NewsletterChangelogMediaImage | NewsletterChangelogMediaVideo


class _NewsletterChangelogEntryRequired(TypedDict):
    title: str


class NewsletterChangelogEntry(_NewsletterChangelogEntryRequired, total=False):
    body: str | None
    url: str | None
    media: list[NewsletterChangelogMedia]
    cta_label: str | None
    cta_url: str | None


class _NewsletterChangelogFinalCtaRequired(TypedDict):
    label: str
    url: str


class NewsletterChangelogFinalCta(_NewsletterChangelogFinalCtaRequired, total=False):
    body: str | None


class _CreateNewsletterFromChangelogRequired(TypedDict):
    audience_id: str
    sender_identity_id: str
    name: str
    subject: str
    entries: list[NewsletterChangelogEntry]


class CreateNewsletterFromChangelogParams(_CreateNewsletterFromChangelogRequired, total=False):
    preview_text: str | None
    tone: NewsletterChangelogTone
    final_cta: NewsletterChangelogFinalCta
    send_window_hours: int
    archive_visibility: NewsletterArchiveVisibility
    publish_target: NewsletterPublishTarget
    view_in_browser: bool
    feed_entry_url: str | None
    styling_mode: NewsletterStylingMode


class ListNewsletterDomainsParams(PaginationParams, total=False):
    pass


class ListNewsletterSenderIdentitiesParams(PaginationParams, total=False):
    pass


class _CreateNewsletterSenderIdentityRequired(TypedDict):
    newsletter_domain_id: str
    from_name: str
    business_name: str


class CreateNewsletterSenderIdentityParams(_CreateNewsletterSenderIdentityRequired, total=False):
    postal_address: str | None
    footer_text: str | None
    # True makes this the default identity. False keeps it from being the default (and an
    # identity that was the default stops being it). Omitted, the organization's first identity
    # becomes the default and the default is otherwise unchanged.
    make_default: bool


class UpdateNewsletterSenderIdentityParams(TypedDict, total=False):
    newsletter_domain_id: str
    from_name: str
    business_name: str
    postal_address: str | None
    footer_text: str | None
    # True makes this the default identity. False keeps it from being the default (and an
    # identity that was the default stops being it). Omitted, the organization's first identity
    # becomes the default and the default is otherwise unchanged.
    make_default: bool


class ListNewslettersParams(PaginationParams, total=False):
    pass


class ListNewsletterAssetsParams(PaginationParams, total=False):
    kind: NewsletterAssetKind
    q: str


class NewsletterAsset(TypedDict):
    object: Literal["newsletter_asset"]
    id: str
    kind: NewsletterAssetKind
    filename: str
    content_type: str
    byte_size: int
    checksum_sha256: str
    url: str
    image_url: str | None
    video_url: str | None
    thumbnail_url: str | None
    thumbnail_content_type: str | None
    thumbnail_byte_size: int | None
    duration_seconds: float | None
    width: int | None
    height: int | None
    created_at: str


class NewsletterAssetStorageUpgrade(TypedDict):
    plan: str
    storage_bytes: int


class NewsletterAssetStorageUsage(TypedDict):
    used_bytes: int
    limit_bytes: int | None
    remaining_bytes: int | None
    over_limit: bool
    plan: str
    is_in_trial: bool
    next_upgrade: NewsletterAssetStorageUpgrade | None


class NewsletterAssetListResponse(PaginatedResponse):
    storage: NewsletterAssetStorageUsage


class _UploadNewsletterAssetRequired(TypedDict):
    filename: str
    data: bytes


class UploadNewsletterAssetParams(_UploadNewsletterAssetRequired, total=False):
    content_type: str


class PrepareNewsletterAssetUploadParams(TypedDict):
    filename: str
    content_type: NewsletterAssetContentType
    size: int
    sha256: str


class _NewsletterAssetUploadBase(TypedDict):
    object: Literal["newsletter_asset_upload"]
    filename: str
    content_type: NewsletterAssetContentType
    size: int
    sha256: str
    upload_url: str
    upload_method: Literal["PUT"]
    upload_headers: dict[str, str]
    complete_url: str
    complete_method: Literal["POST"]
    expires_at: str


class NewsletterImageAssetUpload(_NewsletterAssetUploadBase):
    kind: Literal["image"]


class NewsletterVideoAssetUpload(_NewsletterAssetUploadBase):
    kind: Literal["video"]
    thumbnail_upload_url: str
    thumbnail_upload_method: Literal["PUT"]
    thumbnail_upload_headers: dict[str, str]


NewsletterAssetUpload = NewsletterImageAssetUpload | NewsletterVideoAssetUpload


class _RegisterNewsletterAssetFromUrlRequired(TypedDict):
    url: str


class RegisterNewsletterAssetFromUrlParams(_RegisterNewsletterAssetFromUrlRequired, total=False):
    filename: str
    thumbnail_url: str | None


class SendNewsletterTestParams(TypedDict):
    recipient_email: str


class _ScheduleNewsletterRequired(TypedDict):
    scheduled_at: str


class ScheduleNewsletterParams(_ScheduleNewsletterRequired, total=False):
    limit: int | None


class SendNewsletterToMoreParams(TypedDict, total=False):
    count: int | None
