/**
 * ConstructGuard AI — API Client
 * All API calls to the FastAPI backend.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60s — model inference can take time
});

/**
 * Analyze a construction site image.
 * @param {File} imageFile - Image file to analyze
 * @param {string} siteId - Construction site identifier
 * @returns {Promise} Analysis results
 */
export async function analyzeImage(imageFile, siteId = 'site_001') {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('site_id', siteId);

  const response = await api.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

/**
 * Analyze a construction site video.
 * @param {File} videoFile - Video file to analyze
 * @param {string} siteId - Construction site identifier
 * @param {number} frameInterval - Seconds between frames to extract
 * @returns {Promise} Video analysis results
 */
export async function analyzeVideo(videoFile, siteId = 'site_001', frameInterval = 2.0) {
  const formData = new FormData();
  formData.append('file', videoFile);
  formData.append('site_id', siteId);
  formData.append('frame_interval', frameInterval.toString());

  const response = await api.post('/analyze-video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000, // 5 minutes — video takes longer
  });
  return response.data;
}

/**
 * Get violation history for a site.
 */
export async function getHistory(siteId, limit = 20) {
  const response = await api.get(`/history/${siteId}`, { params: { limit } });
  return response.data;
}

/**
 * Get all known sites.
 */
export async function getSites() {
  const response = await api.get('/sites');
  return response.data;
}

/**
 * Health check.
 */
export async function healthCheck() {
  const response = await api.get('/health');
  return response.data;
}

/**
 * Get full URL for static files served by backend.
 */
export function getStaticUrl(path) {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  return `${API_BASE}${path}`;
}

export default api;
