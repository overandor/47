# Unchained Runtime Demo (repo 48 template)

Runtime plane template for minting language-mix entries as Solana NFTs.

## Flow
1. repo 47 validates and dispatches new `data/entries` batch.
2. repo 48 runtime ingests entry JSON + media.
3. Runtime optionally enriches metadata with LLM.
4. Runtime uploads media/metadata to Pinata.
5. Runtime mints NFT on Solana devnet.
6. Runtime appends `registry/minted.json` and pushes update.

## Required secrets
- `SOLANA_RPC_URL`
- `SOLANA_PRIVATE_KEY_JSON`
- `PINATA_JWT`
- `LLM_ENABLED`
- `LLM_API_KEY`

Never commit secrets or paste credentials into code/workflow files.
