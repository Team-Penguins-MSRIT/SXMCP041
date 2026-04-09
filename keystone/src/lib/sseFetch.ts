/** Parse Server-Sent Events from fetch (supports Authorization; EventSource does not). */
export async function consumeSseJson(
  url: string,
  init: RequestInit | undefined,
  onMessage: (data: unknown) => void,
): Promise<void> {
  const res = await fetch(url, init)
  if (!res.ok) {
    const t = await res.text()
    throw new Error(t || `HTTP ${res.status}`)
  }
  const reader = res.body?.getReader()
  if (!reader) throw new Error('No response body')
  const dec = new TextDecoder()
  let buf = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buf += dec.decode(value, { stream: true })
    for (;;) {
      const sep = buf.indexOf('\n\n')
      if (sep === -1) break
      const block = buf.slice(0, sep).trim()
      buf = buf.slice(sep + 2)
      if (block.startsWith('data: ')) {
        const raw = block.slice(6)
        try {
          onMessage(JSON.parse(raw))
        } catch {
          /* ignore */
        }
      }
    }
  }
}
