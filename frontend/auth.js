/**
 * auth.js — Authentication & role-based navigation for StoryMagic AI
 * Roles: 'parent' | 'child'
 */

document.addEventListener('DOMContentLoaded', () => {
    injectAuthStyles();
    updateNavigation();
});

/* ─────────────────────────────────────────────────────────────
 * injectAuthStyles — adds nav button CSS once into <head>
 * ───────────────────────────────────────────────────────────── */
function injectAuthStyles() {
    if (document.getElementById('auth-nav-styles')) return;
    const style = document.createElement('style');
    style.id = 'auth-nav-styles';
    style.textContent = `
        .nav-pill-auth {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            flex-wrap: nowrap !important;
        }
        .nav-profile-link {
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 50px;
            padding: 5px 14px 5px 5px;
            transition: background 0.2s ease, border-color 0.2s ease;
        }
        .nav-profile-link:hover {
            background: rgba(255,255,255,0.13);
            border-color: rgba(236,72,153,0.4);
        }
        .nav-avatar-ring {
            width: 44px; height: 44px;
            border-radius: 50%;
            padding: 2px;
            background: linear-gradient(135deg, #ec4899, #a855f7, #fbbf24);
            flex-shrink: 0;
        }
        .nav-avatar-ring img,
        .nav-avatar-ring span {
            width: 100%; height: 100%;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #1a1030;
            overflow: hidden;
            font-size: 22px;
        }
        .nav-avatar-ring img {
            object-fit: cover;
        }
        .nav-profile-name {
            font-weight: 700;
            font-size: 14px;
            color: #fff;
        }
        .nav-role-badge {
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 50px;
            letter-spacing: 0.4px;
        }
        .nav-sign-out-btn {
            background: rgba(255,255,255,0.0);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 50px;
            color: rgba(255,255,255,0.45);
            font-size: 12px;
            font-weight: 600;
            padding: 6px 14px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: inherit;
            white-space: nowrap;
            flex-shrink: 0;
        }
        .nav-sign-out-btn:hover {
            background: rgba(239,68,68,0.15);
            border-color: rgba(239,68,68,0.45);
            color: #ff6b6b;
        }
    `;
    document.head.appendChild(style);
}

/* ─────────────────────────────────────────────────────────────
 * updateNavigation — renders nav links + auth area by role
 * ───────────────────────────────────────────────────────────── */
function updateNavigation() {
    const authContainer  = document.querySelector('.nav-pill-auth');
    const linksContainer = document.querySelector('.nav-pill-links');
    if (!authContainer) return;

    const currentUser = getCurrentUser();

    if (currentUser) {
        const isParent   = currentUser.role === 'parent';
        const badgeColor = isParent ? '#a855f7' : '#ec4899';
        const roleLabel  = isParent ? '👨‍👩‍👧 Parent' : '🌈 Child';

        // ── Auth pill (profile + sign out) ──────────────────
        const parentInitials = (currentUser.name || 'P').charAt(0).toUpperCase();
        const avatarInner = currentUser.avatar
            ? `<img src="${currentUser.avatar}" alt="Avatar">`
            : isParent
                ? `<span style="width:100%;height:100%;border-radius:50%;background:linear-gradient(135deg,#a855f7,#7c3aed);
                                display:flex;align-items:center;justify-content:center;font-size:17px;font-weight:800;color:#fff;">${parentInitials}</span>`
                : `<span>${currentUser.avatarEmoji || '🦁'}</span>`;

        authContainer.innerHTML = `
            <a href="profile.html" class="nav-profile-link jelly-hover">
                <div class="nav-avatar-ring">${avatarInner}</div>
                <span class="nav-profile-name">${currentUser.name || 'Explorer'}</span>
            </a>
            <button class="nav-sign-out-btn" onclick="logout()">Sign Out</button>
        `;

        // ── Nav links by role ────────────────────────────────
        if (linksContainer) {
            if (isParent) {
                linksContainer.innerHTML = `
                    <a href="parent.html">Dashboard</a>
                `;
            } else {
                linksContainer.innerHTML = `
                    <a href="index.html">Home</a>
                    <a href="characters.html">Characters</a>
                    <a href="library.html">My Library</a>
                `;
            }
        }

        // ── Redirect parent away from child-only pages ───────
        if (isParent) {
            const page = window.location.pathname.split('/').pop() || 'index.html';
            const childPages = ['index.html', '', 'characters.html', 'story.html', 'library.html'];
            if (childPages.includes(page)) {
                window.location.href = 'parent.html';
            }
        }

    } else {
        // ── Not logged in ────────────────────────────────────
        authContainer.innerHTML = `
            <a href="login.html" class="nav-btn login jelly-hover">Login</a>
            <a href="signup.html" class="nav-btn signup jelly-hover">Sign Up</a>
        `;
        if (linksContainer) {
            linksContainer.innerHTML = `
                <a href="index.html">Home</a>
                <a href="characters.html">Characters</a>
            `;
        }
    }
}

/* ─────────────────────────────────────────────────────────────
 * getCurrentUser — returns parsed user object or null
 * ───────────────────────────────────────────────────────────── */
function getCurrentUser() {
    try {
        const user = JSON.parse(localStorage.getItem('currentUser'));
        if (!user) return null;
        // If name is the generic default, try to retrieve the real name from registry
        if (user.role === 'parent') {
            const registry = JSON.parse(localStorage.getItem('parentRegistry') || '{}');
            const entry = registry[(user.email || '').toLowerCase()];
            if (entry) {
                const realName   = typeof entry === 'object' ? entry.name   : entry;
                const realAvatar = typeof entry === 'object' ? entry.avatar : null;
                let changed = false;
                if (realName && (!user.name || user.name === 'Parent')) { user.name = realName; changed = true; }
                if (realAvatar && user.avatar !== realAvatar)           { user.avatar = realAvatar; changed = true; }
                if (changed) localStorage.setItem('currentUser', JSON.stringify(user));
            }
        }
        return user;
    } catch {
        return null;
    }
}

/* ─────────────────────────────────────────────────────────────
 * mockLogin — stores session and redirects based on role
 * ───────────────────────────────────────────────────────────── */
function mockLogin(emailOrUsername, name = 'Little Explorer', role = 'child', avatarEmoji = null, avatarImg = null) {
    const userData = {
        email:       emailOrUsername || 'guest@example.com',
        name:        name,
        role:        role,
        avatarEmoji: avatarEmoji || (role === 'child' ? '🦁' : null),
        avatar:      avatarImg || (role === 'parent' ? 'images/Profile1.jpeg' : 'images/Rosie.webp'),
        joined:      new Date().toLocaleDateString()
    };
    localStorage.setItem('currentUser', JSON.stringify(userData));

    const redirect = sessionStorage.getItem('redirectAfterLogin');
    sessionStorage.removeItem('redirectAfterLogin');
    if (redirect) {
        window.location.href = redirect;
    } else if (role === 'parent') {
        window.location.href = 'parent.html';
    } else {
        window.location.href = 'index.html';
    }
}

/* ─────────────────────────────────────────────────────────────
 * requireAuth — call at top of any page that needs a login
 * ───────────────────────────────────────────────────────────── */
function requireAuth() {
    if (!getCurrentUser()) {
        sessionStorage.setItem('redirectAfterLogin', window.location.href);
        window.location.href = 'login.html';
    }
}

/* ─────────────────────────────────────────────────────────────
 * requireParentAuth — call at top of parent-only pages
 * ───────────────────────────────────────────────────────────── */
function requireParentAuth() {
    const user = getCurrentUser();
    if (!user || user.role !== 'parent') {
        sessionStorage.setItem('redirectAfterLogin', window.location.href);
        window.location.href = 'login.html?reason=parent-only';
    }
}

/* ─────────────────────────────────────────────────────────────
 * logout — clears session, sends both roles to login page
 * ───────────────────────────────────────────────────────────── */
function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = 'login.html';
}
