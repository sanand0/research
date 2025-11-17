// Minimal render helpers with lit-html-like API
export const html = (strings, ...values) =>
  strings.reduce((acc, str, idx) => `${acc}${str}${idx < values.length ? values[idx] : ''}`, '')

export const render = (template, container) => {
  container.innerHTML = template
}
