// @ts-check
import Fuse from './vendor/fuse.js'
import { html, render } from './vendor/lit-html.js'

/**
 * @typedef {{ text: string, page: number, span: HTMLElement }} TextNode
 * @typedef {{ text: string, page: number, span: HTMLElement, score: number }} Match
 */

const textNodes = /** @type {TextNode[]} */ ([])
let pdfDoc
let pdfRoot
let matchesRoot
let searchInput
let loadingBanner

/**
 * Rank fuzzy matches from text nodes.
 * @param {{text: string, page: number}[]} items
 * @param {string} query
 * @param {number} limit
 * @returns {Match[]}
 */
export function rankMatches(items, query, limit = 5) {
  const trimmed = query.trim()
  if (!trimmed) return []
  const fuse = new Fuse(items, { keys: ['text'], includeScore: true, threshold: 0.4 })
  const results = fuse.search(trimmed, { limit })
  results.sort(
    (a, b) => (a.score - b.score) || ((a.refIndex ?? Number.MAX_SAFE_INTEGER) - (b.refIndex ?? Number.MAX_SAFE_INTEGER)),
  )
  return results.map((result) => ({ ...result.item, score: result.score ?? 0, span: /** @type {any} */ (result.item).span }))
}

const highlightClass = 'highlight'

function clearHighlights() {
  document.querySelectorAll(`.${highlightClass}`).forEach((el) => el.classList.remove(highlightClass))
}

function showMatches(matches) {
  const listMarkup = html`<ul class="list-group small">
    ${matches
      .map(
        (m, idx) =>
          `<li class="list-group-item list-group-item-action ${idx === 0 ? 'active' : ''}" role="button" data-match="${idx}">
            <div class="fw-bold">Page ${m.page}</div>
            <div>${m.text}</div>
          </li>`,
      )
      .join('')}
  </ul>`
  render(listMarkup, matchesRoot)
  matches.forEach((match, idx) => {
    const row = matchesRoot.querySelector(`[data-match="${idx}"]`)
    if (row) row.addEventListener('click', () => focusMatch(match))
  })
}

function focusMatch(match) {
  clearHighlights()
  match.span.classList.add(highlightClass)
  match.span.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

function updateUrl(query) {
  const url = new URL(window.location.href)
  if (query) {
    url.searchParams.set('q', query)
  } else {
    url.searchParams.delete('q')
  }
  window.history.replaceState({}, '', url)
}

function runSearch(query) {
  const matches = rankMatches(textNodes, query, 10)
  showMatches(matches)
  if (matches[0]) focusMatch(matches[0])
}

async function renderPage(pageNumber) {
  const page = await pdfDoc.getPage(pageNumber)
  const viewport = page.getViewport({ scale: 1.2 })
  const container = document.createElement('div')
  container.className = 'pdf-container border bg-white shadow-sm position-relative'

  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')
  canvas.width = viewport.width
  canvas.height = viewport.height
  container.appendChild(canvas)

  const textLayer = document.createElement('div')
  textLayer.className = 'textLayer position-absolute top-0 start-0'
  textLayer.style.height = `${viewport.height}px`
  textLayer.style.width = `${viewport.width}px`
  container.appendChild(textLayer)

  pdfRoot.appendChild(container)
  await page.render({ canvasContext: context, viewport }).promise
  const textContent = await page.getTextContent()
  await pdfjsLib.renderTextLayer({ textContent, container: textLayer, viewport }).promise

  const spans = Array.from(textLayer.querySelectorAll('span'))
  textContent.items.forEach((item, idx) => {
    const span = spans[idx]
    if (!span) return
    textNodes.push({ text: item.str, page: pageNumber, span })
  })
}

async function loadPdf(url) {
  pdfRoot = document.getElementById('pdf-root')
  matchesRoot = document.getElementById('matches')
  searchInput = document.getElementById('search-input')
  loadingBanner = document.getElementById('loading-banner')
  if (!pdfRoot || !matchesRoot || !searchInput || !loadingBanner) return
  textNodes.length = 0

  const initialQuery = new URL(window.location.href).searchParams.get('q') ?? ''
  searchInput.value = initialQuery

  const loadingTask = pdfjsLib.getDocument(url)
  pdfDoc = await loadingTask.promise
  for (let i = 1; i <= pdfDoc.numPages; i += 1) {
    // eslint-disable-next-line no-await-in-loop
    await renderPage(i)
  }
  loadingBanner.remove()
  runSearch(initialQuery)

  searchInput.addEventListener('input', (event) => {
    const query = /** @type {HTMLInputElement} */ (event.target).value
    updateUrl(query)
    runSearch(query)
  })
}

if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => {
    loadPdf(window.PDF_FILE_URL)
  })
}

export const __test = { clearHighlights, focusMatch, runSearch, loadPdf }
