// Navigation-only TypeScript fixture; no external request or runtime adapter.
export interface ExternalSource {
  suggestTopics(tag: string): Promise<string[] | null>
  counts?(topic: string): Promise<number | null>
}

export function providerCapabilities(source: ExternalSource): string[] {
  return source.counts ? ['suggest', 'counts'] : ['suggest']
}

export function nodeFeatures(source: ExternalSource): string[] {
  return providerCapabilities(source)
}
