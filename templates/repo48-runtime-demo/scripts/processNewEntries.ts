import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import "dotenv/config";
import { EntrySchema, type Entry, type MintRegistryRecord } from "../src/schema.js";
import { enrichWithLLM } from "../src/llm.js";
import { uploadFileToPinata, uploadJSONToPinata } from "../src/pinata.js";
import { mintNft } from "../src/solana.js";

const ROOT = process.cwd();
const ENTRIES_DIR = path.join(ROOT, "data", "entries");
const REGISTRY_PATH = path.join(ROOT, "registry", "minted.json");

function walkJsonFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  const out: string[] = [];
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, item.name);
    if (item.isDirectory()) out.push(...walkJsonFiles(full));
    if (item.isFile() && item.name.endsWith(".json")) out.push(full);
  }
  return out.sort();
}

function loadRegistry(): MintRegistryRecord[] {
  if (!fs.existsSync(REGISTRY_PATH)) return [];
  return JSON.parse(fs.readFileSync(REGISTRY_PATH, "utf8"));
}

function saveRegistry(records: MintRegistryRecord[]) {
  fs.mkdirSync(path.dirname(REGISTRY_PATH), { recursive: true });
  fs.writeFileSync(REGISTRY_PATH, JSON.stringify(records, null, 2));
}

function isMinted(slug: string, registry: MintRegistryRecord[]): boolean {
  return registry.some((r) => r.slug === slug);
}

async function processEntry(entry: Entry, registry: MintRegistryRecord[]) {
  if (isMinted(entry.slug, registry)) return;

  const mediaPath = path.join(ROOT, entry.media_file);
  if (!fs.existsSync(mediaPath)) throw new Error(`Missing media file for ${entry.slug}: ${mediaPath}`);

  const imageUri = await uploadFileToPinata(mediaPath);
  const llm = await enrichWithLLM(entry);
  const metadataUri = await uploadJSONToPinata({
    name: entry.title,
    symbol: "UNCHAIN",
    description: llm.description,
    image: imageUri,
    external_url: entry.external_ref,
    attributes: llm.attributes
  }, `${entry.slug}.json`);

  const minted = await mintNft({ name: entry.title, uri: metadataUri });

  registry.push({
    slug: entry.slug,
    title: entry.title,
    mintAddress: minted.mintAddress,
    metadataUri,
    imageUri,
    createdAt: new Date().toISOString(),
    commitSha: process.env.GITHUB_SHA
  });

  saveRegistry(registry);
}

async function main() {
  const registry = loadRegistry();
  for (const file of walkJsonFiles(ENTRIES_DIR)) {
    const raw = JSON.parse(fs.readFileSync(file, "utf8"));
    const entry = EntrySchema.parse(raw);
    await processEntry(entry, registry);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
