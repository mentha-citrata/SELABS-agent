import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  breaks: true
})

markdown.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const href = token.attrGet('href') || ''

  if (/^https?:\/\//i.test(href)) {
    token.attrSet('target', '_blank')
    token.attrSet('rel', 'noreferrer noopener')
  }

  return self.renderToken(tokens, idx, options)
}

export function renderMarkdown(source = '') {
  const html = markdown.render(source)

  return DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true },
    ADD_ATTR: ['target', 'rel']
  })
}
