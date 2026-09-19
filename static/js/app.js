
let currentProfile = null;
let timerInterval = null;
let startTime = null;
let leafletMap = null;
let activeCategoryFilter = 'all';

const landingView = document.getElementById('landingView');
const auditView = document.getElementById('auditView');
const navHomeBtn = document.getElementById('navHomeBtn');
const navAuditBtn = document.getElementById('navAuditBtn');
const logoArea = document.getElementById('logoArea');

const searchForm = document.getElementById('searchForm');
const universityInput = document.getElementById('universityInput');
const searchBtn = document.getElementById('searchBtn');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressStageTitle = document.getElementById('progressStageTitle');
const elapsedTimer = document.getElementById('elapsedTimer');
const resultsSection = document.getElementById('resultsSection');

const downloadPdfBtn = document.getElementById('downloadPdfBtn');
const printReportBtn = document.getElementById('printReportBtn');
const compareThisBtn = document.getElementById('compareThisBtn');
const openCompareBtn = document.getElementById('openCompareBtn');

const ambiguityBanner = document.getElementById('ambiguityBanner');
const ambiguityCandidatesList = document.getElementById('ambiguityCandidatesList');
const didYouMeanBanner = document.getElementById('didYouMeanBanner');
const didYouMeanBtn = document.getElementById('didYouMeanBtn');
const didYouMeanHint = document.getElementById('didYouMeanHint');

const categoryFilterTabs = document.getElementById('categoryFilterTabs');
const filterHighTrustOnly = document.getElementById('filterHighTrustOnly');

const compareModal = document.getElementById('compareModal');
const compareModalCloseBtn = document.getElementById('compareModalCloseBtn');
const compareModalCloseBtn2 = document.getElementById('compareModalCloseBtn2');
const compareForm = document.getElementById('compareForm');
const compareUniv1Input = document.getElementById('compareUniv1Input');
const compareUniv2Input = document.getElementById('compareUniv2Input');
const compareLoading = document.getElementById('compareLoading');
const compareResultsTable = document.getElementById('compareResultsTable');

const attributionModal = document.getElementById('attributionModal');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalCloseBtn2 = document.getElementById('modalCloseBtn2');
const modalImage = document.getElementById('modalImage');
const modalCategory = document.getElementById('modalCategory');
const modalTrustScore = document.getElementById('modalTrustScore');
const modalConfidence = document.getElementById('modalConfidence');
const modalDate = document.getElementById('modalDate');
const modalLicense = document.getElementById('modalLicense');
const modalAuthor = document.getElementById('modalAuthor');
const modalPhash = document.getElementById('modalPhash');
const modalSourceUrl = document.getElementById('modalSourceUrl');

const aboutServiceBtn = document.getElementById('aboutServiceBtn');
const aboutServiceModal = document.getElementById('aboutServiceModal');
const aboutServiceCloseBtn = document.getElementById('aboutServiceCloseBtn');
const aboutServiceCloseBtn2 = document.getElementById('aboutServiceCloseBtn2');

const myAuditsModal = document.getElementById('myAuditsModal');
const myAuditsBtn = document.getElementById('myAuditsBtn');
const myAuditsCloseBtn = document.getElementById('myAuditsCloseBtn');
const myAuditsCloseBtn2 = document.getElementById('myAuditsCloseBtn2');
const myAuditsList = document.getElementById('myAuditsList');
const clearAuditsHistoryBtn = document.getElementById('clearAuditsHistoryBtn');

function switchToLandingView() {
    if (landingView) landingView.classList.remove('hidden');
    if (auditView) auditView.classList.add('hidden');
    if (navHomeBtn) navHomeBtn.classList.add('active');
    if (navAuditBtn) navAuditBtn.classList.remove('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function switchToAuditView(initialQuery = null) {
    if (landingView) landingView.classList.add('hidden');
    if (auditView) auditView.classList.remove('hidden');
    if (navHomeBtn) navHomeBtn.classList.remove('active');
    if (navAuditBtn) navAuditBtn.classList.add('active');

    if (initialQuery && universityInput) {
        universityInput.value = initialQuery;
        triggerAudit(initialQuery);
    } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (universityInput) universityInput.focus();
    }
}

if (logoArea) logoArea.addEventListener('click', switchToLandingView);
if (navHomeBtn) navHomeBtn.addEventListener('click', switchToLandingView);
if (navAuditBtn) navAuditBtn.addEventListener('click', () => switchToAuditView());

document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const lang = btn.getAttribute('data-lang');
        if (window.tcI18n) {
            window.tcI18n.setLanguage(lang);
        }
    });
});

function triggerAudit(query) {
    if (!query) return;

    window.tcCredits.checkAndDeductCredit(() => {
        startAnalysis(query);
    });
}

if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = universityInput.value.trim();
        if (query) {
            triggerAudit(query);
        }
    });
}

document.querySelectorAll('.tag-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        if (universityInput) universityInput.value = query;
        triggerAudit(query);
    });
});

let suggestTimeout = null;
if (universityInput) {
    universityInput.addEventListener('input', () => {
        const query = universityInput.value.trim();
        clearTimeout(suggestTimeout);
        
        if (query.length < 3) {
            if (didYouMeanBanner) didYouMeanBanner.classList.add('hidden');
            if (ambiguityBanner) ambiguityBanner.classList.add('hidden');
            return;
        }

        suggestTimeout = setTimeout(async () => {
            try {
                const data = await window.tcApi.suggest(query);
                if (data) {
                    if (data.is_ambiguous && data.candidates && data.candidates.length > 0) {
                        showAmbiguityCandidates(data.candidates);
                    } else if (ambiguityBanner) {
                        ambiguityBanner.classList.add('hidden');
                    }

                    if (data.has_typo && data.did_you_mean && data.did_you_mean.toLowerCase() !== query.toLowerCase()) {
                        showDidYouMean(data);
                    } else if (didYouMeanBanner) {
                        didYouMeanBanner.classList.add('hidden');
                    }
                }
            } catch (e) {
                console.debug("Suggest lookup error", e);
            }
        }, 350);
    });
}

function showDidYouMean(data) {
    if (!didYouMeanBanner || !didYouMeanBtn) return;
    if (data.has_typo && data.did_you_mean) {
        didYouMeanBtn.textContent = data.did_you_mean;
        if (didYouMeanHint) {
            didYouMeanHint.textContent = `(${data.city ? data.city + ', ' : ''}${data.country || ''})`;
        }
        didYouMeanBanner.classList.remove('hidden');

        didYouMeanBtn.onclick = () => {
            universityInput.value = data.did_you_mean;
            didYouMeanBanner.classList.add('hidden');
            triggerAudit(data.did_you_mean);
        };
    } else {
        didYouMeanBanner.classList.add('hidden');
    }
}

function showAmbiguityCandidates(candidates) {
    if (!ambiguityBanner || !ambiguityCandidatesList) return;
    ambiguityCandidatesList.innerHTML = '';
    candidates.forEach(cand => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'candidate-chip';
        chip.innerHTML = `<strong>${escapeHtml(cand.canonical_name)}</strong> <span class="chip-loc">(${escapeHtml(cand.city)}, ${escapeHtml(cand.country)})</span>`;
        chip.onclick = () => {
            universityInput.value = cand.canonical_name;
            ambiguityBanner.classList.add('hidden');
            triggerAudit(cand.canonical_name);
        };
        ambiguityCandidatesList.appendChild(chip);
    });
    ambiguityBanner.classList.remove('hidden');
}

function startTimer() {
    startTime = Date.now();
    if (elapsedTimer) elapsedTimer.textContent = "0.0s";
    clearInterval(timerInterval);
    
    timerInterval = setInterval(() => {
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        if (elapsedTimer) elapsedTimer.textContent = `${elapsed}s`;
    }, 100);
}

function stopTimer() {
    clearInterval(timerInterval);
}

function setStageState(stepId, state, statusText) {
    const el = document.getElementById(stepId);
    if (!el) return;
    el.classList.remove('active', 'done');
    if (state === 'active') el.classList.add('active');
    if (state === 'done') el.classList.add('done');
    const stEl = el.querySelector('.step-status');
    if (stEl) stEl.textContent = statusText;
}

function resetStages() {
    ['step-disambiguation', 'step-aggregation', 'step-phash', 'step-clip', 'step-rules'].forEach(id => {
        setStageState(id, '', 'Ожидание...');
    });
    if (progressBar) progressBar.style.width = '10%';
}

async function startAnalysis(query) {
    if (resultsSection) resultsSection.classList.add('hidden');
    if (didYouMeanBanner) didYouMeanBanner.classList.add('hidden');
    if (ambiguityBanner) ambiguityBanner.classList.add('hidden');
    if (progressSection) progressSection.classList.remove('hidden');
    if (searchBtn) searchBtn.disabled = true;

    resetStages();
    startTimer();

    if (progressStageTitle) progressStageTitle.textContent = "Шаг 1: Детекция опечаток и сущности университета...";
    setStageState('step-disambiguation', 'active', 'Обработка...');
    if (progressBar) progressBar.style.width = '20%';

    const stage1Timer = setTimeout(() => {
        setStageState('step-disambiguation', 'done', 'Завершено');
        setStageState('step-aggregation', 'active', 'Сбор из Wikimedia, Openverse, Mapillary...');
        if (progressStageTitle) progressStageTitle.textContent = "Шаг 2: Асинхронный параллельный сбор медиа...";
        if (progressBar) progressBar.style.width = '40%';
    }, 1200);

    const stage2Timer = setTimeout(() => {
        setStageState('step-aggregation', 'done', 'Собрано');
        setStageState('step-phash', 'active', 'Вычисление pHash дедупликации...');
        if (progressStageTitle) progressStageTitle.textContent = "Шаг 3: Локальная pHash-дедупликация (Hamming ≤ 6)...";
        if (progressBar) progressBar.style.width = '60%';
    }, 3200);

    const stage3Timer = setTimeout(() => {
        setStageState('step-phash', 'done', 'Отсеяно');
        setStageState('step-clip', 'active', 'Классификация по 8 категориям & Trust Scoring...');
        if (progressStageTitle) progressStageTitle.textContent = "Шаг 4: Zero-shot категоризация & расчет достоверности...";
        if (progressBar) progressBar.style.width = '80%';
    }, 5500);

    try {
        const data = await window.tcApi.analyze(query);
        currentProfile = data;

        clearTimeout(stage1Timer);
        clearTimeout(stage2Timer);
        clearTimeout(stage3Timer);
        stopTimer();

        setStageState('step-disambiguation', 'done', 'Готово');
        setStageState('step-aggregation', 'done', 'Готово');
        setStageState('step-phash', 'done', 'Готово');
        setStageState('step-clip', 'done', 'Готово');
        setStageState('step-rules', 'done', 'Готово');
        if (progressBar) progressBar.style.width = '100%';
        if (progressStageTitle) progressStageTitle.textContent = "Визуальный профиль сформирован!";

        if (data.user_remaining_credits !== undefined) {
            window.tcCredits.setBalance(data.user_remaining_credits);
            const user = window.tcAuth.getCurrentUser();
            if (user) {
                user.credits = data.user_remaining_credits;
                localStorage.setItem('tc_user', JSON.stringify(user));
            }
        }

        setTimeout(() => {
            if (progressSection) progressSection.classList.add('hidden');
            if (data.is_ambiguous && data.candidates && data.candidates.length > 0) {
                showAmbiguityCandidates(data.candidates);
            }
            showDidYouMean(data);
            renderProfile(data);
            saveAuditToHistory(data);
            if (resultsSection) resultsSection.classList.remove('hidden');
            if (searchBtn) searchBtn.disabled = false;
        }, 400);

    } catch (err) {
        clearTimeout(stage1Timer);
        clearTimeout(stage2Timer);
        clearTimeout(stage3Timer);
        stopTimer();
        if (progressSection) progressSection.classList.add('hidden');
        if (searchBtn) searchBtn.disabled = false;

        if (err.status === 401) {
            window.tcAuth.openAuthModal('register', err.message || 'Для анализа университета необходимо войти или зарегистрироваться.');
        } else if (err.status === 402) {
            window.tcCredits.openTopUpModal(err.message || 'Кредиты закончились! Пожалуйста, пополните баланс.');
        } else {
            alert(err.message || 'Произошла ошибка при анализе кампуса');
        }
    }
}

function renderProfile(data) {
    const locEl = document.getElementById('profileLocation');
    if (locEl) locEl.innerHTML = `📍 ${escapeHtml(data.city)}, ${escapeHtml(data.country)}`;
    
    const nameEl = document.getElementById('profileCanonicalName');
    if (nameEl) nameEl.textContent = data.canonical_name;
    
    const enEl = document.getElementById('profileEnglishName');
    if (enEl) enEl.textContent = data.english_name || '';

    const summaryText = document.getElementById('summaryText');
    if (summaryText) summaryText.textContent = data.campus_summary || 'Формирование описания...';

    const rSummary = data.rules_summary || {};
    const metrics = data.metrics || {};

    const kpiCov = document.getElementById('kpiCoverage');
    if (kpiCov) kpiCov.textContent = `${rSummary.verification_coverage_percent || 0}%`;

    const kpiCat = document.getElementById('kpiCategoriesSub');
    if (kpiCat) kpiCat.textContent = `${rSummary.categories_verified || 0} из ${rSummary.total_categories || 8} зон кампуса`;

    const kpiVer = document.getElementById('kpiVerifiedCount');
    if (kpiVer) kpiVer.textContent = `${rSummary.total_verified_photos || 0}`;

    const kpiTrust = document.getElementById('kpiTrustIndex');
    if (kpiTrust) kpiTrust.textContent = `${rSummary.overall_trust_index || 88}%`;

    const kpiDup = document.getElementById('kpiDuplicates');
    if (kpiDup) kpiDup.textContent = `${metrics.duplicates_dropped || 0}`;

    const sourcesContainer = document.getElementById('sourcesBadgesList');
    if (sourcesContainer) {
        sourcesContainer.innerHTML = '';
        const srcStatus = data.sources_status || {};
        for (const [srcName, statusVal] of Object.entries(srcStatus)) {
            const span = document.createElement('span');
            span.className = `src-tag ${statusVal.includes('ok') || statusVal.includes('loaded') ? 'src-ok' : 'src-timeout'}`;
            span.textContent = `${srcName.toUpperCase()}: ${statusVal}`;
            sourcesContainer.appendChild(span);
        }
    }

    if (downloadPdfBtn) {
        downloadPdfBtn.onclick = () => {
            window.location.href = `/api/report/${data.profile_id}/pdf`;
        };
    }
    if (printReportBtn) {
        printReportBtn.href = `/api/report/${data.profile_id}/print`;
    }
    if (compareThisBtn) {
        compareThisBtn.onclick = () => {
            if (compareUniv1Input) compareUniv1Input.value = data.canonical_name;
            openComparisonModal();
        };
    }

    renderCampusMap(data);
    renderLivingData(data);
    renderStudentReviews(data);
    renderCategories(data.categories);
}

function renderCampusMap(data) {
    const campusData = data.campus_data || {};
    const distKm = campusData.distance_km || 3.5;
    
    const distEl = document.getElementById('distanceKm');
    if (distEl) distEl.textContent = `${distKm} км`;

    const ptTitle = document.getElementById('campusPointTitle');
    if (ptTitle) ptTitle.textContent = data.canonical_name;

    const cityCenterTitle = document.getElementById('cityCenterPointTitle');
    if (cityCenterTitle) cityCenterTitle.textContent = campusData.city_center_name || `Центр г. ${data.city}`;

    const transit = campusData.transit_times || {};
    const pubEl = document.getElementById('transitPublic');
    const walkEl = document.getElementById('transitWalk');
    const driveEl = document.getElementById('transitDrive');
    if (pubEl) pubEl.textContent = transit.public_transit || '15-20 мин';
    if (walkEl) walkEl.textContent = transit.walking || '45 мин';
    if (driveEl) driveEl.textContent = transit.driving || '10 мин';

    const cCoords = campusData.campus_coords || data.coordinates || { lat: 43.2241, lon: 76.9247 };
    const centerCoords = campusData.city_center || { lat: cCoords.lat + 0.02, lon: cCoords.lon + 0.01 };

    const campLat = cCoords.lat || 43.2241;
    const campLon = cCoords.lon || 76.9247;
    const centLat = centerCoords.lat || campLat + 0.02;
    const centLon = centerCoords.lon || campLon + 0.01;

    setTimeout(() => {
        if (typeof L !== 'undefined' && document.getElementById('campusMap')) {
            if (leafletMap) {
                leafletMap.remove();
            }
            leafletMap = L.map('campusMap').setView([campLat, campLon], 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18
            }).addTo(leafletMap);

            L.marker([campLat, campLon]).addTo(leafletMap)
                .bindPopup(`<b>${escapeHtml(data.canonical_name)}</b><br/>Кампус`).openPopup();
            
            L.marker([centLat, centLon]).addTo(leafletMap)
                .bindPopup(`<b>${escapeHtml(campusData.city_center_name || 'Центр города')}</b>`);

            const latlngs = [[campLat, campLon], [centLat, centLon]];
            const polyline = L.polyline(latlngs, { color: '#06b6d4', weight: 4, dashArray: '6, 8' }).addTo(leafletMap);
            leafletMap.fitBounds(polyline.getBounds(), { padding: [30, 30] });
        }
    }, 200);
}

function renderLivingData(data) {
    const campusData = data.campus_data || {};
    const climate = campusData.climate || {};
    const cost = campusData.cost_of_living || {};

    const climEl = document.getElementById('livingClimate');
    const transEl = document.getElementById('livingTransport');
    const dormEl = document.getElementById('livingDormCost');
    const foodEl = document.getElementById('livingFoodCost');
    const totalEl = document.getElementById('livingTotalCost');

    if (climEl) climEl.textContent = `${climate.summer_avg || '+25°C'} / ${climate.winter_avg || '-5°C'} (${climate.description || 'Умеренный'})`;
    if (transEl) transEl.textContent = campusData.transport_info || 'Общественный транспорт и маршрутные автобусы';
    if (dormEl) dormEl.textContent = cost.dorm_monthly || 'Доступно общежитие';
    if (foodEl) foodEl.textContent = cost.food_monthly || 'Стандартный студенческий рацион';
    if (totalEl) totalEl.textContent = cost.total_monthly_est || '$250 – $400 / мес';
}

function renderStudentReviews(data) {
    const container = document.getElementById('studentReviewsContainer');
    if (!container) return;
    container.innerHTML = '';
    const reviews = (data.campus_data && data.campus_data.student_reviews) || [];
    
    if (reviews.length === 0) {
        container.innerHTML = '<div class="review-text">Отзывы студентов верифицируются...</div>';
        return;
    }

    reviews.forEach(rev => {
        const item = document.createElement('div');
        item.className = 'review-item';
        item.innerHTML = `
            <div class="review-top">
                <span class="review-author">${escapeHtml(rev.author)}</span>
                <span class="review-rating">★ ${rev.rating}</span>
            </div>
            <div class="review-text">«${escapeHtml(rev.text)}»</div>
            <div style="margin-top: 6px;">
                <span class="review-badge">✓ Верифицированный студент (${escapeHtml(rev.category || 'Общее')})</span>
            </div>
        `;
        container.appendChild(item);
    });
}

function renderCategories(categories) {
    const container = document.getElementById('categoriesContainer');
    if (!container) return;
    container.innerHTML = '';

    const highTrustOnly = filterHighTrustOnly ? filterHighTrustOnly.checked : false;

    for (const [catKey, cat] of Object.entries(categories || {})) {
        if (activeCategoryFilter !== 'all' && activeCategoryFilter !== catKey) {
            continue;
        }

        const block = document.createElement('div');
        block.className = 'category-block';
        block.id = `cat-block-${catKey}`;

        const isVerified = cat.is_verified;
        const statusBadgeClass = isVerified ? 'status-verified' : 'status-unverified';
        const statusBadgeText = isVerified 
            ? `✓ ВЕРИФИЦИРОВАНО (${cat.items_count} ФОТО, ДОСТОВЕРНОСТЬ ${cat.average_trust_score || Math.round((cat.average_confidence || 0.8) * 100)}%)` 
            : '⚠ ЧЕСТНАЯ НЕОПРЕДЕЛЕННОСТЬ: НЕТ ВЕРИФИЦИРОВАННЫХ ДАННЫХ';

        let visibleItems = cat.items || [];
        if (highTrustOnly) {
            visibleItems = visibleItems.filter(it => (it.trust_score || 80) >= 80);
        }

        let bodyHtml = '';
        if (isVerified && visibleItems.length > 0) {
            let cardsHtml = '<div class="cards-grid">';
            visibleItems.forEach(item => {
                const trustScore = item.trust_score || Math.round((item.confidence || 0.8) * 100);
                const trustTierClass = item.trust_tier === 'high' ? 'badge-trust-high' : 
                                      (item.trust_tier === 'medium' ? 'badge-trust-med' : 'badge-trust-low');
                const safeTitle = escapeHtml(item.title);
                const safeAuthor = escapeHtml(item.author);
                const safeLicense = escapeHtml(item.license_name);
                const safeDate = escapeHtml(item.date_published || '2024');

                cardsHtml += `
                    <div class="media-card" onclick="openMediaModal('${item.id}')">
                        <div class="card-thumb-wrap">
                            <img src="${item.preview_url}" alt="${safeTitle}" loading="lazy" />
                            <span class="card-date-badge">📅 ${safeDate}</span>
                            <div class="card-badges-row">
                                <span class="badge-trust ${trustTierClass}">🛡 ${trustScore}% MATCH</span>
                                <span class="badge-license">${safeLicense}</span>
                            </div>
                        </div>
                        <div class="card-details">
                            <div class="card-title" title="${safeTitle}">${safeTitle}</div>
                            <div class="card-author">© ${safeAuthor}</div>
                            <a href="${item.source_url}" target="_blank" class="card-source-link" onclick="event.stopPropagation()">Открыть источник ↗</a>
                        </div>
                    </div>
                `;
            });
            cardsHtml += '</div>';
            bodyHtml = cardsHtml;
        } else {
            bodyHtml = `
                <div class="honest-uncertainty-banner">
                    <div class="banner-icon">ℹ</div>
                    <div>
                        <strong>Принцип честной неопределенности:</strong> В открытых проверенных репозиториях (Wikimedia Commons, Openverse, Mapillary) 
                        ${highTrustOnly ? 'не обнаружено фото с порогом достоверности ≥ 80%.' : 'не найдено подтвержденных снимков данной категории с порогом классификатора CLIP ≥ 0.65.'} 
                        Сервис намеренно понижает индекс полноты вместо выдачи неподтвержденных стоковых изображений.
                    </div>
                </div>
            `;
        }

        block.innerHTML = `
            <div class="cat-top-bar">
                <div class="cat-name-title">${cat.title}</div>
                <span class="badge-status ${statusBadgeClass}">${statusBadgeText}</span>
            </div>
            <div class="cat-desc-text">${cat.description}</div>
            ${bodyHtml}
        `;

        container.appendChild(block);
    }
}

if (categoryFilterTabs) {
    categoryFilterTabs.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            categoryFilterTabs.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeCategoryFilter = tab.getAttribute('data-cat');
            if (currentProfile) {
                renderCategories(currentProfile.categories);
            }
        });
    });
}

if (filterHighTrustOnly) {
    filterHighTrustOnly.addEventListener('change', () => {
        if (currentProfile) {
            renderCategories(currentProfile.categories);
        }
    });
}

function openMediaModal(itemId) {
    if (!currentProfile || !attributionModal) return;
    let found = null;
    let categoryName = '';

    for (const [catKey, cat] of Object.entries(currentProfile.categories || {})) {
        const item = (cat.items || []).find(it => it.id === itemId);
        if (item) {
            found = item;
            categoryName = cat.title;
            break;
        }
    }

    if (!found) return;

    if (modalImage) modalImage.src = found.preview_url;
    if (modalCategory) modalCategory.textContent = categoryName;
    if (modalTrustScore) modalTrustScore.textContent = `${found.trust_score || 85}% (${found.trust_label || 'Подтверждено'})`;
    if (modalConfidence) modalConfidence.textContent = `${found.confidence || 0.88}`;
    if (modalDate) modalDate.textContent = found.date_published || '2024';
    if (modalLicense) modalLicense.textContent = found.license_name || 'CC-BY-SA 4.0';
    if (modalAuthor) modalAuthor.textContent = found.author || 'Wikimedia Commons';
    if (modalPhash) modalPhash.textContent = found.phash || 'a1b2c3d4e5f6';
    if (modalSourceUrl) {
        modalSourceUrl.href = found.source_url || '#';
        modalSourceUrl.textContent = found.source_domain || 'Открыть источник';
    }

    attributionModal.classList.remove('hidden');
}

const closeAttributionModal = () => {
    if (attributionModal) attributionModal.classList.add('hidden');
};
if (modalCloseBtn) modalCloseBtn.onclick = closeAttributionModal;
if (modalCloseBtn2) modalCloseBtn2.onclick = closeAttributionModal;
if (attributionModal) {
    attributionModal.addEventListener('click', (e) => {
        if (e.target === attributionModal) closeAttributionModal();
    });
}

if (aboutServiceBtn && aboutServiceModal) {
    aboutServiceBtn.addEventListener('click', () => {
        aboutServiceModal.classList.remove('hidden');
    });

    const closeAbout = () => aboutServiceModal.classList.add('hidden');
    if (aboutServiceCloseBtn) aboutServiceCloseBtn.onclick = closeAbout;
    if (aboutServiceCloseBtn2) aboutServiceCloseBtn2.onclick = closeAbout;
    aboutServiceModal.addEventListener('click', (e) => {
        if (e.target === aboutServiceModal) closeAbout();
    });
}

function openComparisonModal() {
    if (!compareModal) return;
    compareModal.classList.remove('hidden');
}

function closeComparisonModal() {
    if (!compareModal) return;
    compareModal.classList.add('hidden');
}

if (openCompareBtn) openCompareBtn.addEventListener('click', openComparisonModal);
if (compareModalCloseBtn) compareModalCloseBtn.addEventListener('click', closeComparisonModal);
if (compareModalCloseBtn2) compareModalCloseBtn2.addEventListener('click', closeComparisonModal);
if (compareModal) {
    compareModal.addEventListener('click', (e) => {
        if (e.target === compareModal) closeComparisonModal();
    });
}

if (compareForm) {
    compareForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const q1 = compareUniv1Input.value.trim();
        const q2 = compareUniv2Input.value.trim();
        if (!q1 || !q2) return;

        if (!window.tcAuth.isAuthenticated()) {
            closeComparisonModal();
            window.tcAuth.requireAuth(() => {
                openComparisonModal();
            });
            return;
        }

        if (compareLoading) compareLoading.classList.remove('hidden');
        if (compareResultsTable) compareResultsTable.classList.add('hidden');

        try {
            const data = await window.tcApi.compare(q1, q2);
            if (compareLoading) compareLoading.classList.add('hidden');
            renderCompareTable(data);
            if (compareResultsTable) compareResultsTable.classList.remove('hidden');
        } catch (err) {
            if (compareLoading) compareLoading.classList.add('hidden');
            alert(err.message || 'Ошибка при сравнении');
        }
    });
}

function renderCompareTable(data) {
    if (!compareResultsTable) return;
    const u1 = data.univ1;
    const u2 = data.univ2;

    compareResultsTable.innerHTML = `
        <table class="compare-table">
            <thead>
                <tr>
                    <th>Параметр</th>
                    <th>${escapeHtml(u1.name)}</th>
                    <th>${escapeHtml(u2.name)}</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Город / Локация</strong></td>
                    <td>${escapeHtml(u1.city)}</td>
                    <td>${escapeHtml(u2.city)}</td>
                </tr>
                <tr>
                    <td><strong>Полнота верификации</strong></td>
                    <td><span class="badge badge-verified">${u1.coverage_pct}%</span> (${u1.categories_verified_count}/8 зон)</td>
                    <td><span class="badge badge-verified">${u2.coverage_pct}%</span> (${u2.categories_verified_count}/8 зон)</td>
                </tr>
                <tr>
                    <td><strong>Подтвержденных фото</strong></td>
                    <td>${u1.verified_photos_count} фото</td>
                    <td>${u2.verified_photos_count} фото</td>
                </tr>
                <tr>
                    <td><strong>Индекс достоверности</strong></td>
                    <td>${u1.trust_index}%</td>
                    <td>${u2.trust_index}%</td>
                </tr>
                <tr>
                    <td><strong>Расстояние до центра</strong></td>
                    <td>${u1.distance_to_center_km} км (${u1.transit_time})</td>
                    <td>${u2.distance_to_center_km} км (${u2.transit_time})</td>
                </tr>
                <tr>
                    <td><strong>Бюджет студента</strong></td>
                    <td>${escapeHtml(u1.monthly_cost)}</td>
                    <td>${escapeHtml(u2.monthly_cost)}</td>
                </tr>
                <tr>
                    <td><strong>Климат (лето)</strong></td>
                    <td>${escapeHtml(u1.climate)}</td>
                    <td>${escapeHtml(u2.climate)}</td>
                </tr>
            </tbody>
        </table>
    `;
}

function saveAuditToHistory(data) {
    if (!data || !data.canonical_name) return;
    try {
        let history = JSON.parse(localStorage.getItem('tc_audits') || '[]');
        history = history.filter(item => item.name.toLowerCase() !== data.canonical_name.toLowerCase());
        history.unshift({
            id: data.profile_id,
            name: data.canonical_name,
            location: `${data.city}, ${data.country}`,
            date: new Date().toLocaleDateString('ru-RU'),
            time: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
            coverage: data.rules_summary ? `${data.rules_summary.verification_coverage_percent}%` : '85%'
        });
        if (history.length > 25) history = history.slice(0, 25);
        localStorage.setItem('tc_audits', JSON.stringify(history));
    } catch (e) {
        console.warn('Failed to save audit history:', e);
    }
}

function renderAuditsHistory() {
    if (!myAuditsList) return;
    let history = [];
    try {
        history = JSON.parse(localStorage.getItem('tc_audits') || '[]');
    } catch {
        history = [];
    }

    if (history.length === 0) {
        myAuditsList.innerHTML = `
            <div class="empty-history-notice">
                <p>История проверок пока пуста.</p>
                <span>Проверьте любой университет, и он сохранится здесь.</span>
            </div>
        `;
        return;
    }

    let html = '<div class="audits-history-list">';
    history.forEach(item => {
        html += `
            <div class="audit-history-item">
                <div class="audit-hist-main">
                    <h5 class="audit-hist-name">${escapeHtml(item.name)}</h5>
                    <div class="audit-hist-sub">
                        <span>📍 ${escapeHtml(item.location)}</span>
                        <span>🗓️ ${escapeHtml(item.date)} ${escapeHtml(item.time || '')}</span>
                    </div>
                </div>
                <button type="button" class="btn-sm-open" data-hist-query="${escapeHtml(item.name)}">
                    Открыть отчет ↗
                </button>
            </div>
        `;
    });
    html += '</div>';
    myAuditsList.innerHTML = html;

    myAuditsList.querySelectorAll('.btn-sm-open').forEach(btn => {
        btn.addEventListener('click', () => {
            const q = btn.getAttribute('data-hist-query');
            if (q) {
                closeMyAudits();
                switchToAuditView(q);
            }
        });
    });
}

function openMyAudits() {
    if (!myAuditsModal) return;
    renderAuditsHistory();
    const dropdown = document.getElementById('accountDropdown');
    if (dropdown) dropdown.classList.add('hidden');
    myAuditsModal.classList.remove('hidden');
}

function closeMyAudits() {
    if (!myAuditsModal) return;
    myAuditsModal.classList.add('hidden');
}

if (myAuditsBtn) myAuditsBtn.addEventListener('click', openMyAudits);
if (myAuditsCloseBtn) myAuditsCloseBtn.addEventListener('click', closeMyAudits);
if (myAuditsCloseBtn2) myAuditsCloseBtn2.addEventListener('click', closeMyAudits);
if (myAuditsModal) {
    myAuditsModal.addEventListener('click', (e) => {
        if (e.target === myAuditsModal) closeMyAudits();
    });
}

if (clearAuditsHistoryBtn) {
    clearAuditsHistoryBtn.addEventListener('click', () => {
        localStorage.removeItem('tc_audits');
        renderAuditsHistory();
        showToast('История проверок очищена');
    });
}

function showToast(message, duration = 3500) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, duration);
}
window.showToast = showToast;

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}
window.escapeHtml = escapeHtml;

const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const mobileNavOverlay = document.getElementById('mobileNavOverlay');
const mobileNavPanel = document.getElementById('mobileNavPanel');
const mobileNavClose = document.getElementById('mobileNavClose');

function openMobileMenu() {
    if (mobileNavOverlay) {
        mobileNavOverlay.style.display = 'block';
        requestAnimationFrame(() => mobileNavOverlay.classList.add('open'));
    }
    if (mobileNavPanel) mobileNavPanel.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeMobileMenu() {
    if (mobileNavOverlay) {
        mobileNavOverlay.classList.remove('open');
        setTimeout(() => { mobileNavOverlay.style.display = 'none'; }, 300);
    }
    if (mobileNavPanel) mobileNavPanel.classList.remove('open');
    document.body.style.overflow = '';
}

if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', openMobileMenu);
if (mobileNavClose) mobileNavClose.addEventListener('click', closeMobileMenu);
if (mobileNavOverlay) mobileNavOverlay.addEventListener('click', closeMobileMenu);

const mobileNavHome = document.getElementById('mobileNavHome');
const mobileNavAudit = document.getElementById('mobileNavAudit');
const mobileNavCompare = document.getElementById('mobileNavCompare');
const mobileNavAbout = document.getElementById('mobileNavAbout');
const mobileLoginBtn = document.getElementById('mobileLoginBtn');

function updateMobileNavActive(activeBtn) {
    document.querySelectorAll('.mobile-nav-item').forEach(b => b.classList.remove('active'));
    if (activeBtn) activeBtn.classList.add('active');
}

if (mobileNavHome) {
    mobileNavHome.addEventListener('click', () => {
        switchToLandingView();
        updateMobileNavActive(mobileNavHome);
        closeMobileMenu();
    });
}

if (mobileNavAudit) {
    mobileNavAudit.addEventListener('click', () => {
        switchToAuditView();
        updateMobileNavActive(mobileNavAudit);
        closeMobileMenu();
    });
}

if (mobileNavCompare) {
    mobileNavCompare.addEventListener('click', () => {
        if (compareModal) compareModal.classList.remove('hidden');
        closeMobileMenu();
    });
}

if (mobileNavAbout) {
    mobileNavAbout.addEventListener('click', () => {
        if (aboutServiceModal) aboutServiceModal.classList.remove('hidden');
        closeMobileMenu();
    });
}

if (mobileLoginBtn) {
    mobileLoginBtn.addEventListener('click', () => {
        const authModal = document.getElementById('authModal');
        if (authModal) authModal.classList.remove('hidden');
        closeMobileMenu();
    });
}

const mobileLangGroup = document.getElementById('mobileLangGroup');
if (mobileLangGroup) {
    mobileLangGroup.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang');
            if (window.tcI18n) {
                window.tcI18n.setLanguage(lang);
            }
            mobileLangGroup.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll('#langSwitcherGroup .lang-btn').forEach(b => {
                b.classList.toggle('active', b.getAttribute('data-lang') === lang);
            });
        });
    });
}

function updateMobileUserSection() {
    const mobileUserSection = document.getElementById('mobileUserSection');
    if (!mobileUserSection) return;

    const storedUser = window.tcAuth ? window.tcAuth.getStoredUser() : null;
    if (storedUser) {
        mobileUserSection.innerHTML = `
            <div class="mobile-nav-user-info">
                <span class="user-avatar">${(storedUser.name || 'U')[0].toUpperCase()}</span>
                <div class="mobile-nav-user-details">
                    <span class="mobile-user-name">${escapeHtml(storedUser.name)}</span>
                    <span class="mobile-user-credits">🪙 ${storedUser.credits || 0} кредитов</span>
                </div>
            </div>
            <button id="mobileTopUpBtn" class="mobile-nav-item" type="button">
                <span>🪙</span>
                <span data-i18n="nav_topup">Пополнить кредиты</span>
            </button>
            <button id="mobileHistoryBtn" class="mobile-nav-item" type="button">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span data-i18n="nav_history">История проверок</span>
            </button>
            <button id="mobileLogoutBtn" class="mobile-nav-item" type="button" style="color: #f87171;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
                <span data-i18n="nav_logout">Выйти</span>
            </button>
        `;

        const mobileTopUpBtn = document.getElementById('mobileTopUpBtn');
        const mobileHistoryBtn = document.getElementById('mobileHistoryBtn');
        const mobileLogoutBtn = document.getElementById('mobileLogoutBtn');

        if (mobileTopUpBtn) {
            mobileTopUpBtn.addEventListener('click', () => {
                const topUpModal = document.getElementById('topUpModal');
                if (topUpModal) topUpModal.classList.remove('hidden');
                closeMobileMenu();
            });
        }

        if (mobileHistoryBtn) {
            mobileHistoryBtn.addEventListener('click', () => {
                if (myAuditsModal) myAuditsModal.classList.remove('hidden');
                closeMobileMenu();
            });
        }

        if (mobileLogoutBtn) {
            mobileLogoutBtn.addEventListener('click', () => {
                if (window.tcAuth) window.tcAuth.logout();
                closeMobileMenu();
            });
        }

        if (window.tcI18n) window.tcI18n.applyTranslationsToDOM();
    } else {
        mobileUserSection.innerHTML = `
            <button id="mobileLoginBtn" class="mobile-nav-item" type="button">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <span data-i18n="nav_login_register">Вход / Регистрация</span>
            </button>
        `;
        const newMobileLoginBtn = document.getElementById('mobileLoginBtn');
        if (newMobileLoginBtn) {
            newMobileLoginBtn.addEventListener('click', () => {
                const authModal = document.getElementById('authModal');
                if (authModal) authModal.classList.remove('hidden');
                closeMobileMenu();
            });
        }
        if (window.tcI18n) window.tcI18n.applyTranslationsToDOM();
    }
}
window.updateMobileUserSection = updateMobileUserSection;

document.addEventListener('DOMContentLoaded', () => {
    if (window.tcI18n) {
        window.tcI18n.applyTranslationsToDOM();
    }

    if (window.tcAuth) {
        window.tcAuth.initAuth();
    }

    if (window.tcCredits) {
        window.tcCredits.initCredits();
    }

    if (window.tcLanding) {
        window.tcLanding.initLanding();
    }

    updateMobileUserSection();

    switchToLandingView();
});

window.tcApp = {
    switchToLandingView,
    switchToAuditView,
    triggerAudit,
    startAnalysis,
    updateMobileUserSection
};
