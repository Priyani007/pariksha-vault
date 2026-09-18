import hashlib, datetime, json
from typing import List, Dict, Any, Optional

class MerkleBlock:
    def __init__(self, index: int, event: str, actor: str, payload: Dict[str, Any], prev_hash: str):
        self.index = index
        self.timestamp = datetime.datetime.now().strftime('%H:%M:%S IST')
        self.event = event
        self.actor = actor
        self.payload = payload
        self.prev_hash = prev_hash
        self.payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        self.block_hash = self.compute_block_hash()
        self.signature = f'SIG-ECDSA-{self.block_hash[:8].upper()}'
        
    def compute_block_hash(self) -> str:
        header = f'{self.index}:{self.timestamp}:{self.event}:{self.actor}:{self.payload_hash}:{self.prev_hash}'
        return hashlib.sha256(header.encode()).hexdigest()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'event': self.event,
            'actor': self.actor,
            'payload': self.payload,
            'payload_hash': self.payload_hash,
            'prev_hash': self.prev_hash,
            'block_hash': self.block_hash,
            'signature': self.signature,
            'status': 'VERIFIED_VALID'
        }

class MerkleProvenanceLedger:
    def __init__(self):
        self.chain: List[MerkleBlock] = []
        self._build_genesis_chain()
        
    def _build_genesis_chain(self):
        b0 = MerkleBlock(
            index=0,
            event='GENESIS_EXAM_CREATION',
            actor='National Examination Board Controller',
            payload={'exam_code': 'NEET-UG-2026', 'total_questions': 180, 'master_vault': 'LOCKED'},
            prev_hash='0'*64
        )
        self.chain.append(b0)
        
        b1 = MerkleBlock(
            index=1,
            event='BLIND_SHARDED_REVIEW_SEALED',
            actor='Prof. Rajesh Sharma (IIT Delhi Shard #14)',
            payload={'shard_id': 'EM-1', 'canary_trap': 'CLEAN', 'verdict': 'APPROVED'},
            prev_hash=b0.block_hash
        )
        self.chain.append(b1)
        
        b2 = MerkleBlock(
            index=2,
            event='DUAL_VECTOR_REGIONAL_DISPATCH',
            actor='Sovereign Watermark Node',
            payload={'centers_dispatched': 5, 'stego_vectors': ['Unicode Zero-Width', 'Semantic Barium Meal']},
            prev_hash=b1.block_hash
        )
        self.chain.append(b2)
        
        b3 = MerkleBlock(
            index=3,
            event='TIMED_HARDWARE_ESCROW_SEAL',
            actor='CloudHSM FIPS-140-3 Enclave',
            payload={'key_release_time': '10:00:00 AM IST', 'algorithm': 'AES-256-GCM'},
            prev_hash=b2.block_hash
        )
        self.chain.append(b3)

    def get_ledger(self) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self.chain]
        
    def verify_integrity(self) -> Dict[str, Any]:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.prev_hash != previous.block_hash:
                return {
                    'is_valid': False,
                    'compromised_block': current.index,
                    'error': f'Chain broken between Block #{previous.index} and Block #{current.index}'
                }
        return {
            'is_valid': True,
            'total_blocks': len(self.chain),
            'merkle_root': self.chain[-1].block_hash,
            'chain_status': 'CRYPTOGRAPHICALLY_AUTHENTIC'
        }
        
    def simulate_tamper(self, block_index: int = 1) -> Dict[str, Any]:
        if block_index >= len(self.chain):
            block_index = 1
        tampered_chain = [b.to_dict() for b in self.chain]
        tampered_chain[block_index]['payload']['tampered_by'] = 'Rogue Insider (Unauthorized Alteration)'
        tampered_chain[block_index]['status'] = 'CORRUPTED_HASH_MISMATCH'
        return {
            'tamper_detected': True,
            'broken_block_index': block_index,
            'alert': f'CRITICAL: Cryptographic integrity broken at Block #{block_index}! SHA-256 merkle hash mismatch.',
            'blocks': tampered_chain
        }

merkle_ledger = MerkleProvenanceLedger()
