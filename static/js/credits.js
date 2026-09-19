
let currentBalance = 0;

function getBalance() {
    return currentBalance;
}

function setBalance(credits) {
    currentBalance = Math.max(0, parseInt(credits, 10) || 0);
    updateCreditsUI();
}

function updateCreditsUI() {
    const badgeEl = document.getElementById('userCreditsBadge');
    const countEl = document.getElementById('userCreditsCount');
    const dropdownBalanceEl = document.getElementById('dropdownCreditsBalance');
    const headerBalanceEl = document.getElementById('headerCreditsDisplay');

    const formatted = window.tcI18n ? window.tcI18n.t('credits_count', { n: currentBalance }) : `${currentBalance} кредитов`;

    if (countEl) countEl.textContent = currentBalance;
    if (headerBalanceEl) headerBalanceEl.textContent = formatted;
    if (dropdownBalanceEl) dropdownBalanceEl.textContent = formatted;

    if (badgeEl) {
        badgeEl.classList.toggle('credits-low', currentBalance <= 1);
        badgeEl.classList.toggle('credits-empty', currentBalance === 0);
    }
}

function openTopUpModal(noticeText = null) {
    const modal = document.getElementById('topUpModal');
    const noticeEl = document.getElementById('topUpNotice');
    if (!modal) return;

    if (noticeEl) {
        if (noticeText) {
            noticeEl.textContent = noticeText;
            noticeEl.classList.remove('hidden');
        } else {
            noticeEl.classList.add('hidden');
        }
    }

    const promoError = document.getElementById('promoError');
    const promoSuccess = document.getElementById('promoSuccess');
    if (promoError) promoError.classList.add('hidden');
    if (promoSuccess) promoSuccess.classList.add('hidden');

    modal.classList.remove('hidden');
}

function closeTopUpModal() {
    const modal = document.getElementById('topUpModal');
    if (modal) modal.classList.add('hidden');
}

async function syncBalance() {
    if (!window.tcAuth || !window.tcAuth.isAuthenticated()) {
        setBalance(0);
        return;
    }
    try {
        const data = await window.tcApi.getCredits();
        if (data && data.credits !== undefined) {
            setBalance(data.credits);
            const user = window.tcAuth.getCurrentUser();
            if (user) {
                user.credits = data.credits;
                localStorage.setItem('tc_user', JSON.stringify(user));
            }
        }
    } catch (e) {
        console.debug('Could not sync balance from server', e);
    }
}

function checkAndDeductCredit(onAllowedCallback) {
    if (!window.tcAuth.isAuthenticated()) {
        window.tcAuth.requireAuth(onAllowedCallback, window.tcI18n ? window.tcI18n.t('auth_required_desc') : 'Для анализа университета необходимо войти или зарегистрироваться.');
        return false;
    }

    if (currentBalance <= 0) {
        const notice = window.tcI18n ? window.tcI18n.t('credits_depleted_desc') : 'Кредиты закончились! Пожалуйста, пополните баланс для продолжения проверок.';
        openTopUpModal(notice);
        return false;
    }

    if (typeof onAllowedCallback === 'function') {
        onAllowedCallback();
    }
    return true;
}

function initCredits() {
    const topUpModal = document.getElementById('topUpModal');
    const topUpCloseBtn = document.getElementById('topUpCloseBtn');
    const topUpCloseBtn2 = document.getElementById('topUpCloseBtn2');
    const openTopUpBtn = document.getElementById('openTopUpBtn');
    const navTopUpBtn = document.getElementById('navTopUpBtn');
    const promoForm = document.getElementById('promoForm');
    const promoInput = document.getElementById('promoInput');
    const promoError = document.getElementById('promoError');
    const promoSuccess = document.getElementById('promoSuccess');

    if (topUpCloseBtn) topUpCloseBtn.addEventListener('click', closeTopUpModal);
    if (topUpCloseBtn2) topUpCloseBtn2.addEventListener('click', closeTopUpModal);
    if (topUpModal) {
        topUpModal.addEventListener('click', (e) => {
            if (e.target === topUpModal) closeTopUpModal();
        });
    }

    if (openTopUpBtn) openTopUpBtn.addEventListener('click', () => openTopUpModal());
    if (navTopUpBtn) navTopUpBtn.addEventListener('click', () => openTopUpModal());

    document.querySelectorAll('.pkg-card-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const pkgId = btn.getAttribute('data-pkg-id');
            const credits = parseInt(btn.getAttribute('data-credits'), 10) || 5;
            const price = parseInt(btn.getAttribute('data-price'), 10) || 0;

            btn.disabled = true;
            const originalText = btn.textContent;
            btn.textContent = 'Обработка...';

            try {
                const res = await window.tcApi.topUp(pkgId, credits, price);
                setBalance(res.credits);
                const user = window.tcAuth.getCurrentUser();
                if (user) {
                    user.credits = res.credits;
                    localStorage.setItem('tc_user', JSON.stringify(user));
                }
                closeTopUpModal();
                if (window.showToast) {
                    window.showToast(res.message || `+${credits} кредитов успешно начислено!`);
                }
            } catch (err) {
                alert(err.message || 'Ошибка пополнения');
            } finally {
                btn.disabled = false;
                btn.textContent = originalText;
            }
        });
    });

    if (promoForm) {
        promoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const code = promoInput.value.trim();
            if (!code) return;

            if (promoError) promoError.classList.add('hidden');
            if (promoSuccess) promoSuccess.classList.add('hidden');

            try {
                const res = await window.tcApi.applyPromo(code);
                setBalance(res.credits);
                const user = window.tcAuth.getCurrentUser();
                if (user) {
                    user.credits = res.credits;
                    localStorage.setItem('tc_user', JSON.stringify(user));
                }
                if (promoSuccess) {
                    promoSuccess.textContent = res.message || `Промокод активирован! +${res.bonus_credits} кредитов.`;
                    promoSuccess.classList.remove('hidden');
                }
                promoInput.value = '';
                if (window.showToast) {
                    window.showToast(`🎉 Начислено +${res.bonus_credits} кредитов!`);
                }
            } catch (err) {
                if (promoError) {
                    promoError.textContent = err.message || 'Неверный промокод';
                    promoError.classList.remove('hidden');
                }
            }
        });
    }

    const user = window.tcAuth.getCurrentUser();
    if (user && user.credits !== undefined) {
        setBalance(user.credits);
    } else {
        setBalance(0);
    }

    syncBalance();

    window.addEventListener('languageChanged', updateCreditsUI);
}

window.tcCredits = {
    getBalance,
    setBalance,
    updateCreditsUI,
    openTopUpModal,
    closeTopUpModal,
    syncBalance,
    checkAndDeductCredit,
    initCredits
};
