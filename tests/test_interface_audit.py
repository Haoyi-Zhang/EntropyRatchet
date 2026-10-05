"""Negative controls for text/ledger drift, not a theorem prover."""
import unittest
from audit_interface import audit_texts

CORE='All registers are finite dimensional. Fixed marginal.\n'
TEX=(r'\begin{equation}\label{eq:intro-extractor}2\eta\end{equation}'
     r'\begin{equation}\label{eq:quantum-lhl}2\eta\end{equation}'
     r'\begin{equation}\label{eq:delta-j}2\eta\end{equation}'
     +CORE+'Let $\\mathsf I_j$ replace')
LEDGER='claim_id,manuscript_location\nC1,eq:quantum-lhl\n'

class InterfaceAuditTests(unittest.TestCase):
    def test_consistent_fixture(self):
        self.assertTrue(audit_texts(TEX,LEDGER,CORE)['passed'])
    def test_single_eta_drift_rejected(self):
        with self.assertRaises(ValueError):audit_texts(TEX.replace('2\\eta','\\eta',1),LEDGER,CORE)
    def test_nonexistent_evidence_target_rejected(self):
        with self.assertRaises(ValueError):audit_texts(TEX,LEDGER+'C2,cor:nonexistent\n',CORE)
    def test_stale_proof_excerpt_rejected(self):
        with self.assertRaises(ValueError):audit_texts(TEX,LEDGER,'old unrelated note')

if __name__=='__main__':unittest.main()
