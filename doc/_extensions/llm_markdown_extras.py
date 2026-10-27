"""Markdown translator handlers for the sphinx-llm Markdown build.

The ``sphinx_llm.txt`` extension renders a Markdown version of every
documentation page next to the HTML output. Its translator only knows
the core Sphinx/docutils nodes; any other node is dropped with an
"unknown node type" warning. This extension teaches it the extra nodes
used by the eXSpy documentation so that no content is lost and the
build is warning free:

* ``PassthroughTextElement`` (sphinx-design): transparent wrapper used
  around card titles and card links.
* ``raw`` (sphinx-design icons, etc.): only render content written for
  Markdown; drop HTML-only passthrough content such as the inline SVGs
  emitted by the ``octicon`` role.
* ``caption`` (docutils): figure captions render as italic paragraphs.
* ``classifier`` (docutils): definition-list classifiers render as
  italic inline text.
* ``imgsgnode`` (sphinx-gallery): responsive images render as Markdown
  images.
"""

from docutils import nodes
from sphinx_llm.markdown_builder import SphinxLlmMarkdownTranslator
from sphinx_markdown_builder.contexts import SubContextParams, WrappedContext
from sphinx_markdown_builder.translator import pushing_context


class LlmMarkdownExtrasTranslator(SphinxLlmMarkdownTranslator):
    """Markdown translator with handlers for the nodes sphinx-llm drops."""

    # -- sphinx-design ---------------------------------------------------

    def visit_PassthroughTextElement(self, node):
        """Sphinx-design transparent wrapper: render the children."""

    def visit_raw(self, node):
        """Render ``raw`` content only when it was written for Markdown.

        Drops HTML-only passthrough content, such as the inline SVGs
        emitted by the sphinx-design ``octicon`` role, which would
        otherwise be dumped into the Markdown output verbatim.
        """
        if "markdown" in (node.get("format") or "").split():
            return
        raise nodes.SkipNode

    # -- docutils --------------------------------------------------------

    @pushing_context
    def visit_caption(self, node):
        """Render figure captions as an italic paragraph."""
        self._push_context(WrappedContext("*", "*", params=SubContextParams(2, 1)))

    @pushing_context
    def visit_classifier(self, node):
        """Render definition-list classifiers as italic inline text."""
        self._push_context(WrappedContext(" *", "*", params=SubContextParams(0, 0)))

    # -- sphinx-gallery --------------------------------------------------

    def visit_imgsgnode(self, node):
        """Render sphinx-gallery responsive images as Markdown images."""
        self.visit_image(node)


def setup(app):
    app.set_translator("llms-markdown", LlmMarkdownExtrasTranslator, override=True)
    return {
        "version": "1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
