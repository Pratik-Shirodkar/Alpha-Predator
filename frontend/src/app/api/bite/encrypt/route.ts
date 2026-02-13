import { NextResponse } from 'next/server';

// Real BITE v2 Sandbox 2 on SKALE
const BITE_SANDBOX_RPC = 'https://base-sepolia-testnet.skalenodes.com/v1/bite-v2-sandbox';
const BITE_CHAIN_ID = 103698795;
const BITE_CONTRACT = '0xc4083B1E81ceb461Ccef3FDa8A9F24F0d764B6D8';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { intent, condition } = body;

        // Dynamically import dependencies
        const { BITE } = await import('@skalenetwork/bite');
        const { ethers } = await import('ethers');

        // Initialize provider and signer
        const provider = new ethers.JsonRpcProvider(BITE_SANDBOX_RPC);
        const privateKey = process.env.BITE_PRIVATE_KEY;

        if (!privateKey || privateKey.startsWith('0x0000')) {
            throw new Error('BITE_PRIVATE_KEY is not configured in .env.local');
        }

        const wallet = new ethers.Wallet(privateKey, provider);
        const bite = new BITE(BITE_SANDBOX_RPC);

        // 1. Get committee info
        let committeeInfo: any = null;
        try {
            committeeInfo = await bite.getCommitteesInfo();
        } catch (e: any) {
            console.warn('BITE: Could not fetch committee info:', e.message);
        }

        // 2. Encrypt the intent
        const intentJson = JSON.stringify(intent);
        const intentHex = '0x' + Buffer.from(intentJson).toString('hex');
        const encryptedMessage = await bite.encryptMessage(intentHex);

        console.log(`BITE: Encrypting intent on Chain ${BITE_CHAIN_ID}...`);

        // 3. Create and sign the BITE transaction
        // The BITE SDK's encryptTransaction creates a tx object with:
        // to: BITE_MAGIC_ADDRESS (0x23...), data: [epoch + encrypted blob]
        const txInternal = {
            to: BITE_CONTRACT,
            data: intentHex,
        };

        let encryptedTx: any = null;
        let txHash: string | null = null;
        let explorerUrl: string | null = null;

        try {
            // Encrypts the tx payload (to + data) into the BITE format
            encryptedTx = await bite.encryptTransaction(txInternal);
            console.log('BITE: Transaction encrypted successfully');

            // Send the encrypted transaction on-chain!
            // On SKALE, this is gasless (if sFUEL is provided by faucet/POW), but here we assume user has sFUEL
            const txResponse = await wallet.sendTransaction({
                to: encryptedTx.to,
                data: encryptedTx.data,
                // SKALE BITE often needs manual gas limit adjustment
                gasLimit: 6000000,
            });

            console.log(`BITE: Transaction sent! Hash: ${txResponse.hash}`);
            txHash = txResponse.hash;
            explorerUrl = `https://base-sepolia-testnet-explorer.skalenodes.com/tx/${txHash}`;

        } catch (e: any) {
            console.error('BITE: Transaction submission failed:', e.message);
            // Fallback: return encrypted data without on-chain execution for UI demo if funds missing
            if (e.message.includes('insufficient funds')) {
                console.warn('BITE: Insufficient sFUEL. Returning encrypted data only.');
            } else {
                throw e;
            }
        }

        // Build the BITE receipt
        const biteReceipt = {
            status: txHash ? 'on_chain' : 'encrypted_only',
            sdk: '@skalenetwork/bite',
            chain: 'BITE V2 Sandbox 2',
            chainId: BITE_CHAIN_ID,
            rpc: BITE_SANDBOX_RPC,
            biteContract: BITE_CONTRACT,
            bite_tx_id: txHash || `bite_${Date.now()}`,
            explorerUrl,
            encryptedMessage: encryptedMessage.substring(0, 200) + '...',
            encryptedMessageLength: encryptedMessage.length,
            committee: committeeInfo ? {
                epochId: committeeInfo[0]?.epochId,
                publicKeyPreview: committeeInfo[0]?.commonBLSPublicKey?.substring(0, 40) + '...',
                rotationActive: committeeInfo.length > 1,
            } : null,
            condition,
            timestamp: new Date().toISOString(),
        };

        return NextResponse.json(biteReceipt);

    } catch (error: any) {
        console.error('BITE API Error:', error);
        return NextResponse.json({
            status: 'error',
            message: error.message,
            stack: error.stack?.split('\n').slice(0, 3).join('\n'),
        }, { status: 500 });
    }
}

// GET: Health check + committee info
export async function GET() {
    try {
        const { BITE } = await import('@skalenetwork/bite');
        const bite = new BITE(BITE_SANDBOX_RPC);
        const committeeInfo = await bite.getCommitteesInfo();

        return NextResponse.json({
            status: 'connected',
            chain: 'BITE V2 Sandbox 2',
            chainId: BITE_CHAIN_ID,
            rpc: BITE_SANDBOX_RPC,
            biteContract: BITE_CONTRACT,
            committee: {
                epochId: committeeInfo[0]?.epochId,
                publicKeyPreview: committeeInfo[0]?.commonBLSPublicKey?.substring(0, 40) + '...',
                rotationActive: committeeInfo.length > 1,
            },
        });
    } catch (error: any) {
        return NextResponse.json({
            status: 'error',
            message: error.message,
        }, { status: 500 });
    }
}
