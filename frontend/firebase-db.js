import { db } from './firebase-config.js';
import {
  collection, doc, addDoc, setDoc, getDoc, getDocs, deleteDoc,
  query, orderBy, limit
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

/* ── Helper: current user email as doc ID ───────────────── */
function userId() {
  try { return JSON.parse(localStorage.getItem('currentUser'))?.email || 'guest'; }
  catch { return 'guest'; }
}

/* ── Get Monday of current week (YYYY-MM-DD) ─────────────── */
function weekKey() {
  const d = new Date();
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  const mon = new Date(d.setDate(diff));
  return mon.toISOString().slice(0, 10);
}

/* ══════════════════════════════════════════════════════════
   READING SESSIONS (existing)
══════════════════════════════════════════════════════════ */
async function saveReadingSession(session) {
  try {
    await addDoc(collection(db, 'readingSessions'), {
      ...session,
      userId: userId(),
      completedAt: new Date().toISOString()
    });
  } catch (e) { console.warn('Firebase save session failed:', e.message); }
}

async function getReadingSessions() {
  try {
    const q = query(collection(db, 'readingSessions'), orderBy('completedAt', 'desc'), limit(50));
    const snap = await getDocs(q);
    // Return all sessions — parent sees all family reading activity
    return snap.docs.map(d => d.data());
  } catch (e) { console.warn('Firebase read sessions failed:', e.message); return []; }
}

async function getStats() {
  const sessions = await getReadingSessions();
  const totalStories   = sessions.length;
  const totalTimeMins  = Math.round(sessions.reduce((s, r) => s + (r.readingTimeSecs || 0), 0) / 60);
  const totalChoices   = sessions.filter(s => s.choiceMade).length;
  return { totalStories, totalTimeMins, totalChoices, sessions };
}

async function deleteAllSessions() {
  try {
    const snap = await getDocs(collection(db, 'readingSessions'));
    await Promise.all(snap.docs.map(d => deleteDoc(d.ref)));
  } catch (e) { console.warn('Firebase delete sessions failed:', e.message); }
}

/* ══════════════════════════════════════════════════════════
   USER SETTINGS  (parent controls)
══════════════════════════════════════════════════════════ */
async function saveUserSettings(settings) {
  try {
    await setDoc(doc(db, 'userSettings', userId()), { ...settings, updatedAt: new Date().toISOString() }, { merge: true });
  } catch (e) { console.warn('Firebase save settings failed:', e.message); }
}

async function getUserSettings() {
  try {
    const snap = await getDoc(doc(db, 'userSettings', userId()));
    return snap.exists() ? snap.data() : {};
  } catch (e) { console.warn('Firebase get settings failed:', e.message); return {}; }
}

/* ══════════════════════════════════════════════════════════
   SAVED STORIES  (child library)
══════════════════════════════════════════════════════════ */
async function saveSavedStoriesToFirebase(stories) {
  try {
    await setDoc(doc(db, 'savedStories', userId()), { stories, updatedAt: new Date().toISOString() });
  } catch (e) { console.warn('Firebase save stories failed:', e.message); }
}

async function getSavedStoriesFromFirebase() {
  try {
    const snap = await getDoc(doc(db, 'savedStories', userId()));
    return snap.exists() ? (snap.data().stories || []) : [];
  } catch (e) { console.warn('Firebase get stories failed:', e.message); return []; }
}

/* ══════════════════════════════════════════════════════════
   EARNED BADGES
══════════════════════════════════════════════════════════ */
async function saveBadgesToFirebase(badgeIds) {
  try {
    await setDoc(doc(db, 'earnedBadges', userId()), { badges: badgeIds, updatedAt: new Date().toISOString() });
  } catch (e) { console.warn('Firebase save badges failed:', e.message); }
}

async function getBadgesFromFirebase() {
  try {
    const snap = await getDoc(doc(db, 'earnedBadges', userId()));
    return snap.exists() ? (snap.data().badges || []) : [];
  } catch (e) { console.warn('Firebase get badges failed:', e.message); return []; }
}

/* ══════════════════════════════════════════════════════════
   WEEKLY PROGRESS
══════════════════════════════════════════════════════════ */
async function saveWeeklyProgress(count) {
  try {
    await setDoc(doc(db, 'weeklyProgress', userId()), { count, weekKey: weekKey(), updatedAt: new Date().toISOString() });
  } catch (e) { console.warn('Firebase save weekly failed:', e.message); }
}

async function getWeeklyProgress() {
  try {
    const snap = await getDoc(doc(db, 'weeklyProgress', userId()));
    if (!snap.exists()) return 0;
    const data = snap.data();
    return data.weekKey === weekKey() ? (data.count || 0) : 0;
  } catch (e) { console.warn('Firebase get weekly failed:', e.message); return 0; }
}

/* ── Expose everything ───────────────────────────────────── */
window.saveReadingSession      = saveReadingSession;
window.getReadingSessions      = getReadingSessions;
window.getStats                = getStats;
window.deleteAllSessions       = deleteAllSessions;
window.saveUserSettings        = saveUserSettings;
window.getUserSettings         = getUserSettings;
window.saveSavedStoriesToFirebase  = saveSavedStoriesToFirebase;
window.getSavedStoriesFromFirebase = getSavedStoriesFromFirebase;
window.saveBadgesToFirebase    = saveBadgesToFirebase;
window.getBadgesFromFirebase   = getBadgesFromFirebase;
window.saveWeeklyProgress      = saveWeeklyProgress;
window.getWeeklyProgress       = getWeeklyProgress;
