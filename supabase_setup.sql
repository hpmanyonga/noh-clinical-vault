-- ============================================================================
-- NOH Clinical Vault — Supabase Setup SQL
-- Run this in Supabase SQL Editor (Dashboard > SQL Editor > New Query)
-- ============================================================================

-- 1. Create the storage bucket (private — files served via signed URLs only)
-- NOTE: Create the bucket via Dashboard > Storage > New Bucket instead:
--   Name: clinical-documents
--   Public: OFF (private)
--   File size limit: 50MB
--   Allowed MIME types: application/pdf

-- 2. Storage RLS — authenticated users can download clinical documents
CREATE POLICY "Authenticated users can download clinical documents"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'clinical-documents'
    AND auth.role() = 'authenticated'
);

-- 3. Audit trail table — logs every document download
CREATE TABLE IF NOT EXISTS vault_downloads (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_email  text NOT NULL,
    document_code text NOT NULL,
    document_title text,
    downloaded_at timestamptz NOT NULL DEFAULT now()
);

-- RLS on vault_downloads
ALTER TABLE vault_downloads ENABLE ROW LEVEL SECURITY;

-- Authenticated users can insert their own download records
CREATE POLICY "Users can log their own downloads"
ON vault_downloads FOR INSERT
WITH CHECK (auth.role() = 'authenticated');

-- Authenticated users can read all download records (for admin/audit)
CREATE POLICY "Authenticated users can view download logs"
ON vault_downloads FOR SELECT
USING (auth.role() = 'authenticated');

-- 4. Index for audit queries
CREATE INDEX idx_vault_downloads_code ON vault_downloads (document_code);
CREATE INDEX idx_vault_downloads_user ON vault_downloads (user_email);
CREATE INDEX idx_vault_downloads_date ON vault_downloads (downloaded_at DESC);

-- ============================================================================
-- FOLDER STRUCTURE in clinical-documents bucket:
--   manual/NOH_Clinical_Operations_Manual_V1.0.pdf
--   sops/SOP-001_Controlled_Drugs_Management.pdf
--   sops/SOP-002_Major_Haemorrhage_Protocol.pdf
--   ... (all 11 SOPs)
--   qrcs/QRC-001_PPH_Algorithm.pdf
--   qrcs/QRC-002_Eclampsia_Algorithm.pdf
--   ... (all 10 QRCs)
-- ============================================================================
