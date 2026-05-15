import { z } from "zod";

export const EntrySchema = z.object({
  slug: z.string().min(1),
  title: z.string().min(1),
  text: z.string().min(1),
  languages: z.array(z.string()).min(1),
  mix_mode: z.string().min(1),
  style: z.string().min(1),
  media_file: z.string().min(1),
  external_ref: z.string().min(1)
});

export type Entry = z.infer<typeof EntrySchema>;

export type MintRegistryRecord = {
  slug: string;
  title: string;
  mintAddress: string;
  metadataUri: string;
  imageUri: string;
  createdAt: string;
  commitSha?: string;
};
