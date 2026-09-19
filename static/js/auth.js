
const USER_STORAGE_KEY = 'tc_user';
const TOKEN_STORAGE_KEY = 'tc_token';

let pendingAuthAction = null;

function getCurrentUser() {
    try {
        const raw = localStorage.getItem(USER_STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function setCurrentUser(user, token = null) {
    if (user) {
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
        if (token) localStorage.setItem(TOKEN_STORAGE_KEY, token);
        if (user.credits !== undefined && window.tcCredits) {
            window.tcCredits.setBalance(user.credits);
        }
    } else {
        localStorage.removeItem(USER_STORAGE_KEY);
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        if (window.tcCredits) {
            window.tcCredits.setBalance(0);
        }
    }
    updateAuthUI();
    if (typeof window.updateMobileUserSection === 'function') {
        window.updateMobileUserSection();
    }
}

function isAuthenticated() {
    const user = getCurrentUser();
    return !!(user && (user.email || user.id));
}

function requireAuth(actionCallback, reason = null) {
    if (isAuthenticated()) {
        if (typeof actionCallback === 'function') {
            return actionCallback();
        }
        return true;
    }

    pendingAuthAction = actionCallback;
    const authNotice = reason || (window.tcI18n ? window.tcI18n.t('auth_required_desc') : 'Для анализа университета необходимо войти или зарегистрироваться.');
    openAuthModal('register', authNotice);
    return false;
}

function openAuthModal(tab = 'login', noticeText = null) {
    const authModal = document.getElementById('authModal');
    const noticeEl = document.getElementById('authModalNotice');
    if (!authModal) return;

    if (noticeEl) {
        if (noticeText) {
            noticeEl.textContent = noticeText;
            noticeEl.classList.remove('hidden');
        } else {
            noticeEl.classList.add('hidden');
        }
    }

    switchAuthTab(tab);
    clearAuthErrors();
    authModal.classList.remove('hidden');
}

function closeAuthModal() {
    const authModal = document.getElementById('authModal');
    if (authModal) authModal.classList.add('hidden');
}

function switchAuthTab(tab) {
    const tabLogin = document.getElementById('tabAuthLogin');
    const tabReg = document.getElementById('tabAuthRegister');
    const formLogin = document.getElementById('loginForm');
    const formReg = document.getElementById('registerForm');
    const title = document.getElementById('authModalTitle');

    if (tab === 'login') {
        if (tabLogin) tabLogin.classList.add('active');
        if (tabReg) tabReg.classList.remove('active');
        if (formLogin) formLogin.classList.remove('hidden');
        if (formReg) formReg.classList.add('hidden');
        if (title) title.textContent = window.tcI18n ? window.tcI18n.t('modal_auth_login_title') : 'Вход в личный кабинет';
    } else {
        if (tabReg) tabReg.classList.add('active');
        if (tabLogin) tabLogin.classList.remove('active');
        if (formReg) formReg.classList.remove('hidden');
        if (formLogin) formLogin.classList.add('hidden');
        if (title) title.textContent = window.tcI18n ? window.tcI18n.t('modal_auth_reg_title') : 'Регистрация в TrueCampus';
    }
}

function clearAuthErrors() {
    const loginError = document.getElementById('loginError');
    const regError = document.getElementById('registerError');
    if (loginError) loginError.classList.add('hidden');
    if (regError) regError.classList.add('hidden');
}

function updateAuthUI() {
    const user = getCurrentUser();
    const loggedOutEl = document.getElementById('authLoggedOut');
    const loggedInEl = document.getElementById('authLoggedIn');
    const avatarEl = document.getElementById('userAvatarText');
    const nameEl = document.getElementById('userNameText');
    const dropdownNameEl = document.getElementById('dropdownUserName');
    const dropdownEmailEl = document.getElementById('dropdownUserEmail');
    const dropdownEl = document.getElementById('accountDropdown');

    if (user && (user.name || user.email)) {
        if (loggedOutEl) loggedOutEl.classList.add('hidden');
        if (loggedInEl) loggedInEl.classList.remove('hidden');
        const displayName = user.name || user.email.split('@')[0];
        if (nameEl) nameEl.textContent = displayName;
        if (dropdownNameEl) dropdownNameEl.textContent = displayName;
        if (dropdownEmailEl) dropdownEmailEl.textContent = user.email || '';
        if (avatarEl) avatarEl.textContent = displayName.charAt(0).toUpperCase();
    } else {
        if (loggedOutEl) loggedOutEl.classList.remove('hidden');
        if (loggedInEl) loggedInEl.classList.add('hidden');
        if (dropdownEl) dropdownEl.classList.add('hidden');
    }
}

function initAuth() {
    const openModalBtn = document.getElementById('openAuthModalBtn');
    const closeModalBtn = document.getElementById('authModalCloseBtn');
    const authModal = document.getElementById('authModal');
    const tabLogin = document.getElementById('tabAuthLogin');
    const tabReg = document.getElementById('tabAuthRegister');
    const loginForm = document.getElementById('loginForm');
    const regForm = document.getElementById('registerForm');
    const logoutBtn = document.getElementById('logoutBtn');
    const userPill = document.getElementById('userPillBtn');
    const accountDropdown = document.getElementById('accountDropdown');

    if (openModalBtn) openModalBtn.addEventListener('click', () => openAuthModal('login'));
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeAuthModal);
    if (authModal) {
        authModal.addEventListener('click', (e) => {
            if (e.target === authModal) closeAuthModal();
        });
    }

    if (tabLogin) tabLogin.addEventListener('click', () => switchAuthTab('login'));
    if (tabReg) tabReg.addEventListener('click', () => switchAuthTab('register'));

    if (userPill && accountDropdown) {
        userPill.addEventListener('click', (e) => {
            e.stopPropagation();
            accountDropdown.classList.toggle('hidden');
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('#accountArea')) {
                accountDropdown.classList.add('hidden');
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            setCurrentUser(null);
            if (window.showToast) {
                window.showToast(window.tcI18n ? window.tcI18n.t('toast_logout') : 'Вы вышли из системы');
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value.trim();
            const errorEl = document.getElementById('loginError');

            if (!email || !password) return;

            try {
                const data = await window.tcApi.login(email, password);
                setCurrentUser(data.user, data.token);
                closeAuthModal();
                if (window.showToast) {
                    window.showToast(window.tcI18n ? window.tcI18n.t('toast_login_success') : 'Добро пожаловать!');
                }
                loginForm.reset();

                if (typeof pendingAuthAction === 'function') {
                    const action = pendingAuthAction;
                    pendingAuthAction = null;
                    action();
                }
            } catch (err) {
                if (errorEl) {
                    errorEl.textContent = err.message || 'Ошибка входа';
                    errorEl.classList.remove('hidden');
                }
            }
        });
    }

    if (regForm) {
        regForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('regName').value.trim();
            const email = document.getElementById('regEmail').value.trim();
            const password = document.getElementById('regPassword').value.trim();
            const errorEl = document.getElementById('registerError');

            if (!name || !email || !password) return;

            try {
                const data = await window.tcApi.register(name, email, password);
                setCurrentUser(data.user, data.token);
                closeAuthModal();
                if (window.showToast) {
                    window.showToast(`🎉 ${name}, добро пожаловать! Вам начислено 5 кредитов.`);
                }
                regForm.reset();

                if (typeof pendingAuthAction === 'function') {
                    const action = pendingAuthAction;
                    pendingAuthAction = null;
                    action();
                }
            } catch (err) {
                if (errorEl) {
                    errorEl.textContent = err.message || 'Ошибка при регистрации';
                    errorEl.classList.remove('hidden');
                }
            }
        });
    }

    updateAuthUI();
}

function logout() {
    setCurrentUser(null);
    if (window.showToast) {
        window.showToast(window.tcI18n ? window.tcI18n.t('toast_logout') : 'Вы вышли из системы');
    }
}

window.tcAuth = {
    getCurrentUser,
    getStoredUser: getCurrentUser,
    setCurrentUser,
    isAuthenticated,
    requireAuth,
    openAuthModal,
    closeAuthModal,
    updateAuthUI,
    initAuth,
    logout
};
