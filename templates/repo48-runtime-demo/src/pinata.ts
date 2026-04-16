import fs from "node:fs";
import path from "node:path";

const PINATA_BASE = "https://api.pinata.cloud";

export async function uploadFileToPinata(filePath: string): Promise<string> {
  const jwt = process.env.PINATA_JWT;
  if (!jwt) throw new Error("PINATA_JWT is not set");
  const fileName = path.basename(filePath);
  const form = new FormData();
  form.append("file", new Blob([fs.readFileSync(filePath)]), fileName);

  const res = await fetch(`${PINATA_BASE}/pinning/pinFileToIPFS`, {
    method: "POST",
    headers: { Authorization: `Bearer ${jwt}` },
    body: form
  });

  if (!res.ok) throw new Error(`Pinata file upload failed: ${res.status} ${await res.text()}`);
  const data = (await res.json()) as { IpfsHash: string };
  return `ipfs://${data.IpfsHash}`;
}

export async function uploadJSONToPinata(payload: object, name: string): Promise<string> {
  const jwt = process.env.PINATA_JWT;
  if (!jwt) throw new Error("PINATA_JWT is not set");

  const res = await fetch(`${PINATA_BASE}/pinning/pinJSONToIPFS`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${jwt}`
    },
    body: JSON.stringify({ pinataMetadata: { name }, pinataContent: payload })
  });

  if (!res.ok) throw new Error(`Pinata JSON upload failed: ${res.status} ${await res.text()}`);
  const data = (await res.json()) as { IpfsHash: string };
  return `ipfs://${data.IpfsHash}`;
}
