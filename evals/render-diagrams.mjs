// Optional visual acceptance harness; core skill/helper stays Python-only.
// Needs Playwright and an installed Chrome (or WIKI_BROWSER_CHANNEL).
import { createRequire } from 'node:module'
import { readFileSync, realpathSync, mkdtempSync, mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve, relative, isAbsolute, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { tmpdir } from 'node:os'
import { createHash } from 'node:crypto'

const require = createRequire(import.meta.url)
const args = process.argv.slice(2)
const option = (name, fallback) => args.includes(name) ? args[args.indexOf(name) + 1] : fallback
const root = realpathSync(resolve(option('--root', join(dirname(fileURLToPath(import.meta.url)), 'fixture-project'))))
const requestedOutput = option('--output', null)
const output = requestedOutput ? resolve(requestedOutput) : mkdtempSync(join(tmpdir(), 'project-wiki-diagrams-'))
const url = process.env.WIKI_MERMAID_URL ?? 'https://cdn.jsdelivr.net/npm/mermaid@11.17.2/dist/mermaid.min.js'

let browser
try {
  const { chromium } = require(process.env.WIKI_PLAYWRIGHT_MODULE ?? 'playwright')
  const manifest = JSON.parse(readFileSync(join(root, 'docs/wiki/routes.json'), 'utf8'))
  const files = [...new Set(manifest.routes.flatMap(row => (row.diagrams ?? []).map(item => item.path.split('#')[0])))]
  const entries = []
  for (const file of files) {
    const path = realpathSync(resolve(root, file))
    const inside = relative(root, path)
    if (inside.startsWith('..') || isAbsolute(inside)) throw new Error('Diagram path escapes fixture root')
    const markdown = readFileSync(path, 'utf8').replace(/\r\n/g, '\n')
    for (const match of markdown.matchAll(/```mermaid\n([\s\S]*?)```/g)) entries.push({ file, code: match[1] })
  }
  if (!entries.length) throw new Error('No referenced Mermaid diagrams found')
  browser = await chromium.launch({ channel: process.env.WIKI_BROWSER_CHANNEL ?? 'chrome', headless: true })
  const page = await browser.newPage({ viewport: { width: 1500, height: 1100 } })
  let resolvedVersion = 'not returned by CDN'
  page.on('response', response => {
    if (response.url() === url) resolvedVersion = response.headers()['x-jsd-version'] ?? resolvedVersion
  })
  await page.setContent('<html><meta charset="utf-8"><body style="background:white;font-family:Arial;padding:20px"></body></html>')
  await page.addScriptTag({ url })
  const results = await page.evaluate(async entries => {
    window.mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'default' })
    const results = []
    for (let i = 0; i < entries.length; i++) {
      try {
        await window.mermaid.parse(entries[i].code)
        const { svg } = await window.mermaid.render('wikiView' + i, entries[i].code)
        const box = document.createElement('section')
        box.style.cssText = 'padding:16px;margin-bottom:24px;border:1px solid #ddd'
        box.innerHTML = '<h2>View ' + (i + 1) + '</h2>' + svg
        box.querySelector('svg').style.maxWidth = '100%'
        document.body.appendChild(box)
        results.push({ diagram: i + 1, file: entries[i].file, parsed: true, rendered: true })
      } catch (error) { results.push({ diagram: i + 1, file: entries[i].file, error: String(error) }) }
    }
    return results
  }, entries)
  mkdirSync(output, { recursive: true })
  let rendered = 0
  for (let i = 0; i < results.length; i++) {
    results[i].source_sha256 = createHash('sha256').update(entries[i].code).digest('hex')
    if (!results[i].error) {
      results[i].screenshot = 'diagram-' + i + '.png'
      await page.locator('section').nth(rendered++).screenshot({ path: join(output, results[i].screenshot) })
    }
  }
  const report = { renderer: 'Mermaid 11 via isolated headless Chrome', requested_url: url,
    resolved_mermaid_version: resolvedVersion, browser_version: browser.version(), diagrams: results,
    rendered, total: results.length, scope: 'Syntax/render only. Readability and code semantics need separate review.' }
  writeFileSync(join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n')
  console.log(JSON.stringify({ rendered, total: results.length, output, resolved_mermaid_version: resolvedVersion }))
  if (rendered !== results.length) process.exitCode = 1
} catch (error) {
  console.error(String(error) + '\nInstall Playwright/Chrome or set WIKI_PLAYWRIGHT_MODULE and WIKI_BROWSER_CHANNEL; no installation is performed by this script.')
  process.exitCode = 1
} finally { await browser?.close() }
