import { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
import { generateSigner, keypairIdentity, percentAmount } from "@metaplex-foundation/umi";
import { createNft, mplTokenMetadata } from "@metaplex-foundation/mpl-token-metadata";

function loadSecretKey(): Uint8Array {
  const raw = process.env.SOLANA_PRIVATE_KEY_JSON;
  if (!raw) throw new Error("SOLANA_PRIVATE_KEY_JSON is not set");
  return Uint8Array.from(JSON.parse(raw) as number[]);
}

export async function mintNft(params: { name: string; uri: string; }): Promise<{ mintAddress: string }> {
  const rpc = process.env.SOLANA_RPC_URL || "https://api.devnet.solana.com";
  const umi = createUmi(rpc).use(mplTokenMetadata());
  const signer = umi.eddsa.createKeypairFromSecretKey(loadSecretKey());
  umi.use(keypairIdentity(signer));
  const mint = generateSigner(umi);

  await createNft(umi, {
    mint,
    name: params.name.slice(0, 32),
    uri: params.uri,
    sellerFeeBasisPoints: percentAmount(0)
  }).sendAndConfirm(umi);

  return { mintAddress: mint.publicKey.toString() };
}
