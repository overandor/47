import type { Entry } from "./schema.js";

export async function enrichWithLLM(entry: Entry): Promise<{ description: string; attributes: Array<{ trait_type: string; value: string }>; }> {
  const enabled = process.env.LLM_ENABLED === "true";
  if (!enabled) {
    return {
      description: `${entry.text} | Languages: ${entry.languages.join(", ")} | Mode: ${entry.mix_mode}`,
      attributes: [
        { trait_type: "Style", value: entry.style },
        { trait_type: "Mix Mode", value: entry.mix_mode },
        { trait_type: "Languages", value: entry.languages.join(", ") }
      ]
    };
  }

  return {
    description: `${entry.text} | LLM-enriched artifact metadata`,
    attributes: [
      { trait_type: "Style", value: entry.style },
      { trait_type: "Mix Mode", value: entry.mix_mode },
      { trait_type: "Languages", value: entry.languages.join(", ") },
      { trait_type: "Enriched", value: "true" }
    ]
  };
}
