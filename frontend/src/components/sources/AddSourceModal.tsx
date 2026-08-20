'use client';

import React, { useState } from 'react';
import { UploadCloud, Youtube, Globe, X, Loader2, FileCheck } from 'lucide-react';
import { uploadDocument, ingestUrl } from '@/lib/api';
import { DocumentItem } from '@/lib/types';

interface AddSourceModalProps {
  sessionId: string;
  isOpen: boolean;
  onClose: () => void;
  onSourceAdded: (doc: DocumentItem) => void;
}

export const AddSourceModal: React.FC<AddSourceModalProps> = ({
  sessionId,
  isOpen,
  onClose,
  onSourceAdded,
}) => {
  const [activeTab, setActiveTab] = useState<'file' | 'youtube' | 'web'>('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [urlInput, setUrlInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setIsLoading(true);
    setError(null);
    try {
      const doc = await uploadDocument(sessionId, selectedFile);
      onSourceAdded(doc);
      setSelectedFile(null);
      onClose();
    } catch (err: any) {
      setError(err.message || 'File upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const doc = await ingestUrl(sessionId, urlInput.trim());
      onSourceAdded(doc);
      setUrlInput('');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to ingest URL');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          <h3 className="text-base font-semibold text-slate-100">Add Knowledge Source</h3>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Buttons */}
        <div className="grid grid-cols-3 p-1.5 m-4 rounded-xl bg-slate-950 border border-slate-800 gap-1 text-xs font-medium">
          <button
            onClick={() => { setActiveTab('file'); setError(null); }}
            className={`py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all ${
              activeTab === 'file' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <UploadCloud className="w-3.5 h-3.5" />
            File Upload
          </button>
          <button
            onClick={() => { setActiveTab('youtube'); setError(null); }}
            className={`py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all ${
              activeTab === 'youtube' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Youtube className="w-3.5 h-3.5 text-red-400" />
            YouTube
          </button>
          <button
            onClick={() => { setActiveTab('web'); setError(null); }}
            className={`py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all ${
              activeTab === 'web' ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Globe className="w-3.5 h-3.5 text-emerald-400" />
            Web URL
          </button>
        </div>

        {error && (
          <div className="mx-4 mb-3 p-3 rounded-lg bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs">
            {error}
          </div>
        )}

        {/* Form Body */}
        <div className="p-4 pt-0">
          {activeTab === 'file' && (
            <form onSubmit={handleFileUpload} className="space-y-4">
              <label
                htmlFor="file-upload"
                className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl cursor-pointer bg-slate-950/50 hover:bg-slate-950 transition-colors"
              >
                <UploadCloud className="w-8 h-8 text-blue-400 mb-2" />
                <span className="text-xs font-semibold text-slate-200">
                  {selectedFile ? selectedFile.name : 'Click to select or drag document'}
                </span>
                <span className="text-[11px] text-slate-500 mt-1">
                  Supports PDF, PPTX, and DOCX (up to 50MB)
                </span>
                <input
                  id="file-upload"
                  type="file"
                  accept=".pdf,.pptx,.ppt,.docx,.doc"
                  className="hidden"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                />
              </label>

              {selectedFile && (
                <div className="flex items-center gap-2 p-2.5 rounded-lg bg-blue-950/40 border border-blue-800/50 text-blue-300 text-xs">
                  <FileCheck className="w-4 h-4" />
                  <span className="truncate">{selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                </div>
              )}

              <button
                type="submit"
                disabled={!selectedFile || isLoading}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 font-medium text-xs text-white flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-600/20"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Ingest Document'}
              </button>
            </form>
          )}

          {activeTab === 'youtube' && (
            <form onSubmit={handleUrlSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  YouTube Video Link
                </label>
                <input
                  type="url"
                  placeholder="https://www.youtube.com/watch?v=..."
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-blue-500 text-xs text-slate-100 outline-none"
                  required
                />
                <p className="text-[11px] text-slate-500 mt-1.5">
                  Subtitles and timestamps will automatically be extracted and indexed for precise video citation.
                </p>
              </div>

              <button
                type="submit"
                disabled={!urlInput.trim() || isLoading}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 font-medium text-xs text-white flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-600/20"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Transcribe & Ingest Video'}
              </button>
            </form>
          )}

          {activeTab === 'web' && (
            <form onSubmit={handleUrlSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Webpage / Article URL
                </label>
                <input
                  type="url"
                  placeholder="https://example.com/article..."
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-blue-500 text-xs text-slate-100 outline-none"
                  required
                />
                <p className="text-[11px] text-slate-500 mt-1.5">
                  Article body text and headings will be scraped, chunked, and vectorized.
                </p>
              </div>

              <button
                type="submit"
                disabled={!urlInput.trim() || isLoading}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 font-medium text-xs text-white flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-600/20"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Scrape & Index Webpage'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
