"""Module for util functions."""
from typing import Any, List, Tuple

from content_negotiation import (
    decide_content_type,
    decide_language,
    NoAgreeableContentTypeError,
    NoAgreeableLanguageError,
)
from rdflib import Graph
from rdflib.exceptions import ParserError


class ContentTypeNotSupportedException(Exception):
    """Class representing the content-type not supported exception."""

    pass


class NotValidFileContentException(Exception):
    """Class representing the not valid file content exception."""

    pass


async def decide_content_and_extension(
    accept_header: List[str],
    supported_content_types: List[str],
    accept_language_header: List[str],
    supported_languages: List[str],
) -> Tuple[str, str, str]:
    """Return content_language, content_type and extension based on request."""
    # Default content-type/content-language/extension:
    content_language = ""
    content_type: str = "text/html"
    extension: str = "html"

    # We inspect the accept-header:
    if len(accept_header) > 0:
        try:
            content_type = decide_content_type(accept_header, supported_content_types)
            if content_type == "text/turtle":
                extension = "ttl"
            elif content_type == "text/html":
                extension = "html"
        except NoAgreeableContentTypeError as e:
            raise ContentTypeNotSupportedException(
                f"None of the content-types in {accept_header} are supported."
            ) from e
    else:
        pass  # pragma: no cover

    # for text/html, we inspect the accept-language-header:
    if content_type == "text/html":
        if len(accept_language_header) > 0:
            try:
                content_language = decide_language(
                    accept_language_header, supported_languages
                )
            except NoAgreeableLanguageError:
                content_language = "nb"
        else:
            pass

    return (content_type, content_language, extension)


async def valid_file_content(file_extension: str, file_content: Any) -> None:
    """Return True if file-content is valid."""
    if "ttl" == file_extension:
        try:
            Graph().parse(data=file_content)
        except (ParserError, SyntaxError, UnicodeDecodeError) as e:
            raise NotValidFileContentException(str(e)) from e


async def valid_file_extension(file_extension: str) -> bool:
    """Return True if valid file-extension."""
    if file_extension.lower() in ["ttl", "html", "png", "pdf"]:
        return True

    return False


async def valid_content_type(content_type: str) -> bool:
    """Return True if supported content-type."""
    if content_type.lower() in [
        "text/turtle",
        "text/html",
        "application/pdf",
        "image/png",
    ]:
        return True

    return False


async def rewrite_links(
    html_file: bytes, data_root: str, ontology_type: str, ontology: str
) -> bytes:
    """Rewrite relative links as absolute paths and return file."""
    _html_str = html_file.decode("utf-8")
    html_str = _html_str.replace("images", ontology + "/images")
    html_str = html_str.replace("files", ontology + "/files")
    return html_str.encode("utf-8")
